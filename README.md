# VDDS Prototype

Course: CSE344 – Software Engineering (Spring 2025)
Project: AI-Based Visual Defect Detection System – Prototype Tool
Prepared by: Metehan Yaşar (20223505003-2D)

---

📦 Repository Structure

vdds_prototype/
├── test_input.jpg
├── models/
│   └── yolov5n.pt
├── requirements.txt
├── src/
│   ├── app.py
│   ├── detection.py
│   ├── feedback.py
│   └── templates/
│       ├── officer_dashboard.html
│       ├── manager_dashboard.html
│       └── feedback.html
└── README.md

---

🛠️ Setup & Installation

1. Python environment
   Open Anaconda Prompt and create & activate a new environment:

   conda create -n vdds_env python=3.9 -y
   conda activate vdds_env
   python -m pip install --upgrade pip

2. Project dependencies
   From the project root directory:

   pip install -r requirements.txt

3. YOLOv5n model
   Place the pretrained weights in models/yolov5n.pt. If you don’t have it:

   curl -L -o models/yolov5n.pt \
     https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5n.pt

---

▶️ Running the Application

python src/app.py

Then open your browser at:
http://127.0.0.1:5000

---

🔐 Login Credentials

- Quality Control Officer
  - Username: qofficer
  - Password: 1234

- Quality Control Manager
  - Username: qmanager
  - Password: 1234

---

🚀 Usage

1. As QC Officer
   - Select “Ürün Görüntüsü Seç”
   - Click “Analiz Et”
   - View the detection result
   - If needed, submit “Yanlış Alarm” or “Kusur Atlandı” feedback

2. As QC Manager
   - Log in with the manager account
   - Navigate to Yönetici Paneli
   - Review the summary of feedback and defect metrics

---

📷 Test Input Image

- A sample image for testing is provided as `test_input.jpg` in the repository root. Use this file to verify the detection pipeline.

---

📦 Packaging

All code, folder structure and this README are ready to be archived as:

vdds_prototip.rar

You can download, extract and run immediately.

---

İyi çalışmalar!
