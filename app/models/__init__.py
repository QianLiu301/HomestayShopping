from datetime import datetime
from app import db


def _localized(obj, field, lang):
    """Get localized field with fallback: target lang -> en -> zh"""
    return (
        getattr(obj, f'{field}_{lang}', None)
        or getattr(obj, f'{field}_en', None)
        or getattr(obj, f'{field}_zh', None)
    )


class Admin(db.Model):
    """管理员表"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='admin')
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    address_zh = db.Column(db.String(255), nullable=False)
    address_en = db.Column(db.String(255))
    address_ru = db.Column(db.String(255))
    address_es = db.Column(db.String(255))
    district = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    name_zh = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    name_ru = db.Column(db.String(100))
    name_es = db.Column(db.String(100))
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'images': self.images or [],
            'specs': self.specs,
            'is_featured': self.is_featured,
            'sort_order': self.sort_order,
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
    desc_zh = db.Column(db.String(100))
    desc_en = db.Column(db.String(100))
    desc_ru = db.Column(db.String(100))
    desc_es = db.Column(db.String(100))
    seats = db.Column(db.Integer, nullable=False)
    luggage_capacity = db.Column(db.Integer, nullable=False)
    extra_price = db.Column(db.Numeric(10, 2), default=0)
    image = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, lang='zh'):
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
            'seats': self.seats,
            'luggage_capacity': self.luggage_capacity,
            'extra_price': float(self.extra_price) if self.extra_price else 0,
            'image': self.image,
            'sort_order': self.sort_order,
            'status': self.status
        }


class Setting(db.Model):
    """系统配置表"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
        now = datetime.utcnow()
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
    used_at = db.Column(db.DateTime, default=datetime.utcnow)


class TransferOrder(db.Model):
    """接送机订单表"""
    __tablename__ = 'transfer_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    service_type = db.Column(db.String(20), nullable=False)  # pickup, dropoff, combo
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    flight_no = db.Column(db.String(20))
    flight_time = db.Column(db.DateTime)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    custom_address = db.Column(db.String(255))
    custom_district = db.Column(db.String(50))
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
    payment_screenshot = db.Column(db.String(255))
    status = db.Column(db.SmallInteger, default=0)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    vehicle = db.relationship('Vehicle', backref='orders')
    location = db.relationship('Location', backref='transfer_orders')
    coupon = db.relationship('Coupon', backref='transfer_orders')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'service_type': self.service_type,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'flight_no': self.flight_no,
            'flight_time': self.flight_time.isoformat() if self.flight_time else None,
            'location': self.location.to_dict() if self.location else None,
            'custom_address': self.custom_address,
            'custom_district': self.custom_district,
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
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ShopOrder(db.Model):
    """商城订单表"""
    __tablename__ = 'shop_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    custom_address = db.Column(db.String(255))
    custom_district = db.Column(db.String(50))
    room_number = db.Column(db.String(20))
    contact_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(30))
    contact_email = db.Column(db.String(100))
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20))
    payment_status = db.Column(db.SmallInteger, default=0)
    payment_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(64))
    payment_screenshot = db.Column(db.String(255))
    status = db.Column(db.SmallInteger, default=0)
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    location = db.relationship('Location', backref='shop_orders')
    coupon = db.relationship('Coupon', backref='shop_orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_no': self.order_no,
            'location': self.location.to_dict() if self.location else None,
            'custom_address': self.custom_address,
            'custom_district': self.custom_district,
            'room_number': self.room_number,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'subtotal': float(self.subtotal),
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_price': float(self.total_price),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'payment_screenshot': self.payment_screenshot,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
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
