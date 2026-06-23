"""
Add images column to guides table.
Run: python scripts/migrate_add_guide_images.py
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
        result = conn.execute(text("PRAGMA table_info(guides)"))
        columns = [row[1] for row in result]
    else:
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'guides'"
        ))
        columns = [row[0] for row in result]

    if 'images' not in columns:
        conn.execute(text("ALTER TABLE guides ADD COLUMN images TEXT DEFAULT '[]'"))
        # Migrate existing cover_image into images array
        conn.execute(text(
            "UPDATE guides SET images = '[\"' || cover_image || '\"]' "
            "WHERE cover_image IS NOT NULL AND cover_image != ''"
        ))
        print("Added images column and migrated existing cover_image data")
    else:
        print("images column already exists")

    conn.commit()
    conn.close()
    print("Migration complete.")
