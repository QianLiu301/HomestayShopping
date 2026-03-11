"""
Add airport and dual-flight columns to transfer_orders table.
Usage: python migrate_transfer_airports.py
"""
import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

NEW_COLUMNS = [
    ('transfer_orders', 'pickup_airport', 'VARCHAR(10)'),
    ('transfer_orders', 'dropoff_airport', 'VARCHAR(10)'),
    ('transfer_orders', 'dropoff_flight_no', 'VARCHAR(20)'),
    ('transfer_orders', 'dropoff_flight_time', 'DATETIME'),
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
