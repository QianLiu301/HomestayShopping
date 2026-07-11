"""角色权限定义 + 工具函数
=========================

5 个角色：
    owner         老板/超级管理员（你）— 全部权限
    admin         管理员             — 大部分权限，不能管账号/系统设置
    finance       财务               — 退款审批 + 看所有订单
    cs            客服               — 处理订单、回复评价、跟许愿池客户沟通
    transfer_ops  接送专员           — 只看接送相关业务

权限模型：
    每个 API 用 @require_role('owner', 'admin', ...) 装饰器声明谁能调
    前后端共用同一份角色枚举，避免不一致
"""
from functools import wraps
from flask import request, jsonify


# ============ 角色定义 ============

ROLE_OWNER = 'owner'
ROLE_ADMIN = 'admin'
ROLE_FINANCE = 'finance'
ROLE_CS = 'cs'
ROLE_TRANSFER_OPS = 'transfer_ops'

ALL_ROLES = (ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_CS, ROLE_TRANSFER_OPS)

# 角色显示名（中文）
ROLE_LABELS = {
    ROLE_OWNER: '老板',
    ROLE_ADMIN: '管理员',
    ROLE_FINANCE: '财务',
    ROLE_CS: '客服',
    ROLE_TRANSFER_OPS: '接送专员',
}

# ============ 权限组（按业务模块）============

# 所有"非接送专员"的角色 = 能看综合数据的人
NON_TRANSFER_ONLY = (ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_CS)

# 能管理商品/景点/票种内容（CRUD）的角色
CAN_EDIT_CONTENT = (ROLE_OWNER, ROLE_ADMIN)

# 能查看商品/景点/票种（只读 + 列表）的角色
CAN_READ_CONTENT = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS)

# 能管理接送相关内容（车型/定价/地点）
CAN_EDIT_TRANSFER = (ROLE_OWNER, ROLE_ADMIN, ROLE_TRANSFER_OPS)

# 能查看接送相关内容
CAN_READ_TRANSFER = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_TRANSFER_OPS)

# 能查看商城订单
CAN_VIEW_SHOP_ORDERS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_FINANCE)
# 能处理商城订单（改状态、退款、删）
CAN_MANAGE_SHOP_ORDERS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS)

# 能查看接送订单
CAN_VIEW_TRANSFER_ORDERS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_FINANCE, ROLE_TRANSFER_OPS)
CAN_MANAGE_TRANSFER_ORDERS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_TRANSFER_OPS)

# 能查看门票订单
CAN_VIEW_TICKET_ORDERS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_FINANCE)
CAN_MANAGE_TICKET_ORDERS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS)

# 配送管理
CAN_MANAGE_DELIVERY = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS)

# 退款处理 — 财务/接送专员能审批；CS 只能看
CAN_APPROVE_REFUND = (ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_TRANSFER_OPS)
CAN_VIEW_REFUND = (ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_CS, ROLE_TRANSFER_OPS)

# 优惠券
CAN_MANAGE_COUPONS = (ROLE_OWNER, ROLE_ADMIN)

# 许愿池
CAN_MANAGE_WISHES = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS)

# 评价管理
CAN_MANAGE_REVIEWS = (ROLE_OWNER, ROLE_ADMIN, ROLE_CS)

# 支付设置
CAN_MANAGE_PAYMENT = (ROLE_OWNER,)
CAN_VIEW_PAYMENT = (ROLE_OWNER, ROLE_FINANCE)

# 系统设置
CAN_MANAGE_SETTINGS = (ROLE_OWNER,)

# 账号管理（只 owner 能用）
CAN_MANAGE_ACCOUNTS = (ROLE_OWNER,)

# 仪表盘
CAN_VIEW_DASHBOARD_FULL = NON_TRANSFER_ONLY  # 看全部数据
CAN_VIEW_DASHBOARD_TRANSFER_ONLY = (ROLE_TRANSFER_OPS,)  # 只看接送


# ============ 装饰器 ============

def require_role(*allowed_roles):
    """要求当前登录管理员的角色在 allowed_roles 中。

    用法：
        @api_bp.route('/admin/products', methods=['POST'])
        @admin_required
        @require_role(ROLE_OWNER, ROLE_ADMIN)
        def admin_create_product():
            ...

    必须放在 @admin_required 之后（依赖它注入的 request.admin_role）。
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = getattr(request, 'admin_role', None)
            if role not in allowed_roles:
                return jsonify({
                    'code': 403,
                    'message': '没有权限执行此操作',
                    'data': None
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def current_role():
    """获取当前登录管理员的角色（依赖 admin_required 已经跑过）"""
    return getattr(request, 'admin_role', None)


def is_role(*roles):
    """判断当前角色是否在指定列表中"""
    return current_role() in roles


# ============ 基于 URL 前缀 + HTTP 方法 的全局路由权限矩阵 ============
# (前缀, 写权限角色组, 读权限角色组)
# - 请求方法是 GET → 检查读权限组
# - 请求方法是 POST/PUT/DELETE/PATCH → 检查写权限组
# 注意：用 startswith 前缀匹配，所以**特殊路径放前面**
ROUTE_PERMISSIONS = [
    # 账号管理（owner only）
    ('/api/admin/accounts',        CAN_MANAGE_ACCOUNTS, CAN_MANAGE_ACCOUNTS),

    # 系统设置（owner only）
    ('/api/admin/settings',        CAN_MANAGE_SETTINGS, ALL_ROLES),  # GET 大家都能看（取站点联系方式等）

    # 支付设置
    ('/api/admin/payment',         CAN_MANAGE_PAYMENT,  CAN_VIEW_PAYMENT),

    # 仪表盘（接送专员能看，但数据会被后端过滤）
    ('/api/admin/analytics',       ALL_ROLES, ALL_ROLES),

    # 商品 / 分类
    ('/api/admin/products',        CAN_EDIT_CONTENT, CAN_READ_CONTENT),
    ('/api/admin/categories',      CAN_EDIT_CONTENT, CAN_READ_CONTENT),

    # 接送：车型 / 地点 / 定价
    ('/api/admin/vehicles',        CAN_EDIT_TRANSFER, CAN_READ_TRANSFER),
    ('/api/admin/locations',       CAN_EDIT_TRANSFER, CAN_READ_TRANSFER),
    ('/api/admin/transfer',        CAN_EDIT_TRANSFER, CAN_READ_TRANSFER),

    # 门票（接送专员看不到）
    ('/api/admin/ticket-attractions',     CAN_EDIT_CONTENT, CAN_READ_CONTENT),
    ('/api/admin/ticket-packages',        CAN_EDIT_CONTENT, CAN_READ_CONTENT),
    ('/api/admin/ticket-transport-prices', CAN_EDIT_CONTENT, CAN_READ_CONTENT),
    ('/api/admin/ticket-orders',          CAN_MANAGE_TICKET_ORDERS, CAN_VIEW_TICKET_ORDERS),

    # 订单（接送订单允许 transfer_ops）
    ('/api/admin/orders/shop',     CAN_MANAGE_SHOP_ORDERS, CAN_VIEW_SHOP_ORDERS),
    ('/api/admin/orders/transfer', CAN_MANAGE_TRANSFER_ORDERS, CAN_VIEW_TRANSFER_ORDERS),
    # 退款：transfer_ops 能审批，但只能看接送相关（数据过滤在 API 内）
    ('/api/admin/orders/refund',   CAN_APPROVE_REFUND, CAN_VIEW_REFUND),
    ('/api/admin/orders/cancelled', CAN_VIEW_SHOP_ORDERS + (ROLE_TRANSFER_OPS,),
                                    CAN_VIEW_SHOP_ORDERS + (ROLE_TRANSFER_OPS,)),

    # 配送
    ('/api/admin/delivery',        CAN_MANAGE_DELIVERY, CAN_MANAGE_DELIVERY),

    # 优惠券
    ('/api/admin/coupons',         CAN_MANAGE_COUPONS, CAN_MANAGE_COUPONS),

    # 许愿池
    ('/api/admin/wishes',          CAN_MANAGE_WISHES, CAN_MANAGE_WISHES),

    # 攻略管理
    ('/api/admin/guides',          CAN_MANAGE_WISHES, CAN_MANAGE_WISHES),

    # 评价管理
    ('/api/admin/reviews',         CAN_MANAGE_REVIEWS, CAN_MANAGE_REVIEWS),

    # 住宿登记（护照等敏感证件，仅 owner/admin）
    ('/api/admin/guest-registrations', CAN_EDIT_CONTENT, CAN_EDIT_CONTENT),
    ('/api/admin/guest-doc',           CAN_EDIT_CONTENT, CAN_EDIT_CONTENT),
]


def check_route_permission(path, method, role):
    """检查指定 path + method 在当前 role 下是否被允许。
    返回 (allowed: bool, reason: str)
    """
    is_write = method.upper() not in ('GET', 'HEAD', 'OPTIONS')
    for prefix, write_roles, read_roles in ROUTE_PERMISSIONS:
        if path.startswith(prefix):
            allowed = write_roles if is_write else read_roles
            if role in allowed:
                return True, ''
            return False, f'role={role} not allowed for {method} {path}'
    # 路由没在矩阵里：默认所有已登录 admin 都能用
    return True, ''

