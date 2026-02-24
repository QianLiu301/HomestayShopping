"""
Create default admin account.
Usage: python create_admin.py
"""
import os
from app import create_app, db, bcrypt
from app.models import Admin

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    # Check if admin already exists
    existing = Admin.query.filter_by(username='admin').first()
    if existing:
        print('Admin account already exists!')
        print(f'  Username: {existing.username}')
        print('  Password: (unchanged)')
    else:
        admin = Admin(
            username='admin',
            password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            name='Administrator',
            role='admin',
            status=1
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin account created successfully!')
        print('  Username: admin')
        print('  Password: admin123')
        print('')
        print('Please change the password after first login.')
