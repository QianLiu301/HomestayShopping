from flask import request
from app.api import api_bp
from app.models import Category
from app.utils import success_response, error_response, get_lang


@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取商品分类列表"""
    lang = get_lang()
    
    categories = Category.query.filter_by(status=1)\
        .order_by(Category.sort_order.desc())\
        .all()
    
    return success_response([c.to_dict(lang) for c in categories])


@api_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """获取分类详情"""
    lang = get_lang()
    
    category = Category.query.filter_by(id=category_id, status=1).first()
    
    if not category:
        return error_response('分类不存在', 404)
    
    return success_response(category.to_dict(lang))
