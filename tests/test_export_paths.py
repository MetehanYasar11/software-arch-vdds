import os
import pytest
from app import create_app, db
from app.models import InspectionLog

def test_export_csv_processed_path(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    # Insert dummy inspection
    with app.app_context():
        insp = InspectionLog(
            user_id=1,
            result='DEFECT',
            false_alarm=False,
            missed_defect=False,
            annotation='[]',
            disposition='Accept',
            orig_path='uploads/dummy.jpg',
            proc_path='processed/dummy_proc.jpg',
            processed_img='dummy_proc.jpg',
        )
        db.session.add(insp)
        db.session.commit()
    # Login as manager
    client.post('/', data={'username': 'manager', 'password': 'managerpass'}, follow_redirects=True)
    # Download CSV
    resp = client.get('/export')
    assert resp.status_code == 200
    csv_text = resp.data.decode('utf-8')
    assert 'static/processed/dummy_proc.jpg' in csv_text
    assert 'ProcImage' in csv_text and 'OrigImage' in csv_text
    # Clean up
    with app.app_context():
        db.session.query(InspectionLog).delete()
        db.session.commit()
