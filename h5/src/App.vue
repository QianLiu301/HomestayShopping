<template>
  <div class="app">
    <NavBar v-if="showNavBar" />
    <router-view v-slot="{ Component }">
      <keep-alive :include="['Home', 'Shop', 'Cart']">
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'

const route = useRoute()
const hideNavBarPages = ['OrderResult']
const showNavBar = computed(() => !hideNavBarPages.includes(route.name))
</script>

<style scoped>
.app {
  min-height: 100vh;
}
</style>
