<template>
  <el-container class="layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
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
          <template #title>Dashboard</template>
        </el-menu-item>

        <el-sub-menu index="shop-mgmt">
          <template #title>
            <el-icon><ShoppingBag /></el-icon>
            <span>Shop</span>
          </template>
          <el-menu-item index="/products">Products</el-menu-item>
          <el-menu-item index="/categories">Categories</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="transfer-mgmt">
          <template #title>
            <el-icon><Van /></el-icon>
            <span>Transfer</span>
          </template>
          <el-menu-item index="/vehicles">Vehicles</el-menu-item>
          <el-menu-item index="/locations">Locations</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="order-mgmt">
          <template #title>
            <el-icon><List /></el-icon>
            <span>Orders</span>
          </template>
          <el-menu-item index="/orders/shop">Shop Orders</el-menu-item>
          <el-menu-item index="/orders/transfer">Transfer Orders</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/coupons">
          <el-icon><Ticket /></el-icon>
          <template #title>Coupons</template>
        </el-menu-item>

        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>Settings</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" /><Expand v-else />
          </el-icon>
          <span class="page-title">{{ $route.meta.title }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="onCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              {{ auth.user?.name || auth.user?.username || 'Admin' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">Logout</el-dropdown-item>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { DataAnalysis, ShoppingBag, Van, List, Ticket, Setting, Fold, Expand, UserFilled, ArrowDown } from '@element-plus/icons-vue'

const auth = useAuthStore()
const router = useRouter()
const isCollapse = ref(false)

onMounted(() => auth.fetchUser())

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
.header-right { display: flex; align-items: center; }
.user-info { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 14px; color: #4a3728; }
.main { background: #faf6ef; padding: 24px; }
</style>
