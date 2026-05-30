"""管理员账号管理 API（owner 角色专用）

注意：路由权限在 utils/permissions.py 的 ROUTE_PERMISSIONS 已声明
为 owner only，所以这里所有接口非 owner 都会被前置拦截，无需重复装饰。
"""
from flask import request
from app.api import api_bp
from app.models import Admin
from app import db, bcrypt
from app.utils import success_response, error_response, admin_required, paginate_query
from app.utils.permissions import ALL_ROLES, ROLE_LABELS


@api_bp.route('/admin/accounts', methods=['GET'])
@admin_required
def list_accounts():
    """列出所有管理员账号"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    query = Admin.query.order_by(Admin.id.asc())
    result = paginate_query(query, page=page, per_page=per_page)

    return success_response({
        'list': [a.to_dict() for a in result['items']],
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages'],
        # 把角色枚举返给前端，下拉框直接用
        'available_roles': [
            {'value': r, 'label': ROLE_LABELS.get(r, r)}
            for r in ALL_ROLES
        ],
    })


@api_bp.route('/admin/accounts', methods=['POST'])
@admin_required
def create_account():
    """创建管理员账号"""
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    name = (data.get('name') or '').strip()
    role = (data.get('role') or 'cs').strip()

    if not username or len(username) < 3:
        return error_response('用户名至少 3 个字符')
    if not password or len(password) < 6:
        return error_response('密码至少 6 个字符')
    if role not in ALL_ROLES:
        return error_response('无效的角色')
    # 禁止通过 API 创建 owner（owner 只能通过环境变量生成）
    if role == 'owner':
        return error_response('不允许通过此接口创建 owner 账号')

    if Admin.query.filter_by(username=username).first():
        return error_response('用户名已存在')

    admin = Admin(
        username=username,
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        name=name or username,
        role=role,
        status=1,
    )
    db.session.add(admin)
    db.session.commit()
    return success_response(admin.to_dict(), '账号创建成功')


@api_bp.route('/admin/accounts/<int:account_id>', methods=['PUT'])
@admin_required
def update_account(account_id):
    """更新管理员账号（角色 / 姓名 / 状态 / 密码）"""
    admin = Admin.query.get(account_id)
    if not admin:
        return error_response('账号不存在', 404)

    # 防止把 owner 改成别的角色
    if admin.role == 'owner':
        # owner 账号只允许改 name，其他字段全部锁定
        data = request.get_json() or {}
        if 'name' in data:
            admin.name = (data.get('name') or '').strip() or admin.name
            db.session.commit()
        return success_response(admin.to_dict(), 'Owner 账号只能修改姓名')

    data = request.get_json() or {}

    if 'role' in data:
        new_role = data.get('role')
        if new_role not in ALL_ROLES or new_role == 'owner':
            return error_response('无效的角色')
        admin.role = new_role

    if 'name' in data:
        admin.name = (data.get('name') or '').strip() or admin.name

    if 'status' in data:
        try:
            admin.status = int(data['status'])
        except (ValueError, TypeError):
            return error_response('状态值非法')

    if data.get('password'):
        new_pw = data['password']
        if len(new_pw) < 6:
            return error_response('密码至少 6 个字符')
        admin.password_hash = bcrypt.generate_password_hash(new_pw).decode('utf-8')

    db.session.commit()
    return success_response(admin.to_dict(), '更新成功')


@api_bp.route('/admin/accounts/<int:account_id>', methods=['DELETE'])
@admin_required
def delete_account(account_id):
    """删除管理员账号"""
    admin = Admin.query.get(account_id)
    if not admin:
        return error_response('账号不存在', 404)
    if admin.role == 'owner':
        return error_response('不能删除 Owner 账号')
    # 不能删除当前正在登录的账号
    if admin.id == getattr(request, 'admin_id', None):
        return error_response('不能删除当前登录的账号')

    db.session.delete(admin)
    db.session.commit()
    return success_response(None, '账号已删除')
