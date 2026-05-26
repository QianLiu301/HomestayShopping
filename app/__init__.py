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
        ('shop_orders', 'expected_delivery_date', 'DATE'),
        ('shop_orders', 'expected_delivery_time', 'VARCHAR(10)'),
        ('shop_orders', 'checkout_date', 'DATE'),
        ('shop_orders', 'refund_status', 'SMALLINT DEFAULT 0'),
        ('shop_orders', 'refund_time', 'TIMESTAMP'),
        ('shop_orders', 'cancelled_at', 'TIMESTAMP'),
        ('shop_orders', 'refund_amount', 'NUMERIC(10, 2)'),
        ('transfer_orders', 'cancelled_at', 'TIMESTAMP'),
        ('transfer_orders', 'refund_status', 'SMALLINT DEFAULT 0'),
        ('transfer_orders', 'refund_amount', 'NUMERIC(10, 2)'),
        ('transfer_orders', 'refund_time', 'TIMESTAMP'),
        ('vehicles', 'model_zh', 'VARCHAR(100)'),
        ('vehicles', 'model_en', 'VARCHAR(100)'),
        ('vehicles', 'model_ru', 'VARCHAR(100)'),
        ('vehicles', 'model_es', 'VARCHAR(100)'),
        ('vehicles', 'luggage_28', 'INTEGER DEFAULT 0'),
        ('vehicles', 'luggage_24', 'INTEGER DEFAULT 0'),
        ('vehicles', 'capacity_desc_zh', 'VARCHAR(100)'),
        ('vehicles', 'capacity_desc_en', 'VARCHAR(100)'),
        ('vehicles', 'capacity_desc_ru', 'VARCHAR(100)'),
        ('vehicles', 'capacity_desc_es', 'VARCHAR(100)'),
        ('vehicles', 'images', 'JSON'),
        ('vehicles', 'pickup_price', 'NUMERIC(10, 2) DEFAULT 0'),
        ('vehicles', 'dropoff_price', 'NUMERIC(10, 2) DEFAULT 0'),
        ('vehicles', 'combo_price', 'NUMERIC(10, 2) DEFAULT 0'),

        ('ticket_attractions', 'name_zh', 'VARCHAR(200)'),
        ('ticket_attractions', 'name_en', 'VARCHAR(200)'),
        ('ticket_attractions', 'name_ru', 'VARCHAR(200)'),
        ('ticket_attractions', 'name_es', 'VARCHAR(200)'),
        ('ticket_attractions', 'subtitle_zh', 'VARCHAR(500)'),
        ('ticket_attractions', 'subtitle_en', 'VARCHAR(500)'),
        ('ticket_attractions', 'subtitle_ru', 'VARCHAR(500)'),
        ('ticket_attractions', 'subtitle_es', 'VARCHAR(500)'),
        ('ticket_attractions', 'desc_zh', 'TEXT'),
        ('ticket_attractions', 'desc_en', 'TEXT'),
        ('ticket_attractions', 'desc_ru', 'TEXT'),
        ('ticket_attractions', 'desc_es', 'TEXT'),
        ('ticket_attractions', 'address_zh', 'VARCHAR(500)'),
        ('ticket_attractions', 'address_en', 'VARCHAR(500)'),
        ('ticket_attractions', 'address_ru', 'VARCHAR(500)'),
        ('ticket_attractions', 'address_es', 'VARCHAR(500)'),
        ('ticket_attractions', 'open_hours_zh', 'VARCHAR(500)'),
        ('ticket_attractions', 'open_hours_en', 'VARCHAR(500)'),
        ('ticket_attractions', 'open_hours_ru', 'VARCHAR(500)'),
        ('ticket_attractions', 'open_hours_es', 'VARCHAR(500)'),
        ('ticket_attractions', 'visit_notice_zh', 'TEXT'),
        ('ticket_attractions', 'visit_notice_en', 'TEXT'),
        ('ticket_attractions', 'visit_notice_ru', 'TEXT'),
        ('ticket_attractions', 'visit_notice_es', 'TEXT'),
        ('ticket_attractions', 'refund_rule_zh', 'TEXT'),
        ('ticket_attractions', 'refund_rule_en', 'TEXT'),
        ('ticket_attractions', 'refund_rule_ru', 'TEXT'),
        ('ticket_attractions', 'refund_rule_es', 'TEXT'),
        ('ticket_attractions', 'cover_image', 'VARCHAR(255)'),
        ('ticket_attractions', 'images', 'JSON'),
        ('ticket_attractions', 'city', 'VARCHAR(50)'),
        ('ticket_attractions', 'category', 'VARCHAR(50)'),
        ('ticket_attractions', 'tags', 'JSON'),
        ('ticket_attractions', 'featured', 'BOOLEAN DEFAULT FALSE'),
        ('ticket_attractions', 'real_name_required', 'BOOLEAN DEFAULT FALSE'),
        ('ticket_attractions', 'passport_required', 'BOOLEAN DEFAULT FALSE'),
        ('ticket_attractions', 'status', 'SMALLINT DEFAULT 1'),
        ('ticket_attractions', 'sort_order', 'INTEGER DEFAULT 0'),
        ('ticket_attractions', 'created_at', 'TIMESTAMP'),
        ('ticket_attractions', 'updated_at', 'TIMESTAMP'),

        ('ticket_packages', 'attraction_id', 'INTEGER'),
        ('ticket_packages', 'package_name_zh', 'VARCHAR(200)'),
        ('ticket_packages', 'package_name_en', 'VARCHAR(200)'),
        ('ticket_packages', 'package_name_ru', 'VARCHAR(200)'),
        ('ticket_packages', 'package_name_es', 'VARCHAR(200)'),
        ('ticket_packages', 'ticket_type', 'VARCHAR(20)'),
        ('ticket_packages', 'sale_price', 'NUMERIC(10, 2)'),
        ('ticket_packages', 'original_price', 'NUMERIC(10, 2)'),
        ('ticket_packages', 'age_rule_zh', 'TEXT'),
        ('ticket_packages', 'age_rule_en', 'TEXT'),
        ('ticket_packages', 'age_rule_ru', 'TEXT'),
        ('ticket_packages', 'age_rule_es', 'TEXT'),
        ('ticket_packages', 'booking_notice_zh', 'TEXT'),
        ('ticket_packages', 'booking_notice_en', 'TEXT'),
        ('ticket_packages', 'booking_notice_ru', 'TEXT'),
        ('ticket_packages', 'booking_notice_es', 'TEXT'),
        ('ticket_packages', 'refund_rule_zh', 'TEXT'),
        ('ticket_packages', 'refund_rule_en', 'TEXT'),
        ('ticket_packages', 'refund_rule_ru', 'TEXT'),
        ('ticket_packages', 'refund_rule_es', 'TEXT'),
        ('ticket_packages', 'inventory_mode', "VARCHAR(20) DEFAULT 'unlimited'"),
        ('ticket_packages', 'quota_total', 'INTEGER'),
        ('ticket_packages', 'quota_used', 'INTEGER DEFAULT 0'),
        ('ticket_packages', 'available_days', 'JSON'),
        ('ticket_packages', 'date_rules', 'JSON'),
        ('ticket_packages', 'status', 'SMALLINT DEFAULT 1'),
        ('ticket_packages', 'sort_order', 'INTEGER DEFAULT 0'),
        ('ticket_packages', 'created_at', 'TIMESTAMP'),
        ('ticket_packages', 'updated_at', 'TIMESTAMP'),

        ('ticket_orders', 'order_no', 'VARCHAR(32)'),
        ('ticket_orders', 'attraction_id', 'INTEGER'),
        ('ticket_orders', 'visit_date', 'DATE'),
        ('ticket_orders', 'contact_name', 'VARCHAR(100)'),
        ('ticket_orders', 'contact_phone', 'VARCHAR(30)'),
        ('ticket_orders', 'contact_email', 'VARCHAR(100)'),
        ('ticket_orders', 'booking_no', 'VARCHAR(100)'),
        ('ticket_orders', 'lang', "VARCHAR(10) DEFAULT 'zh'"),
        ('ticket_orders', 'total_price', 'NUMERIC(10, 2)'),
        ('ticket_orders', 'discount_amount', 'NUMERIC(10, 2) DEFAULT 0'),
        ('ticket_orders', 'coupon_id', 'INTEGER'),
        ('ticket_orders', 'status', 'SMALLINT DEFAULT 0'),
        ('ticket_orders', 'payment_method', 'VARCHAR(20)'),
        ('ticket_orders', 'payment_status', 'SMALLINT DEFAULT 0'),
        ('ticket_orders', 'payment_time', 'TIMESTAMP'),
        ('ticket_orders', 'transaction_id', 'VARCHAR(64)'),
        ('ticket_orders', 'payment_screenshot', 'VARCHAR(255)'),
        ('ticket_orders', 'remark', 'TEXT'),
        ('ticket_orders', 'admin_note', 'TEXT'),
        ('ticket_orders', 'need_transfer', 'BOOLEAN DEFAULT FALSE'),
        ('ticket_orders', 'transfer_vehicle_id', 'INTEGER'),
        ('ticket_orders', 'transfer_service_type', 'VARCHAR(20)'),
        ('ticket_orders', 'transfer_price_snapshot', 'NUMERIC(10, 2)'),
        ('ticket_orders', 'transfer_pickup_time', 'TIMESTAMP'),
        ('ticket_orders', 'transfer_return_time', 'TIMESTAMP'),
        ('ticket_orders', 'transfer_user_note', 'TEXT'),
        ('ticket_orders', 'transfer_pickup_location', 'VARCHAR(255)'),
        ('ticket_orders', 'transfer_return_location', 'VARCHAR(255)'),
        ('ticket_orders', 'transfer_status', "VARCHAR(20) DEFAULT 'pending'"),
        ('ticket_orders', 'transfer_admin_note', 'TEXT'),
        ('ticket_orders', 'transfer_confirmed_at', 'TIMESTAMP'),
        ('ticket_orders', 'transfer_vehicle_snapshot', 'JSON'),
        ('ticket_orders', 'transfer_snapshot', 'JSON'),
        ('ticket_orders', 'package_snapshot', 'JSON'),
        ('ticket_orders', 'voucher_delivery_status', 'SMALLINT DEFAULT 0'),
        ('ticket_orders', 'cancelled_at', 'TIMESTAMP'),
        ('ticket_orders', 'refund_status', 'SMALLINT DEFAULT 0'),
        ('ticket_orders', 'refund_amount', 'NUMERIC(10, 2)'),
        ('ticket_orders', 'refund_time', 'TIMESTAMP'),
        ('ticket_orders', 'created_at', 'TIMESTAMP'),
        ('ticket_orders', 'updated_at', 'TIMESTAMP'),

        ('ticket_travelers', 'order_id', 'INTEGER'),
        ('ticket_travelers', 'traveler_type', 'VARCHAR(20)'),
        ('ticket_travelers', 'full_name', 'VARCHAR(100)'),
        ('ticket_travelers', 'nationality', 'VARCHAR(50)'),
        ('ticket_travelers', 'document_type', 'VARCHAR(20)'),
        ('ticket_travelers', 'document_no', 'VARCHAR(50)'),
        ('ticket_travelers', 'date_of_birth', 'DATE'),
        ('ticket_travelers', 'gender', 'VARCHAR(10)'),
        ('ticket_travelers', 'created_at', 'TIMESTAMP'),

        ('ticket_vouchers', 'order_id', 'INTEGER'),
        ('ticket_vouchers', 'file_url', 'VARCHAR(500)'),
        ('ticket_vouchers', 'file_name', 'VARCHAR(255)'),
        ('ticket_vouchers', 'file_type', 'VARCHAR(20)'),
        ('ticket_vouchers', 'uploaded_by', 'INTEGER'),
        ('ticket_vouchers', 'sent_to_customer', 'BOOLEAN DEFAULT FALSE'),
        ('ticket_vouchers', 'sent_at', 'TIMESTAMP'),
        ('ticket_vouchers', 'created_at', 'TIMESTAMP'),

        ('ticket_transport_prices', 'attraction_id', 'INTEGER'),
        ('ticket_transport_prices', 'vehicle_id', 'INTEGER'),
        ('ticket_transport_prices', 'service_type', 'VARCHAR(20)'),
        ('ticket_transport_prices', 'price', 'NUMERIC(10, 2)'),
        ('ticket_transport_prices', 'status', 'SMALLINT DEFAULT 1'),
        ('ticket_transport_prices', 'sort_order', 'INTEGER DEFAULT 0'),
        ('ticket_transport_prices', 'created_at', 'TIMESTAMP'),
        ('ticket_transport_prices', 'updated_at', 'TIMESTAMP'),

        # 许愿池
        ('wishes', 'contact_name', 'VARCHAR(50)'),
        ('wishes', 'contact_phone', 'VARCHAR(30)'),
        ('wishes', 'contact_email', 'VARCHAR(100)'),
        ('wishes', 'content', 'TEXT'),
        ('wishes', 'expected_date', 'TIMESTAMP'),
        ('wishes', 'budget', 'NUMERIC(10, 2)'),
        ('wishes', 'budget_currency', "VARCHAR(10) DEFAULT 'CNY'"),
        ('wishes', 'lang', "VARCHAR(10) DEFAULT 'zh'"),
        ('wishes', 'status', 'SMALLINT DEFAULT 0'),
        ('wishes', 'admin_note', 'TEXT'),
        ('wishes', 'created_at', 'TIMESTAMP'),
        ('wishes', 'updated_at', 'TIMESTAMP'),
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
                    # 先检查列是否已存在
                    exists = db.session.execute(db.text(
                        "SELECT 1 FROM information_schema.columns "
                        "WHERE table_name = :table AND column_name = :column"
                    ), {'table': table, 'column': column}).fetchone()
                    if exists:
                        continue
                    db.session.execute(db.text(
                        f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {col_type}'
                    ))
                else:
                    # SQLite 不支持 IF NOT EXISTS，靠异常跳过
                    db.session.execute(db.text(
                        f'ALTER TABLE {table} ADD COLUMN {column} {col_type}'
                    ))
                db.session.commit()
                app.logger.info(f'Auto-migrate: added {table}.{column}')
            except Exception:
                db.session.rollback()

        # 升级已存在列的类型（仅PG）：把过短的VARCHAR升为TEXT
        # 历史上某些字段被定义成 VARCHAR(500)，多语言长文本会触发
        # StringDataRightTruncation。这里统一升为 TEXT。
        columns_to_widen = [
            ('ticket_packages', 'age_rule_zh'),
            ('ticket_packages', 'age_rule_en'),
            ('ticket_packages', 'age_rule_ru'),
            ('ticket_packages', 'age_rule_es'),
        ]
        if is_pg:
            for table, column in columns_to_widen:
                try:
                    current_type = db.session.execute(db.text(
                        "SELECT data_type FROM information_schema.columns "
                        "WHERE table_name = :table AND column_name = :column"
                    ), {'table': table, 'column': column}).scalar()
                    if current_type and current_type.lower() != 'text':
                        db.session.execute(db.text(
                            f'ALTER TABLE {table} ALTER COLUMN {column} TYPE TEXT'
                        ))
                        db.session.commit()
                        app.logger.info(f'Auto-migrate: widened {table}.{column} to TEXT')
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
        resp = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        return resp

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

        resp = send_from_directory(admin_dist, 'index.html')
        resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp

    # 自动迁移：确保所有新列存在
    _auto_migrate(app)

    # 确保管理员账号存在（通过环境变量配置）
    _ensure_admin(app)

    return app


def _ensure_admin(app):
    """根据环境变量初始化/重置管理员账号"""
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    if not username or not password:
        return

    with app.app_context():
        from app.models import Admin

        # 禁用所有其他管理员账号
        Admin.query.filter(Admin.username != username).update({'status': 0})
        db.session.commit()

        admin = Admin.query.filter_by(username=username).first()
        if admin:
            # 密码可能已更新，每次用环境变量的值覆盖
            new_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            if not bcrypt.check_password_hash(admin.password_hash, password):
                admin.password_hash = new_hash
                admin.status = 1
                db.session.commit()
                app.logger.info(f'Admin password updated for: {username}')
        else:
            admin = Admin(
                username=username,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                name='Administrator',
                role='admin',
                status=1
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f'Admin account created: {username}')
