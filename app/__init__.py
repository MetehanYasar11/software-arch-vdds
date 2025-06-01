from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Serve static files from project-level static directory (using cwd to ensure correct path)
    project_root = os.getcwd()
    static_dir = os.path.abspath(os.path.join(project_root, 'static'))
    app = Flask(__name__, static_folder=static_dir, static_url_path='/static', template_folder='templates')
    app.config['SECRET_KEY'] = 'replace-this-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/vdds.db'
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(app.root_path, '../static/uploads'))
    db.init_app(app)
    login_manager.init_app(app)

    # Ensure upload and data folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.abspath(os.path.join(app.root_path, '../data')), exist_ok=True)

    with app.app_context():
        try:
            from . import routes
        except ImportError:
            import routes
        db.create_all()
        # Create default users if not exist
        try:
            from .models import User
        except ImportError:
            from models import User
        from werkzeug.security import generate_password_hash
        if not User.query.filter_by(username='officer').first():
            db.session.add(User(username='officer', password=generate_password_hash('officerpass'), role='QualityControlOfficer'))
        if not User.query.filter_by(username='manager').first():
            db.session.add(User(username='manager', password=generate_password_hash('managerpass'), role='QualityControlManager'))
        db.session.commit()
    # Register blueprint
    try:
        from .routes import bp
    except ImportError:
        from routes import bp
    app.register_blueprint(bp)
    return app
