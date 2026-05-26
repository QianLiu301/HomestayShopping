"""许愿池 API：用户提交定制需求 + 管理端管理"""
from datetime import datetime, timedelta
from flask import request, current_app
from app.api import api_bp
from app.models import Wish
from app import db
from app.utils import success_response, error_response, admin_required, paginate_query, get_lang
from app.utils.email import send_new_wish_to_admin, send_wish_received_to_customer


# ==================== 公开接口（用户提交） ====================

@api_bp.route('/wishes', methods=['POST'])
def create_wish():
    """用户提交许愿"""
    data = request.get_json() or {}

    contact_name = (data.get('contact_name') or '').strip()
    contact_phone = (data.get('contact_phone') or '').strip()
    contact_email = (data.get('contact_email') or '').strip()
    content = (data.get('content') or '').strip()
    expected_date_str = (data.get('expected_date') or '').strip()
    budget = data.get('budget')
    budget_currency = (data.get('budget_currency') or 'CNY').strip().upper()
    lang = (data.get('lang') or get_lang() or 'zh').strip()

    # 基础校验
    if not contact_name:
        return error_response('请填写联系人姓名')
    if not contact_phone and not contact_email:
        return error_response('请填写手机号或邮箱（至少填一个）')
    if not content or len(content) < 10:
        return error_response('请描述您的需求（至少 10 个字符）')
    if not expected_date_str:
        return error_response('请选择期望服务时间')

    # 期望日期必须 ≥ 当前时间 + 24 小时
    try:
        # 支持 ISO 格式和 'YYYY-MM-DD HH:MM' 格式
        if 'T' in expected_date_str:
            expected_date = datetime.fromisoformat(expected_date_str.replace('Z', '+00:00'))
            if expected_date.tzinfo is not None:
                expected_date = expected_date.replace(tzinfo=None)
        else:
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        try:
            expected_date = datetime.strptime(expected_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return error_response('期望日期格式错误')

    if expected_date < datetime.now() + timedelta(hours=24):
        return error_response('期望服务时间必须至少在 24 小时之后，以便客服及时安排')

    # 预算（选填，但建议填）
    if budget is not None and budget != '':
        try:
            budget = float(budget)
            if budget < 0:
                return error_response('预算不能为负数')
        except (ValueError, TypeError):
            return error_response('预算格式错误')
    else:
        budget = None

    if budget_currency not in ('CNY', 'USD'):
        budget_currency = 'CNY'

    if lang not in ('zh', 'en', 'ru', 'es'):
        lang = 'zh'

    wish = Wish(
        contact_name=contact_name[:50],
        contact_phone=contact_phone[:30] or None,
        contact_email=contact_email[:100] or None,
        content=content,
        expected_date=expected_date,
        budget=budget,
        budget_currency=budget_currency,
        lang=lang,
        status=0,
    )
    db.session.add(wish)
    db.session.commit()

    # 异步发送邮件（不阻塞响应）
    app = current_app._get_current_object()
    try:
        send_new_wish_to_admin(app, wish)
    except Exception as e:
        app.logger.error(f'send_new_wish_to_admin failed: {e}')
    if wish.contact_email:
        try:
            send_wish_received_to_customer(app, wish)
        except Exception as e:
            app.logger.error(f'send_wish_received_to_customer failed: {e}')

    return success_response(wish.to_dict(), '提交成功')


# ==================== 管理端接口 ====================

@api_bp.route('/admin/wishes', methods=['GET'])
@admin_required
def admin_list_wishes():
    """管理端列出许愿（支持分页 + 状态过滤 + 关键词搜索）"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status = request.args.get('status', '')
    keyword = (request.args.get('keyword') or '').strip()

    query = Wish.query
    if status != '':
        try:
            query = query.filter(Wish.status == int(status))
        except (ValueError, TypeError):
            pass
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            db.or_(
                Wish.contact_name.ilike(like),
                Wish.contact_phone.ilike(like),
                Wish.contact_email.ilike(like),
                Wish.content.ilike(like),
            )
        )
    query = query.order_by(Wish.created_at.desc())

    result = paginate_query(query, page=page, per_page=per_page)
    return success_response({
        'list': [w.to_dict() for w in result['items']],
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'pages': result['pages'],
    })


@api_bp.route('/admin/wishes/<int:wish_id>', methods=['PUT'])
@admin_required
def admin_update_wish(wish_id):
    """管理端更新许愿状态/备注"""
    wish = Wish.query.get(wish_id)
    if not wish:
        return error_response('许愿不存在', 404)

    data = request.get_json() or {}
    if 'status' in data:
        try:
            new_status = int(data['status'])
            if new_status not in (0, 1, 2, 3):
                return error_response('状态值非法')
            wish.status = new_status
        except (ValueError, TypeError):
            return error_response('状态值非法')

    if 'admin_note' in data:
        wish.admin_note = (data.get('admin_note') or '').strip() or None

    db.session.commit()
    return success_response(wish.to_dict(), '更新成功')


@api_bp.route('/admin/wishes/<int:wish_id>', methods=['DELETE'])
@admin_required
def admin_delete_wish(wish_id):
    """管理端删除许愿"""
    wish = Wish.query.get(wish_id)
    if not wish:
        return error_response('许愿不存在', 404)

    db.session.delete(wish)
    db.session.commit()
    return success_response(None, '删除成功')
