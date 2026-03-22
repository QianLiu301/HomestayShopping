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


# ==================== 数据分析 ====================

@api_bp.route('/admin/analytics/top-products', methods=['GET'])
@admin_required
def admin_top_products():
    """热销商品排行"""
    from app.models import OrderItem
    limit = request.args.get('limit', 10, type=int)

    # 统计已完成订单（非取消）的商品销量
    rows = db.session.query(
        OrderItem.product_id,
        OrderItem.product_name,
        db.func.sum(OrderItem.quantity).label('total_qty'),
        db.func.sum(OrderItem.subtotal).label('total_revenue')
    ).join(ShopOrder, OrderItem.order_id == ShopOrder.id).filter(
        ShopOrder.status != 4  # 排除已取消
    ).group_by(OrderItem.product_id, OrderItem.product_name).order_by(
        db.func.sum(OrderItem.quantity).desc()
    ).limit(limit).all()

    result = [{
        'product_id': r.product_id,
        'product_name': r.product_name,
        'total_qty': int(r.total_qty),
        'total_revenue': round(float(r.total_revenue), 2)
    } for r in rows]

    return success_response(result)


@api_bp.route('/admin/analytics', methods=['GET'])
@admin_required
def admin_analytics():
    """营业数据分析 — DB-agnostic (aggregate in Python)"""
    from datetime import datetime, timedelta
    from collections import defaultdict

    period = request.args.get('period', 'month')  # month / quarter / half_year

    now = datetime.now()
    if period == 'quarter':
        start = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1)
    elif period == 'half_year':
        start = datetime(now.year, now.month, 1) - timedelta(days=180)
        start = datetime(start.year, start.month, 1)
    else:
        start = datetime(now.year, now.month, 1)

    shop_cancelled = 4   # 商城订单取消状态码
    transfer_cancelled = 3  # 接送订单取消状态码

    # Fetch raw rows (only need created_at + total_price)
    shop_rows = db.session.query(
        ShopOrder.created_at, ShopOrder.total_price
    ).filter(
        ShopOrder.created_at >= start,
        ShopOrder.status != shop_cancelled
    ).all()

    transfer_rows = db.session.query(
        TransferOrder.created_at, TransferOrder.total_price
    ).filter(
        TransferOrder.created_at >= start,
        TransferOrder.status != transfer_cancelled
    ).all()

    shop_count = len(shop_rows)
    shop_total = sum(float(r.total_price or 0) for r in shop_rows)
    transfer_count = len(transfer_rows)
    transfer_total = sum(float(r.total_price or 0) for r in transfer_rows)

    # Build chart data in Python
    if period == 'month':
        # 按天
        fmt = '%Y-%m-%d'
        days = []
        d = start
        while d <= now:
            days.append(d.strftime(fmt))
            d += timedelta(days=1)
        labels = days
    else:
        # 按月
        fmt = '%Y-%m'
        labels = []
        d = start
        while d <= now:
            m = d.strftime(fmt)
            if m not in labels:
                labels.append(m)
            if d.month == 12:
                d = datetime(d.year + 1, 1, 1)
            else:
                d = datetime(d.year, d.month + 1, 1)

    shop_map = defaultdict(float)
    for r in shop_rows:
        if r.created_at:
            shop_map[r.created_at.strftime(fmt)] += float(r.total_price or 0)

    transfer_map = defaultdict(float)
    for r in transfer_rows:
        if r.created_at:
            transfer_map[r.created_at.strftime(fmt)] += float(r.total_price or 0)

    chart = {
        'labels': labels,
        'shop': [round(shop_map.get(l, 0), 2) for l in labels],
        'transfer': [round(transfer_map.get(l, 0), 2) for l in labels]
    }

    return success_response({
        'shop_count': shop_count,
        'shop_total': round(shop_total, 2),
        'transfer_count': transfer_count,
        'transfer_total': round(transfer_total, 2),
        'total_revenue': round(shop_total + transfer_total, 2),
        'chart': chart
    })


# ==================== 订单管理 ====================

@api_bp.route('/admin/orders/shop', methods=['GET'])
@admin_required
def admin_get_shop_orders():
    """获取商城订单列表"""
    from datetime import datetime
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')

    query = ShopOrder.query

    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (ShopOrder.order_no.ilike(f'%{keyword}%')) |
            (ShopOrder.contact_name.ilike(f'%{keyword}%')) |
            (ShopOrder.booking_no.ilike(f'%{keyword}%'))
        )
    if date_start:
        try:
            query = query.filter(ShopOrder.created_at >= datetime.fromisoformat(date_start))
        except ValueError:
            pass
    if date_end:
        try:
            query = query.filter(ShopOrder.created_at <= datetime.fromisoformat(date_end + 'T23:59:59'))
        except ValueError:
            pass

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
        from app.models import china_now
        new_status = data['status']
        old_status = order.status
        order.status = new_status
        # 自动记录配送/完成时间
        if new_status == 2 and old_status != 2 and not order.delivery_time:
            order.delivery_time = china_now()
        if new_status == 3 and old_status != 3 and not order.completed_time:
            order.completed_time = china_now()
    if 'remark' in data:
        order.remark = data['remark']
    if 'booking_no' in data:
        order.booking_no = data['booking_no']
    if 'resolved_address' in data:
        order.resolved_address = data['resolved_address']
    if 'checkout_date' in data:
        from datetime import date as date_cls
        raw = data['checkout_date']
        if raw:
            try:
                order.checkout_date = date_cls.fromisoformat(raw)
            except (ValueError, TypeError):
                pass
        else:
            order.checkout_date = None

    db.session.commit()

    return success_response(order.to_dict(), '更新成功')


@api_bp.route('/admin/orders/transfer', methods=['GET'])
@admin_required
def admin_get_transfer_orders():
    """获取接送机订单列表"""
    from datetime import datetime
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')

    query = TransferOrder.query

    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (TransferOrder.order_no.ilike(f'%{keyword}%')) |
            (TransferOrder.contact_name.ilike(f'%{keyword}%'))
        )
    if date_start:
        try:
            query = query.filter(TransferOrder.created_at >= datetime.fromisoformat(date_start))
        except ValueError:
            pass
    if date_end:
        try:
            query = query.filter(TransferOrder.created_at <= datetime.fromisoformat(date_end + 'T23:59:59'))
        except ValueError:
            pass

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
    if 'booking_no' in data:
        order.booking_no = data['booking_no']
    if 'resolved_address' in data:
        order.resolved_address = data['resolved_address']

    db.session.commit()

    return success_response(order.to_dict(), '更新成功')


# ==================== 批量删除订单 ====================

@api_bp.route('/admin/orders/shop/batch-delete', methods=['POST'])
@admin_required
def admin_batch_delete_shop_orders():
    """批量删除商城订单"""
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return error_response('请选择要删除的订单')
    orders = ShopOrder.query.filter(ShopOrder.id.in_(ids)).all()
    count = len(orders)
    for o in orders:
        db.session.delete(o)
    db.session.commit()
    return success_response({'deleted': count}, f'已删除 {count} 个订单')


@api_bp.route('/admin/orders/transfer/batch-delete', methods=['POST'])
@admin_required
def admin_batch_delete_transfer_orders():
    """批量删除接送机订单"""
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return error_response('请选择要删除的订单')
    orders = TransferOrder.query.filter(TransferOrder.id.in_(ids)).all()
    count = len(orders)
    for o in orders:
        db.session.delete(o)
    db.session.commit()
    return success_response({'deleted': count}, f'已删除 {count} 个订单')


# ==================== 确认收款 ====================

@api_bp.route('/admin/orders/shop/<int:order_id>/confirm-payment', methods=['POST'])
@admin_required
def admin_confirm_shop_payment(order_id):
    """管理员确认商城订单已收款"""
    from app.models import china_now
    order = ShopOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    order.payment_status = 1
    order.payment_time = china_now()
    db.session.commit()
    return success_response(order.to_dict(), '已确认收款')


@api_bp.route('/admin/orders/transfer/<int:order_id>/confirm-payment', methods=['POST'])
@admin_required
def admin_confirm_transfer_payment(order_id):
    """管理员确认接送机订单已收款"""
    from app.models import china_now
    order = TransferOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    order.payment_status = 1
    order.payment_time = china_now()
    db.session.commit()
    return success_response(order.to_dict(), '已确认收款')


# ==================== 配送管理 ====================

@api_bp.route('/admin/delivery/orders', methods=['GET'])
@admin_required
def admin_get_delivery_orders():
    """获取待配送/配送中的订单列表（分页，按期望送达/退房日期排序）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', type=int)  # 1=已确认(待配送), 2=配送中
    keyword = request.args.get('keyword', '')

    query = ShopOrder.query.filter(ShopOrder.status.in_([1, 2]))

    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (ShopOrder.order_no.ilike(f'%{keyword}%')) |
            (ShopOrder.contact_name.ilike(f'%{keyword}%')) |
            (ShopOrder.booking_no.ilike(f'%{keyword}%')) |
            (ShopOrder.resolved_address.ilike(f'%{keyword}%'))
        )

    # 按期望送达日期优先，退房日期次之，最后创建时间
    query = query.order_by(
        ShopOrder.expected_delivery_date.asc().nullslast(),
        ShopOrder.checkout_date.asc().nullslast(),
        ShopOrder.created_at.asc()
    )

    result = paginate_query(query, page, per_page)

    orders = [o.to_dict() for o in result['items']]

    return success_response({
        'orders': orders,
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages']
    })


@api_bp.route('/admin/delivery/start', methods=['POST'])
@admin_required
def admin_start_delivery():
    """批量开始配送"""
    from app.models import china_now
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return error_response('请选择要配送的订单')

    now = china_now()
    count = 0
    orders = ShopOrder.query.filter(ShopOrder.id.in_(ids), ShopOrder.status == 1).all()
    for o in orders:
        o.status = 2
        o.delivery_time = now
        count += 1

    db.session.commit()
    return success_response({'updated': count}, f'已开始配送 {count} 个订单')


@api_bp.route('/admin/delivery/complete', methods=['POST'])
@admin_required
def admin_complete_delivery():
    """批量确认送达"""
    from app.models import china_now
    data = request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return error_response('请选择要完成的订单')

    now = china_now()
    count = 0
    orders = ShopOrder.query.filter(ShopOrder.id.in_(ids), ShopOrder.status == 2).all()
    for o in orders:
        o.status = 3
        o.completed_time = now
        count += 1

    db.session.commit()
    return success_response({'updated': count}, f'已完成配送 {count} 个订单')


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
