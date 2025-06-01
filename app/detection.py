import time

from PIL import Image, ImageDraw
import random
import time

def detect_defects_stub(image_path):
    """
    Simulate defect detection. Returns fake detections in YOLO-style format.
    # TODO replace with real model weights and inference logic
    """
    time.sleep(1.5)
    # Fake result: randomly OK or DEFECT
    result = random.choice(['OK', 'DEFECT'])
    # Fake detection: one box, random class/confidence
    img = Image.open(image_path)
    w, h = img.size
    x1, y1 = int(w * 0.1), int(h * 0.1)
    x2, y2 = int(w * 0.9), int(h * 0.9)
    detection = {
        'class': random.choice(['crack', 'spot', 'none']),
        'confidence': round(random.uniform(0.7, 0.99), 2),
        'bbox': [x1, y1, x2, y2]
    }
    return {'result': result, 'detections': [detection]}

def draw_boxes(image_path, detections, color='green', width=4):
    """
    Draws YOLO-style boxes with label:confidence on the image at image_path.
    """
    import cv2
    img = cv2.imread(image_path)
    if img is None:
        return
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        label = det.get('class', 'obj')
        conf = det.get('confidence', 0)
        text = f"{label}:{conf:.2f}"
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), width)
        cv2.putText(img, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.imwrite(image_path, img)
