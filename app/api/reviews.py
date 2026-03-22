from flask import request
from app.api import api_bp
from app.models import Review, ShopOrder, OrderItem, Product
from app import db
from app.utils import success_response, error_response


@api_bp.route('/reviews', methods=['POST'])
def create_review():
    """客人提交订单评价"""
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
    # 找出包含该商品的已完成订单的评价
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
