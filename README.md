## System Reset (Factory Defaults)

Managers can reset the system to factory defaults from the dashboard:

- Deletes all inspection and query logs from the database
- Removes all uploaded and processed images
- Requires manager password confirmation
- Accessible only to managers from the dashboard (red “Reset All Data” button)

**How to use:**
1. Log in as manager
2. Click the red “Reset All Data” button under the pie chart
3. Enter your password in the modal and confirm
4. All data and images will be deleted, and a success message will be shown

**Note:** This action cannot be undone.
# AI-Based Visual Defect Detection System (VDDS)

## Overview
A Flask + SQLite + Docker prototype for visual defect detection in manufacturing, with role-based access, inspection logging, feedback, and manager dashboard. 

## Features
- User authentication (officer/manager roles)
- Image inspection with YOLOv8/YOLOv5n real detection (first run may download ~50MB weights)
  - Images are now processed at their native resolution for accurate bounding boxes. If you encounter GPU RAM issues, set the environment variable `YOLO_IMAGE_MAX=1024` (or another value) to downscale images consistently for detection. All bounding boxes and CSV annotations will still be reported in the original image's pixel coordinates.
- Feedback form (false alarm, missed defect, annotation, disposition)
- Inspection logging (timestamp, user, result, flags, annotation, disposition, image path)
- Manager dashboard with stats and charts (Chart.js)
- Model update stub (manager only)
- Dockerised for easy deployment


## Database Migration Note (vdds >= 2025-06)

**If you are upgrading from an earlier version:**

- The database schema now includes `orig_path` and `proc_path` columns in the `inspection_log` table for robust image storage.
- You must run the migration script to add these columns to your existing database:

```powershell
python migrate_add_image_paths.py
```

- If you encounter errors or want a clean start, you may delete `data/vdds.db` and restart the app to auto-create a fresh database (note: this will erase all previous inspection logs).

---
## Setup

### 1. Local (pip)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# First run may download YOLO weights (~50MB)
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

## Testing & CI

### Run tests
```powershell
pytest
```
or for quiet output:
```powershell
pytest -q
```

### Notes
- Running YOLO locally / first-time weight download may take 50 MB.
- If model download fails (offline), app will fallback to stub detection ("Model unavailable").
- All flows & CSV export now show real detection annotation JSON.

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
