<template>
  <el-container class="layout">
    <div v-if="isMobile && !isCollapse" class="aside-overlay" @click="isCollapse = true"></div>
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside" :class="{ 'aside-mobile-open': isMobile && !isCollapse }">
      <div class="logo" @click="$router.push('/')">
        <span v-if="!isCollapse">HOMESTAY</span>
        <span v-else>H</span>
      </div>
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        background-color="#3d2e1e"
        text-color="rgba(255,255,255,0.7)"
        active-text-color="#c8a97e"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>{{ $t('nav.dashboard') }}</template>
        </el-menu-item>

        <el-sub-menu index="shop-mgmt">
          <template #title>
            <el-icon><ShoppingBag /></el-icon>
            <span>{{ $t('nav.shop') }}</span>
          </template>
          <el-menu-item index="/products">{{ $t('nav.products') }}</el-menu-item>
          <el-menu-item index="/categories">{{ $t('nav.categories') }}</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="transfer-mgmt">
          <template #title>
            <el-icon><Van /></el-icon>
            <span>{{ $t('nav.transfer') }}</span>
          </template>
          <el-menu-item index="/transfer/pricing">{{ $t('nav.transferPricing') }}</el-menu-item>
          <el-menu-item index="/vehicles">{{ $t('nav.vehicles') }}</el-menu-item>
          <el-menu-item index="/locations">{{ $t('nav.locations') }}</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="tickets-mgmt">
          <template #title>
            <el-icon><Ticket /></el-icon>
            <span>{{ $t('nav.tickets') }}</span>
          </template>
          <el-menu-item index="/tickets/attractions">{{ $t('nav.ticketAttractions') }}</el-menu-item>
          <el-menu-item index="/tickets/packages">{{ $t('nav.ticketPackages') }}</el-menu-item>
          <el-menu-item index="/tickets/transport-pricing">{{ $t('nav.ticketTransportPricing') }}</el-menu-item>
          <el-menu-item index="/tickets/orders">{{ $t('nav.ticketOrders') }}</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="order-mgmt">
          <template #title>
            <el-icon><List /></el-icon>
            <span>{{ $t('nav.orders') }}</span>
          </template>
          <el-menu-item index="/orders/shop">{{ $t('nav.shopOrders') }}</el-menu-item>
          <el-menu-item index="/orders/transfer">{{ $t('nav.transferOrders') }}</el-menu-item>
          <el-menu-item index="/orders/refund">{{ $t('nav.refundManagement') }}</el-menu-item>
          <el-menu-item index="/delivery">{{ $t('nav.delivery') }}</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/coupons">
          <el-icon><Discount /></el-icon>
          <template #title>{{ $t('nav.coupons') }}</template>
        </el-menu-item>

        <el-menu-item index="/wishes">
          <el-icon><ChatLineRound /></el-icon>
          <template #title>{{ $t('nav.wishes') }}</template>
        </el-menu-item>

        <el-menu-item index="/payment">
          <el-icon><CreditCard /></el-icon>
          <template #title>{{ $t('nav.payment') }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown class="lang-switcher" @command="switchLang">
            <span class="lang-btn">
              {{ locale === 'zh' ? '中文' : 'EN' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh" :disabled="locale === 'zh'">中文</el-dropdown-item>
                <el-dropdown-item command="en" :disabled="locale === 'en'">English</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-dropdown @command="onCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              {{ auth.user?.name || auth.user?.username || 'Admin' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">{{ $t('nav.logout') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { DataAnalysis, ShoppingBag, Van, List, Ticket, Discount, CreditCard, Fold, Expand, UserFilled, ArrowDown, ChatLineRound } from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const isMobile = ref(window.innerWidth <= 768)
const isCollapse = ref(isMobile.value)

function onResize() {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) isCollapse.value = true
}


const titleMap = {
  '/dashboard': 'nav.dashboard',
  '/products': 'nav.products',
  '/categories': 'nav.categories',
  '/transfer/pricing': 'nav.transferPricing',
  '/vehicles': 'nav.vehicles',
  '/locations': 'nav.locations',
  '/tickets/attractions': 'nav.ticketAttractions',
  '/tickets/packages': 'nav.ticketPackages',
  '/tickets/transport-pricing': 'nav.ticketTransportPricing',
  '/tickets/orders': 'nav.ticketOrders',
  '/orders/shop': 'nav.shopOrders',
  '/orders/transfer': 'nav.transferOrders',
  '/orders/refund': 'nav.refundManagement',
  '/delivery': 'nav.delivery',
  '/coupons': 'nav.coupons',
  '/payment': 'nav.payment'
}

const pageTitle = computed(() => {
  const key = titleMap[route.path]
  return key ? t(key) : (route.meta.title || '')
})

onMounted(() => { auth.fetchUser(); window.addEventListener('resize', onResize) })
onUnmounted(() => window.removeEventListener('resize', onResize))

function switchLang(lang) {
  locale.value = lang
  localStorage.setItem('admin_lang', lang)
}

function onCommand(cmd) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.aside {
  background: #3d2e1e;
  transition: width 0.3s;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c8a97e;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.el-menu { border-right: none; }
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e8dfd4;
  padding: 0 24px;
}
.header-left { display: flex; align-items: center; gap: 16px; }
.collapse-btn { font-size: 20px; cursor: pointer; color: #8a7b6b; }
.page-title { font-size: 18px; font-weight: 600; color: #4a3728; }
.header-right { display: flex; align-items: center; gap: 16px; }
.lang-switcher { cursor: pointer; }
.lang-btn { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #4a3728; cursor: pointer; padding: 4px 8px; border-radius: 4px; border: 1px solid #e8dfd4; }
.lang-btn:hover { border-color: #c8a97e; color: #c8a97e; }
.user-info { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 14px; color: #4a3728; }
.main { background: #faf6ef; padding: 24px; }

/* Mobile overlay */
.aside-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 999; }

@media (max-width: 768px) {
  .aside { position: fixed !important; left: 0; top: 0; bottom: 0; z-index: 1000; transform: translateX(-100%); transition: transform 0.3s ease; width: 220px !important; }
  .aside.aside-mobile-open { transform: translateX(0); width: 220px !important; }
  .header { padding: 0 12px; }
  .header-left { gap: 8px; }
  .page-title { font-size: 15px; }
  .header-right { gap: 8px; }
  .lang-btn { font-size: 12px; padding: 3px 6px; }
  .user-info { font-size: 12px; }
  .main { padding: 12px; }
}
</style>
