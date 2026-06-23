"""
Add adult_count and child_count columns to transfer_orders table.
Run: python scripts/migrate_add_passenger_count.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    conn = db.engine.connect()

    if db.engine.name == 'sqlite':
        result = conn.execute(text("PRAGMA table_info(transfer_orders)"))
        columns = [row[1] for row in result]
    else:
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'transfer_orders'"
        ))
        columns = [row[0] for row in result]

    if 'adult_count' not in columns:
        conn.execute(text("ALTER TABLE transfer_orders ADD COLUMN adult_count INTEGER DEFAULT 1"))
        print("Added adult_count column")
    else:
        print("adult_count column already exists")

    if 'child_count' not in columns:
        conn.execute(text("ALTER TABLE transfer_orders ADD COLUMN child_count INTEGER DEFAULT 0"))
        print("Added child_count column")
    else:
        print("child_count column already exists")

    conn.commit()
    conn.close()
    print("Migration complete.")
