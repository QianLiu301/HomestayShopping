<template>
  <div class="app">
    <NavBar v-if="showNavBar" />
    <router-view v-slot="{ Component }">
      <keep-alive :include="['Home', 'Shop', 'Cart']">
        <component :is="Component" />
      </keep-alive>
    </router-view>
    <TabBar v-if="showTabBar" />

    <!-- 全站 WhatsApp 浮动按钮：客服一键联系入口 -->
    <WhatsAppFab
      v-if="!hideWhatsAppFab"
      :whatsapp-number="whatsappNumber"
      :has-tabbar="showTabBar"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'
import TabBar from './components/TabBar.vue'
import WhatsAppFab from './components/WhatsAppFab.vue'
import { getContactInfo } from './api'

const route = useRoute()
const isMobile = ref(window.innerWidth <= 768)
const whatsappNumber = ref('')

const showNavBar = computed(() => {
  // 只在首页显示导航栏，其他页面由各自的页面级导航头负责
  return route.path === '/'
})
const showTabBar = computed(() => isMobile.value && route.meta?.tabBar)

// 哪些页面不显示浮动 WhatsApp 按钮：支付、订单查询等已有自己的联系方式
const hideWhatsAppFabRoutes = ['/checkout', '/ticket-checkout']
const hideWhatsAppFab = computed(() => {
  if (!whatsappNumber.value) return true
  return hideWhatsAppFabRoutes.includes(route.path)
})

function onResize() {
  isMobile.value = window.innerWidth <= 768
}

async function loadContactInfo() {
  try {
    const res = await getContactInfo()
    whatsappNumber.value = res.data?.contact_whatsapp || ''
  } catch (e) {
    // 静默失败：拿不到联系方式时浮动按钮直接不显示
    console.warn('contact info load failed:', e?.message)
  }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadContactInfo()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.app {
  min-height: 100vh;
}
</style>
