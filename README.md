# AI-Based Visual Defect Detection System (VDDS)

## Overview
A Flask + SQLite + Docker prototype for visual defect detection in manufacturing, with role-based access, inspection logging, feedback, and manager dashboard. 

## Features
- User authentication (officer/manager roles)
- Image inspection with stubbed AI detection (≤2s response)
- Feedback form (false alarm, missed defect, annotation, disposition)
- Inspection logging (timestamp, user, result, flags, annotation, disposition, image path)
- Manager dashboard with stats and charts (Chart.js)
- Model update stub (manager only)
- Dockerised for easy deployment

## Setup

### 1. Local (pip)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
App runs at http://localhost:5000

### 2. Docker
```powershell
docker build -t vdds .
docker run -p 5000:5000 vdds
```

## Default Logins
- Officer: `officer` / `officerpass`
- Manager: `manager` / `managerpass`

## Usage Flow
1. Officer logs in, uploads image, reviews result, submits feedback.
2. All actions are logged.
3. Manager logs in to view dashboard and trigger model update stub.

## Project Structure
```
app/
  __init__.py  models.py  routes.py  detection.py
  templates/ base.html login.html inspect.html dashboard.html model.html
static/
  uploads/ ...
data/ (auto-created)
models/ (empty for now)
run.py
Dockerfile
requirements.txt
README.md
```

## TODO
- Replace detection stub in `app/detection.py` with real YOLO model weights and inference logic.
- Implement real model update logic in `/model` route.

## Assumptions
- All images are stored in `static/uploads/`.
- Only two roles exist: QualityControlOfficer and QualityControlManager.
- No email/password reset; default users are created on first run.
- All requirements from Analysis & Design reports are mapped as above. If any ambiguity, see this README for rationale.

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
