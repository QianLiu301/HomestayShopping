<template>
  <div class="app">
    <NavBar v-if="showNavBar" />
    <router-view v-slot="{ Component }">
      <keep-alive :include="['Home', 'Shop', 'Cart']">
        <component :is="Component" />
      </keep-alive>
    </router-view>
    <TabBar v-if="showTabBar" />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'
import TabBar from './components/TabBar.vue'

const route = useRoute()
const hideNavBarPages = ['OrderResult']
const isMobile = ref(window.innerWidth <= 768)

const showNavBar = computed(() => !hideNavBarPages.includes(route.name))
const showTabBar = computed(() => isMobile.value && route.meta?.tabBar)

function onResize() {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  window.addEventListener('resize', onResize)
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
