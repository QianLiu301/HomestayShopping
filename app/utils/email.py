import threading
import os
import requests as http_requests


def _get_resend_config():
    """获取 Resend 配置"""
    api_key = os.getenv('RESEND_API_KEY')
    from_email = os.getenv('RESEND_FROM', 'orders@shanghai-tour-guide.com')
    notify_to = os.getenv('MAIL_NOTIFY_TO')  # 管理员通知邮箱
    return api_key, from_email, notify_to


def _send_async(app, api_key, payload):
    """在后台线程中通过 Resend REST API 发送邮件"""
    with app.app_context():
        try:
            resp = http_requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=15,
            )
            body = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else {}
            if resp.status_code == 200 and body.get('id'):
                app.logger.info(f'Email sent to {payload["to"]}, id={body["id"]}')
            else:
                app.logger.error(f'Resend API failed - status={resp.status_code}, body={resp.text[:500]}')
        except Exception as e:
            app.logger.error(f'Failed to send email: {e}')


def _send_email(app, to, subject, html):
    """发送邮件（异步，不阻塞请求）"""
    api_key, from_email, _ = _get_resend_config()
    if not api_key:
        return  # 未配置，静默跳过

    payload = {
        "from": from_email,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "html": html,
    }

    thread = threading.Thread(target=_send_async, args=(app, api_key, payload))
    thread.daemon = True
    thread.start()


def _row(label, value):
    """生成表格行 HTML"""
    if not value:
        return ''
    return f'<tr><td style="padding:8px 12px;color:#888;white-space:nowrap;">{label}</td><td style="padding:8px 12px;">{value}</td></tr>'


def _price_row(label, value):
    """生成价格行 HTML"""
    return f'<tr><td style="padding:8px 12px;color:#888;white-space:nowrap;">{label}</td><td style="padding:8px 12px;font-size:18px;color:#e74c3c;font-weight:700;">¥{value}</td></tr>'


def _table(rows_html, bg='#faf6f1'):
    """包裹表格"""
    return f'<table style="width:100%;border-collapse:collapse;margin:16px 0;background:{bg};border-radius:8px;">{rows_html}</table>'


def _delivery_time_label(time_slot, lang='en'):
    """将 morning/afternoon/evening 转为可读文字"""
    labels = {
        'en': {'morning': 'Morning', 'afternoon': 'Afternoon', 'evening': 'Evening'},
        'zh': {'morning': '上午', 'afternoon': '下午', 'evening': '晚上'},
        'ru': {'morning': 'Утро', 'afternoon': 'День', 'evening': 'Вечер'},
        'es': {'morning': 'Mañana', 'afternoon': 'Tarde', 'evening': 'Noche'},
    }
    return labels.get(lang, labels['en']).get(time_slot, time_slot or '')


def _service_type_label(service_type, lang='en'):
    """接送机服务类型可读文字"""
    labels = {
        'en': {'pickup': 'Airport Pickup', 'dropoff': 'Airport Drop-off', 'combo': 'Pickup + Drop-off'},
        'zh': {'pickup': '接机', 'dropoff': '送机', 'combo': '接机+送机'},
        'ru': {'pickup': 'Встреча в аэропорту', 'dropoff': 'Трансфер в аэропорт', 'combo': 'Встреча + Трансфер'},
        'es': {'pickup': 'Recogida en aeropuerto', 'dropoff': 'Traslado al aeropuerto', 'combo': 'Recogida + Traslado'},
    }
    return labels.get(lang, labels['en']).get(service_type, service_type or '')


def _airport_name(code):
    """机场/火车站代码转名称"""
    stations = {
        'PVG': 'Shanghai Pudong Airport (PVG)',
        'SHA': 'Shanghai Hongqiao Airport (SHA)',
        'SHRW': 'Shanghai Hongqiao Railway Station (SHRW)',
        'SHS': 'Shanghai Railway Station (SHS)',
    }
    return stations.get(code, code or '')


def _format_dt(dt_val):
    """格式化 datetime 为可读字符串"""
    if not dt_val:
        return ''
    if hasattr(dt_val, 'strftime'):
        return dt_val.strftime('%Y-%m-%d %H:%M')
    return str(dt_val)


# ==================== 管理员通知邮件（中文） ====================

def send_new_order_email(app, order_type, order_no, total_price, contact_name,
                         items_summary='', contact_phone='', contact_email='',
                         booking_no='', remark='',
                         # 商城订单额外字段
                         expected_delivery_date=None, expected_delivery_time=None,
                         # 接送机订单额外字段
                         service_type=None, vehicle_name=None,
                         flight_no=None, flight_time=None, pickup_airport=None,
                         dropoff_flight_no=None, dropoff_flight_time=None, dropoff_airport=None,
                         luggage_count=None, sign_name=None):
    """新订单通知邮件 → 发给管理员"""
    _, _, notify_to = _get_resend_config()
    if not notify_to:
        return

    type_label = '商城订单' if order_type == 'shop' else '接送机订单'
    subject = f'【新订单】{type_label} {order_no} - ¥{total_price}'

    # 构建表格行
    rows = _row('订单号', order_no)
    rows += _row('客户', contact_name)

    # 联系方式
    contact_parts = []
    if contact_phone:
        contact_parts.append(contact_phone)
    if contact_email:
        contact_parts.append(contact_email)
    if contact_parts:
        rows += _row('联系方式', ' / '.join(contact_parts))

    rows += _price_row('金额', total_price)

    if order_type == 'shop':
        if items_summary:
            rows += _row('商品', items_summary)
        if booking_no:
            rows += _row('预订单号', booking_no)
        if expected_delivery_date:
            delivery_str = str(expected_delivery_date)
            if expected_delivery_time:
                time_zh = {'morning': '上午', 'afternoon': '下午', 'evening': '晚上'}
                delivery_str += f' {time_zh.get(expected_delivery_time, expected_delivery_time)}'
            rows += _row('期望送达', delivery_str)
    else:
        if service_type:
            stype_zh = {'pickup': '接机', 'dropoff': '送机', 'combo': '接机+送机'}
            rows += _row('服务类型', stype_zh.get(service_type, service_type))
        if vehicle_name:
            rows += _row('车型', vehicle_name)
        if flight_no:
            flight_label = '接机航班' if service_type in ['pickup', 'combo'] else '送机航班'
            rows += _row(flight_label, f'{flight_no}  {_format_dt(flight_time)}')
        if pickup_airport:
            rows += _row('接机机场', _airport_name(pickup_airport))
        if dropoff_flight_no:
            rows += _row('送机航班', f'{dropoff_flight_no}  {_format_dt(dropoff_flight_time)}')
        elif service_type == 'dropoff' and flight_no:
            pass  # already shown above
        if dropoff_airport:
            rows += _row('送机机场', _airport_name(dropoff_airport))
        if luggage_count:
            rows += _row('行李件数', str(luggage_count))
        if sign_name:
            rows += _row('接机牌姓名', sign_name)
        if booking_no:
            rows += _row('预订单号', booking_no)

    if remark:
        rows += _row('备注', remark)

    html = f"""
<div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:20px;">
  <h2 style="color:#4a3728;border-bottom:2px solid #e8d5c4;padding-bottom:10px;">
    新{type_label}通知
  </h2>
  {_table(rows)}
  <p style="color:#888;font-size:13px;">请登录管理后台查看详情并处理订单。</p>
</div>
"""
    _send_email(app, notify_to, subject, html)


def send_refund_notify_email(app, order_no, total_price, contact_name,
                             contact_phone='', contact_email='', items_summary=''):
    """退款通知 → 发给管理员"""
    _, _, notify_to = _get_resend_config()
    if not notify_to:
        return

    subject = f'【退款通知】订单 {order_no} - ¥{total_price}'

    rows = _row('订单号', order_no)
    rows += _row('客户', contact_name)
    contact_parts = []
    if contact_phone:
        contact_parts.append(contact_phone)
    if contact_email:
        contact_parts.append(contact_email)
    if contact_parts:
        rows += _row('联系方式', ' / '.join(contact_parts))
    rows += _price_row('退款金额', total_price)
    if items_summary:
        rows += _row('商品', items_summary)

    html = f"""
<div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:20px;">
  <h2 style="color:#e74c3c;border-bottom:2px solid #ffccc7;padding-bottom:10px;">
    退款通知
  </h2>
  {_table(rows, '#fff5f5')}
  <p style="color:#888;font-size:13px;">客户已申请退款，请尽快联系客户处理退款事宜。</p>
</div>
"""
    _send_email(app, notify_to, subject, html)


# ==================== 客户通知邮件（多语言） ====================

def send_order_confirmation_to_customer(app, email, order_no, total_price, contact_name,
                                        items_summary='', lang='en',
                                        booking_no='', contact_phone='', contact_email='',
                                        remark='',
                                        # 商城订单
                                        expected_delivery_date=None, expected_delivery_time=None,
                                        # 接送机订单
                                        order_type='shop', service_type=None, vehicle_name=None,
                                        flight_no=None, flight_time=None, pickup_airport=None,
                                        dropoff_flight_no=None, dropoff_flight_time=None,
                                        dropoff_airport=None):
    """订单确认邮件 → 发给客户"""
    if not email:
        return

    texts = {
        'zh': {
            'subject': f'订单确认 - {order_no}',
            'title': '您的订单已收到',
            'greeting': f'您好，{contact_name}！',
            'body': '感谢您的下单，我们已收到您的订单，将尽快为您处理。',
            'order_no': '订单号',
            'amount': '订单金额',
            'items': '商品',
            'booking_no': '民宿预订号',
            'delivery': '期望送达',
            'contact': '联系方式',
            'remark': '备注',
            'service_type': '服务类型',
            'vehicle': '车型',
            'flight': '航班',
            'pickup_airport': '接机机场',
            'dropoff_flight': '送机航班',
            'dropoff_airport': '送机机场',
            'footer': '如有任何问题，请回复此邮件或联系我们的客服。',
            'team': 'Shanghai Tour Guide 团队',
        },
        'en': {
            'subject': f'Order Confirmation - {order_no}',
            'title': 'Your Order Has Been Received',
            'greeting': f'Hello, {contact_name}!',
            'body': 'Thank you for your order. We have received it and will process it as soon as possible.',
            'order_no': 'Order No.',
            'amount': 'Amount',
            'items': 'Items',
            'booking_no': 'Booking No.',
            'delivery': 'Expected Delivery',
            'contact': 'Contact',
            'remark': 'Note',
            'service_type': 'Service',
            'vehicle': 'Vehicle',
            'flight': 'Flight',
            'pickup_airport': 'Pickup Airport',
            'dropoff_flight': 'Drop-off Flight',
            'dropoff_airport': 'Drop-off Airport',
            'footer': 'If you have any questions, please reply to this email or contact our team.',
            'team': 'Shanghai Tour Guide Team',
        },
        'ru': {
            'subject': f'Подтверждение заказа - {order_no}',
            'title': 'Ваш заказ получен',
            'greeting': f'Здравствуйте, {contact_name}!',
            'body': 'Спасибо за ваш заказ. Мы его получили и обработаем в ближайшее время.',
            'order_no': 'Номер заказа',
            'amount': 'Сумма',
            'items': 'Товары',
            'booking_no': 'Номер бронирования',
            'delivery': 'Ожидаемая доставка',
            'contact': 'Контакт',
            'remark': 'Примечание',
            'service_type': 'Услуга',
            'vehicle': 'Автомобиль',
            'flight': 'Рейс',
            'pickup_airport': 'Аэропорт встречи',
            'dropoff_flight': 'Рейс отправления',
            'dropoff_airport': 'Аэропорт отправления',
            'footer': 'Если у вас есть вопросы, ответьте на это письмо или свяжитесь с нами.',
            'team': 'Команда Shanghai Tour Guide',
        },
        'es': {
            'subject': f'Confirmación de pedido - {order_no}',
            'title': 'Su pedido ha sido recibido',
            'greeting': f'¡Hola, {contact_name}!',
            'body': 'Gracias por su pedido. Lo hemos recibido y lo procesaremos lo antes posible.',
            'order_no': 'N° de pedido',
            'amount': 'Monto',
            'items': 'Artículos',
            'booking_no': 'N° de reserva',
            'delivery': 'Entrega esperada',
            'contact': 'Contacto',
            'remark': 'Nota',
            'service_type': 'Servicio',
            'vehicle': 'Vehículo',
            'flight': 'Vuelo',
            'pickup_airport': 'Aeropuerto de recogida',
            'dropoff_flight': 'Vuelo de salida',
            'dropoff_airport': 'Aeropuerto de salida',
            'footer': 'Si tiene alguna pregunta, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    # 构建详情行
    rows = _row(t['order_no'], order_no)
    rows += _price_row(t['amount'], total_price)

    if order_type == 'shop':
        if items_summary:
            rows += _row(t['items'], items_summary)
        if booking_no:
            rows += _row(t['booking_no'], booking_no)
        if expected_delivery_date:
            delivery_str = str(expected_delivery_date)
            if expected_delivery_time:
                delivery_str += f' ({_delivery_time_label(expected_delivery_time, lang)})'
            rows += _row(t['delivery'], delivery_str)
    else:
        if service_type:
            rows += _row(t['service_type'], _service_type_label(service_type, lang))
        if vehicle_name:
            rows += _row(t['vehicle'], vehicle_name)
        if flight_no:
            flight_str = flight_no
            if flight_time:
                flight_str += f'  {_format_dt(flight_time)}'
            rows += _row(t['flight'], flight_str)
        if pickup_airport:
            rows += _row(t['pickup_airport'], _airport_name(pickup_airport))
        if dropoff_flight_no:
            df_str = dropoff_flight_no
            if dropoff_flight_time:
                df_str += f'  {_format_dt(dropoff_flight_time)}'
            rows += _row(t['dropoff_flight'], df_str)
        if dropoff_airport:
            rows += _row(t['dropoff_airport'], _airport_name(dropoff_airport))
        if booking_no:
            rows += _row(t['booking_no'], booking_no)

    # 联系方式
    contact_parts = []
    if contact_phone:
        contact_parts.append(contact_phone)
    if contact_email:
        contact_parts.append(contact_email)
    if contact_parts:
        rows += _row(t['contact'], ' / '.join(contact_parts))

    if remark:
        rows += _row(t['remark'], remark)

    html = f"""
<div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:20px;">
  <h2 style="color:#4a3728;border-bottom:2px solid #e8d5c4;padding-bottom:10px;">{t['title']}</h2>
  <p style="color:#333;margin:16px 0;">{t['greeting']}</p>
  <p style="color:#555;">{t['body']}</p>
  {_table(rows)}
  <p style="color:#888;font-size:13px;margin-top:24px;">{t['footer']}</p>
  <p style="color:#aaa;font-size:12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, email, t['subject'], html)


def send_refund_success_to_customer(app, email, order_no, total_price, contact_name,
                                     lang='en', items_summary=''):
    """退款成功通知 → 发给客户"""
    if not email:
        return

    texts = {
        'zh': {
            'subject': f'退款通知 - {order_no}',
            'title': '退款申请已通过',
            'greeting': f'您好，{contact_name}！',
            'body': '您的退款申请已通过，客服将在 3 个工作日内与您联系并完成退款，请保持联系方式畅通。',
            'order_no': '订单号',
            'amount': '退款金额',
            'items': '商品',
            'footer': '如有任何问题，请回复此邮件或联系我们的客服。',
            'team': 'Shanghai Tour Guide 团队',
        },
        'en': {
            'subject': f'Refund Notification - {order_no}',
            'title': 'Refund Request Approved',
            'greeting': f'Hello, {contact_name}!',
            'body': 'Your refund request has been approved. Our team will contact you within 3 business days to process the refund. Please keep your contact information available.',
            'order_no': 'Order No.',
            'amount': 'Refund Amount',
            'items': 'Items',
            'footer': 'If you have any questions, please reply to this email or contact our team.',
            'team': 'Shanghai Tour Guide Team',
        },
        'ru': {
            'subject': f'Уведомление о возврате - {order_no}',
            'title': 'Запрос на возврат одобрен',
            'greeting': f'Здравствуйте, {contact_name}!',
            'body': 'Ваш запрос на возврат одобрен. Наша команда свяжется с вами в течение 3 рабочих дней. Пожалуйста, оставайтесь на связи.',
            'order_no': 'Номер заказа',
            'amount': 'Сумма возврата',
            'items': 'Товары',
            'footer': 'Если у вас есть вопросы, ответьте на это письмо или свяжитесь с нами.',
            'team': 'Команда Shanghai Tour Guide',
        },
        'es': {
            'subject': f'Notificación de reembolso - {order_no}',
            'title': 'Solicitud de reembolso aprobada',
            'greeting': f'¡Hola, {contact_name}!',
            'body': 'Su solicitud de reembolso ha sido aprobada. Nuestro equipo se pondrá en contacto con usted en 3 días hábiles. Por favor, mantenga disponible su información de contacto.',
            'order_no': 'N° de pedido',
            'amount': 'Monto del reembolso',
            'items': 'Artículos',
            'footer': 'Si tiene alguna pregunta, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    rows = _row(t['order_no'], order_no)
    rows += f'<tr><td style="padding:8px 12px;color:#888;white-space:nowrap;">{t["amount"]}</td><td style="padding:8px 12px;font-size:18px;color:#52c41a;font-weight:700;">¥{total_price}</td></tr>'
    if items_summary:
        rows += _row(t['items'], items_summary)

    html = f"""
<div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:20px;">
  <h2 style="color:#4a3728;border-bottom:2px solid #e8d5c4;padding-bottom:10px;">{t['title']}</h2>
  <p style="color:#333;margin:16px 0;">{t['greeting']}</p>
  <p style="color:#555;">{t['body']}</p>
  {_table(rows, '#f0f9eb')}
  <p style="color:#888;font-size:13px;margin-top:24px;">{t['footer']}</p>
  <p style="color:#aaa;font-size:12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, email, t['subject'], html)


def send_cancel_notify_to_customer(app, email, order_no, contact_name, lang='en',
                                    items_summary='', total_price=None):
    """订单取消通知 → 发给客户（未付款直接取消）"""
    if not email:
        return

    texts = {
        'zh': {
            'subject': f'订单已取消 - {order_no}',
            'title': '订单已取消',
            'greeting': f'您好，{contact_name}！',
            'body': '您的订单已成功取消。如需重新下单，欢迎随时访问我们的商城。',
            'order_no': '订单号',
            'amount': '订单金额',
            'items': '商品',
            'footer': '如有任何问题，请回复此邮件或联系我们的客服。',
            'team': 'Shanghai Tour Guide 团队',
        },
        'en': {
            'subject': f'Order Cancelled - {order_no}',
            'title': 'Order Cancelled',
            'greeting': f'Hello, {contact_name}!',
            'body': 'Your order has been successfully cancelled. Feel free to visit our shop again anytime.',
            'order_no': 'Order No.',
            'amount': 'Amount',
            'items': 'Items',
            'footer': 'If you have any questions, please reply to this email or contact our team.',
            'team': 'Shanghai Tour Guide Team',
        },
        'ru': {
            'subject': f'Заказ отменён - {order_no}',
            'title': 'Заказ отменён',
            'greeting': f'Здравствуйте, {contact_name}!',
            'body': 'Ваш заказ успешно отменён. Будем рады видеть вас снова в нашем магазине.',
            'order_no': 'Номер заказа',
            'amount': 'Сумма',
            'items': 'Товары',
            'footer': 'Если у вас есть вопросы, ответьте на это письмо или свяжитесь с нами.',
            'team': 'Команда Shanghai Tour Guide',
        },
        'es': {
            'subject': f'Pedido cancelado - {order_no}',
            'title': 'Pedido cancelado',
            'greeting': f'¡Hola, {contact_name}!',
            'body': 'Su pedido ha sido cancelado exitosamente. No dude en visitar nuestra tienda nuevamente.',
            'order_no': 'N° de pedido',
            'amount': 'Monto',
            'items': 'Artículos',
            'footer': 'Si tiene alguna pregunta, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    rows = _row(t['order_no'], order_no)
    if total_price is not None:
        rows += _row(t['amount'], f'¥{total_price}')
    if items_summary:
        rows += _row(t['items'], items_summary)

    html = f"""
<div style="font-family:sans-serif;max-width:500px;margin:0 auto;padding:20px;">
  <h2 style="color:#4a3728;border-bottom:2px solid #e8d5c4;padding-bottom:10px;">{t['title']}</h2>
  <p style="color:#333;margin:16px 0;">{t['greeting']}</p>
  <p style="color:#555;">{t['body']}</p>
  {_table(rows, '#f5f5f5')}
  <p style="color:#888;font-size:13px;margin-top:24px;">{t['footer']}</p>
  <p style="color:#aaa;font-size:12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, email, t['subject'], html)


# ==================== 许愿池邮件 ====================

def send_new_wish_to_admin(app, wish):
    """新许愿通知 → 发给管理员"""
    _, _, notify_to = _get_resend_config()
    if not notify_to:
        return

    budget_str = ''
    if wish.budget is not None:
        symbol = '$' if wish.budget_currency == 'USD' else '¥'
        budget_str = f'{symbol}{wish.budget}'

    contact_parts = []
    if wish.contact_phone:
        contact_parts.append(wish.contact_phone)
    if wish.contact_email:
        contact_parts.append(wish.contact_email)

    rows = _row('许愿编号', f'#{wish.id}')
    rows += _row('客户', wish.contact_name)
    rows += _row('联系方式', ' / '.join(contact_parts))
    rows += _row('期望服务时间', _format_dt(wish.expected_date))
    if budget_str:
        rows += _row('预算', budget_str)
    rows += _row('语言', wish.lang)
    # 内容单独成段，避免长文本撑表格
    content_html = (wish.content or '').replace('\n', '<br/>')

    subject = f'【新许愿】{wish.contact_name} - {budget_str or "未填预算"}'

    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:20px;">
  <h2 style="color:#4a3728;border-bottom:2px solid #e8d5c4;padding-bottom:10px;">
    许愿池新需求
  </h2>
  {_table(rows)}
  <div style="margin:16px 0;padding:14px;background:#fffaf2;border-left:3px solid #c69a62;border-radius:6px;">
    <div style="color:#888;font-size:13px;margin-bottom:8px;">需求描述</div>
    <div style="line-height:1.7;color:#3b2b1f;">{content_html}</div>
  </div>
  <p style="color:#888;font-size:13px;">请登录管理后台查看详情并尽快联系客户。</p>
</div>
"""
    _send_email(app, notify_to, subject, html)


def send_wish_received_to_customer(app, wish):
    """许愿已收到回执 → 发给客户（多语言）"""
    if not wish.contact_email:
        return

    lang = wish.lang if wish.lang in ('zh', 'en', 'ru', 'es') else 'en'
    texts = {
        'zh': {
            'subject': '我们已收到您的许愿',
            'title': '许愿已收到',
            'greeting': f'您好，{wish.contact_name}！',
            'body': '我们已收到您的需求，客服会在 24 小时内主动与您联系，为您安排专属方案。',
            'detail_label': '您的需求',
            'expected_label': '期望服务时间',
            'budget_label': '预算',
            'footer': '如有任何变更，请回复此邮件或联系客服。',
            'team': 'Shanghai Tour Guide 团队',
        },
        'en': {
            'subject': 'We received your request',
            'title': 'Your Request Has Been Received',
            'greeting': f'Hello, {wish.contact_name}!',
            'body': 'We have received your custom request. Our team will contact you within 24 hours to prepare a tailored plan.',
            'detail_label': 'Your Request',
            'expected_label': 'Expected Time',
            'budget_label': 'Budget',
            'footer': 'If anything changes, please reply to this email or contact our team.',
            'team': 'Shanghai Tour Guide Team',
        },
        'ru': {
            'subject': 'Мы получили ваш запрос',
            'title': 'Ваш запрос получен',
            'greeting': f'Здравствуйте, {wish.contact_name}!',
            'body': 'Мы получили ваш индивидуальный запрос. Наша команда свяжется с вами в течение 24 часов, чтобы подготовить персональный план.',
            'detail_label': 'Ваш запрос',
            'expected_label': 'Желаемое время',
            'budget_label': 'Бюджет',
            'footer': 'Если что-то изменится, ответьте на это письмо или свяжитесь с нами.',
            'team': 'Команда Shanghai Tour Guide',
        },
        'es': {
            'subject': 'Hemos recibido su solicitud',
            'title': 'Su solicitud ha sido recibida',
            'greeting': f'¡Hola, {wish.contact_name}!',
            'body': 'Hemos recibido su solicitud personalizada. Nuestro equipo se pondrá en contacto con usted dentro de 24 horas para preparar un plan a medida.',
            'detail_label': 'Su solicitud',
            'expected_label': 'Hora deseada',
            'budget_label': 'Presupuesto',
            'footer': 'Si algo cambia, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    budget_str = ''
    if wish.budget is not None:
        symbol = '$' if wish.budget_currency == 'USD' else '¥'
        budget_str = f'{symbol}{wish.budget}'

    rows = _row(t['expected_label'], _format_dt(wish.expected_date))
    if budget_str:
        rows += _row(t['budget_label'], budget_str)

    content_html = (wish.content or '').replace('\n', '<br/>')

    html = f"""
<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:20px;">
  <h2 style="color:#4a3728;border-bottom:2px solid #e8d5c4;padding-bottom:10px;">{t['title']}</h2>
  <p style="color:#333;margin:16px 0;">{t['greeting']}</p>
  <p style="color:#555;line-height:1.7;">{t['body']}</p>
  {_table(rows)}
  <div style="margin:16px 0;padding:14px;background:#fffaf2;border-left:3px solid #c69a62;border-radius:6px;">
    <div style="color:#888;font-size:13px;margin-bottom:8px;">{t['detail_label']}</div>
    <div style="line-height:1.7;color:#3b2b1f;">{content_html}</div>
  </div>
  <p style="color:#888;font-size:13px;margin-top:24px;">{t['footer']}</p>
  <p style="color:#aaa;font-size:12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, wish.contact_email, t['subject'], html)
