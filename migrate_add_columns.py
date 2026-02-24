"""
Add missing multilingual columns to vehicles and locations tables.
Usage: python migrate_add_columns.py
"""
import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

# Columns to add: (table, column, type)
NEW_COLUMNS = [
    ('vehicles', 'desc_ru', 'VARCHAR(100)'),
    ('vehicles', 'desc_es', 'VARCHAR(100)'),
    ('locations', 'address_ru', 'VARCHAR(255)'),
    ('locations', 'address_es', 'VARCHAR(255)'),
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
