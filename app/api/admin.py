import os
import uuid
from flask import request, current_app
from app.api import api_bp
from app.models import (
    Admin, Product, Category, Vehicle, Location, Setting, Coupon,
    TransferOrder, ShopOrder
)
from app import db, bcrypt
from app.utils import (
    success_response, error_response, admin_required, paginate_query
)
from app.translations import auto_fill_translations


# ==================== 文件上传 ====================

def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@api_bp.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload_file():
    """上传文件"""
    if 'file' not in request.files:
        return error_response('没有选择文件')

    file = request.files['file']
    if file.filename == '':
        return error_response('没有选择文件')

    if not allowed_file(file.filename):
        return error_response('不支持的文件格式，请上传 png/jpg/jpeg/gif/webp')

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file.save(os.path.join(upload_folder, filename))

    url = f"/uploads/{filename}"
    return success_response({'url': url}, '上传成功')


# ==================== 商品管理 ====================

@api_bp.route('/admin/products', methods=['GET'])
@admin_required
def admin_get_products():
    """获取商品列表（管理端）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (Product.name_zh.ilike(f'%{keyword}%')) |
            (Product.name_en.ilike(f'%{keyword}%'))
        )
    
    query = query.order_by(Product.sort_order.desc(), Product.id.desc())
    result = paginate_query(query, page, per_page)
    
    return success_response({
        'list': [p.to_dict() for p in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages']
    })


@api_bp.route('/admin/products', methods=['POST'])
@admin_required
def admin_create_product():
    """创建商品"""
    data = request.get_json()
    data = auto_fill_translations(data, ['name', 'desc'])

    name_zh = data.get('name_zh') or data.get('name_en')
    name_en = data.get('name_en') or data.get('name_zh')

    if not name_zh and not name_en:
        return error_response('商品名称不能为空')
    if not data.get('price'):
        return error_response('价格不能为空')

    product = Product(
        category_id=data.get('category_id'),
        name_zh=name_zh,
        name_en=name_en,
        name_ru=data.get('name_ru'),
        name_es=data.get('name_es'),
        desc_zh=data.get('desc_zh') or data.get('desc_en'),
        desc_en=data.get('desc_en') or data.get('desc_zh'),
        desc_ru=data.get('desc_ru'),
        desc_es=data.get('desc_es'),
        price=data.get('price'),
        original_price=data.get('original_price'),
        images=data.get('images', []),
        specs=data.get('specs'),
        sort_order=data.get('sort_order', 0),
        is_featured=data.get('is_featured', False),
        status=data.get('status', 1)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return success_response(product.to_dict(), '创建成功')


@api_bp.route('/admin/products/<int:product_id>', methods=['PUT'])
@admin_required
def admin_update_product(product_id):
    """更新商品"""
    product = Product.query.get(product_id)
    if not product:
        return error_response('商品不存在', 404)

    data = request.get_json()
    data = auto_fill_translations(data, ['name', 'desc'])

    # 更新字段
    fields = [
        'category_id', 'name_zh', 'name_en', 'name_ru', 'name_es',
        'desc_zh', 'desc_en', 'desc_ru', 'desc_es',
        'price', 'original_price', 'images', 'specs',
        'sort_order', 'is_featured', 'status'
    ]
    
    for field in fields:
        if field in data:
            setattr(product, field, data[field])
    
    db.session.commit()
    
    return success_response(product.to_dict(), '更新成功')


@api_bp.route('/admin/products/<int:product_id>', methods=['DELETE'])
@admin_required
def admin_delete_product(product_id):
    """删除商品"""
    product = Product.query.get(product_id)
    if not product:
        return error_response('商品不存在', 404)
    
    db.session.delete(product)
    db.session.commit()
    
    return success_response(None, '删除成功')


# ==================== 分类管理 ====================

@api_bp.route('/admin/categories', methods=['GET'])
@admin_required
def admin_get_categories():
    """获取分类列表（管理端）"""
    categories = Category.query.order_by(Category.sort_order.desc()).all()
    return success_response([c.to_dict() for c in categories])


@api_bp.route('/admin/categories', methods=['POST'])
@admin_required
def admin_create_category():
    """创建分类"""
    data = request.get_json()
    data = auto_fill_translations(data, ['name'])

    name_zh = data.get('name_zh') or data.get('name_en')
    name_en = data.get('name_en') or data.get('name_zh')

    if not name_zh and not name_en:
        return error_response('分类名称不能为空')

    category = Category(
        name_zh=name_zh,
        name_en=name_en,
        name_ru=data.get('name_ru'),
        name_es=data.get('name_es'),
        icon=data.get('icon'),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 1)
    )
    
    db.session.add(category)
    db.session.commit()
    
    return success_response(category.to_dict(), '创建成功')


@api_bp.route('/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def admin_update_category(category_id):
    """更新分类"""
    category = Category.query.get(category_id)
    if not category:
        return error_response('分类不存在', 404)

    data = request.get_json()
    data = auto_fill_translations(data, ['name'])

    fields = ['name_zh', 'name_en', 'name_ru', 'name_es', 'icon', 'sort_order', 'status']
    for field in fields:
        if field in data:
            setattr(category, field, data[field])
    
    db.session.commit()
    
    return success_response(category.to_dict(), '更新成功')


@api_bp.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def admin_delete_category(category_id):
    """删除分类"""
    category = Category.query.get(category_id)
    if not category:
        return error_response('分类不存在', 404)
    
    # 检查是否有商品使用此分类
    if Product.query.filter_by(category_id=category_id).first():
        return error_response('该分类下有商品，无法删除')
    
    db.session.delete(category)
    db.session.commit()
    
    return success_response(None, '删除成功')


# ==================== 车型管理 ====================

@api_bp.route('/admin/vehicles', methods=['GET'])
@admin_required
def admin_get_vehicles():
    """获取车型列表（管理端）"""
    vehicles = Vehicle.query.order_by(Vehicle.sort_order.desc()).all()
    return success_response([v.to_dict() for v in vehicles])


@api_bp.route('/admin/vehicles', methods=['POST'])
@admin_required
def admin_create_vehicle():
    """创建车型"""
    data = request.get_json()
    data = auto_fill_translations(data, ['name', 'desc'])

    name_zh = data.get('name_zh') or data.get('name_en')
    name_en = data.get('name_en') or data.get('name_zh')

    if not name_zh and not name_en:
        return error_response('车型名称不能为空')

    vehicle = Vehicle(
        name_zh=name_zh,
        name_en=name_en,
        name_ru=data.get('name_ru'),
        name_es=data.get('name_es'),
        desc_zh=data.get('desc_zh') or data.get('desc_en'),
        desc_en=data.get('desc_en') or data.get('desc_zh'),
        desc_ru=data.get('desc_ru'),
        desc_es=data.get('desc_es'),
        seats=data.get('seats', 5),
        luggage_capacity=data.get('luggage_capacity', 2),
        extra_price=data.get('extra_price', 0),
        image=data.get('image'),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 1)
    )
    
    db.session.add(vehicle)
    db.session.commit()
    
    return success_response(vehicle.to_dict(), '创建成功')


@api_bp.route('/admin/vehicles/<int:vehicle_id>', methods=['PUT'])
@admin_required
def admin_update_vehicle(vehicle_id):
    """更新车型"""
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return error_response('车型不存在', 404)

    data = request.get_json()
    data = auto_fill_translations(data, ['name', 'desc'])

    fields = [
        'name_zh', 'name_en', 'name_ru', 'name_es',
        'desc_zh', 'desc_en', 'desc_ru', 'desc_es',
        'seats', 'luggage_capacity',
        'extra_price', 'image', 'sort_order', 'status'
    ]
    
    for field in fields:
        if field in data:
            setattr(vehicle, field, data[field])
    
    db.session.commit()
    
    return success_response(vehicle.to_dict(), '更新成功')


@api_bp.route('/admin/vehicles/<int:vehicle_id>', methods=['DELETE'])
@admin_required
def admin_delete_vehicle(vehicle_id):
    """删除车型"""
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return error_response('车型不存在', 404)
    
    db.session.delete(vehicle)
    db.session.commit()
    
    return success_response(None, '删除成功')


# ==================== 民宿点管理 ====================

@api_bp.route('/admin/locations', methods=['GET'])
@admin_required
def admin_get_locations():
    """获取民宿点列表（管理端）"""
    locations = Location.query.order_by(Location.sort_order.desc()).all()
    return success_response([loc.to_dict() for loc in locations])


@api_bp.route('/admin/locations', methods=['POST'])
@admin_required
def admin_create_location():
    """创建民宿点"""
    data = request.get_json()
    data = auto_fill_translations(data, ['name', 'address'])

    name_zh = data.get('name_zh') or data.get('name_en')
    name_en = data.get('name_en') or data.get('name_zh')
    address_zh = data.get('address_zh') or data.get('address_en')
    address_en = data.get('address_en') or data.get('address_zh')

    if not name_zh and not name_en:
        return error_response('名称不能为空')
    if not address_zh and not address_en:
        return error_response('地址不能为空')

    location = Location(
        name_zh=name_zh,
        name_en=name_en,
        name_ru=data.get('name_ru'),
        name_es=data.get('name_es'),
        address_zh=address_zh,
        address_en=address_en,
        address_ru=data.get('address_ru'),
        address_es=data.get('address_es'),
        district=data.get('district'),
        sort_order=data.get('sort_order', 0),
        status=data.get('status', 1)
    )
    
    db.session.add(location)
    db.session.commit()
    
    return success_response(location.to_dict(), '创建成功')


@api_bp.route('/admin/locations/<int:location_id>', methods=['PUT'])
@admin_required
def admin_update_location(location_id):
    """更新民宿点"""
    location = Location.query.get(location_id)
    if not location:
        return error_response('民宿点不存在', 404)

    data = request.get_json()
    data = auto_fill_translations(data, ['name', 'address'])

    fields = [
        'name_zh', 'name_en', 'name_ru', 'name_es',
        'address_zh', 'address_en', 'address_ru', 'address_es',
        'district', 'sort_order', 'status'
    ]
    
    for field in fields:
        if field in data:
            setattr(location, field, data[field])
    
    db.session.commit()
    
    return success_response(location.to_dict(), '更新成功')


@api_bp.route('/admin/locations/<int:location_id>', methods=['DELETE'])
@admin_required
def admin_delete_location(location_id):
    """删除民宿点"""
    location = Location.query.get(location_id)
    if not location:
        return error_response('民宿点不存在', 404)
    
    db.session.delete(location)
    db.session.commit()
    
    return success_response(None, '删除成功')


# ==================== 订单管理 ====================

@api_bp.route('/admin/orders/shop', methods=['GET'])
@admin_required
def admin_get_shop_orders():
    """获取商城订单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    
    query = ShopOrder.query
    
    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (ShopOrder.order_no.ilike(f'%{keyword}%')) |
            (ShopOrder.contact_name.ilike(f'%{keyword}%'))
        )
    
    query = query.order_by(ShopOrder.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return success_response({
        'list': [o.to_dict() for o in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages']
    })


@api_bp.route('/admin/orders/shop/<int:order_id>', methods=['PUT'])
@admin_required
def admin_update_shop_order(order_id):
    """更新商城订单状态"""
    order = ShopOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    
    data = request.get_json()
    
    if 'status' in data:
        order.status = data['status']
    if 'remark' in data:
        order.remark = data['remark']
    
    db.session.commit()
    
    return success_response(order.to_dict(), '更新成功')


@api_bp.route('/admin/orders/transfer', methods=['GET'])
@admin_required
def admin_get_transfer_orders():
    """获取接送机订单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    
    query = TransferOrder.query
    
    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (TransferOrder.order_no.ilike(f'%{keyword}%')) |
            (TransferOrder.contact_name.ilike(f'%{keyword}%'))
        )
    
    query = query.order_by(TransferOrder.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return success_response({
        'list': [o.to_dict() for o in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages']
    })


@api_bp.route('/admin/orders/transfer/<int:order_id>', methods=['PUT'])
@admin_required
def admin_update_transfer_order(order_id):
    """更新接送机订单状态"""
    order = TransferOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    
    data = request.get_json()
    
    if 'status' in data:
        order.status = data['status']
    if 'remark' in data:
        order.remark = data['remark']
    
    db.session.commit()
    
    return success_response(order.to_dict(), '更新成功')


# ==================== 确认收款 ====================

@api_bp.route('/admin/orders/shop/<int:order_id>/confirm-payment', methods=['POST'])
@admin_required
def admin_confirm_shop_payment(order_id):
    """管理员确认商城订单已收款"""
    from datetime import datetime
    order = ShopOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    order.payment_status = 1
    order.payment_time = datetime.utcnow()
    db.session.commit()
    return success_response(order.to_dict(), '已确认收款')


@api_bp.route('/admin/orders/transfer/<int:order_id>/confirm-payment', methods=['POST'])
@admin_required
def admin_confirm_transfer_payment(order_id):
    """管理员确认接送机订单已收款"""
    from datetime import datetime
    order = TransferOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    order.payment_status = 1
    order.payment_time = datetime.utcnow()
    db.session.commit()
    return success_response(order.to_dict(), '已确认收款')


# ==================== 优惠券管理 ====================

@api_bp.route('/admin/coupons', methods=['GET'])
@admin_required
def admin_get_coupons():
    """获取优惠券列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Coupon.query.order_by(Coupon.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return success_response({
        'list': [c.to_dict() for c in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages']
    })


@api_bp.route('/admin/coupons', methods=['POST'])
@admin_required
def admin_create_coupon():
    """创建优惠券"""
    data = request.get_json()
    
    if not data.get('code') or not data.get('name_zh'):
        return error_response('优惠券码和名称不能为空')
    
    # 检查优惠券码是否存在
    if Coupon.query.filter_by(code=data.get('code').upper()).first():
        return error_response('优惠券码已存在')
    
    coupon = Coupon(
        code=data.get('code').upper(),
        name_zh=data.get('name_zh'),
        name_en=data.get('name_en'),
        discount_type=data.get('discount_type', 'fixed'),
        discount_value=data.get('discount_value', 0),
        min_amount=data.get('min_amount', 0),
        max_discount=data.get('max_discount'),
        apply_to=data.get('apply_to', 'all'),
        total_count=data.get('total_count'),
        per_limit=data.get('per_limit', 1),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        status=data.get('status', 1)
    )
    
    db.session.add(coupon)
    db.session.commit()
    
    return success_response(coupon.to_dict(), '创建成功')


@api_bp.route('/admin/coupons/<int:coupon_id>', methods=['PUT'])
@admin_required
def admin_update_coupon(coupon_id):
    """更新优惠券"""
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return error_response('优惠券不存在', 404)
    
    data = request.get_json()
    
    fields = [
        'name_zh', 'name_en', 'discount_type', 'discount_value',
        'min_amount', 'max_discount', 'apply_to', 'total_count',
        'per_limit', 'start_time', 'end_time', 'status'
    ]
    
    for field in fields:
        if field in data:
            setattr(coupon, field, data[field])
    
    db.session.commit()
    
    return success_response(coupon.to_dict(), '更新成功')


@api_bp.route('/admin/coupons/<int:coupon_id>', methods=['DELETE'])
@admin_required
def admin_delete_coupon(coupon_id):
    """删除优惠券"""
    coupon = Coupon.query.get(coupon_id)
    if not coupon:
        return error_response('优惠券不存在', 404)
    
    db.session.delete(coupon)
    db.session.commit()
    
    return success_response(None, '删除成功')
