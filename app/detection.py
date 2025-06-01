
# --- YOLOv8/Ultralytics Real Detection Engine ---
import threading
import json
import torch
from ultralytics import YOLO
import cv2
import os

_model_lock = threading.Lock()
_model_instance = None

def _get_model():
    global _model_instance
    with _model_lock:
        if _model_instance is None:
            try:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                # Try v8n first, fallback to v5n
                model_path = os.path.join('models', 'yolov8n_crack.pt')
                if not os.path.exists(model_path):
                    model_path = os.path.join('models', 'yolov5nu.pt')
                _model_instance = YOLO(model_path)
                _model_instance.to(device)
            except Exception as e:
                print(f"[YOLO] Model load failed: {e}")
                _model_instance = None
        return _model_instance

def detect_defects(image_path):
    """
    Run YOLO detection on the given image. Returns list of dicts:
    {class, confidence, bbox} where class is COCO string.
    Handles model load errors gracefully (fallback to stub).
    """
    from PIL import Image
    img = Image.open(image_path)
    orig_w, orig_h = img.size
    model = _get_model()
    if model is None:
        raise RuntimeError('YOLO model could not be loaded. No fallback/stub bbox allowed in production.')

    # Optionally downscale for RAM, but keep track of scaling
    import os
    YOLO_IMAGE_MAX = int(os.environ.get('YOLO_IMAGE_MAX', 0))
    resize_ratio = 1.0
    img_for_pred = img
    if YOLO_IMAGE_MAX and (orig_w > YOLO_IMAGE_MAX or orig_h > YOLO_IMAGE_MAX):
        scale = YOLO_IMAGE_MAX / max(orig_w, orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        img_for_pred = img.resize((new_w, new_h))
        resize_ratio = scale
    try:
        # Use Ultralytics API to avoid internal resize if possible
        results = model.predict(img_for_pred, imgsz=(img_for_pred.height, img_for_pred.width), verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            names = r.names if hasattr(r, 'names') else model.names
            for box in boxes:
                cls_id = int(box.cls[0]) if hasattr(box.cls, '__len__') else int(box.cls)
                label = names[cls_id] if names and cls_id < len(names) else str(cls_id)
                conf = float(box.conf[0]) if hasattr(box.conf, '__len__') else float(box.conf)
                xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy, '__len__') else box.xyxy.cpu().numpy()
                # Rescale to original image size if needed
                if resize_ratio != 1.0:
                    x1, y1, x2, y2 = [int(round(coord / resize_ratio)) for coord in xyxy]
                else:
                    x1, y1, x2, y2 = [int(round(coord)) for coord in xyxy]
                # Clip to image bounds
                x1 = max(0, min(x1, orig_w-1))
                y1 = max(0, min(y1, orig_h-1))
                x2 = max(0, min(x2, orig_w-1))
                y2 = max(0, min(y2, orig_h-1))
                detections.append({
                    'class': label,
                    'confidence': round(conf, 2),
                    'bbox': [x1, y1, x2, y2]
                })
        result = 'DEFECT' if detections else 'OK'
        return {'result': result, 'detections': detections}
    except Exception as e:
        print(f"[YOLO] Detection failed: {e}")
        

def draw_boxes(image_path, detections, color='green', width=4):
    """
    Draws YOLO-style boxes with label:confidence on the image at image_path.
    """
    import cv2
    color_map = {
        'green': (0,255,0),
        'lime': (50,255,50),
        'red': (0,0,255),
        'blue': (255,0,0),
        'yellow': (0,255,255)
    }
    box_color = color_map.get(color, (0,255,0))
    img = cv2.imread(image_path)
    if img is None:
        return
    h, w = img.shape[:2]
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        # Clip to image bounds
        x1 = max(0, min(int(round(x1)), w-1))
        y1 = max(0, min(int(round(y1)), h-1))
        x2 = max(0, min(int(round(x2)), w-1))
        y2 = max(0, min(int(round(y2)), h-1))
        label = det.get('class', 'obj')
        conf = det.get('confidence', 0)
        text = f"{label}:{conf:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), box_color, width)
        cv2.putText(img, text, (x1, max(y1-10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)
    cv2.imwrite(image_path, img)
