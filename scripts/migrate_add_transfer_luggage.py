"""
Add luggage_count and sign_name columns to transfer_orders table.
Run: python scripts/migrate_add_transfer_luggage.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    conn = db.engine.connect()

    # Check if columns already exist
    if db.engine.name == 'sqlite':
        result = conn.execute(text("PRAGMA table_info(transfer_orders)"))
        columns = [row[1] for row in result]
    else:
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'transfer_orders'"
        ))
        columns = [row[0] for row in result]

    if 'luggage_count' not in columns:
        conn.execute(text("ALTER TABLE transfer_orders ADD COLUMN luggage_count INTEGER"))
        print("Added luggage_count column")
    else:
        print("luggage_count column already exists")

    if 'sign_name' not in columns:
        conn.execute(text("ALTER TABLE transfer_orders ADD COLUMN sign_name VARCHAR(100)"))
        print("Added sign_name column")
    else:
        print("sign_name column already exists")

    conn.commit()
    conn.close()
    print("Migration complete.")
