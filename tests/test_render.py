import os
import sys
import cv2
import numpy as np
import pytest
from PIL import Image

# Ensure app/ is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from detection import detect_defects, draw_boxes

def test_render_green_boxes():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/uploads/test_input.jpg'))
    if not os.path.exists(img_path):
        pytest.skip('test_input.jpg not found')
    # Run detection
    result = detect_defects(img_path)
    dets = result['detections']
    # Copy image to processed path
    processed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/processed/test_input_rendered.jpg'))
    img = Image.open(img_path)
    img.save(processed_path)
    draw_boxes(processed_path, dets, color='lime', width=4)
    # Load processed image and count green rectangles
    img_cv = cv2.imread(processed_path)
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
    # Lime/green mask
    lower = np.array([40, 100, 100])
    upper = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # We expect at least as many green rectangles as detections
    assert len(contours) >= len(dets), f"Expected at least {len(dets)} green rectangles, found {len(contours)}"
