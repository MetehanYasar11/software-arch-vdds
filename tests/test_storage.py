import os
import sys
import pytest
from uuid import uuid4
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from app import create_app, db
from app.models import InspectionLog

def test_inspect_storage(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    # Login as officer
    client.post('/', data={'username': 'officer', 'password': 'officerpass'}, follow_redirects=True)
    # Upload image
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/uploads/test_input.jpg'))
    if not os.path.exists(img_path):
        pytest.skip('test_input.jpg not found')
    with open(img_path, 'rb') as f:
        data = {'image': (BytesIO(f.read()), f'unique_{uuid4().hex[:8]}.jpg')}
        resp = client.post('/inspect', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert resp.status_code == 200
    # Submit feedback to commit to DB
    resp = client.post('/result', data={
        'false_alarm': 'on',
        'missed_defect': '',
        'annotation': 'test',
        'disposition': 'Accept'
    }, follow_redirects=True)
    assert resp.status_code == 200
    # Check last InspectionLog
    with app.app_context():
        log = InspectionLog.query.order_by(InspectionLog.id.desc()).first()
        assert log is not None
        assert log.orig_path and log.proc_path
        # Check files exist
        orig_file = os.path.abspath(os.path.join(app.root_path, '../static', log.orig_path))
        proc_file = os.path.abspath(os.path.join(app.root_path, '../static', log.proc_path))
        assert os.path.exists(orig_file), f"Original file missing: {orig_file}"
        assert os.path.exists(proc_file), f"Processed file missing: {proc_file}"
        # Ensure filenames are unique per request (simulate a second upload)
        # Upload again
        with open(img_path, 'rb') as f2:
            data2 = {'image': (BytesIO(f2.read()), f'unique_{uuid4().hex[:8]}.jpg')}
            client.post('/inspect', data=data2, content_type='multipart/form-data', follow_redirects=True)
            client.post('/result', data={
                'false_alarm': '',
                'missed_defect': 'on',
                'annotation': 'test2',
                'disposition': 'Rework'
            }, follow_redirects=True)
        log2 = InspectionLog.query.order_by(InspectionLog.id.desc()).first()
        assert log2 is not None
        assert log2.orig_path != log.orig_path, "orig_path should be unique per inspection"
        assert log2.proc_path != log.proc_path, "proc_path should be unique per inspection"
        assert os.path.exists(orig_file), f"Missing original: {orig_file}"
        assert os.path.exists(proc_file), f"Missing processed: {proc_file}"

        # Now do a second upload and ensure filenames differ
        with open(img_path, 'rb') as f2:
            data2 = {'image': (BytesIO(f2.read()), f'unique_{uuid4().hex[:8]}.jpg')}
            client.post('/inspect', data=data2, content_type='multipart/form-data', follow_redirects=True)
            client.post('/result', data={
                'false_alarm': '',
                'missed_defect': 'on',
                'annotation': 'test2',
                'disposition': 'Rework'
            }, follow_redirects=True)
        log2 = InspectionLog.query.order_by(InspectionLog.id.desc()).first()
        assert log2.orig_path != log.orig_path, "orig_path not unique"
        assert log2.proc_path != log.proc_path, "proc_path not unique"
