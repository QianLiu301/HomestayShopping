import os
import uuid
from datetime import datetime
from flask import request, current_app
from app.api import api_bp
from app.models import (
    Product, Vehicle, Location, Setting, Coupon, CouponUsage,
    TransferOrder, ShopOrder, OrderItem
)
from app import db
from app.utils import success_response, error_response, generate_order_no, get_lang


@api_bp.route('/upload', methods=['POST'])
def guest_upload_file():
    """公开上传接口 - 用于买家上传付款截图"""
    if 'file' not in request.files:
        return error_response('没有选择文件')

    file = request.files['file']
    if file.filename == '':
        return error_response('没有选择文件')

    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed:
        return error_response('不支持的文件格式')

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file.save(os.path.join(upload_folder, filename))

    url = f"/uploads/{filename}"
    return success_response({'url': url}, '上传成功')


# ==================== 接送机订单 ====================

@api_bp.route('/transfer/price', methods=['GET'])
def get_transfer_price():
    """获取接送机价格配置"""
    pickup_price = float(Setting.get_value('pickup_price', 300))
    dropoff_price = float(Setting.get_value('dropoff_price', 300))
    combo_discount_pct = float(Setting.get_value('combo_discount', 10))
    combo_factor = 1 - combo_discount_pct / 100

    return success_response({
        'pickup_price': pickup_price,
        'dropoff_price': dropoff_price,
        'combo_price': round((pickup_price + dropoff_price) * combo_factor, 2),
        'combo_discount': combo_discount_pct
    })


@api_bp.route('/transfer/orders', methods=['POST'])
def create_transfer_order():
    """创建接送机订单"""
    data = request.get_json()

    if not data:
        return error_response('请求数据为空')

    # 验证必填字段
    required_fields = ['service_type', 'vehicle_id', 'contact_name']
    for field in required_fields:
        if not data.get(field):
            return error_response(f'缺少必填字段: {field}')

    # 验证服务类型
    service_type = data.get('service_type')
    if service_type not in ['pickup', 'dropoff', 'combo']:
        return error_response('无效的服务类型')

    # 验证航班信息（必填）
    if service_type in ['pickup', 'combo']:
        if not data.get('flight_no'):
            return error_response('请填写接机航班号')
        if not data.get('pickup_airport'):
            return error_response('请选择接机机场')
    if service_type in ['dropoff', 'combo']:
        dropoff_fn = data.get('dropoff_flight_no') if service_type == 'combo' else data.get('flight_no')
        if not dropoff_fn:
            return error_response('请填写送机航班号')
        dropoff_ap = data.get('dropoff_airport') if service_type == 'combo' else data.get('dropoff_airport')
        if not dropoff_ap:
            return error_response('请选择送机机场')

    # 验证车型
    vehicle = Vehicle.query.filter_by(id=data.get('vehicle_id'), status=1).first()
    if not vehicle:
        return error_response('车型不存在')

    # 验证民宿地址
    location_id = data.get('location_id')
    custom_address = data.get('custom_address')
    custom_district = data.get('custom_district')

    if location_id:
        location = Location.query.filter_by(id=location_id, status=1).first()
        if not location:
            return error_response('民宿点不存在')
    elif custom_address:
        if not custom_district:
            return error_response('请选择所在区')
    else:
        return error_response('请选择或填写民宿地址')

    # 验证联系方式
    contact_phone = data.get('contact_phone')
    contact_email = data.get('contact_email')
    if not contact_phone and not contact_email:
        return error_response('请填写手机号或邮箱')

    # 计算价格
    pickup_price = float(Setting.get_value('pickup_price', 300))
    dropoff_price = float(Setting.get_value('dropoff_price', 300))
    combo_discount_pct = float(Setting.get_value('combo_discount', 10))
    combo_factor = 1 - combo_discount_pct / 100

    if service_type == 'pickup':
        base_price = pickup_price
    elif service_type == 'dropoff':
        base_price = dropoff_price
    else:  # combo
        base_price = round((pickup_price + dropoff_price) * combo_factor, 2)

    vehicle_extra = float(vehicle.extra_price) if vehicle.extra_price else 0
    discount_amount = 0
    coupon_id = None

    # 验证优惠券
    coupon_code = data.get('coupon_code')
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon:
            is_valid, msg = coupon.is_valid()
            if is_valid and coupon.apply_to in ['all', 'transfer']:
                discount_amount = coupon.calculate_discount(base_price + vehicle_extra)
                coupon_id = coupon.id

    total_price = base_price + vehicle_extra - discount_amount

    # 处理航班信息
    if service_type == 'pickup':
        flight_no = data.get('flight_no')
        flight_time = data.get('flight_time')
        pickup_airport = data.get('pickup_airport')
        dropoff_airport_val = None
        dropoff_flight_no = None
        dropoff_flight_time = None
    elif service_type == 'dropoff':
        flight_no = data.get('flight_no')
        flight_time = data.get('flight_time')
        pickup_airport = None
        dropoff_airport_val = data.get('dropoff_airport')
        dropoff_flight_no = None
        dropoff_flight_time = None
    else:  # combo
        flight_no = data.get('flight_no')
        flight_time = data.get('flight_time')
        pickup_airport = data.get('pickup_airport')
        dropoff_airport_val = data.get('dropoff_airport')
        dropoff_flight_no = data.get('dropoff_flight_no')
        dropoff_flight_time = data.get('dropoff_flight_time')

    # 创建订单
    try:
        order = TransferOrder(
            order_no=generate_order_no('TR'),
            service_type=service_type,
            vehicle_id=vehicle.id,
            pickup_airport=pickup_airport,
            flight_no=flight_no,
            flight_time=flight_time,
            dropoff_airport=dropoff_airport_val,
            dropoff_flight_no=dropoff_flight_no,
            dropoff_flight_time=dropoff_flight_time,
            location_id=location_id,
            custom_address=custom_address,
            custom_district=custom_district,
            contact_name=data.get('contact_name'),
            contact_phone=contact_phone,
            contact_email=contact_email,
            base_price=base_price,
            vehicle_extra=vehicle_extra,
            discount_amount=discount_amount,
            coupon_id=coupon_id,
            total_price=total_price,
            payment_method=data.get('payment_method'),
            remark=data.get('remark'),
            status=0
        )

        db.session.add(order)
        db.session.flush()  # 获取 order.id

        # 记录优惠券使用
        if coupon_id:
            usage = CouponUsage(
                coupon_id=coupon_id,
                order_type='transfer',
                order_id=order.id,
                contact_email=contact_email,
                contact_phone=contact_phone,
                discount_amount=discount_amount
            )
            db.session.add(usage)
            coupon.used_count += 1

        db.session.commit()

        return success_response({
            'order_no': order.order_no,
            'total_price': float(order.total_price)
        }, '订单创建成功')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return error_response(f'订单创建失败: {str(e)}', 500)


# ==================== 商城订单 ====================

@api_bp.route('/shop/orders', methods=['POST'])
def create_shop_order():
    """创建商城订单"""
    data = request.get_json()
    
    if not data:
        return error_response('请求数据为空')
    
    # 验证商品列表
    items_data = data.get('items', [])
    if not items_data:
        return error_response('购物车为空')
    
    # 验证地址
    location_id = data.get('location_id')
    custom_address = data.get('custom_address')
    custom_district = data.get('custom_district')
    room_number = data.get('room_number')
    
    if location_id:
        location = Location.query.filter_by(id=location_id, status=1).first()
        if not location:
            return error_response('民宿点不存在')
    elif custom_address:
        if not custom_district:
            return error_response('请选择所在区')
    else:
        return error_response('请选择或填写地址')
    
    # 验证联系信息
    contact_name = data.get('contact_name')
    contact_phone = data.get('contact_phone')
    contact_email = data.get('contact_email')
    
    if not room_number:
        return error_response('请填写房间号')
    if not contact_name:
        return error_response('请填写收件人姓名')
    if not contact_phone and not contact_email:
        return error_response('请填写手机号或邮箱')
    
    # 计算商品小计
    subtotal = 0
    order_items = []
    
    for item_data in items_data:
        product_id = item_data.get('product_id')
        quantity = item_data.get('quantity', 1)
        spec_name = item_data.get('spec_name')
        
        product = Product.query.filter_by(id=product_id, status=1).first()
        if not product:
            return error_response(f'商品(ID:{product_id})不存在或已下架')
        
        # 获取价格（考虑规格）
        price = float(product.price)
        if spec_name and product.specs:
            for spec in product.specs:
                if spec.get('name') == spec_name:
                    price = float(spec.get('price', product.price))
                    break
        
        item_subtotal = price * quantity
        subtotal += item_subtotal
        
        order_items.append({
            'product_id': product_id,
            'product_name': product.name_zh,
            'spec_name': spec_name,
            'price': price,
            'quantity': quantity,
            'subtotal': item_subtotal
        })
    
    # 验证优惠券
    discount_amount = 0
    coupon_id = None
    coupon_code = data.get('coupon_code')
    
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon:
            is_valid, msg = coupon.is_valid()
            if is_valid and coupon.apply_to in ['all', 'shop']:
                discount_amount = coupon.calculate_discount(subtotal)
                coupon_id = coupon.id
    
    total_price = subtotal - discount_amount
    
    # 创建订单
    order = ShopOrder(
        order_no=generate_order_no('SH'),
        location_id=location_id,
        custom_address=custom_address,
        custom_district=custom_district,
        room_number=room_number,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        subtotal=subtotal,
        discount_amount=discount_amount,
        coupon_id=coupon_id,
        total_price=total_price,
        payment_method=data.get('payment_method'),
        remark=data.get('remark'),
        status=0  # 待支付
    )
    
    db.session.add(order)
    db.session.flush()  # 获取order.id
    
    # 创建订单明细
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            product_name=item['product_name'],
            spec_name=item['spec_name'],
            price=item['price'],
            quantity=item['quantity'],
            subtotal=item['subtotal']
        )
        db.session.add(order_item)
    
    # 记录优惠券使用
    if coupon_id:
        usage = CouponUsage(
            coupon_id=coupon_id,
            order_type='shop',
            order_id=order.id,
            contact_email=contact_email,
            contact_phone=contact_phone,
            discount_amount=discount_amount
        )
        db.session.add(usage)
        coupon.used_count += 1
    
    db.session.commit()
    
    return success_response({
        'order_no': order.order_no,
        'total_price': float(order.total_price)
    }, '订单创建成功')


# ==================== 订单查询 ====================

@api_bp.route('/orders/query', methods=['POST'])
def query_order():
    """查询订单（通过订单号+邮箱/手机号）"""
    data = request.get_json()
    
    if not data:
        return error_response('请求数据为空')
    
    order_no = data.get('order_no')
    contact = data.get('contact')  # 邮箱或手机号
    
    if not order_no or not contact:
        return error_response('请填写订单号和联系方式')
    
    # 先查商城订单
    shop_order = ShopOrder.query.filter_by(order_no=order_no).first()
    if shop_order:
        if shop_order.contact_email == contact or shop_order.contact_phone == contact:
            return success_response({
                'type': 'shop',
                'order': shop_order.to_dict()
            })
        else:
            return error_response('联系方式不匹配')
    
    # 再查接送机订单
    transfer_order = TransferOrder.query.filter_by(order_no=order_no).first()
    if transfer_order:
        if transfer_order.contact_email == contact or transfer_order.contact_phone == contact:
            return success_response({
                'type': 'transfer',
                'order': transfer_order.to_dict()
            })
        else:
            return error_response('联系方式不匹配')
    
    return error_response('订单不存在', 404)


# ==================== 用户确认已支付 ====================

@api_bp.route('/orders/confirm-paid', methods=['POST'])
def confirm_paid():
    """用户点击'我已支付'后，标记订单为待确认状态"""
    data = request.get_json()
    order_no = data.get('order_no')

    if not order_no:
        return error_response('缺少订单号')

    # 查找订单
    order = ShopOrder.query.filter_by(order_no=order_no).first()
    order_type = 'shop'
    if not order:
        order = TransferOrder.query.filter_by(order_no=order_no).first()
        order_type = 'transfer'

    if not order:
        return error_response('订单不存在', 404)

    # 保存支付凭证（交易单号或付款截图，二选一）
    transaction_id = data.get('transaction_id', '').strip()
    payment_screenshot = data.get('payment_screenshot', '').strip()
    if transaction_id:
        order.transaction_id = transaction_id
    if payment_screenshot:
        order.payment_screenshot = payment_screenshot

    # 标记为"用户已点击支付"（payment_status=0仍为未确认，status改为1待确认）
    if order.status == 0:
        order.status = 1  # 待确认（管理员需核实收款）
    db.session.commit()

    return success_response({
        'order_no': order.order_no,
        'type': order_type
    }, '已提交支付确认，请等待商家核实')
