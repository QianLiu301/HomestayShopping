from flask import Blueprint

api_bp = Blueprint('api', __name__)

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
from app.api import tickets
from app.api import wishes
from app.api import accounts
from app.api import guides
