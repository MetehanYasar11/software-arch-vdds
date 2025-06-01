
# --- YOLOv8/Ultralytics Real Detection Engine ---
import threading
import json
import torch
from ultralytics import YOLO
import cv2
import os

_model_lock = threading.Lock()
_model_instance = None


# Simpler singleton for YOLOv8/YOLOv5 fallback
_model = None
import logging
logging.basicConfig(level=logging.DEBUG)

def _get_model():
    global _model
    if _model is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model_path = os.path.join('models', 'yolov8n_crack.pt')
        if not os.path.exists(model_path):
            model_path = os.path.join('models', 'yolov5nu.pt')
        logging.debug(f"[YOLO] Loading model from: {model_path} on device: {device}")
        try:
            _model = YOLO(model_path)
            _model.to(device)
            logging.debug(f"[YOLO] Model loaded: {_model}")
        except Exception as e:
            logging.error(f"[YOLO] Model load failed: {e}")
            raise
    return _model


def detect_defects(image_path):
    import cv2
    img = cv2.imread(image_path)
    if img is None:
        logging.error(f"[YOLO] Could not read image: {image_path}")
        raise FileNotFoundError(f"Image not found: {image_path}")
    h, w = img.shape[:2]
    model = _get_model()
    logging.debug(f"[YOLO] Running model.predict on image: {image_path} (shape: {img.shape})")
    try:
        results = model.predict(source=img, conf=0.25, iou=0.45, verbose=False)[0]
        logging.debug(f"[YOLO] model.predict results: {results}")
    except Exception as e:
        logging.error(f"[YOLO] model.predict failed: {e}")
        raise
    dets = []
    for box, cls_id, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
        x1, y1, x2, y2 = map(int, box.cpu().tolist())
        label = model.model.names[int(cls_id)]
        dets.append({
            "class": label,
            "confidence": float(conf),
            "bbox": [x1, y1, x2, y2]
        })
    logging.debug(f"[YOLO] detect_defects: {len(dets)} detections found.")
    return {"result": "DEFECT" if dets else "OK", "detections": dets}
        


# draw_bboxes is now in utils.py
