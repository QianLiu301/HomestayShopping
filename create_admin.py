"""
Create or reset admin account.
Usage: ADMIN_USERNAME=xxx ADMIN_PASSWORD=xxx python create_admin.py
Or:    python create_admin.py (will prompt for input)
"""
import os
from app import create_app, db, bcrypt
from app.models import Admin

USERNAME = os.environ.get('ADMIN_USERNAME') or input('Username: ').strip()
PASSWORD = os.environ.get('ADMIN_PASSWORD') or input('Password: ').strip()

if not USERNAME or not PASSWORD:
    print('Error: username and password are required')
    exit(1)

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    # 禁用所有旧账号
    old_admins = Admin.query.filter(Admin.username != USERNAME, Admin.status == 1).all()
    for old in old_admins:
        old.status = 0
    if old_admins:
        print(f'Disabled {len(old_admins)} old admin account(s)')

    existing = Admin.query.filter_by(username=USERNAME).first()

    if existing:
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

    # Verify
    admin = Admin.query.filter_by(username=USERNAME).first()
    check = bcrypt.check_password_hash(admin.password_hash, PASSWORD)
    print(f'  Username: {USERNAME}')
    print(f'  Password verify: {"OK" if check else "FAILED"}')
