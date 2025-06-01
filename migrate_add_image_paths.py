# Lightweight migration for adding orig_path and proc_path columns

from app import create_app, db
from app.models import InspectionLog
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Add columns if not exist (SQLite only)
    try:
        db.session.execute(text('ALTER TABLE inspection_log ADD COLUMN orig_path VARCHAR(256)'))
    except Exception as e:
        if 'duplicate column name' not in str(e):
            print('orig_path:', e)
    try:
        db.session.execute(text('ALTER TABLE inspection_log ADD COLUMN proc_path VARCHAR(256)'))
    except Exception as e:
        if 'duplicate column name' not in str(e):
            print('proc_path:', e)
    db.session.commit()
    print('Migration complete.')
