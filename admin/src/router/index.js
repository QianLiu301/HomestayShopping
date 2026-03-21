import { createRouter, createWebHistory } from 'vue-router'

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
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: 'Dashboard' } },
      { path: 'products', name: 'Products', component: () => import('../views/Products.vue'), meta: { title: 'Products' } },
      { path: 'categories', name: 'Categories', component: () => import('../views/Categories.vue'), meta: { title: 'Categories' } },
      { path: 'vehicles', name: 'Vehicles', component: () => import('../views/Vehicles.vue'), meta: { title: 'Vehicles' } },
      { path: 'locations', name: 'Locations', component: () => import('../views/Locations.vue'), meta: { title: 'Locations' } },
      { path: 'orders/shop', name: 'ShopOrders', component: () => import('../views/ShopOrders.vue'), meta: { title: 'Shop Orders' } },
      { path: 'orders/transfer', name: 'TransferOrders', component: () => import('../views/TransferOrders.vue'), meta: { title: 'Transfer Orders' } },
      { path: 'delivery', name: 'Delivery', component: () => import('../views/DeliveryManagement.vue'), meta: { title: 'Delivery' } },
      { path: 'coupons', name: 'Coupons', component: () => import('../views/Coupons.vue'), meta: { title: 'Coupons' } },
      { path: 'transfer/pricing', name: 'TransferPricing', component: () => import('../views/Settings.vue'), meta: { title: 'Transfer Pricing' } },
      { path: 'payment', name: 'Payment', component: () => import('../views/Payment.vue'), meta: { title: 'Payment' } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
