"""
Add booking_no and resolved_address columns to shop_orders table.
Usage: python migrate_shop_booking_no.py
"""
import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

NEW_COLUMNS = [
    ('shop_orders', 'booking_no', 'VARCHAR(100)'),
    ('shop_orders', 'resolved_address', 'VARCHAR(255)'),
]

with app.app_context():
    for table, column, col_type in NEW_COLUMNS:
        try:
            db.session.execute(
                db.text(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
            )
            db.session.commit()
            print(f'  Added {table}.{column} ({col_type})')
        except Exception as e:
            db.session.rollback()
            if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                print(f'  Skipped {table}.{column} (already exists)')
            else:
                print(f'  Error {table}.{column}: {e}')

    print('\nMigration complete!')
