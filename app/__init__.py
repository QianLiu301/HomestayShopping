import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config

# 初始化扩展
db = SQLAlchemy()
bcrypt = Bcrypt()

# 限流器：按客户端 IP 限制访问频率
# - 兜底每分钟 200 次（任何接口都会受限）
# - 关键接口在路由上用 @limiter.limit("X per minute") 单独加严
# - DEBUG 模式（本地开发）自动跳过限流，方便测试
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],
    storage_uri="memory://",  # 单实例够用；多实例时改为 redis://...
)


def _auto_migrate(app):
    """自动检查并添加缺失的数据库列，确保表存在"""
    columns_to_ensure = [
        ('transfer_orders', 'transport_mode', "VARCHAR(10) DEFAULT 'flight'"),
        ('transfer_orders', 'pickup_airport', 'VARCHAR(10)'),
        ('transfer_orders', 'dropoff_airport', 'VARCHAR(10)'),
        ('transfer_orders', 'dropoff_flight_no', 'VARCHAR(20)'),
        ('transfer_orders', 'dropoff_flight_time', 'TIMESTAMP'),
        ('transfer_orders', 'payment_screenshot', 'TEXT'),
        ('transfer_orders', 'transaction_id', 'VARCHAR(64)'),
        ('shop_orders', 'payment_screenshot', 'TEXT'),
        ('shop_orders', 'transaction_id', 'VARCHAR(64)'),
        ('transfer_orders', 'booking_no', 'VARCHAR(100)'),
        ('transfer_orders', 'resolved_address', 'TEXT'),
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
        ('vehicles', 'model_zh', 'TEXT'),
        ('vehicles', 'model_en', 'TEXT'),
        ('vehicles', 'model_ru', 'TEXT'),
        ('vehicles', 'model_es', 'TEXT'),
        ('vehicles', 'luggage_28', 'INTEGER DEFAULT 0'),
        ('vehicles', 'luggage_24', 'INTEGER DEFAULT 0'),
        ('vehicles', 'capacity_desc_zh', 'TEXT'),
        ('vehicles', 'capacity_desc_en', 'TEXT'),
        ('vehicles', 'capacity_desc_ru', 'TEXT'),
        ('vehicles', 'capacity_desc_es', 'TEXT'),
        ('vehicles', 'images', 'JSON'),
        ('vehicles', 'pickup_price', 'NUMERIC(10, 2) DEFAULT 0'),
        ('vehicles', 'dropoff_price', 'NUMERIC(10, 2) DEFAULT 0'),
        ('vehicles', 'combo_price', 'NUMERIC(10, 2) DEFAULT 0'),

        ('ticket_attractions', 'name_zh', 'VARCHAR(200)'),
        ('ticket_attractions', 'name_en', 'VARCHAR(200)'),
        ('ticket_attractions', 'name_ru', 'VARCHAR(200)'),
        ('ticket_attractions', 'name_es', 'VARCHAR(200)'),
        ('ticket_attractions', 'subtitle_zh', 'TEXT'),
        ('ticket_attractions', 'subtitle_en', 'TEXT'),
        ('ticket_attractions', 'subtitle_ru', 'TEXT'),
        ('ticket_attractions', 'subtitle_es', 'TEXT'),
        ('ticket_attractions', 'desc_zh', 'TEXT'),
        ('ticket_attractions', 'desc_en', 'TEXT'),
        ('ticket_attractions', 'desc_ru', 'TEXT'),
        ('ticket_attractions', 'desc_es', 'TEXT'),
        ('ticket_attractions', 'address_zh', 'TEXT'),
        ('ticket_attractions', 'address_en', 'TEXT'),
        ('ticket_attractions', 'address_ru', 'TEXT'),
        ('ticket_attractions', 'address_es', 'TEXT'),
        ('ticket_attractions', 'open_hours_zh', 'TEXT'),
        ('ticket_attractions', 'open_hours_en', 'TEXT'),
        ('ticket_attractions', 'open_hours_ru', 'TEXT'),
        ('ticket_attractions', 'open_hours_es', 'TEXT'),
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
        ('ticket_orders', 'payment_screenshot', 'TEXT'),
        ('ticket_orders', 'remark', 'TEXT'),
        ('ticket_orders', 'admin_note', 'TEXT'),
        ('ticket_orders', 'need_transfer', 'BOOLEAN DEFAULT FALSE'),
        ('ticket_orders', 'transfer_vehicle_id', 'INTEGER'),
        ('ticket_orders', 'transfer_service_type', 'VARCHAR(20)'),
        ('ticket_orders', 'transfer_price_snapshot', 'NUMERIC(10, 2)'),
        ('ticket_orders', 'transfer_pickup_time', 'TIMESTAMP'),
        ('ticket_orders', 'transfer_return_time', 'TIMESTAMP'),
        ('ticket_orders', 'transfer_user_note', 'TEXT'),
        ('ticket_orders', 'transfer_pickup_location', 'TEXT'),
        ('ticket_orders', 'transfer_return_location', 'TEXT'),
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
        ('ticket_vouchers', 'file_url', 'TEXT'),
        ('ticket_vouchers', 'file_name', 'TEXT'),
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

        # 通用业务评价表（接送/门票/商城）
        ('service_reviews', 'order_type', 'VARCHAR(20)'),
        ('service_reviews', 'order_id', 'INTEGER'),
        ('service_reviews', 'order_no', 'VARCHAR(32)'),
        ('service_reviews', 'target_id', 'INTEGER'),
        ('service_reviews', 'rating', 'SMALLINT'),
        ('service_reviews', 'comment', 'TEXT'),
        ('service_reviews', 'reviewer_name', 'VARCHAR(50)'),
        ('service_reviews', 'lang', "VARCHAR(10) DEFAULT 'zh'"),
        ('service_reviews', 'status', 'SMALLINT DEFAULT 0'),
        ('service_reviews', 'admin_reply', 'TEXT'),
        ('service_reviews', 'replied_at', 'TIMESTAMP'),
        ('service_reviews', 'created_at', 'TIMESTAMP'),
        ('service_reviews', 'updated_at', 'TIMESTAMP'),

        # 接送订单出行人数
        ('transfer_orders', 'adult_count', 'INTEGER DEFAULT 1'),
        ('transfer_orders', 'child_count', 'INTEGER DEFAULT 0'),

        # 攻略多图
        ('guides', 'images', 'JSON'),

        # 成本价（利润核算）
        ('shop_orders', 'cost_price', 'NUMERIC(10, 2)'),
        ('ticket_orders', 'cost_price', 'NUMERIC(10, 2)'),

        # 住宿登记证件类型 + 住宿日期
        ('guest_registrations', 'document_type', "VARCHAR(20) DEFAULT 'passport'"),
        ('guest_registrations', 'document_no', 'VARCHAR(50)'),
        ('guest_registrations', 'checkin_date', 'DATE'),
        ('guest_registrations', 'checkout_date', 'DATE'),
        ('guest_registrations', 'room_note', 'VARCHAR(100)'),
        ('guest_registrations', 'group_id', 'VARCHAR(40)'),

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

        # 住宿登记单号清洗：去掉客户复制 Booking 单号时带入的小数点和空格（幂等，每次启动检查）
        try:
            result = db.session.execute(db.text(
                "UPDATE guest_registrations "
                "SET booking_no = REPLACE(REPLACE(booking_no, '.', ''), ' ', '') "
                "WHERE booking_no LIKE '%.%' OR booking_no LIKE '% %'"
            ))
            db.session.commit()
            if getattr(result, 'rowcount', 0):
                app.logger.info(f'Auto-migrate: cleaned {result.rowcount} guest_registrations booking_no')
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
            # ===== ticket_packages =====
            ('ticket_packages', 'age_rule_zh'),
            ('ticket_packages', 'age_rule_en'),
            ('ticket_packages', 'age_rule_ru'),
            ('ticket_packages', 'age_rule_es'),

            # ===== ticket_attractions：副标题/地址/开放时间多语言长文本 =====
            ('ticket_attractions', 'subtitle_zh'),
            ('ticket_attractions', 'subtitle_en'),
            ('ticket_attractions', 'subtitle_ru'),
            ('ticket_attractions', 'subtitle_es'),
            ('ticket_attractions', 'address_zh'),
            ('ticket_attractions', 'address_en'),
            ('ticket_attractions', 'address_ru'),
            ('ticket_attractions', 'address_es'),
            ('ticket_attractions', 'open_hours_zh'),
            ('ticket_attractions', 'open_hours_en'),
            ('ticket_attractions', 'open_hours_ru'),
            ('ticket_attractions', 'open_hours_es'),

            # ===== locations：民宿地址多语言可能很长 =====
            ('locations', 'address_zh'),
            ('locations', 'address_en'),
            ('locations', 'address_ru'),
            ('locations', 'address_es'),

            # ===== vehicles：描述/型号/容量描述多语言 =====
            ('vehicles', 'desc_zh'),
            ('vehicles', 'desc_en'),
            ('vehicles', 'desc_ru'),
            ('vehicles', 'desc_es'),
            ('vehicles', 'model_zh'),
            ('vehicles', 'model_en'),
            ('vehicles', 'model_ru'),
            ('vehicles', 'model_es'),
            ('vehicles', 'capacity_desc_zh'),
            ('vehicles', 'capacity_desc_en'),
            ('vehicles', 'capacity_desc_ru'),
            ('vehicles', 'capacity_desc_es'),

            # ===== settings：value/description 可能存长文本 =====
            ('settings', 'value'),
            ('settings', 'description'),

            # ===== reviews：用户评论可能超过 500 字符 =====
            ('reviews', 'comment'),

            # ===== 各类订单：地址、支付凭证 URL 可能很长（签名URL等） =====
            ('transfer_orders', 'custom_address'),
            ('transfer_orders', 'resolved_address'),
            ('transfer_orders', 'payment_screenshot'),
            ('shop_orders', 'custom_address'),
            ('shop_orders', 'resolved_address'),
            ('shop_orders', 'payment_screenshot'),
            ('ticket_orders', 'payment_screenshot'),
            ('ticket_orders', 'transfer_pickup_location'),
            ('ticket_orders', 'transfer_return_location'),

            # ===== ticket_vouchers：电子凭证 URL/文件名 =====
            ('ticket_vouchers', 'file_url'),
            ('ticket_vouchers', 'file_name'),
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

        # ============ 性能索引：批量创建索引（仅 PG）============
        # 给高频查询/过滤/排序的列加索引，订单量上来后查询不会变慢
        # 命名规范: idx_<table>_<column>
        indexes_to_ensure = [
            # ----- 商城订单 -----
            ('shop_orders', 'contact_phone'),
            ('shop_orders', 'contact_email'),
            ('shop_orders', 'status'),
            ('shop_orders', 'created_at'),
            ('shop_orders', 'booking_no'),
            ('shop_orders', 'payment_status'),
            # ----- 接送订单 -----
            ('transfer_orders', 'contact_phone'),
            ('transfer_orders', 'contact_email'),
            ('transfer_orders', 'status'),
            ('transfer_orders', 'created_at'),
            ('transfer_orders', 'vehicle_id'),
            ('transfer_orders', 'booking_no'),
            ('transfer_orders', 'payment_status'),
            # ----- 门票订单 -----
            ('ticket_orders', 'contact_phone'),
            ('ticket_orders', 'contact_email'),
            ('ticket_orders', 'status'),
            ('ticket_orders', 'created_at'),
            ('ticket_orders', 'attraction_id'),
            ('ticket_orders', 'booking_no'),
            ('ticket_orders', 'payment_status'),
            ('ticket_orders', 'visit_date'),
            # ----- 商品 -----
            ('products', 'status'),
            ('products', 'is_featured'),
            ('products', 'category_id'),
            ('products', 'created_at'),
            # ----- 订单明细：JOIN/聚合关键 -----
            ('order_items', 'order_id'),
            ('order_items', 'product_id'),
            # ----- 门票景点 / 票种 -----
            ('ticket_attractions', 'status'),
            ('ticket_attractions', 'featured'),
            ('ticket_attractions', 'city'),
            ('ticket_packages', 'attraction_id'),
            ('ticket_packages', 'status'),
            # ----- 车辆 -----
            ('vehicles', 'status'),
            # ----- 分类 -----
            ('categories', 'status'),
            # ----- 优惠券 -----
            ('coupons', 'status'),
            # ----- 评价（老 + 新）-----
            ('reviews', 'order_id'),
            ('service_reviews', 'order_type'),
            ('service_reviews', 'target_id'),
            ('service_reviews', 'status'),
            ('service_reviews', 'created_at'),
            # ----- 许愿池 -----
            ('wishes', 'status'),
            ('wishes', 'created_at'),
        ]
        if is_pg:
            for table, column in indexes_to_ensure:
                index_name = f'idx_{table}_{column}'
                try:
                    db.session.execute(db.text(
                        f'CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({column})'
                    ))
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    # 列可能不存在（旧表/新功能），静默跳过
                    app.logger.debug(f'Skip index {index_name}: {e}')


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # ProxyFix：让 Flask 信任反向代理（Railway/Nginx/Cloudflare）的
    # X-Forwarded-For 等 header，这样 request.remote_addr 拿到的是真实用户 IP，
    # 而不是代理的固定 IP（否则限流会把所有用户当成同一人，全部互相挤掉）
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # 确保上传目录存在
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)

    # 初始化限流器
    # DEBUG 模式下完全禁用，避免本地反复测试被 429 卡住
    if app.config.get('DEBUG'):
        app.config['RATELIMIT_ENABLED'] = False
    limiter.init_app(app)

    # 429 限流响应：统一 JSON 格式（不要 Flask-Limiter 默认的 HTML）
    from flask import jsonify
    @app.errorhandler(429)
    def handle_ratelimit_exceeded(e):
        return jsonify({
            'code': 429,
            'message': '请求过于频繁，请稍后再试',
            'detail': str(getattr(e, 'description', '')),
            'data': None
        }), 429

    # 配置CORS
    # 解析 CORS_ORIGINS：支持 '*' 或逗号分隔的多个域名
    # 例: "https://a.com,https://b.com" → ["https://a.com", "https://b.com"]
    _cors_raw = app.config.get('CORS_ORIGINS', '*')
    if _cors_raw == '*' or not _cors_raw:
        _cors_origins = '*'
    else:
        _cors_origins = [o.strip() for o in _cors_raw.split(',') if o.strip()]

    CORS(app, resources={
        r"/api/*": {
            "origins": _cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        },
        r"/uploads/*": {
            "origins": _cors_origins,
        }
    })

    # ==================== 全局错误处理器 ====================
    # 目的：所有错误返回统一 JSON 格式（不返回 HTML），
    # 1) 让 Flask-CORS 能正常在错误响应上加 CORS 头（避免"假 CORS 错误"）
    # 2) 不向前端暴露 Python 堆栈、代码路径等敏感信息
    # 3) 真实错误堆栈写入服务器日志，便于排查
    import traceback
    import uuid
    from werkzeug.exceptions import HTTPException
    from flask import jsonify, request as flask_request

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理 4xx 类已知错误（如 404、405、413 等）"""
        return jsonify({
            'code': e.code,
            'message': e.description or e.name,
            'data': None
        }), e.code

    @app.errorhandler(Exception)
    def handle_uncaught_exception(e):
        """兜底处理所有未捕获的异常（如 500、数据库错误、第三方接口错误等）"""
        # 给这次错误一个唯一 ID，方便用户报错时让客服查日志
        error_id = uuid.uuid4().hex[:8]

        # 详细堆栈写日志（生产环境只 admin/运维能看到）
        app.logger.error(
            f'[error_id={error_id}] {flask_request.method} {flask_request.path} '
            f'unhandled exception: {e}\n{traceback.format_exc()}'
        )

        # 给前端的响应保持简洁、不泄露内部细节
        # 仅在 debug 模式下返回详细错误（方便本地调试）
        if app.config.get('DEBUG'):
            return jsonify({
                'code': 500,
                'message': f'{type(e).__name__}: {str(e)}',
                'error_id': error_id,
                'traceback': traceback.format_exc().splitlines()[-10:],
                'data': None
            }), 500

        return jsonify({
            'code': 500,
            'message': '系统繁忙，请稍后再试',
            'error_id': error_id,  # 用户可截图给客服，客服拿这个 ID 查日志
            'data': None
        }), 500

    # 注册蓝图（API路由）
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 静态文件服务 - 上传的图片
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        resp = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        return resp

    # 健康检查路由（heic 字段用于确认 pillow-heif 是否安装成功）
    try:
        import pillow_heif  # noqa: F401
        _heic_ok = True
        app.logger.info('pillow-heif 已安装：HEIC 照片上传自动转换已启用')
    except ImportError:
        _heic_ok = False
        app.logger.warning('pillow-heif 未安装：HEIC 照片上传将返回格式指引提示')

    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Homestay API is running', 'heic_support': _heic_ok}

    # ==================== SEO: sitemap.xml + robots.txt ====================
    # 主站域名（用户访问的公开域名，不是 api 域名）
    SITE_DOMAIN = os.getenv('SITE_DOMAIN', 'https://shanghai-tour-guide.com')

    @app.route('/robots.txt')
    def robots_txt():
        """搜索引擎抓取规则"""
        from flask import Response
        body = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin\n"
            "Disallow: /api\n"
            "Disallow: /order-query\n"
            "Disallow: /checkout\n"
            "Disallow: /ticket-checkout\n"
            "Disallow: /order-result\n"
            "Disallow: /ticket-order-result\n"
            f"\nSitemap: {SITE_DOMAIN}/sitemap.xml\n"
            f"Sitemap: {SITE_DOMAIN}/api/sitemap.xml\n"
        )
        return Response(body, mimetype='text/plain')

    @app.route('/sitemap.xml')
    @app.route('/api/sitemap.xml')
    def sitemap_xml():
        """动态生成 sitemap.xml：包含所有公开商品/景点/静态页"""
        from flask import Response
        from app.models import Product, TicketAttraction
        from datetime import datetime

        today = datetime.utcnow().strftime('%Y-%m-%d')
        base = SITE_DOMAIN.rstrip('/')

        urls = []

        # 静态页面（高频访问）
        for path, priority, freq in [
            ('/',         '1.0', 'daily'),
            ('/shop',     '0.9', 'daily'),
            ('/tickets',  '0.9', 'daily'),
            ('/transfer', '0.8', 'weekly'),
        ]:
            urls.append({
                'loc': f'{base}{path}',
                'lastmod': today,
                'changefreq': freq,
                'priority': priority,
            })

        # 商品详情页
        try:
            for p in Product.query.filter_by(status=1).all():
                lastmod = p.updated_at if getattr(p, 'updated_at', None) else None
                urls.append({
                    'loc': f'{base}/product/{p.id}',
                    'lastmod': lastmod.strftime('%Y-%m-%d') if lastmod else today,
                    'changefreq': 'weekly',
                    'priority': '0.7',
                })
        except Exception as e:
            app.logger.warning(f'sitemap: failed to list products: {e}')

        # 景点详情页
        try:
            for a in TicketAttraction.query.filter_by(status=1).all():
                lastmod = a.updated_at if getattr(a, 'updated_at', None) else None
                urls.append({
                    'loc': f'{base}/tickets/{a.id}',
                    'lastmod': lastmod.strftime('%Y-%m-%d') if lastmod else today,
                    'changefreq': 'weekly',
                    'priority': '0.7',
                })
        except Exception as e:
            app.logger.warning(f'sitemap: failed to list attractions: {e}')

        # 拼接 XML
        items_xml = '\n'.join(
            f'  <url>\n'
            f'    <loc>{u["loc"]}</loc>\n'
            f'    <lastmod>{u["lastmod"]}</lastmod>\n'
            f'    <changefreq>{u["changefreq"]}</changefreq>\n'
            f'    <priority>{u["priority"]}</priority>\n'
            f'  </url>'
            for u in urls
        )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{items_xml}\n'
            '</urlset>\n'
        )
        return Response(xml, mimetype='application/xml')

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

    # 启动定时任务（自动取消超时未支付订单等）
    from app.tasks import init_scheduler
    init_scheduler(app)

    return app


def _ensure_admin(app):
    """根据环境变量初始化/重置主管理员账号（owner 角色）"""
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    if not username or not password:
        return

    with app.app_context():
        from app.models import Admin

        # 注意：不再禁用其他账号（要支持多角色账号共存）
        # 老逻辑会把所有其他 admin status=0，现在改为只保证主账号是 owner + 启用

        admin = Admin.query.filter_by(username=username).first()
        if admin:
            # 主账号始终保持 owner 角色 + 启用状态
            changed = False
            if admin.role != 'owner':
                admin.role = 'owner'
                changed = True
            if admin.status != 1:
                admin.status = 1
                changed = True
            if not bcrypt.check_password_hash(admin.password_hash, password):
                admin.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                changed = True
            if changed:
                db.session.commit()
                app.logger.info(f'Owner account synced: {username}')
        else:
            admin = Admin(
                username=username,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                name='Owner',
                role='owner',
                status=1
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f'Owner account created: {username}')
