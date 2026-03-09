from flask import request
from app.api import api_bp
from app.models import Setting
from app import db
from app.utils import success_response, error_response, admin_required


@api_bp.route('/payment/qrcodes', methods=['GET'])
def get_payment_qrcodes():
    """获取支付收款二维码（公开接口）"""
    wechat_qr = Setting.get_value('wechat_qr_url', '')
    alipay_qr = Setting.get_value('alipay_qr_url', '')
    return success_response({
        'wechat_qr_url': wechat_qr,
        'alipay_qr_url': alipay_qr
    })


@api_bp.route('/admin/settings', methods=['GET'])
@admin_required
def admin_get_settings():
    """获取所有系统配置"""
    settings = Setting.query.all()
    return success_response({s.key: s.value for s in settings})


@api_bp.route('/admin/settings', methods=['PUT'])
@admin_required
def admin_update_settings():
    """批量更新系统配置"""
    data = request.get_json()
    
    if not data:
        return error_response('请求数据为空')
    
    for key, value in data.items():
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = Setting(key=key, value=str(value))
            db.session.add(setting)
    
    db.session.commit()
    
    return success_response(None, '更新成功')


@api_bp.route('/admin/settings/<key>', methods=['PUT'])
@admin_required
def admin_update_setting(key):
    """更新单个配置"""
    data = request.get_json()
    value = data.get('value')
    
    if value is None:
        return error_response('value不能为空')
    
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        setting.value = str(value)
    else:
        setting = Setting(key=key, value=str(value))
        db.session.add(setting)
    
    db.session.commit()
    
    return success_response({'key': key, 'value': value}, '更新成功')
