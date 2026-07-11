import jwt
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app


def generate_order_no(prefix='ORD'):
    """生成订单号: 前缀 + 日期 + 6位随机数"""
    date_str = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{date_str}{random_str}"


def generate_token(admin_id, username, role):
    """生成JWT Token"""
    payload = {
        'admin_id': admin_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_token(token):
    """解析JWT Token"""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def admin_required(f):
    """管理员认证装饰器：验证 Token + 检查路由级角色权限"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 从Header获取Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        # 兼容文件下载等无法方便设置 Authorization Header 的场景
        if not token:
            token = request.args.get('token')

        if not token:
            return jsonify({'code': 401, 'message': '缺少认证Token'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'message': 'Token无效或已过期'}), 401

        # 将用户信息添加到请求上下文
        request.admin_id = payload.get('admin_id')
        request.admin_username = payload.get('username')
        request.admin_role = payload.get('role') or 'admin'

        # 全局角色路由权限检查（RBAC）
        # 用 import-on-call 避免循环导入
        from app.utils.permissions import check_route_permission
        ok, reason = check_route_permission(
            request.path, request.method, request.admin_role
        )
        if not ok:
            return jsonify({
                'code': 403,
                'message': '没有权限访问此功能',
                'data': None
            }), 403

        return f(*args, **kwargs)
    return decorated


def escape_like(keyword):
    """转义 LIKE/ILIKE 通配符，防止用户输入 % 或 _ 干扰查询"""
    return keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def get_lang():
    """获取请求的语言参数"""
    lang = request.args.get('lang', 'zh')
    # 日语/韩语界面：内容字段暂无 ja/ko 翻译，回退英文
    if lang in ('ja', 'ko'):
        return 'en'
    if lang not in ['zh', 'en', 'ru', 'es']:
        lang = 'zh'
    return lang


def success_response(data=None, message='success'):
    """成功响应"""
    return jsonify({
        'code': 200,
        'message': message,
        'data': data
    })


def error_response(message='error', code=400):
    """错误响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': None
    }), code


def paginate_query(query, page=1, per_page=10):
    """分页查询"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': pagination.items,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages
    }
