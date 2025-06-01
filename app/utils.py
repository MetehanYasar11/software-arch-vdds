import cv2
from uuid import uuid4
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG)

def draw_bboxes(orig_path, detections):
    img = cv2.imread(orig_path)
    if img is None:
        logging.error(f"[BBOX] Could not read image: {orig_path}")
        raise FileNotFoundError(f"Image not found: {orig_path}")
    logging.debug(f"[BBOX] {len(detections)} bbox(es) to draw.")
    if len(detections) == 0:
        logging.debug("[BBOX] No detections received!")
    for idx, d in enumerate(detections):
        logging.debug(f"[BBOX] bbox {idx}: {d}")
        x1, y1, x2, y2 = d["bbox"]
        label = f"{d['class']}:{d['confidence']:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(img, label, (x1, max(y1-6,10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    out_name = f"{uuid4().hex}.jpg"
    out_path = Path('static/processed')/out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), img)
    logging.debug(f"[BBOX] Output image saved as {out_path}")
    return out_name
