
import os
import sys
import pytest

# Ensure app/ is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from detection import detect_defects

def test_detect_defects_bus():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/uploads/test_input.jpg'))
    if not os.path.exists(img_path):
        pytest.skip('test_input.jpg not found')
    from PIL import Image
    result = detect_defects(img_path)
    assert 'detections' in result
    assert isinstance(result['detections'], list)
    # Must see at least one bus and one person in the detections
    classes = [det['class'] for det in result['detections']]
    assert any('bus' in c for c in classes), f"No 'bus' detected, got: {classes}"
    assert any('person' in c for c in classes), f"No 'person' detected, got: {classes}"
    # All bboxes must be within image bounds
    img = Image.open(img_path)
    w, h = img.size
    for det in result['detections']:
        x1, y1, x2, y2 = det['bbox']
        assert 0 <= x1 < x2 <= w, f"bbox x out of bounds: {det['bbox']} for image width {w}"
        assert 0 <= y1 < y2 <= h, f"bbox y out of bounds: {det['bbox']} for image height {h}"
