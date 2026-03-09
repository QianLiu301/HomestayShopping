<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6" v-for="card in statCards" :key="card.key">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: card.bg }">
            <el-icon :size="24"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ card.value }}</p>
            <p class="stat-title">{{ $t(`dashboard.${card.key}`) }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>{{ $t('dashboard.recentShopOrders') }}</template>
          <el-table :data="recentShopOrders" size="small" stripe>
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" width="180" />
            <el-table-column prop="contact_name" :label="$t('dashboard.customer')" />
            <el-table-column prop="total_price" :label="$t('dashboard.total')" width="100">
              <template #default="{ row }">¥{{ row.total_price }}</template>
            </el-table-column>
            <el-table-column prop="status" :label="$t('common.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>{{ $t('dashboard.recentTransferOrders') }}</template>
          <el-table :data="recentTransferOrders" size="small" stripe>
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" width="180" />
            <el-table-column prop="contact_name" :label="$t('dashboard.customer')" />
            <el-table-column prop="service_type" :label="$t('dashboard.type')" width="90" />
            <el-table-column prop="status" :label="$t('common.status')" width="100">
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
import { useI18n } from 'vue-i18n'
import { ShoppingCart, Van, Goods, Ticket } from '@element-plus/icons-vue'
import { getShopOrders, getTransferOrders, getProducts, getCoupons } from '../api'

const { t } = useI18n()

const statCards = ref([
  { key: 'products', value: '-', icon: Goods, bg: '#e6f7ff' },
  { key: 'shopOrders', value: '-', icon: ShoppingCart, bg: '#f6ffed' },
  { key: 'transferOrders', value: '-', icon: Van, bg: '#fff7e6' },
  { key: 'coupons', value: '-', icon: Ticket, bg: '#fff1f0' }
])

const recentShopOrders = ref([])
const recentTransferOrders = ref([])

const statusTypes = { 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }
const statusLabel = s => t(`orders.${['pending','confirmed','completed','cancelled'][s] || 'unknown'}`)
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
    recentShopOrders.value = shopRes.data?.list || shopRes.data?.items || []
    recentTransferOrders.value = transRes.data?.list || transRes.data?.items || []
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
