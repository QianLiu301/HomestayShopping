import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import config

# 初始化扩展
db = SQLAlchemy()
bcrypt = Bcrypt()


def _auto_migrate(app):
    """自动检查并添加缺失的数据库列，确保表存在"""
    columns_to_ensure = [
        ('transfer_orders', 'pickup_airport', 'VARCHAR(10)'),
        ('transfer_orders', 'dropoff_airport', 'VARCHAR(10)'),
        ('transfer_orders', 'dropoff_flight_no', 'VARCHAR(20)'),
        ('transfer_orders', 'dropoff_flight_time', 'TIMESTAMP'),
        ('transfer_orders', 'payment_screenshot', 'VARCHAR(255)'),
        ('transfer_orders', 'transaction_id', 'VARCHAR(64)'),
        ('shop_orders', 'payment_screenshot', 'VARCHAR(255)'),
        ('shop_orders', 'transaction_id', 'VARCHAR(64)'),
        ('transfer_orders', 'booking_no', 'VARCHAR(100)'),
        ('transfer_orders', 'resolved_address', 'VARCHAR(255)'),
        ('shop_orders', 'delivery_time', 'TIMESTAMP'),
        ('shop_orders', 'completed_time', 'TIMESTAMP'),
    ]
    with app.app_context():
        # 先确保所有表都存在
        db.create_all()

        # 一次性迁移旧状态码: 原 2=已完成→3, 原 3=已取消→4（仅shop_orders）
        # 仅当 delivery_time 列刚添加（全为 NULL）且存在旧 status=2 的订单时执行
        try:
            has_delivery_col = db.session.execute(db.text(
                "SELECT COUNT(*) FROM shop_orders WHERE delivery_time IS NOT NULL"
            )).scalar()
            has_old_status2 = db.session.execute(db.text(
                "SELECT COUNT(*) FROM shop_orders WHERE status = 2"
            )).scalar()
            if has_delivery_col == 0 and has_old_status2 > 0:
                # 先把3(旧取消)改成4，再把2(旧完成)改成3
                db.session.execute(db.text(
                    "UPDATE shop_orders SET status = 4 WHERE status = 3"
                ))
                db.session.execute(db.text(
                    "UPDATE shop_orders SET status = 3 WHERE status = 2"
                ))
                db.session.commit()
                app.logger.info('Auto-migrate: shop_orders status codes updated (2→3, 3→4)')
        except Exception:
            db.session.rollback()

        # 检测数据库类型
        db_url = str(db.engine.url)
        is_pg = 'postgresql' in db_url or 'postgres' in db_url

        # 再添加可能缺失的列
        for table, column, col_type in columns_to_ensure:
            try:
                if is_pg:
                    # PostgreSQL 支持 IF NOT EXISTS
                    db.session.execute(db.text(
                        f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {col_type}'
                    ))
                else:
                    # SQLite 不支持 IF NOT EXISTS，靠异常跳过
                    db.session.execute(db.text(
                        f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'
                    ))
                db.session.commit()
                app.logger.info(f'Auto-migrate: ensured {table}.{column}')
            except Exception:
                db.session.rollback()


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 确保上传目录存在
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)

    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/uploads/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
        }
    })

    # 注册蓝图（API路由）
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 静态文件服务 - 上传的图片
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # 健康检查路由
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Homestay API is running'}

    # 提供 admin 前端静态文件
    admin_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'admin', 'dist')

    @app.route('/assets/<path:filename>')
    def admin_assets(filename):
        return send_from_directory(os.path.join(admin_dist, 'assets'), filename)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_admin(path):
        """SPA catch-all: serve index.html for all non-API routes"""
        file_path = os.path.join(admin_dist, path)
        if path and os.path.isfile(file_path):
            return send_from_directory(admin_dist, path)
        return send_from_directory(admin_dist, 'index.html')

    # 自动迁移：确保所有新列存在
    _auto_migrate(app)

    return app
