from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User, InspectionLog
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
            # Save processed image in static/processed/
            processed_dir = os.path.abspath(os.path.join(current_app.root_path, '../static/processed'))
            os.makedirs(processed_dir, exist_ok=True)
            processed_path = os.path.join(processed_dir, filename)
            shutil.copy(upload_path, processed_path)
            # Draw stub bounding boxes on processed image
            draw_boxes(processed_path, detection.get('boxes', []), color='lime', width=4)
            session['processed_image'] = filename  # Only filename, not path
            session['last_result'] = detection['result']
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
        flash('Feedback submitted!')
        return redirect(url_for('main.inspect'))
    return render_template('result.html', filename=filename, processed=processed, result=result)

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'QualityControlManager':
        return redirect(url_for('main.inspect'))
    logs = InspectionLog.query.all()
    total = len(logs)
    false_alarms = sum(1 for l in logs if l.false_alarm)
    missed = sum(1 for l in logs if l.missed_defect)
    disposition_counts = {'Accept': 0, 'Rework': 0, 'Scrap': 0}
    for l in logs:
        if l.disposition in disposition_counts:
            disposition_counts[l.disposition] += 1
    return render_template('dashboard.html', total=total, false_alarms=false_alarms, missed=missed, disposition_counts=disposition_counts, logs=logs)

@bp.route('/model', methods=['GET', 'POST'])
@login_required
def model():
    if current_user.role != 'QualityControlManager':
        return redirect(url_for('main.inspect'))
    if request.method == 'POST':
        flash('Model update stub! # TODO replace with real weight swap')
    return render_template('model.html')
