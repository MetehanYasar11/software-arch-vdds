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
from .detection import detect_defects_stub, draw_boxes
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
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            # Stub detection (TODO: replace with real inference)
            detection = detect_defects_stub(upload_path)
            # Save original and processed images
            session['last_image'] = filename
            # Ensure processed folder exists
            processed_dir = os.path.abspath(os.path.join(current_app.root_path, '../static/processed'))
            os.makedirs(processed_dir, exist_ok=True)
            processed_path = os.path.join(processed_dir, filename)
            shutil.copy(upload_path, processed_path)
            # Draw YOLO-style boxes with label:conf on processed image
            draw_boxes(processed_path, detection.get('detections', []), color='lime', width=4)
            session['processed_image'] = filename  # Only filename, not path
            session['last_result'] = detection['result']
            # Log the inspection request
            log_request(request, detection)
            return redirect(url_for('main.result'))
        flash('No file uploaded')
    return render_template('inspect.html')

@bp.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    if current_user.role != 'QualityControlOfficer':
        return redirect(url_for('main.dashboard'))
    filename = session.get('last_image')
    result = session.get('last_result')
    if not filename or not result:
        return redirect(url_for('main.inspect'))
    processed = session.get('processed_image')
    if request.method == 'POST':
        false_alarm = 'false_alarm' in request.form
        missed_defect = 'missed_defect' in request.form
        annotation = request.form.get('annotation', '')
        disposition = request.form.get('disposition')
        log = InspectionLog(
            user_id=current_user.id,
            result=result,
            false_alarm=false_alarm,
            missed_defect=missed_defect,
            annotation=annotation,
            disposition=disposition,
            image_path=filename
        )
        db.session.add(log)
        db.session.commit()
        # Log the feedback/submit request
        log_request(request, {'status': 'feedback_submitted', 'inspection_id': log.id})
        flash('Feedback submitted!')
        return redirect(url_for('main.inspect'))
    return render_template('result.html', filename=filename, processed=processed, result=result)

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
    writer.writerow(['ID', 'Timestamp', 'User', 'Result', 'FalseAlarm', 'MissedDefect', 'Annotation', 'Disposition', 'ImagePath'])
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
            log.image_path
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
