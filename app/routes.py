from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User, InspectionLog, QueryLog
import json

# Helper to log every mutating request
def log_request(request, result):
    try:
        endpoint = request.endpoint or ''
        username = current_user.username if hasattr(current_user, 'username') else ''
        # Try to get JSON or form data, fallback to args
        if request.is_json:
            params = request.get_json(silent=True) or {}
        elif request.form:
            params = dict(request.form)
        else:
            params = dict(request.args)
        params_json = json.dumps(params, ensure_ascii=False)
        # Result can be dict or str
        if isinstance(result, dict):
            result_json = json.dumps(result, ensure_ascii=False)
        else:
            result_json = str(result)
        log = QueryLog(endpoint=endpoint, username=username, params_json=params_json, result_json=result_json)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Don't crash app if logging fails
        print(f"[QueryLog] Logging failed: {e}")
from .detection import detect_defects
from .utils import draw_bboxes
import os
import shutil
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask import Blueprint

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'QualityControlOfficer':
                return redirect(url_for('main.inspect'))
            else:
                return redirect(url_for('main.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/inspect', methods=['GET', 'POST'])
@login_required
def inspect():
    if current_user.role != 'QualityControlOfficer':
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        from uuid import uuid4
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('No file uploaded')
            return render_template('inspect.html')
        ext = file.filename.rsplit('.', 1)[-1].lower()
        uid = uuid4().hex[:8]
        orig_fname = f"{uid}_orig.{ext}"
        orig_rel = f"uploads/{orig_fname}"
        upload_dir = os.path.join(current_app.root_path, '../static/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, orig_fname)
        file.save(upload_path)
        dets_result = detect_defects(upload_path)
        dets = dets_result.get('detections', [])
        proc_name = draw_bboxes(upload_path, dets)
        proc_rel = f"processed/{proc_name}"
        # Save to DB immediately for traceability
        from .models import InspectionLog
        import datetime
        log = InspectionLog(
            user_id=current_user.id if hasattr(current_user, 'id') else None,
            result=dets_result.get('result', 'OK'),
            false_alarm=False,
            missed_defect=False,
            annotation=json.dumps(dets, ensure_ascii=False),
            disposition=None,
            orig_path=orig_rel,
            proc_path=proc_rel,
            image_path=orig_rel,
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        # Save relative names for template and session
        session['last_image'] = orig_rel
        session['processed_image'] = proc_rel
        session['last_result'] = dets_result.get('result', 'OK')
        session['last_detections'] = dets
        session['last_annotation_json'] = json.dumps(dets, ensure_ascii=False)
        session['last_uid'] = uid
        session['last_ext'] = ext
        session['last_inspection_id'] = log.id
        # Log the inspection request
        log_request(request, {'detections': dets, 'inspection_id': log.id})
        return redirect(url_for('main.result'))
    return render_template('inspect.html')

@bp.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    if current_user.role != 'QualityControlOfficer':
        return redirect(url_for('main.dashboard'))
    # Get last inspection from DB for full consistency
    inspection_id = session.get('last_inspection_id')
    from .models import InspectionLog
    log = None
    if inspection_id:
        log = InspectionLog.query.get(inspection_id)
    if not log:
        return redirect(url_for('main.inspect'))
    orig_path = log.orig_path
    proc_path = log.proc_path
    result = log.result
    detections = json.loads(log.annotation) if log.annotation else []
    annotation_json = log.annotation or ''
    uid = session.get('last_uid', '')
    ext = session.get('last_ext', '')
    # On POST, update feedback fields only
    if request.method == 'POST':
        false_alarm = 'false_alarm' in request.form
        missed_defect = 'missed_defect' in request.form
        annotation = request.form.get('annotation', '')
        disposition = request.form.get('disposition')
        # Update log with feedback
        log.false_alarm = false_alarm
        log.missed_defect = missed_defect
        log.annotation = annotation_json if annotation_json else annotation
        log.disposition = disposition
        db.session.commit()
        log_request(request, {'status': 'feedback_submitted', 'inspection_id': log.id})
        flash('Feedback submitted!')
        return redirect(url_for('main.inspect'))
    # Her zaman DB'den kutulu resmi üret (güncel bbox ile)
    from .utils import draw_bboxes
    import os
    orig_abs = os.path.join(current_app.root_path, '../static', orig_path)
    proc_abs = os.path.join(current_app.root_path, '../static', proc_path)
    if os.path.exists(orig_abs) and detections:
        # Her GET'te kutulu resmi tekrar üret (en güncel bbox ile)
        draw_bboxes(orig_abs, detections)
    return render_template('result.html', filename=orig_path, processed=proc_path, result=result, detections=detections, uid=uid)

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'QualityControlManager':
        return redirect(url_for('main.inspect'))
    logs = InspectionLog.query.order_by(InspectionLog.timestamp.desc()).all()
    total = len(logs)
    false_alarms = sum(1 for l in logs if l.false_alarm)
    missed = sum(1 for l in logs if l.missed_defect)
    disposition_counts = {'Accept': 0, 'Rework': 0, 'Scrap': 0}
    for l in logs:
        if l.disposition in disposition_counts:
            disposition_counts[l.disposition] += 1
    last_logs = logs[:10]
    return render_template('dashboard.html', total=total, false_alarms=false_alarms, missed=missed, disposition_counts=disposition_counts, last_logs=last_logs)

# Manager-only CSV export
import csv
from flask import send_file, make_response
import io

@bp.route('/export')
@login_required
def export_csv():
    if current_user.role != 'QualityControlManager':
        return redirect(url_for('main.inspect'))
    logs = InspectionLog.query.order_by(InspectionLog.timestamp.desc()).all()
    # Prepare CSV in memory
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Timestamp', 'User', 'Result', 'FalseAlarm', 'MissedDefect', 'Annotation', 'Disposition', 'OrigImg', 'ProcImg', 'ImagePath'])
    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp,
            log.user.username if log.user else '',
            log.result,
            log.false_alarm,
            log.missed_defect,
            log.annotation,
            log.disposition,
            log.orig_path or '',
            log.proc_path or '',
            log.image_path or ''
        ])
    output = make_response(si.getvalue())
    from datetime import datetime
    dt = datetime.now().strftime('%Y%m%d')
    output.headers["Content-Disposition"] = f"attachment; filename=vdds_full_log_{dt}.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

@bp.route('/model', methods=['GET', 'POST'])
@login_required
def model():
    if current_user.role != 'QualityControlManager':
        return redirect(url_for('main.inspect'))
    if request.method == 'POST':
        flash('Model update stub! # TODO replace with real weight swap')
    return render_template('model.html')
