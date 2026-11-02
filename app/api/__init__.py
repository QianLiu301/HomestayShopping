from flask import Blueprint, request
from app.utils.cache import cache_clear

api_bp = Blueprint('api', __name__)


@api_bp.after_request
def _invalidate_cache_on_write(response):
    # 后台改了商品/分类/车型/配置，或新增评价后，立即清空公开接口缓存
    if (request.method != 'GET' and response.status_code < 400
            and (request.path.startswith('/api/admin/') or request.path == '/api/reviews')):
        cache_clear()
    return response

# 导入所有路由
from app.api import auth
from app.api import products
from app.api import categories
from app.api import vehicles
from app.api import locations
from app.api import orders
from app.api import coupons
from app.api import admin
from app.api import settings
from app.api import reviews
