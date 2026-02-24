<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: card.bg }">
            <el-icon :size="24"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ card.value }}</p>
            <p class="stat-title">{{ card.title }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>Recent Shop Orders</template>
          <el-table :data="recentShopOrders" size="small" stripe>
            <el-table-column prop="order_no" label="Order No" width="180" />
            <el-table-column prop="contact_name" label="Customer" />
            <el-table-column prop="total_price" label="Total" width="100">
              <template #default="{ row }">¥{{ row.total_price }}</template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>Recent Transfer Orders</template>
          <el-table :data="recentTransferOrders" size="small" stripe>
            <el-table-column prop="order_no" label="Order No" width="180" />
            <el-table-column prop="contact_name" label="Customer" />
            <el-table-column prop="service_type" label="Type" width="90" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ShoppingCart, Van, Goods, Ticket } from '@element-plus/icons-vue'
import { getShopOrders, getTransferOrders, getProducts, getCoupons } from '../api'

const statCards = ref([
  { title: 'Products', value: '-', icon: Goods, bg: '#e6f7ff' },
  { title: 'Shop Orders', value: '-', icon: ShoppingCart, bg: '#f6ffed' },
  { title: 'Transfer Orders', value: '-', icon: Van, bg: '#fff7e6' },
  { title: 'Coupons', value: '-', icon: Ticket, bg: '#fff1f0' }
])

const recentShopOrders = ref([])
const recentTransferOrders = ref([])

const statusLabels = { 0: 'Pending', 1: 'Confirmed', 2: 'Completed', 3: 'Cancelled' }
const statusTypes = { 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }
const statusLabel = s => statusLabels[s] || 'Unknown'
const statusType = s => statusTypes[s] || 'info'

onMounted(async () => {
  try {
    const [prodRes, shopRes, transRes, couponRes] = await Promise.all([
      getProducts({ page: 1, per_page: 1 }),
      getShopOrders({ page: 1, per_page: 5 }),
      getTransferOrders({ page: 1, per_page: 5 }),
      getCoupons({ page: 1, per_page: 1 })
    ])
    statCards.value[0].value = prodRes.data?.total ?? prodRes.data?.length ?? 0
    statCards.value[1].value = shopRes.data?.total ?? 0
    statCards.value[2].value = transRes.data?.total ?? 0
    statCards.value[3].value = couponRes.data?.total ?? couponRes.data?.length ?? 0
    recentShopOrders.value = shopRes.data?.items || shopRes.data || []
    recentTransferOrders.value = transRes.data?.items || transRes.data || []
  } catch {}
})
</script>

<style scoped>
.stat-card { display: flex; align-items: center; }
.stat-card :deep(.el-card__body) { display: flex; align-items: center; gap: 16px; width: 100%; }
.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 28px; font-weight: 700; color: #4a3728; line-height: 1; }
.stat-title { font-size: 13px; color: #8a7b6b; margin-top: 4px; }
</style>
