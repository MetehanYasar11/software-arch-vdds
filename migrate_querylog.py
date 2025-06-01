# Script to create the QueryLog table in the existing SQLite DB
from app import create_app, db
from app.models import QueryLog

app = create_app()

with app.app_context():
    db.create_all()
    print("QueryLog table created (if not already present)")
