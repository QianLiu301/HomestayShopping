from flask import request
from app.api import api_bp
from app.models import Coupon
from app.utils import success_response, error_response, get_lang


@api_bp.route('/coupons/verify', methods=['POST'])
def verify_coupon():
    """验证优惠券"""
    data = request.get_json()
    
    if not data:
        return error_response('请求数据为空')
    
    code = data.get('code')
    amount = data.get('amount', 0)  # 订单金额
    apply_to = data.get('apply_to', 'all')  # shop 或 transfer
    
    if not code:
        return error_response('请输入优惠券码')
    
    lang = get_lang()
    
    coupon = Coupon.query.filter_by(code=code.upper()).first()
    
    if not coupon:
        return error_response('优惠券不存在')
    
    # 验证有效性
    is_valid, msg = coupon.is_valid()
    if not is_valid:
        return error_response(msg)
    
    # 验证适用范围
    if coupon.apply_to != 'all' and coupon.apply_to != apply_to:
        scope = '商城' if coupon.apply_to == 'shop' else '接送机'
        return error_response(f'该优惠券仅限{scope}使用')
    
    # 验证最低消费
    if amount < float(coupon.min_amount):
        return error_response(f'订单金额需满{coupon.min_amount}元')
    
    # 计算优惠金额
    discount = coupon.calculate_discount(amount)
    
    return success_response({
        'coupon': coupon.to_dict(lang),
        'discount_amount': discount,
        'final_amount': round(amount - discount, 2)
    })
