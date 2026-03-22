import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def _send_email_async(app, msg, mail_server, mail_port, mail_username, mail_password):
    """在后台线程中发送邮件"""
    with app.app_context():
        try:
            with smtplib.SMTP_SSL(mail_server, mail_port, timeout=10) as server:
                server.login(mail_username, mail_password)
                server.send_message(msg)
            app.logger.info(f'Email sent to {msg["To"]}')
        except Exception as e:
            app.logger.error(f'Failed to send email: {e}')


def send_new_order_email(app, order_type, order_no, total_price, contact_name, items_summary=''):
    """新订单通知邮件（异步发送，不阻塞请求）"""
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = int(os.getenv('MAIL_PORT', 465))
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_to = os.getenv('MAIL_NOTIFY_TO')

    if not all([mail_server, mail_username, mail_password, mail_to]):
        return  # 邮件未配置，静默跳过

    type_label = '商城订单' if order_type == 'shop' else '接送机订单'
    subject = f'【新订单】{type_label} {order_no} - ¥{total_price}'

    body = f"""
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

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mail_username
    msg['To'] = mail_to
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    thread = threading.Thread(
        target=_send_email_async,
        args=(app, msg, mail_server, mail_port, mail_username, mail_password)
    )
    thread.daemon = True
    thread.start()
