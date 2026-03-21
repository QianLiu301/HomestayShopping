<template>
  <div>
    <!-- Period selector -->
    <div class="period-bar">
      <el-radio-group v-model="period" @change="loadAnalytics">
        <el-radio-button value="month">{{ $t('dashboard.thisMonth') }}</el-radio-button>
        <el-radio-button value="quarter">{{ $t('dashboard.thisQuarter') }}</el-radio-button>
        <el-radio-button value="half_year">{{ $t('dashboard.halfYear') }}</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Row 1: Revenue cards (3) -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#f0f5ff">
            <el-icon :size="24" color="#4a7cf7"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value total">¥{{ formatNum(analytics.total_revenue) }}</p>
            <p class="stat-title">{{ $t('dashboard.totalRevenue') }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#f6ffed">
            <el-icon :size="24" color="#52c41a"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">¥{{ formatNum(analytics.shop_total) }}</p>
            <p class="stat-title">{{ $t('dashboard.shopRevenue') }}（{{ analytics.shop_count }} {{ $t('dashboard.orders') }}）</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#fff7e6">
            <el-icon :size="24" color="#fa8c16"><Van /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">¥{{ formatNum(analytics.transfer_total) }}</p>
            <p class="stat-title">{{ $t('dashboard.transferRevenue') }}（{{ analytics.transfer_count }} {{ $t('dashboard.orders') }}）</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 2: Count cards (4) -->
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :xs="12" :sm="6" v-for="card in countCards" :key="card.key">
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

    <!-- Recent orders (before chart, convenient for operators) -->
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>{{ $t('dashboard.recentShopOrders') }}</template>
          <el-table :data="recentShopOrders" size="small" stripe>
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" width="180">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push('/orders/shop')">{{ row.order_no }}</el-button>
              </template>
            </el-table-column>
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
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>{{ $t('dashboard.recentTransferOrders') }}</template>
          <el-table :data="recentTransferOrders" size="small" stripe>
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" width="180">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push('/orders/transfer')">{{ row.order_no }}</el-button>
              </template>
            </el-table-column>
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

    <!-- Chart (at the bottom) -->
    <el-card shadow="hover" style="margin-top:20px">
      <template #header>
        <div class="chart-header">
          <span>{{ $t('dashboard.revenueTrend') }}</span>
          <span class="chart-hint">{{ $t('dashboard.excludeCancelled') }}</span>
        </div>
      </template>
      <v-chart :option="chartOption" style="height:360px" autoresize />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ShoppingCart, Van, TrendCharts, Goods, Ticket } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { getShopOrders, getTransferOrders, getProducts, getCoupons, getAnalytics } from '../api'

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const { t } = useI18n()

const period = ref('month')
const analytics = ref({
  shop_count: 0, shop_total: 0,
  transfer_count: 0, transfer_total: 0,
  total_revenue: 0,
  chart: { labels: [], shop: [], transfer: [] }
})

const countCards = ref([
  { key: 'products', value: '-', icon: markRaw(Goods), bg: '#e6f7ff' },
  { key: 'shopOrders', value: '-', icon: markRaw(ShoppingCart), bg: '#f6ffed' },
  { key: 'transferOrders', value: '-', icon: markRaw(Van), bg: '#fff7e6' },
  { key: 'coupons', value: '-', icon: markRaw(Ticket), bg: '#fff1f0' }
])

const recentShopOrders = ref([])
const recentTransferOrders = ref([])

const statusTypes = { 0: 'warning', 1: 'primary', 2: 'success', 3: 'info' }
const statusLabel = s => t(`orders.${['pending','confirmed','completed','cancelled'][s] || 'unknown'}`)
const statusType = s => statusTypes[s] || 'info'

function formatNum(n) {
  if (n == null) return '0'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const chartOption = computed(() => {
  const c = analytics.value.chart
  return {
    tooltip: {
      trigger: 'axis',
      formatter: params => {
        let html = `<b>${params[0].axisValue}</b><br/>`
        let total = 0
        for (const p of params) {
          html += `${p.marker} ${p.seriesName}: ¥${Number(p.value).toLocaleString()}<br/>`
          total += p.value
        }
        html += `<b>${t('dashboard.totalLabel')}: ¥${Number(total).toLocaleString()}</b>`
        return html
      }
    },
    legend: { data: [t('dashboard.shopLabel'), t('dashboard.transferLabel')], top: 0 },
    grid: { left: 50, right: 20, bottom: 30, top: 36 },
    xAxis: {
      type: 'category',
      data: c.labels.map(l => l.length > 7 ? l.slice(5) : l),
      axisLabel: { rotate: c.labels.length > 15 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: v => v >= 1000 ? (v / 1000) + 'k' : v }
    },
    series: [
      {
        name: t('dashboard.shopLabel'),
        type: 'bar',
        stack: 'revenue',
        data: c.shop,
        itemStyle: { color: '#52c41a', borderRadius: c.transfer.every(v => v === 0) ? [4, 4, 0, 0] : 0 }
      },
      {
        name: t('dashboard.transferLabel'),
        type: 'bar',
        stack: 'revenue',
        data: c.transfer,
        itemStyle: { color: '#fa8c16', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
})

async function loadAnalytics() {
  try {
    const res = await getAnalytics({ period: period.value })
    analytics.value = res.data
  } catch (e) {
    console.error('Analytics load error:', e)
  }
}

async function loadCounts() {
  try {
    const [prodRes, shopRes, transRes, couponRes] = await Promise.all([
      getProducts({ page: 1, per_page: 1 }),
      getShopOrders({ page: 1, per_page: 1 }),
      getTransferOrders({ page: 1, per_page: 1 }),
      getCoupons({ page: 1, per_page: 1 })
    ])
    countCards.value[0].value = prodRes.data?.total ?? prodRes.data?.length ?? 0
    countCards.value[1].value = shopRes.data?.total ?? 0
    countCards.value[2].value = transRes.data?.total ?? 0
    countCards.value[3].value = couponRes.data?.total ?? couponRes.data?.length ?? 0
  } catch (e) {
    console.error('Count cards load error:', e)
  }
}

async function loadRecentOrders() {
  try {
    const [shopRes, transRes] = await Promise.all([
      getShopOrders({ page: 1, per_page: 15 }),
      getTransferOrders({ page: 1, per_page: 15 })
    ])
    recentShopOrders.value = shopRes.data?.list || shopRes.data?.items || []
    recentTransferOrders.value = transRes.data?.list || transRes.data?.items || []
  } catch (e) {
    console.error('Recent orders load error:', e)
  }
}

onMounted(() => {
  loadAnalytics()
  loadCounts()
  loadRecentOrders()
})
</script>

<style scoped>
.period-bar { margin-bottom: 20px; }

.stat-card { display: flex; align-items: center; }
.stat-card :deep(.el-card__body) { display: flex; align-items: center; gap: 16px; width: 100%; }
.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 24px; font-weight: 700; color: #4a3728; line-height: 1; }
.stat-value.total { font-size: 28px; color: #4a7cf7; }
.stat-title { font-size: 13px; color: #8a7b6b; margin-top: 4px; }

.chart-header { display: flex; justify-content: space-between; align-items: center; }
.chart-hint { font-size: 12px; color: #aaa; }
</style>
