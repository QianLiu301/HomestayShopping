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


# ==================== 管理员通知邮件 ====================

def send_new_order_email(app, order_type, order_no, total_price, contact_name, items_summary=''):
    """新订单通知邮件 → 发给管理员"""
    _, _, notify_to = _get_resend_config()
    if not notify_to:
        return

    type_label = '商城订单' if order_type == 'shop' else '接送机订单'
    subject = f'【新订单】{type_label} {order_no} - ¥{total_price}'

    html = f"""
<div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
  <h2 style="color: #4a3728; border-bottom: 2px solid #e8d5c4; padding-bottom: 10px;">
    新{type_label}通知
  </h2>
  <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
    <tr><td style="padding: 8px 0; color: #888;">订单号</td><td style="padding: 8px 0; font-weight: 600;">{order_no}</td></tr>
    <tr><td style="padding: 8px 0; color: #888;">客户</td><td style="padding: 8px 0;">{contact_name}</td></tr>
    <tr><td style="padding: 8px 0; color: #888;">金额</td><td style="padding: 8px 0; font-size: 18px; color: #e74c3c; font-weight: 700;">¥{total_price}</td></tr>
    {f'<tr><td style="padding: 8px 0; color: #888;">商品</td><td style="padding: 8px 0;">{items_summary}</td></tr>' if items_summary else ''}
  </table>
  <p style="color: #888; font-size: 13px;">请登录管理后台查看详情并处理订单。</p>
</div>
"""
    _send_email(app, notify_to, subject, html)


def send_refund_notify_email(app, order_no, total_price, contact_name):
    """退款通知 → 发给管理员"""
    _, _, notify_to = _get_resend_config()
    if not notify_to:
        return

    subject = f'【退款通知】订单 {order_no} - ¥{total_price}'
    html = f"""
<div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
  <h2 style="color: #e74c3c; border-bottom: 2px solid #ffccc7; padding-bottom: 10px;">
    退款通知
  </h2>
  <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
    <tr><td style="padding: 8px 0; color: #888;">订单号</td><td style="padding: 8px 0; font-weight: 600;">{order_no}</td></tr>
    <tr><td style="padding: 8px 0; color: #888;">客户</td><td style="padding: 8px 0;">{contact_name}</td></tr>
    <tr><td style="padding: 8px 0; color: #888;">退款金额</td><td style="padding: 8px 0; font-size: 18px; color: #e74c3c; font-weight: 700;">¥{total_price}</td></tr>
  </table>
  <p style="color: #888; font-size: 13px;">客户已申请退款，请尽快联系客户处理退款事宜。</p>
</div>
"""
    _send_email(app, notify_to, subject, html)


# ==================== 客户通知邮件 ====================

def send_order_confirmation_to_customer(app, email, order_no, total_price, contact_name, items_summary='', lang='zh'):
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
            'footer': 'Si tiene alguna pregunta, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    items_row = f'<tr><td style="padding: 8px 0; color: #888;">{t["items"]}</td><td style="padding: 8px 0;">{items_summary}</td></tr>' if items_summary else ''

    html = f"""
<div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
  <h2 style="color: #4a3728; border-bottom: 2px solid #e8d5c4; padding-bottom: 10px;">{t['title']}</h2>
  <p style="color: #333; margin: 16px 0;">{t['greeting']}</p>
  <p style="color: #555;">{t['body']}</p>
  <table style="width: 100%; border-collapse: collapse; margin: 16px 0; background: #faf6f1; border-radius: 8px; padding: 12px;">
    <tr><td style="padding: 8px 12px; color: #888;">{t['order_no']}</td><td style="padding: 8px 12px; font-weight: 600;">{order_no}</td></tr>
    <tr><td style="padding: 8px 12px; color: #888;">{t['amount']}</td><td style="padding: 8px 12px; font-size: 18px; color: #e74c3c; font-weight: 700;">¥{total_price}</td></tr>
    {items_row}
  </table>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">{t['footer']}</p>
  <p style="color: #aaa; font-size: 12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, email, t['subject'], html)


def send_refund_success_to_customer(app, email, order_no, total_price, contact_name, lang='zh'):
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
            'footer': 'Si tiene alguna pregunta, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    html = f"""
<div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
  <h2 style="color: #4a3728; border-bottom: 2px solid #e8d5c4; padding-bottom: 10px;">{t['title']}</h2>
  <p style="color: #333; margin: 16px 0;">{t['greeting']}</p>
  <p style="color: #555;">{t['body']}</p>
  <table style="width: 100%; border-collapse: collapse; margin: 16px 0; background: #f0f9eb; border-radius: 8px; padding: 12px;">
    <tr><td style="padding: 8px 12px; color: #888;">{t['order_no']}</td><td style="padding: 8px 12px; font-weight: 600;">{order_no}</td></tr>
    <tr><td style="padding: 8px 12px; color: #888;">{t['amount']}</td><td style="padding: 8px 12px; font-size: 18px; color: #52c41a; font-weight: 700;">¥{total_price}</td></tr>
  </table>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">{t['footer']}</p>
  <p style="color: #aaa; font-size: 12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, email, t['subject'], html)


def send_cancel_notify_to_customer(app, email, order_no, contact_name, lang='zh'):
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
            'footer': '如有任何问题，请回复此邮件或联系我们的客服。',
            'team': 'Shanghai Tour Guide 团队',
        },
        'en': {
            'subject': f'Order Cancelled - {order_no}',
            'title': 'Order Cancelled',
            'greeting': f'Hello, {contact_name}!',
            'body': 'Your order has been successfully cancelled. Feel free to visit our shop again anytime.',
            'order_no': 'Order No.',
            'footer': 'If you have any questions, please reply to this email or contact our team.',
            'team': 'Shanghai Tour Guide Team',
        },
        'ru': {
            'subject': f'Заказ отменён - {order_no}',
            'title': 'Заказ отменён',
            'greeting': f'Здравствуйте, {contact_name}!',
            'body': 'Ваш заказ успешно отменён. Будем рады видеть вас снова в нашем магазине.',
            'order_no': 'Номер заказа',
            'footer': 'Если у вас есть вопросы, ответьте на это письмо или свяжитесь с нами.',
            'team': 'Команда Shanghai Tour Guide',
        },
        'es': {
            'subject': f'Pedido cancelado - {order_no}',
            'title': 'Pedido cancelado',
            'greeting': f'¡Hola, {contact_name}!',
            'body': 'Su pedido ha sido cancelado exitosamente. No dude en visitar nuestra tienda nuevamente.',
            'order_no': 'N° de pedido',
            'footer': 'Si tiene alguna pregunta, responda a este correo o contacte a nuestro equipo.',
            'team': 'Equipo Shanghai Tour Guide',
        },
    }
    t = texts.get(lang, texts['en'])

    html = f"""
<div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
  <h2 style="color: #4a3728; border-bottom: 2px solid #e8d5c4; padding-bottom: 10px;">{t['title']}</h2>
  <p style="color: #333; margin: 16px 0;">{t['greeting']}</p>
  <p style="color: #555;">{t['body']}</p>
  <table style="width: 100%; border-collapse: collapse; margin: 16px 0; background: #f5f5f5; border-radius: 8px; padding: 12px;">
    <tr><td style="padding: 8px 12px; color: #888;">{t['order_no']}</td><td style="padding: 8px 12px; font-weight: 600;">{order_no}</td></tr>
  </table>
  <p style="color: #888; font-size: 13px; margin-top: 24px;">{t['footer']}</p>
  <p style="color: #aaa; font-size: 12px;">— {t['team']}</p>
</div>
"""
    _send_email(app, email, t['subject'], html)
