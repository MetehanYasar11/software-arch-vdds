from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
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
    processed_img = db.Column(db.String(256), nullable=True)  # New: processed image filename
    user = db.relationship('User')

# Production-level query log

class QueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    endpoint = db.Column(db.String(128))
    username = db.Column(db.String(80))
    params_json = db.Column(db.Text)
    result_json = db.Column(db.Text)

# SystemSetting for global config (e.g. current model)
class SystemSetting(db.Model):
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(256))

    @classmethod
    def get(cls, key, default=None):
        rec = cls.query.get(key)
        return rec.value if rec else default

    @classmethod
    def set(cls, key, val):
        rec = cls.query.get(key) or cls(key=key)
        rec.value = val
        db.session.add(rec)
        db.session.commit()
