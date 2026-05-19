import uuid
from datetime import datetime, timedelta, timezone
from flask import request
from app.api import api_bp
from app.models import (
    TicketAttraction, TicketPackage, TicketOrder, TicketTraveler,
    TicketTransportPrice, Vehicle, Coupon
)
from app import db
from app.utils import success_response, error_response, paginate_query
from config import config

CHINA_TZ = timezone(timedelta(hours=8))


def china_now():
    return datetime.now(CHINA_TZ).replace(tzinfo=None)


def _generate_order_no():
    return f'TK{datetime.now(CHINA_TZ).strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6].upper()}'


def _localized(obj, field, lang):
    return (
        getattr(obj, f'{field}_{lang}', None)
        or getattr(obj, f'{field}_en', None)
        or getattr(obj, f'{field}_zh', None)
    )


# ==================== 公开接口 ====================

@api_bp.route('/tickets/attractions', methods=['GET'])
def get_attractions():
    """获取景点列表（H5公开）"""
    lang = request.args.get('lang', 'zh')
    status = request.args.get('status', 1, type=int)
    city = request.args.get('city')
    category = request.args.get('category')
    featured = request.args.get('featured')
    keyword = request.args.get('keyword')

    query = TicketAttraction.query.filter_by(status=status)

    if city:
        query = query.filter_by(city=city)
    if category:
        query = query.filter_by(category=category)
    if featured is not None:
        query = query.filter_by(featured=featured.lower() == 'true')
    if keyword:
        query = query.filter(
            (TicketAttraction.name_zh.ilike(f'%{keyword}%')) |
            (TicketAttraction.name_en.ilike(f'%{keyword}%'))
        )

    query = query.order_by(TicketAttraction.sort_order.desc(), TicketAttraction.id.desc())

    # 简化返回：带上最低价
    attractions = query.all()
    result = []
    for attr in attractions:
        attr_dict = attr.to_dict(lang)
        # 取该景点下所有启用票种的最低价
        min_price = db.session.query(db.func.min(TicketPackage.sale_price)).filter(
            TicketPackage.attraction_id == attr.id,
            TicketPackage.status == 1
        ).scalar()
        attr_dict['min_price'] = float(min_price) if min_price else None
        result.append(attr_dict)

    return success_response(result)


@api_bp.route('/tickets/attractions/<int:attraction_id>', methods=['GET'])
def get_attraction_detail(attraction_id):
    """获取景点详情（H5公开）"""
    lang = request.args.get('lang', 'zh')
    attraction = TicketAttraction.query.get(attraction_id)
    if not attraction or attraction.status != 1:
        return error_response('景点不存在或已下架', 404)

    result = attraction.to_dict(lang)

    # 带上票种列表
    packages = TicketPackage.query.filter_by(
        attraction_id=attraction_id, status=1
    ).order_by(TicketPackage.sort_order.desc(), TicketPackage.id.asc()).all()

    result['packages'] = [p.to_dict(lang) for p in packages]

    return success_response(result)


@api_bp.route('/tickets/packages', methods=['GET'])
def get_packages():
    """按景点获取票种列表（H5公开）"""
    lang = request.args.get('lang', 'zh')
    attraction_id = request.args.get('attraction_id', type=int)
    ticket_type = request.args.get('ticket_type')
    status = request.args.get('status', 1, type=int)

    if not attraction_id:
        return error_response('缺少 attraction_id 参数')

    query = TicketPackage.query.filter_by(attraction_id=attraction_id, status=status)

    if ticket_type:
        query = query.filter_by(ticket_type=ticket_type)

    packages = query.order_by(TicketPackage.sort_order.desc(), TicketPackage.id.asc()).all()
    return success_response([p.to_dict(lang) for p in packages])


@api_bp.route('/tickets/transport-options', methods=['GET'])
def get_transport_options():
    """获取景点加购用车选项（H5公开）"""
    lang = request.args.get('lang', 'zh')
    attraction_id = request.args.get('attraction_id', type=int)

    if not attraction_id:
        return error_response('缺少 attraction_id 参数')

    options = TicketTransportPrice.query.filter_by(
        attraction_id=attraction_id, status=1
    ).order_by(TicketTransportPrice.sort_order.desc()).all()

    return success_response([o.to_dict(lang) for o in options])


@api_bp.route('/tickets/orders', methods=['POST'])
def create_ticket_order():
    """创建门票订单"""
    data = request.get_json()
    lang = data.get('lang', 'zh')

    # 参数校验
    attraction_id = data.get('attraction_id')
    if not attraction_id:
        return error_response('缺少景点 ID')

    attraction = TicketAttraction.query.get(attraction_id)
    if not attraction or attraction.status != 1:
        return error_response('景点不存在或已下架')

    visit_date_str = data.get('visit_date')
    if not visit_date_str:
        return error_response('缺少游玩日期')

    try:
        visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
    except ValueError:
        return error_response('游玩日期格式错误，请使用 YYYY-MM-DD')

    if visit_date < datetime.now().date():
        return error_response('游玩日期不能早于今天')

    # 票种明细
    selected_packages = data.get('packages', [])
    if not selected_packages:
        return error_response('请至少选择一个票种')

    # 计算价格
    total_ticket_price = 0.0
    package_snapshot = []

    for pkg_item in selected_packages:
        pkg_id = pkg_item.get('package_id')
        quantity = pkg_item.get('quantity', 1)
        if not pkg_id or quantity < 1:
            return error_response('票种数据格式错误')

        pkg = TicketPackage.query.get(pkg_id)
        if not pkg or pkg.attraction_id != attraction_id:
            return error_response(f'票种 {pkg_id} 不存在')
        if pkg.status != 1:
            return error_response(f'票种 {pkg.package_name_zh or pkg.package_name_en} 已下架')

        # 日期规则检查
        if pkg.date_rules:
            matched_rule = next((rule for rule in pkg.date_rules if rule.get('date') == visit_date_str), None)
            if matched_rule and not matched_rule.get('enabled', True):
                return error_response(f'票种 {pkg.package_name_zh or pkg.package_name_en} 在该日期不可预订')
            rule_price = matched_rule.get('price') if matched_rule else None
        elif pkg.available_days:
            if visit_date_str not in pkg.available_days:
                return error_response(f'票种 {pkg.package_name_zh or pkg.package_name_en} 在该日期不可预订')
            rule_price = None
        else:
            rule_price = None

        # 配额检查
        if pkg.inventory_mode == 'manual_quota' and pkg.quota_total is not None:
            if (pkg.quota_used or 0) + quantity > pkg.quota_total:
                return error_response(f'票种 {pkg.package_name_zh or pkg.package_name_en} 库存不足')

        sale_price = float(rule_price) if rule_price is not None else (float(pkg.sale_price) if pkg.sale_price else 0)
        total_ticket_price += sale_price * quantity

        package_snapshot.append({
            'package_id': pkg.id,
            'package_name': _localized(pkg, 'package_name', lang) or pkg.package_name_zh,
            'ticket_type': pkg.ticket_type,
            'sale_price': sale_price,
            'base_sale_price': float(pkg.sale_price) if pkg.sale_price else 0,
            'quantity': quantity,
            'visit_date': visit_date_str,
            'subtotal': round(sale_price * quantity, 2)
        })

    # 出行人校验
    travelers_data = data.get('travelers', [])
    total_tickets = sum(item.get('quantity', 1) for item in selected_packages)

    if attraction.real_name_required:
        if len(travelers_data) < total_tickets:
            return error_response(f'该景点需要提供 {total_tickets} 位出行人信息')

        for t in travelers_data:
            if not t.get('full_name'):
                return error_response('出行人姓名不能为空')
            if attraction.passport_required and not t.get('document_no'):
                return error_response('该景点需要提供证件信息')

    # 联系方式
    contact_name = data.get('contact_name')
    if not contact_name:
        return error_response('联系人姓名不能为空')

    booking_no = data.get('booking_no')
    if not booking_no:
        return error_response('请填写民宿预订单号')

    # 用车加购
    need_transfer = data.get('need_transfer', False)
    transfer_price = 0.0
    transfer_vehicle_id = None
    transfer_service_type = None
    transfer_vehicle_snapshot = None

    if need_transfer:
        tp_id = data.get('transport_price_id')
        if tp_id:
            tp = TicketTransportPrice.query.get(tp_id)
            if tp and tp.attraction_id == attraction_id and tp.status == 1:
                transfer_price = float(tp.price) if tp.price else 0
                transfer_vehicle_id = tp.vehicle_id
                transfer_service_type = tp.service_type
                transfer_vehicle_snapshot = tp.vehicle.to_dict(lang) if tp.vehicle else None
            else:
                return error_response('选定的接送服务不存在或已下架')

    total_price = round(total_ticket_price + transfer_price, 2)

    # 优惠码
    discount_amount = 0.0
    coupon_id = None
    coupon_snapshot = None
    coupon_code = data.get('coupon_code')
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, status=1).first()
        if not coupon:
            return error_response('优惠码无效')
        valid, msg = coupon.is_valid()
        if not valid:
            return error_response(msg)
        if float(coupon.min_amount) > total_ticket_price:
            return error_response(f'订单金额未达优惠券使用门槛（需满 {coupon.min_amount} 元）')
        discount_amount = round(coupon.calculate_discount(total_ticket_price), 2)
        coupon_id = coupon.id
        coupon_snapshot = coupon.to_dict(lang)

    final_price = round(total_price - discount_amount, 2)

    # 创建订单
    order = TicketOrder(
        order_no=_generate_order_no(),
        attraction_id=attraction_id,
        visit_date=visit_date,
        contact_name=contact_name,
        contact_phone=data.get('contact_phone'),
        contact_email=data.get('contact_email'),
        booking_no=booking_no,
        lang=lang,
        total_price=final_price,
        discount_amount=discount_amount if discount_amount else 0,
        coupon_id=coupon_id,
        status=0,
        payment_method=data.get('payment_method'),
        payment_status=0,
        remark=data.get('remark'),
        need_transfer=need_transfer,
        transfer_vehicle_id=transfer_vehicle_id,
        transfer_service_type=transfer_service_type,
        transfer_price_snapshot=transfer_price if transfer_price else None,
        package_snapshot=package_snapshot,
        voucher_delivery_status=0
    )
    db.session.add(order)
    db.session.flush()  # 获取 order.id

    # 更新票种配额
    for pkg_item in selected_packages:
        pkg_id = pkg_item.get('package_id')
        quantity = pkg_item.get('quantity', 1)
        pkg = TicketPackage.query.get(pkg_id)
        if pkg and pkg.inventory_mode == 'manual_quota':
            pkg.quota_used = (pkg.quota_used or 0) + quantity

    # 保存出行人
    for t_data in travelers_data[:total_tickets]:
        dob_value = None
        dob_raw = t_data.get('date_of_birth')
        if dob_raw:
            try:
                dob_value = datetime.strptime(dob_raw, '%d/%m/%Y').date()
            except ValueError:
                return error_response('出生日期格式错误，请使用 DD/MM/YYYY')

        traveler = TicketTraveler(
            order_id=order.id,
            traveler_type=t_data.get('traveler_type', 'adult'),
            full_name=t_data.get('full_name'),
            nationality=t_data.get('nationality'),
            document_type=t_data.get('document_type'),
            document_no=t_data.get('document_no'),
            date_of_birth=dob_value,
            gender=t_data.get('gender')
        )
        db.session.add(traveler)

    # 更新优惠券使用量
    if coupon_id:
        coupon.used_count = (coupon.used_count or 0) + 1

    db.session.commit()

    return success_response(order.to_dict(), '订单创建成功')


@api_bp.route('/tickets/orders/query', methods=['POST'])
def query_ticket_order():
    """查询门票订单（通过 order_no 或 contact_email + contact_name）"""
    data = request.get_json()
    order_no = data.get('order_no')
    contact_email = data.get('contact_email')
    contact_name = data.get('contact_name')

    if order_no:
        order = TicketOrder.query.filter_by(order_no=order_no).first()
    elif contact_email and contact_name:
        order = TicketOrder.query.filter_by(
            contact_email=contact_email, contact_name=contact_name
        ).order_by(TicketOrder.id.desc()).first()
    else:
        return error_response('请提供订单号或联系方式')

    if not order:
        return error_response('未找到订单', 404)

    return success_response(order.to_dict())


@api_bp.route('/tickets/orders/<order_no>', methods=['GET'])
def get_ticket_order(order_no):
    """获取门票订单详情"""
    order = TicketOrder.query.filter_by(order_no=order_no).first()
    if not order:
        return error_response('订单不存在', 404)

    return success_response(order.to_dict())


@api_bp.route('/tickets/cities', methods=['GET'])
def get_ticket_cities():
    """获取所有景点所在城市列表"""
    cities = db.session.query(TicketAttraction.city).filter(
        TicketAttraction.status == 1,
        TicketAttraction.city.isnot(None)
    ).distinct().all()
    return success_response([c[0] for c in cities if c[0]])
