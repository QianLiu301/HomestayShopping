from datetime import datetime
from flask import request
from app.api import api_bp
from app.models import Review, ShopOrder, OrderItem, Product, ServiceReview, TransferOrder, TicketOrder
from app import db, limiter
from app.utils import success_response, error_response, paginate_query, admin_required, escape_like


@api_bp.route('/reviews', methods=['POST'])
def create_review():
    """客人提交订单评价（商城旧接口，保持兼容）"""
    data = request.get_json()
    if not data:
        return error_response('请求数据为空')

    order_id = data.get('order_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()

    if not order_id or not rating:
        return error_response('缺少必填字段')

    if rating not in (1, 2, 3, 4, 5):
        return error_response('评分范围 1-5')

    if comment and len(comment) > 500:
        return error_response('评价内容不能超过500字')

    order = ShopOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)

    if order.status != 3:
        return error_response('只能评价已完成的订单')

    existing = Review.query.filter_by(order_id=order_id).first()
    if existing:
        return error_response('该订单已评价')

    review = Review(order_id=order_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()

    return success_response(review.to_dict(), '评价成功')


@api_bp.route('/products/<int:product_id>/rating', methods=['GET'])
def get_product_rating(product_id):
    """获取商品平均评分和评价数"""
    result = db.session.query(
        db.func.avg(Review.rating).label('avg_rating'),
        db.func.count(Review.id).label('review_count')
    ).join(ShopOrder, Review.order_id == ShopOrder.id).join(
        OrderItem, OrderItem.order_id == ShopOrder.id
    ).filter(OrderItem.product_id == product_id).first()

    avg_rating = round(float(result.avg_rating), 1) if result.avg_rating else None
    review_count = result.review_count or 0

    return success_response({
        'avg_rating': avg_rating,
        'review_count': review_count
    })


# ==================== 通用评价系统（接送 / 门票）====================

def _validate_review_data(data):
    """提交评价数据校验"""
    rating = data.get('rating')
    comment = (data.get('comment') or '').strip()

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return None, error_response('评分范围 1-5')
    if comment and len(comment) > 1000:
        return None, error_response('评价内容不能超过 1000 字')

    lang = (data.get('lang') or 'zh').strip()
    if lang not in ('zh', 'en', 'ru', 'es'):
        lang = 'zh'

    return {'rating': rating, 'comment': comment, 'lang': lang}, None


@api_bp.route('/reviews/transfer', methods=['POST'])
@limiter.limit("10 per minute")
def submit_transfer_review():
    """提交接送订单评价"""
    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id:
        return error_response('缺少订单 ID')

    parsed, err = _validate_review_data(data)
    if err:
        return err

    order = TransferOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    # 接送订单状态：0=待支付 1=已支付 2=已完成 3=已取消
    if order.status not in (1, 2):
        return error_response('只能评价已完成的订单')

    # 防重复
    existing = ServiceReview.query.filter_by(order_type='transfer', order_id=order_id).first()
    if existing:
        return error_response('该订单已评价过')

    review = ServiceReview(
        order_type='transfer',
        order_id=order_id,
        order_no=order.order_no,
        target_id=order.vehicle_id,    # 关联到车型，便于按车型查询评价
        rating=parsed['rating'],
        comment=parsed['comment'] or None,
        reviewer_name=order.contact_name,
        lang=parsed['lang'],
        status=0,
    )
    db.session.add(review)
    db.session.commit()
    return success_response(review.to_dict(masked=True), '评价成功')


@api_bp.route('/reviews/ticket', methods=['POST'])
@limiter.limit("10 per minute")
def submit_ticket_review():
    """提交门票订单评价"""
    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id:
        return error_response('缺少订单 ID')

    parsed, err = _validate_review_data(data)
    if err:
        return err

    order = TicketOrder.query.get(order_id)
    if not order:
        return error_response('订单不存在', 404)
    # 门票订单状态：0=待支付 1=已支付 2=已使用 3=已取消 4=已退款
    if order.status not in (1, 2):
        return error_response('只能评价已支付/已使用的订单')

    existing = ServiceReview.query.filter_by(order_type='ticket', order_id=order_id).first()
    if existing:
        return error_response('该订单已评价过')

    review = ServiceReview(
        order_type='ticket',
        order_id=order_id,
        order_no=order.order_no,
        target_id=order.attraction_id,    # 关联到景点，便于按景点查询评价
        rating=parsed['rating'],
        comment=parsed['comment'] or None,
        reviewer_name=order.contact_name,
        lang=parsed['lang'],
        status=0,
    )
    db.session.add(review)
    db.session.commit()
    return success_response(review.to_dict(masked=True), '评价成功')


@api_bp.route('/reviews/ticket/<int:attraction_id>', methods=['GET'])
def get_ticket_reviews(attraction_id):
    """获取某景点的所有评价 + 平均分（供 TicketDetail 页展示）"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    query = ServiceReview.query.filter_by(
        order_type='ticket',
        target_id=attraction_id,
        status=0  # 只显示未被隐藏的
    ).order_by(ServiceReview.created_at.desc())

    # 平均分 + 总数
    stats = db.session.query(
        db.func.avg(ServiceReview.rating).label('avg_rating'),
        db.func.count(ServiceReview.id).label('total'),
    ).filter_by(order_type='ticket', target_id=attraction_id, status=0).first()

    result = paginate_query(query, page=page, per_page=per_page)

    return success_response({
        'avg_rating': round(float(stats.avg_rating), 1) if stats.avg_rating else None,
        'total': stats.total or 0,
        'list': [r.to_dict(masked=True) for r in result['items']],
        'page': result['page'],
        'pages': result['pages'],
    })


@api_bp.route('/reviews/transfer/recent', methods=['GET'])
def get_transfer_recent_reviews():
    """获取最近的接送评价 + 平均分（供 Transfer/Home 页展示）"""
    per_page = int(request.args.get('per_page', 6))

    query = ServiceReview.query.filter_by(
        order_type='transfer',
        status=0
    ).order_by(ServiceReview.created_at.desc()).limit(per_page)

    stats = db.session.query(
        db.func.avg(ServiceReview.rating).label('avg_rating'),
        db.func.count(ServiceReview.id).label('total'),
    ).filter_by(order_type='transfer', status=0).first()

    return success_response({
        'avg_rating': round(float(stats.avg_rating), 1) if stats.avg_rating else None,
        'total': stats.total or 0,
        'list': [r.to_dict(masked=True) for r in query.all()],
    })


@api_bp.route('/reviews/check', methods=['GET'])
def check_review_status():
    """检查某订单是否已评价（OrderQuery 页用，判断是否显示'去评价'按钮）"""
    order_type = request.args.get('order_type', '').strip()
    order_id = request.args.get('order_id', type=int)
    if order_type not in ('transfer', 'ticket', 'shop') or not order_id:
        return error_response('参数错误')

    existing = ServiceReview.query.filter_by(
        order_type=order_type,
        order_id=order_id
    ).first()
    return success_response({
        'reviewed': bool(existing),
        'review': existing.to_dict(masked=True) if existing else None,
    })


# ==================== 管理端：评价管理 ====================

@api_bp.route('/admin/reviews', methods=['GET'])
@admin_required
def admin_list_reviews():
    """评价列表（带筛选 + 分页）"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    order_type = (request.args.get('order_type') or '').strip()
    status = request.args.get('status', '')
    rating = request.args.get('rating', type=int)
    keyword = (request.args.get('keyword') or '').strip()

    query = ServiceReview.query
    if order_type in ('transfer', 'ticket', 'shop'):
        query = query.filter(ServiceReview.order_type == order_type)
    if status != '':
        try:
            query = query.filter(ServiceReview.status == int(status))
        except (ValueError, TypeError):
            pass
    if rating in (1, 2, 3, 4, 5):
        query = query.filter(ServiceReview.rating == rating)
    if keyword:
        like = f'%{escape_like(keyword)}%'
        query = query.filter(
            db.or_(
                ServiceReview.order_no.ilike(like),
                ServiceReview.reviewer_name.ilike(like),
                ServiceReview.comment.ilike(like),
            )
        )

    query = query.order_by(ServiceReview.created_at.desc())
    result = paginate_query(query, page=page, per_page=per_page)

    # 统计概览
    base_q = ServiceReview.query
    if order_type in ('transfer', 'ticket', 'shop'):
        base_q = base_q.filter(ServiceReview.order_type == order_type)
    overall = db.session.query(
        db.func.avg(ServiceReview.rating).label('avg'),
        db.func.count(ServiceReview.id).label('total'),
    ).filter(base_q.whereclause if base_q.whereclause is not None else True).first()

    return success_response({
        'list': [r.to_dict(masked=False) for r in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages'],
        'overall': {
            'avg_rating': round(float(overall.avg), 1) if overall.avg else None,
            'total': overall.total or 0,
        },
    })


@api_bp.route('/admin/reviews/<int:review_id>', methods=['PUT'])
@admin_required
def admin_update_review(review_id):
    """更新评价：隐藏/显示 + 管理员回复"""
    review = ServiceReview.query.get(review_id)
    if not review:
        return error_response('评价不存在', 404)

    data = request.get_json() or {}

    if 'status' in data:
        try:
            new_status = int(data['status'])
            if new_status not in (0, 1):
                return error_response('状态值非法（0=显示 1=隐藏）')
            review.status = new_status
        except (ValueError, TypeError):
            return error_response('状态值非法')

    if 'admin_reply' in data:
        reply = (data.get('admin_reply') or '').strip()
        if reply and len(reply) > 1000:
            return error_response('回复内容不能超过 1000 字')
        review.admin_reply = reply or None
        review.replied_at = datetime.utcnow() if reply else None

    db.session.commit()
    return success_response(review.to_dict(masked=False), '更新成功')


@api_bp.route('/admin/reviews/<int:review_id>', methods=['DELETE'])
@admin_required
def admin_delete_review(review_id):
    """删除评价"""
    review = ServiceReview.query.get(review_id)
    if not review:
        return error_response('评价不存在', 404)
    db.session.delete(review)
    db.session.commit()
    return success_response(None, '删除成功')
