from flask import request
from app.api import api_bp
from app.models import Admin
from app import bcrypt
from app.utils import generate_token, success_response, error_response


@api_bp.route('/auth/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    data = request.get_json()
    
    if not data:
        return error_response('请求数据为空')
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return error_response('用户名和密码不能为空')
    
    # 查询管理员
    admin = Admin.query.filter_by(username=username, status=1).first()
    
    if not admin:
        return error_response('用户名或密码错误')
    
    # 验证密码
    if not bcrypt.check_password_hash(admin.password_hash, password):
        return error_response('用户名或密码错误')
    
    # 生成Token
    token = generate_token(admin.id, admin.username, admin.role)
    
    return success_response({
        'token': token,
        'admin': admin.to_dict()
    }, '登录成功')


@api_bp.route('/auth/info', methods=['GET'])
def admin_info():
    """获取当前管理员信息（需要Token）"""
    from app.utils import admin_required
    
    @admin_required
    def get_info():
        admin = Admin.query.get(request.admin_id)
        if not admin:
            return error_response('管理员不存在', 404)
        return success_response(admin.to_dict())
    
    return get_info()
