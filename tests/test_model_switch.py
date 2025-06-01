import pytest
from app import create_app, db
from app.models import User, SystemSetting
from flask import url_for
from pathlib import Path

@pytest.fixture
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    with app.app_context():
        db.create_all()
        # Create manager user
        u = User(username='manager', password='$pbkdf2-sha256$29000$test$test', role='QualityControlManager')
        u.set_password = lambda x: None  # stub
        u.check_password = lambda x: x == 'managerpass'
        db.session.add(u)
        db.session.commit()
    with app.test_client() as client:
        yield client

def test_model_switch(client):
    # Login as manager
    rv = client.post('/login', data={'username': 'manager', 'password': 'managerpass'}, follow_redirects=True)
    assert b'Dashboard' in rv.data or b'dashboard' in rv.data
    # Place a fake model file
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    (models_dir / 'testmodel.pt').write_text('fake')
    # Activate model
    rv = client.post('/activate_model', data={'model_name': 'testmodel.pt', 'password': 'managerpass'}, follow_redirects=True)
    assert b'activated' in rv.data
    # Check SystemSetting updated
    with client.application.app_context():
        assert SystemSetting.get('current_model') == 'testmodel.pt'
    # Clean up
    (models_dir / 'testmodel.pt').unlink()
