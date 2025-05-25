import csv
import os
from datetime import datetime

LOG_PATH = 'data/feedback_log.csv'

def init_feedback_log():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp','image','type','note'])

def record_feedback(image_name: str, fb_type: str, note: str = ''):
    """
    fb_type: 'false_positive' veya 'missed_defect'
    note: kullanıcının ek açıklaması
    """
    init_feedback_log()
    with open(LOG_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            image_name,
            fb_type,
            note
        ])
