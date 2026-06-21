import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { canAccess, defaultPathForRole } from '../utils/permissions'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    redirect: to => {
      // 根据当前用户角色跳到对应"首页"
      // 注意：这里拿不到 auth store（不在 setup 环境），用 sessionStorage 缓存或回退 /dashboard
      const cachedRole = sessionStorage.getItem('admin_role')
      return defaultPathForRole(cachedRole)
    },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: 'Dashboard' } },
      { path: 'products', name: 'Products', component: () => import('../views/Products.vue'), meta: { title: 'Products' } },
      { path: 'categories', name: 'Categories', component: () => import('../views/Categories.vue'), meta: { title: 'Categories' } },
      { path: 'vehicles', name: 'Vehicles', component: () => import('../views/Vehicles.vue'), meta: { title: 'Vehicles' } },
      { path: 'locations', name: 'Locations', component: () => import('../views/Locations.vue'), meta: { title: 'Locations' } },
      { path: 'orders/shop', name: 'ShopOrders', component: () => import('../views/ShopOrders.vue'), meta: { title: 'Shop Orders' } },
      { path: 'orders/transfer', name: 'TransferOrders', component: () => import('../views/TransferOrders.vue'), meta: { title: 'Transfer Orders' } },
      { path: 'orders/refund', name: 'RefundManagement', component: () => import('../views/RefundManagement.vue'), meta: { title: 'Refund Management' } },
      { path: 'delivery', name: 'Delivery', component: () => import('../views/DeliveryManagement.vue'), meta: { title: 'Delivery' } },
      { path: 'coupons', name: 'Coupons', component: () => import('../views/Coupons.vue'), meta: { title: 'Coupons' } },
      { path: 'transfer/pricing', name: 'TransferPricing', component: () => import('../views/Settings.vue'), meta: { title: 'Transfer Pricing' } },
      { path: 'payment', name: 'Payment', component: () => import('../views/Payment.vue'), meta: { title: 'Payment' } },
      { path: 'tickets/attractions', name: 'TicketAttractions', component: () => import('../views/TicketAttractions.vue'), meta: { title: 'Ticket Attractions' } },
      { path: 'tickets/packages', name: 'TicketPackages', component: () => import('../views/TicketPackages.vue'), meta: { title: 'Ticket Packages' } },
      { path: 'tickets/transport-pricing', name: 'TicketTransportPricing', component: () => import('../views/TicketTransportPricing.vue'), meta: { title: 'Ticket Transport Pricing' } },
      { path: 'tickets/orders', name: 'TicketOrders', component: () => import('../views/TicketOrders.vue'), meta: { title: 'Ticket Orders' } },
      { path: 'guides', name: 'Guides', component: () => import('../views/Guides.vue'), meta: { title: 'Guides' } },
      { path: 'wishes', name: 'Wishes', component: () => import('../views/Wishes.vue'), meta: { title: 'Wishes' } },
      { path: 'reviews', name: 'Reviews', component: () => import('../views/Reviews.vue'), meta: { title: 'Reviews' } },
      { path: 'accounts', name: 'Accounts', component: () => import('../views/Accounts.vue'), meta: { title: 'Accounts' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async to => {
  const auth = useAuthStore()
  const token = auth.token || localStorage.getItem('admin_token')

  if (to.meta.public) {
    if (to.path === '/login' && token) {
      const user = auth.initialized ? auth.user : await auth.initAuth()
      if (user) return defaultPathForRole(user.role)
    }
    return true
  }

  if (!token) return '/login'

  const user = auth.initialized ? auth.user : await auth.initAuth()
  if (!user) return '/login'

  // 角色权限检查：当前用户能否访问目标路由
  // 跳过根路径（'/' 是 Layout 容器，会自动 redirect 到 dashboard）
  if (to.path !== '/' && !canAccess(to.path, user.role)) {
    // 没权限 → 跳到该角色的默认首页
    return defaultPathForRole(user.role)
  }

  return true
})

export default router
