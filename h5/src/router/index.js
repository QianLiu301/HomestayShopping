import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/shop',
    name: 'Shop',
    component: () => import('../views/Shop.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/ProductDetail.vue')
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../views/Cart.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/tickets',
    name: 'Tickets',
    component: () => import('../views/Tickets.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/tickets/:id',
    name: 'TicketDetail',
    component: () => import('../views/TicketDetail.vue')
  },
  {
    path: '/ticket-checkout',
    name: 'TicketCheckout',
    component: () => import('../views/TicketCheckout.vue')
  },
  {
    path: '/ticket-order-result',
    name: 'TicketOrderResult',
    component: () => import('../views/TicketOrderResult.vue')
  },
  {
    path: '/ticket-order-query',
    name: 'TicketOrderQuery',
    component: () => import('../views/OrderQuery.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/guides',
    name: 'Guides',
    component: () => import('../views/Guides.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/guides/:id',
    name: 'GuideDetail',
    component: () => import('../views/GuideDetail.vue')
  },
  {
    path: '/transfer',
    name: 'Transfer',
    component: () => import('../views/Transfer.vue')
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('../views/Checkout.vue')
  },
  {
    path: '/order-result',
    name: 'OrderResult',
    component: () => import('../views/OrderResult.vue')
  },
  {
    path: '/order-query',
    name: 'OrderQuery',
    component: () => import('../views/OrderQuery.vue'),
    meta: { tabBar: true }
  },
  {
    path: '/checkin',
    name: 'Checkin',
    component: () => import('../views/Checkin.vue')
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/Privacy.vue')
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('../views/Terms.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
