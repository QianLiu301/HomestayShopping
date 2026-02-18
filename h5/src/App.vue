<template>
  <div class="app">
    <router-view v-slot="{ Component }">
      <keep-alive :include="['Home', 'Shop', 'Cart']">
        <component :is="Component" />
      </keep-alive>
    </router-view>
    <TabBar v-if="showTabBar" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from './components/TabBar.vue'

const route = useRoute()

const tabBarPages = ['Home', 'Shop', 'Cart', 'OrderQuery']
const showTabBar = computed(() => tabBarPages.includes(route.name))
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f5f5f5;
}
</style>
