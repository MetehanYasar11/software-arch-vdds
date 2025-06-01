import cv2, json, pytest
from pathlib import Path
from app.detection import detect_defects
from app.utils import draw_bboxes

IMG = Path("test_input.jpg")

def test_coords_inside():
    dets_result = detect_defects(str(IMG))
    dets = dets_result['detections'] if isinstance(dets_result, dict) else dets_result
    img = cv2.imread(str(IMG))
    h, w = img.shape[:2]
    assert all(0 <= d["bbox"][0] < w and 0 < d["bbox"][2] <= w for d in dets)
    assert all(0 <= d["bbox"][1] < h and 0 < d["bbox"][3] <= h for d in dets)

def test_draw_bbox():
    dets_result = detect_defects(str(IMG))
    dets = dets_result['detections'] if isinstance(dets_result, dict) else dets_result
    out = draw_bboxes(str(IMG), dets)
    assert Path("static/processed", out).exists()
