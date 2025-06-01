import time

from PIL import Image, ImageDraw
import random
import time

def detect_defects_stub(image_path):
    """
    Simulate defect detection. Draws stub bounding box and returns fake detections.
    # TODO replace with real model weights and inference logic
    """
    time.sleep(1.5)
    # Fake result: randomly OK or DEFECT
    result = random.choice(['OK', 'DEFECT'])
    # Load image and compute a single box inset by 10%
    img = Image.open(image_path)
    w, h = img.size
    x1, y1 = int(w * 0.1), int(h * 0.1)
    x2, y2 = int(w * 0.9), int(h * 0.9)
    boxes = [(x1, y1, x2, y2)]
    return {'result': result, 'boxes': boxes}

def draw_boxes(image_path, boxes, color='green', width=4):
    """
    Draws rectangular boxes on the image at image_path.
    """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    for (x1, y1, x2, y2) in boxes:
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
    img.save(image_path)
