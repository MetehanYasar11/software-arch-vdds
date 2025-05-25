# src/detection.py

import os
import cv2
from ultralytics import YOLO

# Tek sefer modele yükleme (models/yolov5n.pt dosyasının orada olduğundan emin olun)
MODEL = YOLO('models/yolov5nu.pt')

def analyze_image(input_path: str, output_dir: str = 'static/processed/') -> str:
    """
    input_path: yüklenen resmin yolu
    output_dir: işaretlenmiş çıktının kaydedileceği klasör
    return: işlenmiş görüntünün yeni dosya yolu
    """
    # 1) Çıktı klasörünü hazırla
    os.makedirs(output_dir, exist_ok=True)

    # 2) Model inferansı (liste döner, biz ilk sonucu alıyoruz)
    results = MODEL(input_path)  
    res = results[0]

    # 3) Orijinal görüntüyü OpenCV ile oku
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Görüntü okunamadı: {input_path}")

    # 4) Tespit edilen kutuları çiz
    # res.boxes.xyxy, res.boxes.cls, res.boxes.conf içerir
    for box in res.boxes:
        # Koordinatları al
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        # Sınıf etiketi
        label = MODEL.names[cls_id] if MODEL.names else str(cls_id)
        # Kutu çizimi (kırmızı)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # Etiket ve skor
        text = f"{label} {conf:.2f}"
        cv2.putText(img, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # 5) İşlenmiş görüntüyü kaydet
    out_path = os.path.join(output_dir, os.path.basename(input_path))
    cv2.imwrite(out_path, img)

    return out_path
