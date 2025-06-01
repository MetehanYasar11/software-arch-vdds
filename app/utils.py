import cv2
from uuid import uuid4
from pathlib import Path

def draw_bboxes(img_path, dets):
    img = cv2.imread(img_path)
    for d in dets:
        x1, y1, x2, y2 = map(int, d['bbox'])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{d['class']}:{d['confidence']:.2f}"
        cv2.putText(img, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    out_name = f"{uuid4().hex}.jpg"
    out_path = Path('static/processed') / out_name
    Path('static/processed').mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), img)
    return out_name
