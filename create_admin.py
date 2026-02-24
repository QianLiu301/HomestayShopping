"""
Create or reset default admin account.
Usage: python create_admin.py
"""
import os
from app import create_app, db, bcrypt
from app.models import Admin

USERNAME = 'admin'
PASSWORD = 'admin123'

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    existing = Admin.query.filter_by(username=USERNAME).first()

    if existing:
        # Reset password
        existing.password_hash = bcrypt.generate_password_hash(PASSWORD).decode('utf-8')
        existing.status = 1
        db.session.commit()
        print('Admin password has been reset!')
    else:
        admin = Admin(
            username=USERNAME,
            password_hash=bcrypt.generate_password_hash(PASSWORD).decode('utf-8'),
            name='Administrator',
            role='admin',
            status=1
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin account created successfully!')

    # Verify password works
    admin = Admin.query.filter_by(username=USERNAME).first()
    check = bcrypt.check_password_hash(admin.password_hash, PASSWORD)
    print(f'  Username: {USERNAME}')
    print(f'  Password: {PASSWORD}')
    print(f'  Password verify: {"OK" if check else "FAILED"}')
