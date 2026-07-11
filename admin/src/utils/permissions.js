/**
 * 前端权限矩阵：定义每个菜单/路由谁能看
 * 后端有同名的权限矩阵 (app/utils/permissions.py)，两边保持一致
 */

export const ROLE_OWNER = 'owner'
export const ROLE_ADMIN = 'admin'
export const ROLE_FINANCE = 'finance'
export const ROLE_CS = 'cs'
export const ROLE_TRANSFER_OPS = 'transfer_ops'

export const ROLE_LABELS = {
  owner: '老板',
  admin: '管理员',
  finance: '财务',
  cs: '客服',
  transfer_ops: '接送专员',
}

// 全部非接送专员（综合视角的人）
const NON_TRANSFER = [ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_CS]

/**
 * 每个菜单项 / 路由谁能看
 * key = router path 或菜单 index
 */
export const MENU_PERMISSIONS = {
  '/dashboard': [ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_CS, ROLE_TRANSFER_OPS],

  // 商城
  '/products':    [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],
  '/categories':  [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],

  // 接送服务（接送专员能看）
  '/transfer/pricing': [ROLE_OWNER, ROLE_ADMIN, ROLE_TRANSFER_OPS],
  '/vehicles':         [ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_TRANSFER_OPS],
  '/locations':        [ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_TRANSFER_OPS],

  // 门票（接送专员看不到）
  '/tickets/attractions':       [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],
  '/tickets/packages':          [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],
  '/tickets/transport-pricing': [ROLE_OWNER, ROLE_ADMIN],
  '/tickets/orders':            [ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_FINANCE],

  // 订单
  '/orders/shop':     [ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_FINANCE],
  '/orders/transfer': [ROLE_OWNER, ROLE_ADMIN, ROLE_CS, ROLE_FINANCE, ROLE_TRANSFER_OPS],
  '/orders/refund':   [ROLE_OWNER, ROLE_ADMIN, ROLE_FINANCE, ROLE_CS, ROLE_TRANSFER_OPS],
  '/delivery':        [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],

  // 营销 / 服务
  '/coupons': [ROLE_OWNER, ROLE_ADMIN],
  '/guides':  [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],
  '/wishes':  [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],
  '/reviews': [ROLE_OWNER, ROLE_ADMIN, ROLE_CS],
  '/guest-registrations': [ROLE_OWNER, ROLE_ADMIN],  // 护照敏感信息，仅 owner/admin

  // 系统
  '/payment':  [ROLE_OWNER, ROLE_FINANCE],   // 财务只读
  '/accounts': [ROLE_OWNER],                 // 仅老板
  '/settings': [ROLE_OWNER],
}

// 子菜单分组：用于 Layout 决定整个分组是否显示
export const MENU_GROUPS = {
  'shop-mgmt':     ['/products', '/categories'],
  'transfer-mgmt': ['/transfer/pricing', '/vehicles', '/locations'],
  'tickets-mgmt':  ['/tickets/attractions', '/tickets/packages', '/tickets/transport-pricing', '/tickets/orders'],
  'order-mgmt':    ['/orders/shop', '/orders/transfer', '/orders/refund', '/delivery'],
}

/**
 * 当前角色能否看到某个菜单/路由
 */
export function canAccess(path, role) {
  if (!role) return false
  const allowed = MENU_PERMISSIONS[path]
  if (!allowed) return true   // 没在矩阵里的路由默认可见
  return allowed.includes(role)
}

/**
 * 当前角色能否看到一组菜单（用于子菜单分组）—— 任何一个子项可见就显示分组
 */
export function canAccessGroup(groupKey, role) {
  const paths = MENU_GROUPS[groupKey] || []
  return paths.some(p => canAccess(p, role))
}

/**
 * 当前角色登录后默认跳转的页面（每个角色的"主页"）
 */
export function defaultPathForRole(role) {
  if (role === ROLE_TRANSFER_OPS) return '/orders/transfer'  // 接送专员直接到接送订单
  return '/dashboard'
}
