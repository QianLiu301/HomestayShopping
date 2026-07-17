import os
import json
from datetime import datetime, timezone, timedelta
from app import db

CHINA_TZ = timezone(timedelta(hours=8))

def china_now():
    """返回中国时间（UTC+8），不含时区信息以兼容 SQLite"""
    return datetime.now(CHINA_TZ).replace(tzinfo=None)


def _localized(obj, field, lang):
    """Get localized field with fallback: target lang -> en -> zh"""
    return (
        getattr(obj, f'{field}_{lang}', None)
        or getattr(obj, f'{field}_en', None)
        or getattr(obj, f'{field}_zh', None)
    )


import re

def _ensure_list(val):
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def _normalize_image_urls(images):
    """
    标准化图片 URL：
    - 本地上传文件保持 /uploads/<key>
    - R2 文件优先转为 R2_PUBLIC_URL 直链（CDN 直达）
    - 未配置 R2_PUBLIC_URL 时，回退到后端代理路径 /api/images/<key>
    - 兼容多种历史格式：完整 R2/CDN URL、代理路径、本地路径、纯文件名
    """
    result = []
    r2_public_url = os.getenv('R2_PUBLIC_URL', '').rstrip('/')

    for url in images:
        if not url:
            continue

        url = str(url).strip()
        if not url:
            continue

        key = None
        is_local_upload = False

        if url.startswith('/api/images/'):
            key = url.replace('/api/images/', '', 1)
        elif url.startswith('/uploads/'):
            key = url.replace('/uploads/', '', 1)
            is_local_upload = True
        elif url.startswith('http://') or url.startswith('https://') or url.startswith('//'):
            key = url.rstrip('/').rsplit('/', 1)[-1]
        else:
            key = url

        if not key:
            continue

        # R2 生成的标准文件名：32位十六进制 UUID + 扩展名
        if re.match(r'^[a-f0-9]{32}\.\w+$', key):
            if is_local_upload:
                result.append(f'/uploads/{key}')
            elif r2_public_url:
                result.append(f'{r2_public_url}/{key}')
            else:
                result.append(f'/api/images/{key}')
            continue

        # 明确的本地上传路径保持不变
        if is_local_upload:
            result.append(f'/uploads/{key}')
            continue

        # 已是完整 URL 的非标准历史数据，先原样保留
        if url.startswith('http://') or url.startswith('https://'):
            result.append(url)
            continue

        # 纯文件名历史数据：优先走 CDN 直链，没有再回退代理
        if r2_public_url:
            result.append(f'{r2_public_url}/{key}')
        else:
            result.append(f'/api/images/{key}')

    return result


class Admin(db.Model):
    """管理员表"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='admin')
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Location(db.Model):
    """民宿点表"""
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name_zh = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    name_ru = db.Column(db.String(100))
    name_es = db.Column(db.String(100))
    address_zh = db.Column(db.Text, nullable=False)
    address_en = db.Column(db.Text)
    address_ru = db.Column(db.Text)
    address_es = db.Column(db.Text)
    district = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=china_now)

    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'name': _localized(self, 'name', lang),
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'name_ru': self.name_ru,
            'name_es': self.name_es,
            'address': _localized(self, 'address', lang),
            'address_zh': self.address_zh,
            'address_en': self.address_en,
            'address_ru': self.address_ru,
            'address_es': self.address_es,
            'district': self.district,
            'sort_order': self.sort_order,
            'status': self.status
        }


class Category(db.Model):
    """商品分类表"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_zh = db.Column(db.String(50), nullable=False)
    name_en = db.Column(db.String(50))
    name_ru = db.Column(db.String(50))
    name_es = db.Column(db.String(50))
    icon = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=china_now)
    
    # 关联商品
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'name': _localized(self, 'name', lang),
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'name_ru': self.name_ru,
            'name_es': self.name_es,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'status': self.status
        }


class Product(db.Model):
    """商品表"""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name_zh = db.Column(db.String(1000), nullable=False)
    name_en = db.Column(db.String(1000))
    name_ru = db.Column(db.String(1000))
    name_es = db.Column(db.String(1000))
    desc_zh = db.Column(db.Text)
    desc_en = db.Column(db.Text)
    desc_ru = db.Column(db.Text)
    desc_es = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    images = db.Column(db.JSON, default=[])
    specs = db.Column(db.JSON)
    sort_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': _localized(self, 'name', lang),
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'name_ru': self.name_ru,
            'name_es': self.name_es,
            'desc': _localized(self, 'desc', lang),
            'desc_zh': self.desc_zh,
            'desc_en': self.desc_en,
            'desc_ru': self.desc_ru,
            'desc_es': self.desc_es,
            'price': float(self.price) if self.price else 0,
            'original_price': float(self.original_price) if self.original_price else None,
            'images': _normalize_image_urls(_ensure_list(self.images)),
            'specs': self.specs,
            'is_featured': self.is_featured,
            'sort_order': self.sort_order,
            'sales_count': int(getattr(self, 'sales_count', 0) or 0),
            'avg_rating': getattr(self, 'avg_rating', None),
            'review_count': int(getattr(self, 'review_count', 0) or 0),
            'status': self.status
        }


class Vehicle(db.Model):
    """车型表"""
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    name_zh = db.Column(db.String(50), nullable=False)
    name_en = db.Column(db.String(50))
    name_ru = db.Column(db.String(50))
    name_es = db.Column(db.String(50))
    desc_zh = db.Column(db.Text)
    desc_en = db.Column(db.Text)
    desc_ru = db.Column(db.Text)
    desc_es = db.Column(db.Text)
    model_zh = db.Column(db.Text)
    model_en = db.Column(db.Text)
    model_ru = db.Column(db.Text)
    model_es = db.Column(db.Text)
    seats = db.Column(db.Integer, nullable=False)
    luggage_capacity = db.Column(db.Integer, nullable=False)
    luggage_28 = db.Column(db.Integer, default=0)
    luggage_24 = db.Column(db.Integer, default=0)
    capacity_desc_zh = db.Column(db.Text)
    capacity_desc_en = db.Column(db.Text)
    capacity_desc_ru = db.Column(db.Text)
    capacity_desc_es = db.Column(db.Text)
    extra_price = db.Column(db.Numeric(10, 2), default=0)
    pickup_price = db.Column(db.Numeric(10, 2), default=0)
    dropoff_price = db.Column(db.Numeric(10, 2), default=0)
    combo_price = db.Column(db.Numeric(10, 2), default=0)
    image = db.Column(db.String(255))
    images = db.Column(db.JSON, default=[])
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=china_now)

    def to_dict(self, lang='zh'):
        # 标准化图片 URL（与 Product 保持一致）
        image_list = _normalize_image_urls(_ensure_list(self.images) or ([] if not self.image else [self.image]))
        image_url = image_list[0] if image_list else None

        capacity_desc = _localized(self, 'capacity_desc', lang)
        model_name = _localized(self, 'model', lang)
        luggage_28 = self.luggage_28 if self.luggage_28 is not None else 0
        luggage_24 = self.luggage_24 if self.luggage_24 is not None else 0

        if not capacity_desc:
            parts = []
            if luggage_28:
                parts.append(f'{luggage_28} x 28"')
            if luggage_24:
                parts.append(f'{luggage_24} x 24"')
            capacity_desc = ' + '.join(parts) if parts else None

        return {
            'id': self.id,
            'name': _localized(self, 'name', lang),
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'name_ru': self.name_ru,
            'name_es': self.name_es,
            'desc': _localized(self, 'desc', lang),
            'desc_zh': self.desc_zh,
            'desc_en': self.desc_en,
            'desc_ru': self.desc_ru,
            'desc_es': self.desc_es,
            'model': model_name,
            'model_zh': self.model_zh,
            'model_en': self.model_en,
            'model_ru': self.model_ru,
            'model_es': self.model_es,
            'seats': self.seats,
            'luggage_capacity': self.luggage_capacity,
            'luggage_28': luggage_28,
            'luggage_24': luggage_24,
            'capacity_desc': capacity_desc,
            'capacity_desc_zh': self.capacity_desc_zh,
            'capacity_desc_en': self.capacity_desc_en,
            'capacity_desc_ru': self.capacity_desc_ru,
            'capacity_desc_es': self.capacity_desc_es,
            'extra_price': float(self.extra_price) if self.extra_price else 0,
            'pickup_price': float(self.pickup_price) if self.pickup_price else 0,
            'dropoff_price': float(self.dropoff_price) if self.dropoff_price else 0,
            'combo_price': float(self.combo_price) if self.combo_price else 0,
            'image': image_url,
            'images': image_list,
            'sort_order': self.sort_order,
            'status': self.status
        }


class Setting(db.Model):
    """系统配置表"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)
    
    @staticmethod
    def get_value(key, default=None):
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default


class Coupon(db.Model):
    """优惠券表"""
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    name_zh = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    discount_type = db.Column(db.String(20), nullable=False)  # fixed, percent
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    min_amount = db.Column(db.Numeric(10, 2), default=0)
    max_discount = db.Column(db.Numeric(10, 2))
    apply_to = db.Column(db.String(20), default='all')  # all, shop, transfer
    total_count = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    per_limit = db.Column(db.Integer, default=1)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)
    
    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'code': self.code,
            'name': _localized(self, 'name', lang),
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value),
            'min_amount': float(self.min_amount) if self.min_amount else 0,
            'max_discount': float(self.max_discount) if self.max_discount else None,
            'apply_to': self.apply_to,
            'total_count': self.total_count,
            'used_count': self.used_count,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status
        }
    
    def is_valid(self):
        """检查优惠券是否有效"""
        now = china_now()
        if self.status != 1:
            return False, '优惠券已失效'
        if self.start_time and now < self.start_time:
            return False, '优惠券未到使用时间'
        if self.end_time and now > self.end_time:
            return False, '优惠券已过期'
        if self.total_count and self.used_count >= self.total_count:
            return False, '优惠券已领完'
        return True, 'ok'
    
    def calculate_discount(self, amount):
        """计算优惠金额"""
        if amount < float(self.min_amount):
            return 0
        if self.discount_type == 'fixed':
            return float(self.discount_value)
        elif self.discount_type == 'percent':
            discount = amount * float(self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, float(self.max_discount))
            return round(discount, 2)
        return 0


class CouponUsage(db.Model):
    """优惠券使用记录表"""
    __tablename__ = 'coupon_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(30))
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=china_now)


class TransferOrder(db.Model):
    """接送机订单表"""
    __tablename__ = 'transfer_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    transport_mode = db.Column(db.String(10), default='flight')  # flight, train
    service_type = db.Column(db.String(20), nullable=False)  # pickup, dropoff, combo
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    # Pickup leg (接机/接站)
    pickup_airport = db.Column(db.String(10))   # PVG, SHA, SHRW, SHS
    flight_no = db.Column(db.String(20))
    flight_time = db.Column(db.DateTime)
    # Dropoff leg (送机)
    dropoff_airport = db.Column(db.String(10))   # PVG or SHA
    dropoff_flight_no = db.Column(db.String(20))
    dropoff_flight_time = db.Column(db.DateTime)
    # Homestay address
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    custom_address = db.Column(db.Text)
    custom_district = db.Column(db.String(50))
    luggage_count = db.Column(db.Integer)
    sign_name = db.Column(db.String(100))
    adult_count = db.Column(db.Integer, default=1)
    child_count = db.Column(db.Integer, default=0)
    # Booking number (third-party platform order number, e.g. Airbnb/Booking)
    booking_no = db.Column(db.String(100))
    # Resolved address (admin fills in after looking up booking_no)
    resolved_address = db.Column(db.Text)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(30))
    contact_email = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    vehicle_extra = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.SmallInteger, default=0)
    payment_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(64))
    payment_screenshot = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=0)
    cancelled_at = db.Column(db.DateTime)  # 取消时间
    refund_status = db.Column(db.SmallInteger, default=0)  # 0无需退款 1待退款 2已退款
    refund_amount = db.Column(db.Numeric(10, 2))  # 实际退款金额
    refund_time = db.Column(db.DateTime)  # 退款完成时间
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    # 关联
    vehicle = db.relationship('Vehicle', backref='orders')
    location = db.relationship('Location', backref='transfer_orders')
    coupon = db.relationship('Coupon', backref='transfer_orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'transport_mode': self.transport_mode or 'flight',
            'service_type': self.service_type,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'pickup_airport': self.pickup_airport,
            'flight_no': self.flight_no,
            'flight_time': self.flight_time.isoformat() if self.flight_time else None,
            'dropoff_airport': self.dropoff_airport,
            'dropoff_flight_no': self.dropoff_flight_no,
            'dropoff_flight_time': self.dropoff_flight_time.isoformat() if self.dropoff_flight_time else None,
            'location': self.location.to_dict() if self.location else None,
            'custom_address': self.custom_address,
            'custom_district': self.custom_district,
            'luggage_count': self.luggage_count,
            'sign_name': self.sign_name,
            'adult_count': self.adult_count or 1,
            'child_count': self.child_count or 0,
            'booking_no': self.booking_no,
            'resolved_address': self.resolved_address,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'base_price': float(self.base_price),
            'vehicle_extra': float(self.vehicle_extra) if self.vehicle_extra else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_price': float(self.total_price),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_screenshot': self.payment_screenshot,
            'status': self.status,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'refund_status': self.refund_status or 0,
            'refund_amount': float(self.refund_amount) if self.refund_amount is not None else None,
            'refund_time': self.refund_time.isoformat() if self.refund_time else None,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ShopOrder(db.Model):
    """商城订单表"""
    __tablename__ = 'shop_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    booking_no = db.Column(db.String(100))
    resolved_address = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    custom_address = db.Column(db.Text)
    custom_district = db.Column(db.String(50))
    room_number = db.Column(db.String(20))
    expected_delivery_date = db.Column(db.Date)           # 客户期望送达日期
    expected_delivery_time = db.Column(db.String(10))     # 客户期望送达时间段: morning/afternoon/evening
    checkout_date = db.Column(db.Date)                    # 退房日期 (admin录入)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(30))
    contact_email = db.Column(db.String(100))
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2))  # 成本价（管理员手动录入，用于利润核算）
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.SmallInteger, default=0)
    payment_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(64))
    payment_screenshot = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=0)  # 0待处理 1已确认 2配送中 3已完成 4已取消
    cancelled_at = db.Column(db.DateTime)  # 取消时间
    refund_status = db.Column(db.SmallInteger, default=0)  # 0无需退款 1待退款 2已退款
    refund_amount = db.Column(db.Numeric(10, 2))  # 实际退款金额
    refund_time = db.Column(db.DateTime)      # 退款时间
    delivery_time = db.Column(db.DateTime)    # 开始配送时间
    completed_time = db.Column(db.DateTime)   # 完成配送时间
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    # 关联
    location = db.relationship('Location', backref='shop_orders')
    coupon = db.relationship('Coupon', backref='shop_orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'booking_no': self.booking_no,
            'resolved_address': self.resolved_address,
            'location': self.location.to_dict() if self.location else None,
            'custom_address': self.custom_address,
            'custom_district': self.custom_district,
            'room_number': self.room_number,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'expected_delivery_time': self.expected_delivery_time,
            'checkout_date': self.checkout_date.isoformat() if self.checkout_date else None,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'subtotal': float(self.subtotal),
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_price': float(self.total_price),
            'cost_price': float(self.cost_price) if self.cost_price is not None else None,
            'profit': round(float(self.total_price) - float(self.cost_price), 2) if self.cost_price is not None else None,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_screenshot': self.payment_screenshot,
            'status': self.status,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'refund_status': self.refund_status or 0,
            'refund_amount': float(self.refund_amount) if self.refund_amount is not None else None,
            'refund_time': self.refund_time.isoformat() if self.refund_time else None,
            'delivery_time': self.delivery_time.isoformat() if self.delivery_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'items': [item.to_dict() for item in self.items],
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'review': self.review.to_dict() if self.review else None
        }


class OrderItem(db.Model):
    """订单明细表"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('shop_orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    spec_name = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # 关联
    product = db.relationship('Product', backref='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'spec_name': self.spec_name,
            'price': float(self.price),
            'quantity': self.quantity,
            'subtotal': float(self.subtotal)
        }


class Review(db.Model):
    """订单评价表"""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('shop_orders.id'), unique=True, nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=china_now)

    order = db.relationship('ShopOrder', backref=db.backref('review', uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ServiceReview(db.Model):
    """通用业务评价表：覆盖接送/门票/商城各业务线"""
    __tablename__ = 'service_reviews'

    id = db.Column(db.Integer, primary_key=True)
    # 业务类型：transfer / ticket / shop
    order_type = db.Column(db.String(20), nullable=False, index=True)
    # 订单 ID（逻辑引用，不加 FK 约束以保持灵活）
    order_id = db.Column(db.Integer, nullable=False, index=True)
    # 订单号（冗余存储，便于排查）
    order_no = db.Column(db.String(32), index=True)
    # 评价对象 ID：transfer→vehicle_id; ticket→attraction_id; shop→留空或 product_id
    target_id = db.Column(db.Integer, index=True)
    # 评分 1-5
    rating = db.Column(db.SmallInteger, nullable=False)
    # 评价内容
    comment = db.Column(db.Text)
    # 评价人显示名（取自订单 contact_name）
    reviewer_name = db.Column(db.String(50))
    # 提交时的语言
    lang = db.Column(db.String(10), default='zh')
    # 0=已发布 1=管理员隐藏
    status = db.Column(db.SmallInteger, default=0, index=True)
    # 管理员回复
    admin_reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=china_now, index=True)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    # 复合唯一约束：同一订单只能评价一次
    __table_args__ = (
        db.UniqueConstraint('order_type', 'order_id', name='uq_review_order'),
    )

    def to_dict(self, masked=False):
        # masked=True 时姓名脱敏（公开列表用），masked=False 时完整（管理端用）
        name = self.reviewer_name or ''
        if masked and name:
            # 用第一个字符 + ***，保护隐私
            name = name[0] + '***'
        return {
            'id': self.id,
            'order_type': self.order_type,
            'order_id': self.order_id,
            'order_no': self.order_no,
            'target_id': self.target_id,
            'rating': self.rating,
            'comment': self.comment,
            'reviewer_name': name,
            'lang': self.lang,
            'status': self.status,
            'admin_reply': self.admin_reply,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Wish(db.Model):
    """许愿池：用户提交的定制需求"""
    __tablename__ = 'wishes'

    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(50), nullable=False)
    contact_phone = db.Column(db.String(30))
    contact_email = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    expected_date = db.Column(db.DateTime, nullable=False)  # 期望服务时间（要求 ≥ 提交时间 + 24h）
    budget = db.Column(db.Numeric(10, 2))
    budget_currency = db.Column(db.String(10), default='CNY')
    lang = db.Column(db.String(10), default='zh')
    # 0=待处理 1=已联系 2=已完成 3=已关闭
    status = db.Column(db.SmallInteger, default=0)
    admin_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    def to_dict(self):
        return {
            'id': self.id,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'content': self.content,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'budget': float(self.budget) if self.budget is not None else None,
            'budget_currency': self.budget_currency,
            'lang': self.lang,
            'status': self.status,
            'admin_note': self.admin_note,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== 门票业务模型 ====================

class TicketAttraction(db.Model):
    """景点主表"""
    __tablename__ = 'ticket_attractions'

    id = db.Column(db.Integer, primary_key=True)
    name_zh = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))
    name_ru = db.Column(db.String(200))
    name_es = db.Column(db.String(200))
    subtitle_zh = db.Column(db.Text)
    subtitle_en = db.Column(db.Text)
    subtitle_ru = db.Column(db.Text)
    subtitle_es = db.Column(db.Text)
    desc_zh = db.Column(db.Text)
    desc_en = db.Column(db.Text)
    desc_ru = db.Column(db.Text)
    desc_es = db.Column(db.Text)
    address_zh = db.Column(db.Text)
    address_en = db.Column(db.Text)
    address_ru = db.Column(db.Text)
    address_es = db.Column(db.Text)
    open_hours_zh = db.Column(db.Text)
    open_hours_en = db.Column(db.Text)
    open_hours_ru = db.Column(db.Text)
    open_hours_es = db.Column(db.Text)
    visit_notice_zh = db.Column(db.Text)
    visit_notice_en = db.Column(db.Text)
    visit_notice_ru = db.Column(db.Text)
    visit_notice_es = db.Column(db.Text)
    refund_rule_zh = db.Column(db.Text)
    refund_rule_en = db.Column(db.Text)
    refund_rule_ru = db.Column(db.Text)
    refund_rule_es = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    images = db.Column(db.JSON, default=[])
    city = db.Column(db.String(50))
    category = db.Column(db.String(50))
    tags = db.Column(db.JSON, default=[])
    featured = db.Column(db.Boolean, default=False)
    real_name_required = db.Column(db.Boolean, default=False)
    passport_required = db.Column(db.Boolean, default=False)
    status = db.Column(db.SmallInteger, default=1)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    # ���联
    packages = db.relationship('TicketPackage', backref='attraction', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('TicketOrder', backref='attraction', lazy='dynamic')

    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'name': _localized(self, 'name', lang),
            'name_zh': self.name_zh,
            'name_en': self.name_en,
            'name_ru': self.name_ru,
            'name_es': self.name_es,
            'subtitle': _localized(self, 'subtitle', lang),
            'subtitle_zh': self.subtitle_zh,
            'subtitle_en': self.subtitle_en,
            'subtitle_ru': self.subtitle_ru,
            'subtitle_es': self.subtitle_es,
            'desc': _localized(self, 'desc', lang),
            'desc_zh': self.desc_zh,
            'desc_en': self.desc_en,
            'desc_ru': self.desc_ru,
            'desc_es': self.desc_es,
            'address': _localized(self, 'address', lang),
            'address_zh': self.address_zh,
            'address_en': self.address_en,
            'address_ru': self.address_ru,
            'address_es': self.address_es,
            'open_hours': _localized(self, 'open_hours', lang),
            'open_hours_zh': self.open_hours_zh,
            'open_hours_en': self.open_hours_en,
            'open_hours_ru': self.open_hours_ru,
            'open_hours_es': self.open_hours_es,
            'visit_notice': _localized(self, 'visit_notice', lang),
            'visit_notice_zh': self.visit_notice_zh,
            'visit_notice_en': self.visit_notice_en,
            'visit_notice_ru': self.visit_notice_ru,
            'visit_notice_es': self.visit_notice_es,
            'refund_rule': _localized(self, 'refund_rule', lang),
            'refund_rule_zh': self.refund_rule_zh,
            'refund_rule_en': self.refund_rule_en,
            'refund_rule_ru': self.refund_rule_ru,
            'refund_rule_es': self.refund_rule_es,
            'cover_image': _normalize_image_urls([self.cover_image])[0] if self.cover_image else None,
            'images': _normalize_image_urls(_ensure_list(self.images)),
            'city': self.city,
            'category': self.category,
            'tags': self.tags or [],
            'featured': self.featured,
            'real_name_required': self.real_name_required,
            'passport_required': self.passport_required,
            'status': self.status,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TicketPackage(db.Model):
    """票种表"""
    __tablename__ = 'ticket_packages'

    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('ticket_attractions.id', ondelete='CASCADE'), nullable=False)
    package_name_zh = db.Column(db.String(200), nullable=False)
    package_name_en = db.Column(db.String(200))
    package_name_ru = db.Column(db.String(200))
    package_name_es = db.Column(db.String(200))
    ticket_type = db.Column(db.String(20), nullable=False)  # adult, child, senior, family, combo
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    original_price = db.Column(db.Numeric(10, 2))
    age_rule_zh = db.Column(db.Text)
    age_rule_en = db.Column(db.Text)
    age_rule_ru = db.Column(db.Text)
    age_rule_es = db.Column(db.Text)
    booking_notice_zh = db.Column(db.Text)
    booking_notice_en = db.Column(db.Text)
    booking_notice_ru = db.Column(db.Text)
    booking_notice_es = db.Column(db.Text)
    refund_rule_zh = db.Column(db.Text)
    refund_rule_en = db.Column(db.Text)
    refund_rule_ru = db.Column(db.Text)
    refund_rule_es = db.Column(db.Text)
    inventory_mode = db.Column(db.String(20), default='unlimited')  # unlimited, manual_quota
    quota_total = db.Column(db.Integer)
    quota_used = db.Column(db.Integer, default=0)
    available_days = db.Column(db.JSON)  # 兼容旧版简单日期配置
    date_rules = db.Column(db.JSON)  # 新版日期规则：按日价格/可售/节假日标签
    status = db.Column(db.SmallInteger, default=1)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'attraction_id': self.attraction_id,
            'package_name': _localized(self, 'package_name', lang),
            'package_name_zh': self.package_name_zh,
            'package_name_en': self.package_name_en,
            'package_name_ru': self.package_name_ru,
            'package_name_es': self.package_name_es,
            'ticket_type': self.ticket_type,
            'sale_price': float(self.sale_price) if self.sale_price else 0,
            'original_price': float(self.original_price) if self.original_price else None,
            'age_rule': _localized(self, 'age_rule', lang),
            'age_rule_zh': self.age_rule_zh,
            'age_rule_en': self.age_rule_en,
            'age_rule_ru': self.age_rule_ru,
            'age_rule_es': self.age_rule_es,
            'booking_notice': _localized(self, 'booking_notice', lang),
            'booking_notice_zh': self.booking_notice_zh,
            'booking_notice_en': self.booking_notice_en,
            'booking_notice_ru': self.booking_notice_ru,
            'booking_notice_es': self.booking_notice_es,
            'refund_rule': _localized(self, 'refund_rule', lang),
            'refund_rule_zh': self.refund_rule_zh,
            'refund_rule_en': self.refund_rule_en,
            'refund_rule_ru': self.refund_rule_ru,
            'refund_rule_es': self.refund_rule_es,
            'inventory_mode': self.inventory_mode,
            'quota_total': self.quota_total,
            'quota_used': self.quota_used or 0,
            'available_days': self.available_days,
            'date_rules': self.date_rules,
            'status': self.status,
            'sort_order': self.sort_order
        }


class TicketOrder(db.Model):
    """门票订单表"""
    __tablename__ = 'ticket_orders'

    @staticmethod
    def _normalize_package_snapshot(snapshot):
        if isinstance(snapshot, list):
            return [item for item in snapshot if isinstance(item, dict)]
        if isinstance(snapshot, dict):
            return [snapshot]
        return []

    @classmethod
    def _build_package_summary(cls, snapshot):
        items = cls._normalize_package_snapshot(snapshot)
        if not items:
            return {
                'ticket_items': [],
                'package_names': [],
                'package_names_text': '-',
                'ticket_types': [],
                'ticket_types_text': '-',
                'total_quantity': 0,
                'ticket_subtotal': 0
            }

        package_names = []
        ticket_types = []
        total_quantity = 0
        ticket_subtotal = 0.0

        for item in items:
            package_name = item.get('package_name_zh') or item.get('package_name_en') or item.get('package_name')
            if package_name:
                package_names.append(package_name)

            ticket_type = item.get('ticket_type')
            if ticket_type and ticket_type not in ticket_types:
                ticket_types.append(ticket_type)

            quantity = int(item.get('quantity') or 0)
            total_quantity += quantity

            subtotal = item.get('subtotal')
            if subtotal is None:
                subtotal = float(item.get('sale_price') or 0) * quantity
            ticket_subtotal += float(subtotal or 0)

        package_names_text = ' / '.join(
            f"{(item.get('package_name_zh') or item.get('package_name_en') or item.get('package_name') or '-')} x{int(item.get('quantity') or 0)}"
            for item in items
        )
        ticket_types_text = ' / '.join(ticket_types) if ticket_types else '-'

        return {
            'ticket_items': items,
            'package_names': package_names,
            'package_names_text': package_names_text or '-',
            'ticket_types': ticket_types,
            'ticket_types_text': ticket_types_text,
            'total_quantity': total_quantity,
            'ticket_subtotal': round(ticket_subtotal, 2)
        }

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('ticket_attractions.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(30))
    contact_email = db.Column(db.String(100))
    booking_no = db.Column(db.String(100))
    lang = db.Column(db.String(10), default='zh')
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    cost_price = db.Column(db.Numeric(10, 2))  # 成本价（管理员手动录入，用于利润核算）
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))
    status = db.Column(db.SmallInteger, default=0)  # 0待处理 1已确认 2已完成 3已取消
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.SmallInteger, default=0)  # 0待支付 1已支付
    payment_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(64))
    payment_screenshot = db.Column(db.Text)
    remark = db.Column(db.Text)
    admin_note = db.Column(db.Text)
    need_transfer = db.Column(db.Boolean, default=False)
    transfer_vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    transfer_service_type = db.Column(db.String(20))  # pickup_only, dropoff_only, round_trip, charter
    transfer_price_snapshot = db.Column(db.Numeric(10, 2))
    transfer_pickup_time = db.Column(db.DateTime)
    transfer_return_time = db.Column(db.DateTime)
    transfer_user_note = db.Column(db.Text)
    transfer_pickup_location = db.Column(db.Text)
    transfer_return_location = db.Column(db.Text)
    transfer_status = db.Column(db.String(20), default='pending')
    transfer_admin_note = db.Column(db.Text)
    transfer_confirmed_at = db.Column(db.DateTime)
    transfer_vehicle_snapshot = db.Column(db.JSON)
    transfer_snapshot = db.Column(db.JSON)
    package_snapshot = db.Column(db.JSON)  # 保存订单时的票种信息快照
    voucher_delivery_status = db.Column(db.SmallInteger, default=0)  # 0未发送 1已发送
    cancelled_at = db.Column(db.DateTime)
    refund_status = db.Column(db.SmallInteger, default=0)  # 0无需退款 1待退款 2已退款
    refund_amount = db.Column(db.Numeric(10, 2))
    refund_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    # 关联
    coupon = db.relationship('Coupon', backref='ticket_orders')
    transfer_vehicle = db.relationship('Vehicle', backref='ticket_orders')
    travelers = db.relationship('TicketTraveler', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    vouchers = db.relationship('TicketVoucher', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, mask_pii=False):
        package_summary = self._build_package_summary(self.package_snapshot)
        return {
            'id': self.id,
            'order_no': self.order_no,
            'attraction': self.attraction.to_dict(self.lang) if self.attraction else None,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'booking_no': self.booking_no,
            'lang': self.lang,
            'total_price': float(self.total_price),
            'cost_price': float(self.cost_price) if self.cost_price is not None else None,
            'profit': round(float(self.total_price) - float(self.cost_price), 2) if self.cost_price is not None else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'payment_time': self.payment_time.isoformat() if self.payment_time else None,
            'transaction_id': self.transaction_id,
            'payment_screenshot': self.payment_screenshot,
            'remark': self.remark,
            'admin_note': self.admin_note,
            'need_transfer': self.need_transfer,
            'transfer_vehicle': self.transfer_vehicle.to_dict(self.lang) if self.transfer_vehicle else None,
            'transfer_service_type': self.transfer_service_type,
            'transfer_price_snapshot': float(self.transfer_price_snapshot) if self.transfer_price_snapshot else None,
            'transfer_pickup_time': self.transfer_pickup_time.isoformat() if self.transfer_pickup_time else None,
            'transfer_return_time': self.transfer_return_time.isoformat() if self.transfer_return_time else None,
            'transfer_user_note': self.transfer_user_note,
            'transfer_pickup_location': self.transfer_pickup_location,
            'transfer_return_location': self.transfer_return_location,
            'transfer_status': self.transfer_status,
            'transfer_admin_note': self.transfer_admin_note,
            'transfer_confirmed_at': self.transfer_confirmed_at.isoformat() if self.transfer_confirmed_at else None,
            'transfer_vehicle_snapshot': self.transfer_vehicle_snapshot,
            'transfer_snapshot': self.transfer_snapshot,
            'package_snapshot': package_summary['ticket_items'],
            'ticket_items': package_summary['ticket_items'],
            'package_names': package_summary['package_names'],
            'package_names_text': package_summary['package_names_text'],
            'ticket_types': package_summary['ticket_types'],
            'ticket_types_text': package_summary['ticket_types_text'],
            'total_quantity': package_summary['total_quantity'],
            'ticket_subtotal': package_summary['ticket_subtotal'],
            'voucher_delivery_status': self.voucher_delivery_status,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'refund_status': self.refund_status or 0,
            'refund_amount': float(self.refund_amount) if self.refund_amount is not None else None,
            'refund_time': self.refund_time.isoformat() if self.refund_time else None,
            'travelers': [t.to_dict(masked=mask_pii) for t in self.travelers],
            'vouchers': [v.to_dict() for v in self.vouchers],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TicketTraveler(db.Model):
    """出行人表"""
    __tablename__ = 'ticket_travelers'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('ticket_orders.id', ondelete='CASCADE'), nullable=False)
    traveler_type = db.Column(db.String(20), nullable=False)  # adult, child, senior
    full_name = db.Column(db.String(100), nullable=False)
    nationality = db.Column(db.String(50))
    document_type = db.Column(db.String(20))  # passport, id_card, etc.
    document_no = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=china_now)

    @staticmethod
    def _mask_document_no(doc_no):
        """证件号脱敏：保留前2位和后2位，中间用*替代"""
        if not doc_no:
            return None
        if len(doc_no) <= 4:
            return doc_no[0] + '***'
        return doc_no[:2] + '*' * (len(doc_no) - 4) + doc_no[-2:]

    @staticmethod
    def _mask_name(name):
        """姓名脱敏：保留第一个字符，其余用*替代"""
        if not name:
            return None
        if len(name) <= 1:
            return name + '**'
        return name[0] + '*' * (len(name) - 1)

    def to_dict(self, masked=False):
        full_name = self.full_name
        document_no = self.document_no
        dob = self.date_of_birth.isoformat() if self.date_of_birth else None

        if masked:
            full_name = self._mask_name(full_name)
            document_no = self._mask_document_no(document_no)
            if dob:
                dob = dob[:4] + '-**-**'

        return {
            'id': self.id,
            'order_id': self.order_id,
            'traveler_type': self.traveler_type,
            'full_name': full_name,
            'nationality': self.nationality,
            'document_type': self.document_type,
            'document_no': document_no,
            'date_of_birth': dob,
            'gender': self.gender
        }


class TicketVoucher(db.Model):
    """票据文件表"""
    __tablename__ = 'ticket_vouchers'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('ticket_orders.id', ondelete='CASCADE'), nullable=False)
    file_url = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.Text)
    file_type = db.Column(db.String(20))  # pdf, jpg, png, etc.
    uploaded_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    sent_to_customer = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=china_now)

    # 关联
    uploader = db.relationship('Admin', backref='uploaded_vouchers')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'uploaded_by': self.uploaded_by,
            'sent_to_customer': self.sent_to_customer,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Guide(db.Model):
    """免费攻略"""
    __tablename__ = 'guides'

    id = db.Column(db.Integer, primary_key=True)
    title_zh = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200))
    title_ru = db.Column(db.String(200))
    title_es = db.Column(db.String(200))
    summary_zh = db.Column(db.Text)
    summary_en = db.Column(db.Text)
    summary_ru = db.Column(db.Text)
    summary_es = db.Column(db.Text)
    content_zh = db.Column(db.Text)
    content_en = db.Column(db.Text)
    content_ru = db.Column(db.Text)
    content_es = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    images = db.Column(db.JSON, default=[])
    category = db.Column(db.String(50))  # food, attraction, entertainment, shopping
    attraction_id = db.Column(db.Integer, db.ForeignKey('ticket_attractions.id'))
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)  # 0=下架 1=上架
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    attraction = db.relationship('TicketAttraction', backref='guides')

    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'title': _localized(self, 'title', lang),
            'title_zh': self.title_zh,
            'title_en': self.title_en,
            'title_ru': self.title_ru,
            'title_es': self.title_es,
            'summary': _localized(self, 'summary', lang),
            'summary_zh': self.summary_zh,
            'summary_en': self.summary_en,
            'summary_ru': self.summary_ru,
            'summary_es': self.summary_es,
            'content': _localized(self, 'content', lang),
            'content_zh': self.content_zh,
            'content_en': self.content_en,
            'content_ru': self.content_ru,
            'content_es': self.content_es,
            'cover_image': _normalize_image_urls([self.cover_image])[0] if self.cover_image else None,
            'images': _normalize_image_urls(_ensure_list(self.images)),
            'category': self.category,
            'attraction_id': self.attraction_id,
            'attraction': self.attraction.to_dict(lang) if self.attraction else None,
            'sort_order': self.sort_order,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class TicketTransportPrice(db.Model):
    """门票加购用车价格表"""
    __tablename__ = 'ticket_transport_prices'

    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('ticket_attractions.id', ondelete='CASCADE'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    service_type = db.Column(db.String(20), nullable=False)  # pickup_only, dropoff_only, round_trip, charter
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.SmallInteger, default=1)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    # 关联
    attraction = db.relationship('TicketAttraction', backref='transport_prices')
    vehicle = db.relationship('Vehicle', backref='ticket_transport_prices')

    def to_dict(self, lang='zh'):
        return {
            'id': self.id,
            'attraction_id': self.attraction_id,
            'vehicle_id': self.vehicle_id,
            'vehicle': self.vehicle.to_dict(lang) if self.vehicle else None,
            'service_type': self.service_type,
            'price': float(self.price) if self.price else 0,
            'status': self.status,
            'sort_order': self.sort_order
        }


class GuestRegistration(db.Model):
    """境外人员住宿登记表"""
    __tablename__ = 'guest_registrations'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)  # booking / trip / agoda / expedia
    booking_no = db.Column(db.String(100), nullable=False)
    document_type = db.Column(db.String(20), default='passport')  # passport / hkmo / taiwan
    document_no = db.Column(db.String(50))  # 证件号码
    surname = db.Column(db.String(100), nullable=False)
    given_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date, nullable=False)
    passport_image = db.Column(db.String(255), nullable=False)   # 私密存储 key: private/<uuid>.<ext>
    handheld_image = db.Column(db.String(255), nullable=False)   # 手持护照照片 key
    checkin_date = db.Column(db.Date)   # 入住日期
    checkin_time = db.Column(db.String(20))  # 入住时间（如 "18:00" 或 "03:00 (+1)" 次日凌晨）
    checkout_date = db.Column(db.Date)  # 离开日期
    room_note = db.Column(db.String(100))  # 房间备注（管理员填写，组内共享）
    group_id = db.Column(db.String(40))    # 手动合并分组ID；为空时按 平台+预约单号 自动分组
    lang = db.Column(db.String(10), default='en')  # 登记时使用的界面语言
    status = db.Column(db.SmallInteger, default=0)  # 0待申报 1已申报
    created_at = db.Column(db.DateTime, default=china_now)
    updated_at = db.Column(db.DateTime, default=china_now, onupdate=china_now)

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'booking_no': self.booking_no,
            'document_type': self.document_type or 'passport',
            'document_no': self.document_no,
            'surname': self.surname,
            'given_name': self.given_name,
            'middle_name': self.middle_name,
            'full_name': ' '.join(filter(None, [self.surname, self.middle_name, self.given_name])),
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'passport_image': self.passport_image,
            'handheld_image': self.handheld_image,
            'checkin_date': self.checkin_date.isoformat() if self.checkin_date else None,
            'checkin_time': self.checkin_time,
            'checkout_date': self.checkout_date.isoformat() if self.checkout_date else None,
            'room_note': self.room_note,
            'group_id': self.group_id,
            'lang': self.lang,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
