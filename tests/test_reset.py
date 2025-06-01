import os
import pytest
from app import create_app, db
from app.models import InspectionLog, QueryLog

def test_manager_reset(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    # Insert dummy data
    with app.app_context():
        db.session.add(InspectionLog(user_id=1, result='OK', annotation='[]'))
        db.session.add(QueryLog(endpoint='/test', username='manager', params_json='{}', result_json='{}'))
        db.session.commit()
    # Login as manager
    client.post('/', data={'username': 'manager', 'password': 'managerpass'}, follow_redirects=True)
    # Post to /reset with correct password
    resp = client.post('/reset', data={'password': 'managerpass'}, follow_redirects=True)
    assert b'System reset to factory defaults.' in resp.data
    # Check DB is empty
    with app.app_context():
        assert InspectionLog.query.count() == 0
        assert QueryLog.query.count() == 0
