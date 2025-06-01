
import os
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_inspect_post(client):
    # First, login as officer
    login_resp = client.post('/', data={'username': 'officer', 'password': 'officerpass'}, follow_redirects=True)
    assert login_resp.status_code == 200
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/uploads/test_input.jpg'))
    if not os.path.exists(img_path):
        pytest.skip('test_input.jpg not found')
    with open(img_path, 'rb') as f:
        data = {'image': (f, 'test_input.jpg')}
        response = client.post('/inspect', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'No defects' not in html
