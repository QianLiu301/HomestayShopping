from flask import request
from app.api import api_bp
from app.models import Product, Category, OrderItem, ShopOrder
from app.utils import success_response, error_response, get_lang, paginate_query
from app import db


def _get_product_sales_map(product_ids):
    if not product_ids:
        return {}

    rows = db.session.query(
        OrderItem.product_id,
        db.func.coalesce(db.func.sum(OrderItem.quantity), 0).label('sales')
    ).join(ShopOrder, OrderItem.order_id == ShopOrder.id).filter(
        OrderItem.product_id.in_(product_ids),
        ShopOrder.status != 4,
        ShopOrder.payment_status == 1
    ).group_by(OrderItem.product_id).all()

    return {product_id: int(sales or 0) for product_id, sales in rows}


@api_bp.route('/products', methods=['GET'])
def get_products():
    """获取商品列表"""
    lang = get_lang()

    # 查询参数
    category_id = request.args.get('category_id', type=int)
    is_featured = request.args.get('featured', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort = request.args.get('sort', 'default')  # default / sales_desc / price_asc / price_desc / newest

    # 构建查询
    query = Product.query.filter_by(status=1)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if is_featured:
        query = query.filter_by(is_featured=True)

    # 排序
    if sort in ['sales', 'sales_desc']:
        # 按销量排序：仅统计已支付且未取消订单，避免未付款订单干扰排序
        sales_sub = db.session.query(
            OrderItem.product_id,
            db.func.coalesce(db.func.sum(OrderItem.quantity), 0).label('sales')
        ).join(ShopOrder, OrderItem.order_id == ShopOrder.id).filter(
            ShopOrder.status != 4,
            ShopOrder.payment_status == 1
        ).group_by(OrderItem.product_id).subquery()

        query = query.outerjoin(sales_sub, Product.id == sales_sub.c.product_id).order_by(
            db.func.coalesce(sales_sub.c.sales, 0).desc(),
            Product.sort_order.desc(),
            Product.id.desc()
        )
    elif sort == 'price_asc':
        query = query.order_by(
            Product.price.asc(),
            Product.sort_order.desc(),
            Product.id.desc()
        )
    elif sort == 'price_desc':
        query = query.order_by(
            Product.price.desc(),
            Product.sort_order.desc(),
            Product.id.desc()
        )
    elif sort == 'newest':
        query = query.order_by(
            Product.created_at.desc(),
            Product.id.desc()
        )
    else:
        query = query.order_by(
            Product.is_featured.desc(),
            Product.sort_order.desc(),
            Product.id.desc()
        )

    # 分页
    result = paginate_query(query, page, per_page)
    product_ids = [p.id for p in result['items']]
    sales_map = _get_product_sales_map(product_ids)

    for product in result['items']:
        product.sales_count = sales_map.get(product.id, 0)

    return success_response({
        'list': [p.to_dict(lang) for p in result['items']],
        'total': result['total'],
        'page': result['page'],
        'per_page': result['per_page'],
        'pages': result['pages']
    })


@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取商品详情"""
    lang = get_lang()
    
    product = Product.query.filter_by(id=product_id, status=1).first()

    if not product:
        return error_response('商品不存在', 404)

    product.sales_count = _get_product_sales_map([product.id]).get(product.id, 0)

    return success_response(product.to_dict(lang))


@api_bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """获取推荐商品"""
    lang = get_lang()
    limit = request.args.get('limit', 6, type=int)
    
    products = Product.query.filter_by(status=1, is_featured=True)\
        .order_by(Product.sort_order.desc())\
        .limit(limit)\
        .all()

    sales_map = _get_product_sales_map([p.id for p in products])
    for product in products:
        product.sales_count = sales_map.get(product.id, 0)

    return success_response([p.to_dict(lang) for p in products])
