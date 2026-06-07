import os
from datetime import datetime, date
from flask import request, current_app
from app.api import api_bp
from app.models import (
    Product, Vehicle, Location, Setting, Coupon, CouponUsage,
    TransferOrder, ShopOrder, OrderItem, TicketOrder
)
from app import db, limiter
from app.utils import success_response, error_response, generate_order_no, get_lang
from app.utils.storage import upload_file
from app.utils.email import (
    send_new_order_email,
    send_order_confirmation_to_customer,
    send_refund_notify_email,
    send_refund_success_to_customer,
    send_cancel_notify_to_customer,
)


@api_bp.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
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

    upload_folder = current_app.config['UPLOAD_FOLDER']
    url = upload_file(file, upload_folder)
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
@limiter.limit("10 per minute")
def create_transfer_order():
    """创建接送机/接送站订单"""
    data = request.get_json()

    if not data:
        return error_response('请求数据为空')

    # 验证必填字段
    required_fields = ['service_type', 'vehicle_id', 'contact_name']
    for field in required_fields:
        if not data.get(field):
            return error_response(f'缺少必填字段: {field}')

    # 交通方式：flight(飞机) 或 train(火车)
    transport_mode = data.get('transport_mode', 'flight')
    if transport_mode not in ('flight', 'train'):
        transport_mode = 'flight'

    # 合法站点代码
    VALID_STATIONS = {
        'flight': {'PVG', 'SHA'},
        'train': {'SHRW', 'SHS'},
    }
    valid_codes = VALID_STATIONS[transport_mode]

    # 验证服务类型
    service_type = data.get('service_type')
    if service_type not in ['pickup', 'dropoff', 'combo']:
        return error_response('无效的服务类型')

    # 验证航班/车次信息（必填）
    no_label = '车次号' if transport_mode == 'train' else '航班号'
    station_label = '车站' if transport_mode == 'train' else '机场'

    if service_type in ['pickup', 'combo']:
        if not data.get('flight_no'):
            return error_response(f'请填写接机/接站{no_label}')
        pickup_station = data.get('pickup_airport')
        if not pickup_station or pickup_station not in valid_codes:
            return error_response(f'请选择正确的{station_label}')
    if service_type in ['dropoff', 'combo']:
        dropoff_fn = data.get('dropoff_flight_no') if service_type == 'combo' else data.get('flight_no')
        if not dropoff_fn:
            return error_response(f'请填写送机/送站{no_label}')
        dropoff_ap = data.get('dropoff_airport') if service_type == 'combo' else data.get('dropoff_airport')
        if not dropoff_ap or dropoff_ap not in valid_codes:
            return error_response(f'请选择正确的{station_label}')

    # 验证车型
    vehicle = Vehicle.query.filter_by(id=data.get('vehicle_id'), status=1).first()
    if not vehicle:
        return error_response('车型不存在')

    # 验证民宿预订单号
    booking_no = data.get('booking_no')
    location_id = data.get('location_id')
    custom_address = data.get('custom_address')
    custom_district = data.get('custom_district')

    if not booking_no and not location_id and not custom_address:
        return error_response('请填写民宿预订单号')

    if location_id:
        location = Location.query.filter_by(id=location_id, status=1).first()
        if not location:
            return error_response('民宿点不存在')

    # 验证联系方式
    contact_phone = data.get('contact_phone')
    contact_email = data.get('contact_email')
    if not contact_phone and not contact_email:
        return error_response('请填写手机号或邮箱')

    # 计算价格：按车型独立报价
    pickup_price = float(vehicle.pickup_price) if vehicle.pickup_price else 0
    dropoff_price = float(vehicle.dropoff_price) if vehicle.dropoff_price else 0
    combo_price = float(vehicle.combo_price) if vehicle.combo_price else 0

    if service_type == 'pickup':
        base_price = pickup_price
    elif service_type == 'dropoff':
        base_price = dropoff_price
    else:  # combo
        base_price = combo_price

    if base_price <= 0:
        return error_response('当前车型暂未配置对应服务价格')

    vehicle_extra = 0
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

    # 解析日期时间字符串为 datetime 对象
    def parse_dt(val):
        if not val:
            return None
        if isinstance(val, datetime):
            return val
        try:
            return datetime.fromisoformat(val.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    # 处理航班信息
    if service_type == 'pickup':
        flight_no = data.get('flight_no')
        flight_time = parse_dt(data.get('flight_time'))
        pickup_airport = data.get('pickup_airport')
        dropoff_airport_val = None
        dropoff_flight_no = None
        dropoff_flight_time = None
    elif service_type == 'dropoff':
        flight_no = data.get('flight_no')
        flight_time = parse_dt(data.get('flight_time'))
        pickup_airport = None
        dropoff_airport_val = data.get('dropoff_airport')
        dropoff_flight_no = None
        dropoff_flight_time = None
    else:  # combo
        flight_no = data.get('flight_no')
        flight_time = parse_dt(data.get('flight_time'))
        pickup_airport = data.get('pickup_airport')
        dropoff_airport_val = data.get('dropoff_airport')
        dropoff_flight_no = data.get('dropoff_flight_no')
        dropoff_flight_time = parse_dt(data.get('dropoff_flight_time'))

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
            booking_no=booking_no,
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
            transport_mode=transport_mode,
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

        # 发送邮件通知
        from flask import current_app
        lang = request.args.get('lang', 'en')
        app_obj = current_app._get_current_object()
        # 通知管理员
        send_new_order_email(
            app_obj, 'transfer', order.order_no,
            float(order.total_price), data.get('contact_name'),
            contact_phone=contact_phone or '', contact_email=contact_email or '',
            booking_no=booking_no or '', remark=data.get('remark', ''),
            service_type=service_type, vehicle_name=vehicle.name_zh,
            flight_no=flight_no, flight_time=flight_time,
            pickup_airport=pickup_airport,
            dropoff_flight_no=dropoff_flight_no, dropoff_flight_time=dropoff_flight_time,
            dropoff_airport=dropoff_airport_val,
        )
        # 通知客户
        send_order_confirmation_to_customer(
            app_obj, contact_email, order.order_no,
            float(order.total_price), data.get('contact_name'),
            lang=lang, order_type='transfer',
            booking_no=booking_no or '',
            contact_phone=contact_phone or '', contact_email=contact_email or '',
            remark=data.get('remark', ''),
            service_type=service_type, vehicle_name=vehicle.name_zh,
            flight_no=flight_no, flight_time=flight_time,
            pickup_airport=pickup_airport,
            dropoff_flight_no=dropoff_flight_no, dropoff_flight_time=dropoff_flight_time,
            dropoff_airport=dropoff_airport_val,
        )

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
@limiter.limit("10 per minute")
def create_shop_order():
    """创建商城订单"""
    data = request.get_json()
    
    if not data:
        return error_response('请求数据为空')
    
    # 验证商品列表
    items_data = data.get('items', [])
    if not items_data:
        return error_response('购物车为空')
    
    # 验证预订单号
    booking_no = data.get('booking_no')
    if not booking_no:
        return error_response('请填写民宿预订单号')

    # 地址信息（可选，保留兼容）
    location_id = data.get('location_id')
    custom_address = data.get('custom_address')
    custom_district = data.get('custom_district')
    room_number = data.get('room_number')

    if location_id:
        location = Location.query.filter_by(id=location_id, status=1).first()
        if not location:
            location_id = None
    
    # 验证联系信息
    contact_name = data.get('contact_name')
    contact_phone = data.get('contact_phone')
    contact_email = data.get('contact_email')
    
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
    
    # 解析期望送达日期
    expected_delivery_date = None
    expected_delivery_time = None
    raw_date = data.get('expected_delivery_date')
    if raw_date:
        try:
            parsed = date.fromisoformat(raw_date)
            if parsed >= date.today():
                expected_delivery_date = parsed
        except (ValueError, TypeError):
            pass
    raw_time = data.get('expected_delivery_time')
    if raw_time in ('morning', 'afternoon', 'evening'):
        expected_delivery_time = raw_time

    # 创建订单
    order = ShopOrder(
        order_no=generate_order_no('SH'),
        booking_no=booking_no,
        location_id=location_id,
        custom_address=custom_address,
        custom_district=custom_district,
        room_number=room_number,
        expected_delivery_date=expected_delivery_date,
        expected_delivery_time=expected_delivery_time,
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

    # 发送邮件通知
    from flask import current_app
    lang = request.args.get('lang', 'en')
    items_str = ', '.join(f"{it['product_name']}x{it['quantity']}" for it in order_items)
    app_obj = current_app._get_current_object()
    # 通知管理员
    send_new_order_email(
        app_obj, 'shop', order.order_no, float(order.total_price),
        contact_name, items_summary=items_str,
        contact_phone=contact_phone or '', contact_email=contact_email or '',
        booking_no=booking_no or '', remark=data.get('remark', ''),
        expected_delivery_date=expected_delivery_date,
        expected_delivery_time=expected_delivery_time,
    )
    # 通知客户
    send_order_confirmation_to_customer(
        app_obj, contact_email, order.order_no,
        float(order.total_price), contact_name,
        items_summary=items_str, lang=lang, order_type='shop',
        booking_no=booking_no or '',
        contact_phone=contact_phone or '', contact_email=contact_email or '',
        remark=data.get('remark', ''),
        expected_delivery_date=expected_delivery_date,
        expected_delivery_time=expected_delivery_time,
    )

    return success_response({
        'order_no': order.order_no,
        'total_price': float(order.total_price)
    }, '订单创建成功')


# ==================== 订单查询 ====================

@api_bp.route('/orders/query', methods=['POST'])
@limiter.limit("30 per minute")  # 防止用手机号撞库批量拉取订单
def query_order():
    """查询订单（通过联系方式查询所有关联订单，或通过订单号+联系方式查询单个订单）"""
    data = request.get_json()

    if not data:
        return error_response('请求数据为空')

    order_no = data.get('order_no', '').strip()
    contact = data.get('contact', '').strip()

    if not contact:
        return error_response('请填写联系人姓名、手机号或邮箱')

    def _matches(order):
        return contact in {
            (order.contact_name or '').strip(),
            (order.contact_phone or '').strip(),
            (order.contact_email or '').strip()
        }

    # 如果提供了订单号，精确查询单个订单
    if order_no:
        shop_order = ShopOrder.query.filter_by(order_no=order_no).first()
        if shop_order:
            if _matches(shop_order):
                return success_response({
                    'orders': [{'type': 'shop', 'order': shop_order.to_dict()}]
                })
            return error_response('联系方式不匹配')

        transfer_order = TransferOrder.query.filter_by(order_no=order_no).first()
        if transfer_order:
            if _matches(transfer_order):
                return success_response({
                    'orders': [{'type': 'transfer', 'order': transfer_order.to_dict()}]
                })
            return error_response('联系方式不匹配')

        ticket_order = TicketOrder.query.filter_by(order_no=order_no).first()
        if ticket_order:
            if _matches(ticket_order):
                return success_response({
                    'orders': [{'type': 'ticket', 'order': ticket_order.to_dict(mask_pii=True)}]
                })
            return error_response('联系方式不匹配')

        return error_response('订单不存在', 404)

    # 没有订单号，通过联系方式查询所有关联订单
    results = []

    shop_orders = ShopOrder.query.filter(
        (ShopOrder.contact_name == contact) |
        (ShopOrder.contact_phone == contact) |
        (ShopOrder.contact_email == contact)
    ).order_by(ShopOrder.created_at.desc()).limit(50).all()
    for o in shop_orders:
        results.append({'type': 'shop', 'order': o.to_dict()})

    transfer_orders = TransferOrder.query.filter(
        (TransferOrder.contact_name == contact) |
        (TransferOrder.contact_phone == contact) |
        (TransferOrder.contact_email == contact)
    ).order_by(TransferOrder.created_at.desc()).limit(50).all()
    for o in transfer_orders:
        results.append({'type': 'transfer', 'order': o.to_dict()})

    ticket_orders = TicketOrder.query.filter(
        (TicketOrder.contact_name == contact) |
        (TicketOrder.contact_phone == contact) |
        (TicketOrder.contact_email == contact)
    ).order_by(TicketOrder.created_at.desc()).limit(50).all()
    for o in ticket_orders:
        results.append({'type': 'ticket', 'order': o.to_dict(mask_pii=True)})

    # 按创建时间排序
    results.sort(key=lambda x: x['order'].get('created_at', ''), reverse=True)

    if not results:
        return error_response('未找到相关订单', 404)

    return success_response({'orders': results})


# ==================== 退款申请 ====================

@api_bp.route('/orders/refund', methods=['POST'])
@limiter.limit("10 per minute")
def request_refund():
    """客户取消/退款订单
    - 未确认订单(status=0)：直接取消（未付款无需退款）
    - 已确认订单(status=1/2)：距离离店日期或期望送达日期 ≥ 48小时可免费取消退款
    """
    from app.models import china_now
    from datetime import datetime, timedelta

    data = request.get_json()
    if not data:
        return error_response('请求数据为空')

    order_no = data.get('order_no', '').strip()
    contact = data.get('contact', '').strip()

    if not order_no or not contact:
        return error_response('缺少订单号或联系方式')

    order = ShopOrder.query.filter_by(order_no=order_no).first()
    if not order:
        return error_response('订单不存在', 404)

    # 验证联系方式
    if order.contact_email != contact and order.contact_phone != contact:
        return error_response('联系方式不匹配')

    # 检查订单状态：已完成或已取消的不能操作
    if order.status in (3, 4):
        return error_response('该订单状态不支持取消')

    # 检查是否已退款
    if order.refund_status == 2:
        return error_response('该订单已退款')

    now = china_now()

    # 未确认订单（未付款）：直接取消
    if order.status == 0:
        order.status = 4  # 已取消
        order.cancelled_at = now
        order.refund_status = 0
        order.refund_amount = 0
        db.session.commit()

        # 发送取消通知给客户
        from flask import current_app
        lang = request.args.get('lang', 'en')
        items_str = ', '.join(f"{it.product_name}x{it.quantity}" for it in order.items)
        send_cancel_notify_to_customer(
            current_app._get_current_object(),
            order.contact_email, order.order_no, order.contact_name, lang=lang,
            items_summary=items_str, total_price=float(order.total_price),
        )

        return success_response({
            'order_no': order.order_no,
            'cancelled': True
        }, '订单已取消')

    # 已确认/配送中的订单：检查48小时规则
    # 取离店日期和期望送达日期中较早的一个
    target_date = None
    if order.expected_delivery_date and order.checkout_date:
        target_date = min(order.expected_delivery_date, order.checkout_date)
    elif order.expected_delivery_date:
        target_date = order.expected_delivery_date
    elif order.checkout_date:
        target_date = order.checkout_date

    if not target_date:
        return error_response('订单缺少送达日期或离店日期信息，请联系客服处理')

    # 将 date 转为 datetime（当天 00:00）用于计算时间差
    target_datetime = datetime.combine(target_date, datetime.min.time())
    hours_until_target = (target_datetime - now).total_seconds() / 3600

    if hours_until_target < 48:
        return error_response('距离送达/离店日期不足48小时，无法免费取消，请联系客服处理')

    # 自动审批通过：标记退款状态，订单状态改为已取消
    order.refund_status = 2
    order.refund_amount = order.total_price
    order.refund_time = now
    order.cancelled_at = now
    order.status = 4  # 已取消

    db.session.commit()

    # 发送退款通知
    from flask import current_app
    lang = request.args.get('lang', 'en')
    app_obj = current_app._get_current_object()
    items_str = ', '.join(f"{it.product_name}x{it.quantity}" for it in order.items)
    # 通知管理员
    send_refund_notify_email(app_obj, order.order_no, float(order.total_price), order.contact_name,
                             contact_phone=order.contact_phone or '',
                             contact_email=order.contact_email or '',
                             items_summary=items_str)
    # 通知客户
    send_refund_success_to_customer(app_obj, order.contact_email, order.order_no,
                                    float(order.total_price), order.contact_name, lang=lang,
                                    items_summary=items_str)

    return success_response({
        'order_no': order.order_no,
        'refund_amount': float(order.total_price),
        'refund_time': order.refund_time.isoformat()
    }, '退款申请成功')


# ==================== 接送机订单取消/退款 ====================

@api_bp.route('/orders/transfer/refund', methods=['POST'])
@limiter.limit("10 per minute")
def request_transfer_refund():
    """客户取消接送机订单
    - 未确认订单(status=0)：直接取消（未付款无需退款）
    - 已确认订单(status=1)：距离航班时间 ≥ 48小时可免费取消退款
    - 已完成/已取消(status=2,3)：不可操作
    """
    from app.models import china_now
    from datetime import datetime, timedelta

    data = request.get_json()
    if not data:
        return error_response('请求数据为空')

    order_no = data.get('order_no', '').strip()
    contact = data.get('contact', '').strip()

    if not order_no or not contact:
        return error_response('缺少订单号或联系方式')

    order = TransferOrder.query.filter_by(order_no=order_no).first()
    if not order:
        return error_response('订单不存在', 404)

    # 验证联系方式
    if contact not in {
        (order.contact_email or '').strip(),
        (order.contact_phone or '').strip(),
        (order.contact_name or '').strip(),
    }:
        return error_response('联系方式不匹配')

    # 已完成或已取消的不能操作
    if order.status in (2, 3):
        return error_response('该订单状态不支持取消')

    if order.refund_status == 2:
        return error_response('该订单已退款')

    now = china_now()

    # 未确认订单：直接取消
    if order.status == 0:
        order.status = 3  # 接送机: 3=已取消
        order.cancelled_at = now
        order.refund_status = 0
        order.refund_amount = 0
        db.session.commit()

        # 通知客户
        from flask import current_app
        lang = request.args.get('lang', 'en')
        send_cancel_notify_to_customer(
            current_app._get_current_object(),
            order.contact_email, order.order_no, order.contact_name, lang=lang,
            total_price=float(order.total_price),
        )

        return success_response({
            'order_no': order.order_no,
            'cancelled': True
        }, '订单已取消')

    # 已确认订单：检查48小时规则（以最近的航班时间为基准）
    target_datetime = None
    # 取所有航班时间中最早的一个
    candidates = []
    if order.flight_time:
        candidates.append(order.flight_time)
    if order.dropoff_flight_time:
        candidates.append(order.dropoff_flight_time)
    if candidates:
        target_datetime = min(candidates)

    if not target_datetime:
        return error_response('订单缺少航班时间信息，请联系客服处理')

    hours_until_target = (target_datetime - now).total_seconds() / 3600

    if hours_until_target < 48:
        return error_response('距离航班时间不足48小时，无法免费取消，请联系客服处理')

    # 自动审批：退款 + 取消
    order.refund_status = 2
    order.refund_amount = order.total_price
    order.refund_time = now
    order.cancelled_at = now
    order.status = 3  # 已取消

    db.session.commit()

    # 发送通知
    from flask import current_app
    lang = request.args.get('lang', 'en')
    app_obj = current_app._get_current_object()
    vehicle_name = order.vehicle.name_zh if order.vehicle else ''
    send_refund_notify_email(app_obj, order.order_no, float(order.total_price), order.contact_name,
                             contact_phone=order.contact_phone or '',
                             contact_email=order.contact_email or '',
                             items_summary=f'{order.service_type} - {vehicle_name}')
    send_refund_success_to_customer(app_obj, order.contact_email, order.order_no,
                                    float(order.total_price), order.contact_name, lang=lang,
                                    items_summary=f'{order.service_type} - {vehicle_name}')

    return success_response({
        'order_no': order.order_no,
        'refund_amount': float(order.total_price),
        'refund_time': order.refund_time.isoformat()
    }, '退款申请成功')


# ==================== 门票订单取消/退款 ====================

@api_bp.route('/orders/ticket/refund', methods=['POST'])
@limiter.limit("10 per minute")
def request_ticket_refund():
    """客户取消门票订单
    - 未确认订单(status=0)：直接取消（未付款无需退款）
    - 已确认订单(status=1)：距离游玩日期 ≥ 48小时可免费取消退款
    - 已完成/已取消(status=2,3)：不可操作
    """
    from app.models import china_now
    from datetime import datetime, timedelta

    data = request.get_json()
    if not data:
        return error_response('请求数据为空')

    order_no = data.get('order_no', '').strip()
    contact = data.get('contact', '').strip()

    if not order_no or not contact:
        return error_response('缺少订单号或联系方式')

    order = TicketOrder.query.filter_by(order_no=order_no).first()
    if not order:
        return error_response('订单不存在', 404)

    # 验证联系方式
    if contact not in {
        (order.contact_email or '').strip(),
        (order.contact_phone or '').strip(),
        (order.contact_name or '').strip(),
    }:
        return error_response('联系方式不匹配')

    # 已完成或已取消的不能操作
    if order.status in (2, 3):
        return error_response('该订单状态不支持取消')

    if order.refund_status == 2:
        return error_response('该订单已退款')

    now = china_now()

    # 未确认订单：直接取消
    if order.status == 0:
        order.status = 3  # 门票: 3=已取消
        order.cancelled_at = now
        order.refund_status = 0
        order.refund_amount = 0
        db.session.commit()

        # 恢复库存
        _restore_ticket_quota(order)

        # 通知客户
        from flask import current_app
        lang = request.args.get('lang', 'en')
        attraction_name = order.attraction.name_zh if order.attraction else ''
        send_cancel_notify_to_customer(
            current_app._get_current_object(),
            order.contact_email, order.order_no, order.contact_name, lang=lang,
            items_summary=attraction_name, total_price=float(order.total_price),
        )

        return success_response({
            'order_no': order.order_no,
            'cancelled': True
        }, '订单已取消')

    # 已确认订单：检查48小时规则（以游玩日期为基准）
    if not order.visit_date:
        return error_response('订单缺少游玩日期信息，请联系客服处理')

    target_datetime = datetime.combine(order.visit_date, datetime.min.time())
    hours_until_target = (target_datetime - now).total_seconds() / 3600

    if hours_until_target < 48:
        return error_response('距离游玩日期不足48小时，无法免费取消，请联系客服处理')

    # 自动审批：退款 + 取消
    order.refund_status = 2
    order.refund_amount = order.total_price
    order.refund_time = now
    order.cancelled_at = now
    order.status = 3  # 已取消

    db.session.commit()

    # 恢复库存
    _restore_ticket_quota(order)

    # 发送通知
    from flask import current_app
    lang = request.args.get('lang', 'en')
    app_obj = current_app._get_current_object()
    attraction_name = order.attraction.name_zh if order.attraction else ''
    send_refund_notify_email(app_obj, order.order_no, float(order.total_price), order.contact_name,
                             contact_phone=order.contact_phone or '',
                             contact_email=order.contact_email or '',
                             items_summary=attraction_name)
    send_refund_success_to_customer(app_obj, order.contact_email, order.order_no,
                                    float(order.total_price), order.contact_name, lang=lang,
                                    items_summary=attraction_name)

    return success_response({
        'order_no': order.order_no,
        'refund_amount': float(order.total_price),
        'refund_time': order.refund_time.isoformat()
    }, '退款申请成功')


def _restore_ticket_quota(order):
    """取消门票订单时恢复配额"""
    from app.models import TicketPackage
    if not order.package_snapshot:
        return
    snapshots = order.package_snapshot if isinstance(order.package_snapshot, list) else [order.package_snapshot]
    for item in snapshots:
        if not isinstance(item, dict):
            continue
        pkg_id = item.get('package_id')
        quantity = item.get('quantity', 0)
        if pkg_id and quantity:
            pkg = TicketPackage.query.get(pkg_id)
            if pkg and pkg.inventory_mode == 'manual_quota':
                pkg.quota_used = max((pkg.quota_used or 0) - quantity, 0)
    db.session.commit()


# ==================== 用户确认已支付 ====================

@api_bp.route('/orders/confirm-paid', methods=['POST'])
@limiter.limit("10 per minute")
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
        order = TicketOrder.query.filter_by(order_no=order_no).first()
        order_type = 'ticket'

    if not order:
        return error_response('订单不存在', 404)

    # 保存支付凭证（交易单号或付款截图，二选一）
    transaction_id = data.get('transaction_id', '').strip()
    payment_screenshot = data.get('payment_screenshot', '').strip()
    if transaction_id:
        order.transaction_id = transaction_id
    if payment_screenshot:
        order.payment_screenshot = payment_screenshot

    # 标记为"用户已点击支付"（payment_status=0仍为未确认）
    # 门票订单的状态 1 表示已确认，不能直接复用商城/接送机的待确认语义，
    # 因此仅为门票订单保存付款凭证，不自动推进订单状态。
    if order_type in ['shop', 'transfer'] and order.status == 0:
        order.status = 1  # 待确认（管理员需核实收款）
    db.session.commit()

    return success_response({
        'order_no': order.order_no,
        'type': order_type
    }, '已提交支付确认，请等待商家核实')
