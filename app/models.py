from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(32), nullable=False)

class InspectionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    result = db.Column(db.String(16))
    false_alarm = db.Column(db.Boolean, default=False)
    missed_defect = db.Column(db.Boolean, default=False)
    annotation = db.Column(db.Text)
    disposition = db.Column(db.String(16))
    # Legacy: image_path (keep for compatibility)
    image_path = db.Column(db.String(256))
    # New: explicit original and processed image paths
    orig_path = db.Column(db.String(256))
    proc_path = db.Column(db.String(256))
    user = db.relationship('User')

# Production-level query log
class QueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    endpoint = db.Column(db.String(128))
    username = db.Column(db.String(80))
    params_json = db.Column(db.Text)
    result_json = db.Column(db.Text)
