"""迁移脚本：创建 guides 表（免费攻略）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

app = create_app()

with app.app_context():
    conn = db.engine.connect()
    # 检查表是否已存在
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    if 'guides' in inspector.get_table_names():
        print('guides 表已存在，跳过创建')
    else:
        from app.models import Guide  # noqa: F401
        Guide.__table__.create(db.engine)
        print('guides 表创建成功')
    conn.close()
