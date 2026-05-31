<template>
  <div>
    <!-- Period selector + Export -->
    <div class="period-bar">
      <el-radio-group v-model="period" @change="loadAnalytics">
        <el-radio-button value="month">{{ $t('dashboard.thisMonth') }}</el-radio-button>
        <el-radio-button value="quarter">{{ $t('dashboard.thisQuarter') }}</el-radio-button>
        <el-radio-button value="half_year">{{ $t('dashboard.halfYear') }}</el-radio-button>
      </el-radio-group>

      <div class="period-bar__right">
        <el-checkbox v-model="exportPaidOnly">
          {{ $t('dashboard.exportPaidOnly') }}
        </el-checkbox>

        <el-tooltip :content="$t('dashboard.exportTooltip')" placement="top">
          <el-button
            type="success"
            :icon="Download"
            :loading="exporting"
            @click="onExportExcel"
          >
            {{ exporting ? $t('dashboard.exporting') : $t('dashboard.exportExcel') }}
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- Row 1: Revenue cards -->
    <!-- 接送专员只看到接送营收一张卡 -->
    <el-row :gutter="16">
      <el-col v-if="!isTransferOps" :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card stat-card--compact">
          <div class="stat-icon" style="background:#f0f5ff">
            <el-icon :size="22" color="#4a7cf7"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value total">¥{{ formatNum(analytics.total_revenue) }}</p>
            <p class="stat-title">{{ $t('dashboard.totalRevenue') }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="!isTransferOps" :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card stat-card--compact">
          <div class="stat-icon" style="background:#f6ffed">
            <el-icon :size="22" color="#52c41a"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">¥{{ formatNum(analytics.shop_total) }}</p>
            <p class="stat-title">{{ $t('dashboard.shopRevenue') }}（{{ analytics.shop_count }} {{ $t('dashboard.orders') }}）</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card stat-card--compact">
          <div class="stat-icon" style="background:#fff7e6">
            <el-icon :size="22" color="#fa8c16"><Van /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">¥{{ formatNum(analytics.transfer_total) }}</p>
            <p class="stat-title">{{ $t('dashboard.transferRevenue') }}（{{ analytics.transfer_count }} {{ $t('dashboard.orders') }}）</p>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="!isTransferOps" :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card stat-card--compact">
          <div class="stat-icon" style="background:#fff1f0">
            <el-icon :size="22" color="#eb6f5c"><Ticket /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">¥{{ formatNum(analytics.ticket_total) }}</p>
            <p class="stat-title">{{ $t('dashboard.ticketRevenue') }}（{{ analytics.ticket_count }} {{ $t('dashboard.orders') }}）</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 2: Count cards (按角色过滤) -->
    <div class="count-row">
      <div class="count-cell" v-for="card in visibleCountCards" :key="card.key">
        <el-card shadow="hover" class="stat-card stat-card--compact" @click="card.go && router.push(card.go)" :class="{ clickable: card.go }">
          <div class="stat-icon" :style="{ background: card.bg }">
            <el-icon :size="22" :color="card.iconColor"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-value">{{ card.value }}</p>
            <p class="stat-title">{{ $t(`dashboard.${card.key}`) }}</p>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Pending orders (按角色显示不同列) -->
    <el-row :gutter="16" style="margin-top:20px">
      <el-col v-if="!isTransferOps" :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="pending-card">
          <template #header>{{ $t('dashboard.recentShopOrders') }}</template>
          <el-table :data="recentShopOrders" size="small" stripe height="280">
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" min-width="140">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push('/orders/shop')">{{ row.order_no }}</el-button>
              </template>
            </el-table-column>
            <el-table-column prop="contact_name" :label="$t('dashboard.customer')" width="90" />
            <el-table-column :label="$t('dashboard.total')" width="80">
              <template #default="{ row }">¥{{ row.total_price }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="isTransferOps ? 24 : 6">
        <el-card shadow="hover" class="pending-card">
          <template #header>{{ $t('dashboard.recentTransferOrders') }}</template>
          <el-table :data="recentTransferOrders" size="small" stripe height="280">
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" min-width="140">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push('/orders/transfer')">{{ row.order_no }}</el-button>
              </template>
            </el-table-column>
            <el-table-column prop="contact_name" :label="$t('dashboard.customer')" width="90" />
            <el-table-column prop="service_type" :label="$t('dashboard.type')" width="80" />
          </el-table>
        </el-card>
      </el-col>

      <el-col v-if="!isTransferOps" :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="pending-card">
          <template #header>{{ $t('dashboard.recentTicketOrders') }}</template>
          <el-table :data="recentTicketOrders" size="small" stripe height="280">
            <el-table-column prop="order_no" :label="$t('dashboard.orderNo')" min-width="140">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push('/tickets/orders')">{{ row.order_no }}</el-button>
              </template>
            </el-table-column>
            <el-table-column prop="contact_name" :label="$t('dashboard.customer')" width="90" />
            <el-table-column :label="$t('dashboard.total')" width="80">
              <template #default="{ row }">¥{{ row.total_price }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col v-if="!isTransferOps" :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="pending-card">
          <template #header>{{ $t('dashboard.recentWishes') }}</template>
          <el-table :data="recentWishes" size="small" stripe height="280">
            <el-table-column prop="contact_name" :label="$t('dashboard.customer')" width="90">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push('/wishes')">{{ row.contact_name }}</el-button>
              </template>
            </el-table-column>
            <el-table-column prop="content" :label="$t('dashboard.wishContent')" min-width="160">
              <template #default="{ row }">
                <span class="wish-cell">{{ row.content }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Revenue trend chart -->
    <el-card shadow="hover" style="margin-top:20px">
      <template #header>
        <div class="chart-header">
          <span>{{ $t('dashboard.revenueTrend') }}</span>
          <span class="chart-hint">{{ $t('dashboard.excludeCancelled') }}</span>
        </div>
      </template>
      <v-chart :option="chartOption" style="height:360px" autoresize />
    </el-card>

    <!-- Top selling products -->
    <el-card shadow="hover" style="margin-top:20px" v-if="topProducts.length">
      <template #header>{{ $t('dashboard.topProducts') }}</template>
      <el-table :data="topProducts" size="small" stripe>
        <el-table-column type="index" width="50" label="#" />
        <el-table-column prop="product_name" :label="$t('dashboard.productName')" />
        <el-table-column prop="total_qty" :label="$t('dashboard.totalSales')" width="120" />
        <el-table-column :label="$t('dashboard.totalSalesAmount')" width="140">
          <template #default="{ row }">¥{{ formatNum(row.total_revenue) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, markRaw, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ShoppingCart, Van, TrendCharts, Goods, Ticket, ChatLineRound, Download } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import http, { getShopOrders, getTransferOrders, getProducts, getAnalytics, getTopProducts, getWishes } from '../api'
import { getTicketOrders } from '../api/tickets'
import { useAuthStore } from '../stores/auth'
import { ROLE_TRANSFER_OPS } from '../utils/permissions'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const isTransferOps = computed(() => auth.user?.role === ROLE_TRANSFER_OPS)

use([BarChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()
const { t } = useI18n()

const period = ref('month')
const analytics = ref({
  shop_count: 0, shop_total: 0,
  transfer_count: 0, transfer_total: 0,
  ticket_count: 0, ticket_total: 0,
  total_revenue: 0,
  chart: { labels: [], shop: [], transfer: [], ticket: [] }
})

const countCards = ref([
  { key: 'products',       value: '-', icon: markRaw(Goods),         bg: '#e6f7ff', iconColor: '#1890ff', go: '/products' },
  { key: 'shopOrders',     value: '-', icon: markRaw(ShoppingCart),  bg: '#f6ffed', iconColor: '#52c41a', go: '/orders/shop' },
  { key: 'transferOrders', value: '-', icon: markRaw(Van),           bg: '#fff7e6', iconColor: '#fa8c16', go: '/orders/transfer' },
  { key: 'ticketOrders',   value: '-', icon: markRaw(Ticket),        bg: '#fff1f0', iconColor: '#eb6f5c', go: '/tickets/orders' },
  { key: 'pendingWishes',  value: '-', icon: markRaw(ChatLineRound), bg: '#f9f0ff', iconColor: '#9254de', go: '/wishes' },
])

// 接送专员只看到"接送订单"这一张计数卡
const visibleCountCards = computed(() =>
  isTransferOps.value
    ? countCards.value.filter(c => c.key === 'transferOrders')
    : countCards.value
)

const recentShopOrders = ref([])
const recentTransferOrders = ref([])
const recentTicketOrders = ref([])
const recentWishes = ref([])
const topProducts = ref([])

// ===== Excel 导出 =====
const exporting = ref(false)
const exportPaidOnly = ref(false)   // ☑ 仅已支付（财务对账常用）

async function onExportExcel() {
  if (exporting.value) return
  exporting.value = true
  try {
    // 用 axios 拉 blob，自动带上 JWT（http 实例会注入 Authorization 头）
    const res = await http.get('/admin/analytics/export', {
      params: {
        period: period.value,
        paid_only: exportPaidOnly.value ? 1 : 0,
      },
      responseType: 'blob',
    })

    // 解析后端返回的 filename（在 Content-Disposition 头里）
    let filename = `report_${period.value}_${Date.now()}.xlsx`
    const cd = res.headers?.['content-disposition'] || ''
    const match = cd.match(/filename\*?=(?:UTF-8'')?["']?([^"';]+)/i)
    if (match) {
      filename = decodeURIComponent(match[1])
    }

    // 触发浏览器下载
    const blob = new Blob([res.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Export failed:', e)
    ElMessage.error(e?.response?.data?.message || 'Export failed')
  } finally {
    exporting.value = false
  }
}

const statusTypes = { 0: 'warning', 1: 'primary', 2: '', 3: 'success', 4: 'info' }
const statusLabel = s => t(`orders.${['pending','confirmed','delivering','completed','cancelled'][s] || 'unknown'}`)
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
    legend: {
      data: [t('dashboard.shopLabel'), t('dashboard.transferLabel'), t('dashboard.ticketLabel')],
      top: 0,
    },
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
        itemStyle: { color: '#52c41a' }
      },
      {
        name: t('dashboard.transferLabel'),
        type: 'bar',
        stack: 'revenue',
        data: c.transfer,
        itemStyle: { color: '#fa8c16' }
      },
      {
        name: t('dashboard.ticketLabel'),
        type: 'bar',
        stack: 'revenue',
        data: c.ticket || [],
        itemStyle: { color: '#eb6f5c', borderRadius: [4, 4, 0, 0] }
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
    // 接送专员只能调接送订单接口
    if (isTransferOps.value) {
      const transRes = await getTransferOrders({ page: 1, per_page: 1 })
      countCards.value[2].value = transRes.data?.total ?? 0
      return
    }

    const [prodRes, shopRes, transRes, ticketRes, wishRes] = await Promise.all([
      getProducts({ page: 1, per_page: 1 }),
      getShopOrders({ page: 1, per_page: 1 }),
      getTransferOrders({ page: 1, per_page: 1 }),
      getTicketOrders({ page: 1, per_page: 1 }),
      getWishes({ page: 1, per_page: 1, status: 0 })  // 只统计待处理的许愿
    ])
    countCards.value[0].value = prodRes.data?.total ?? prodRes.data?.length ?? 0
    countCards.value[1].value = shopRes.data?.total ?? 0
    countCards.value[2].value = transRes.data?.total ?? 0
    countCards.value[3].value = ticketRes.data?.total ?? 0
    countCards.value[4].value = wishRes.data?.total ?? 0
  } catch (e) {
    console.error('Count cards load error:', e)
  }
}

async function loadRecentOrders() {
  try {
    if (isTransferOps.value) {
      // 接送专员只拉接送订单
      const transRes = await getTransferOrders({ page: 1, per_page: 10, status: 0 })
      recentTransferOrders.value = transRes.data?.list || transRes.data?.items || []
      return
    }

    const [shopRes, transRes, ticketRes, wishRes] = await Promise.all([
      getShopOrders({ page: 1, per_page: 10, status: 0 }),
      getTransferOrders({ page: 1, per_page: 10, status: 0 }),
      getTicketOrders({ page: 1, per_page: 10, status: 0 }),
      getWishes({ page: 1, per_page: 10, status: 0 })
    ])
    recentShopOrders.value = shopRes.data?.list || shopRes.data?.items || []
    recentTransferOrders.value = transRes.data?.list || transRes.data?.items || []
    recentTicketOrders.value = ticketRes.data?.list || ticketRes.data?.items || []
    recentWishes.value = wishRes.data?.list || wishRes.data?.items || []
  } catch (e) {
    console.error('Recent orders load error:', e)
  }
}

async function loadTopProducts() {
  if (isTransferOps.value) return  // 接送专员看不到商品销售榜
  try {
    const res = await getTopProducts({ limit: 10 })
    topProducts.value = res.data || []
  } catch (e) {
    console.error('Top products load error:', e)
  }
}

onMounted(() => {
  loadAnalytics()
  loadCounts()
  loadRecentOrders()
  loadTopProducts()
})
</script>

<style scoped>
.period-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.period-bar__right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-card { display: flex; align-items: center; }
.stat-card :deep(.el-card__body) { display: flex; align-items: center; gap: 12px; width: 100%; padding: 14px 16px; }

/* 紧凑版：节省垂直空间，所有数据卡可在 1-2 行容纳 */
.stat-card--compact .stat-icon { width: 44px; height: 44px; border-radius: 10px; }
.stat-card--compact .stat-value { font-size: 20px; }
.stat-card--compact .stat-value.total { font-size: 22px; color: #4a7cf7; }
.stat-card--compact .stat-title { font-size: 12px; margin-top: 3px; }

.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-size: 24px; font-weight: 700; color: #4a3728; line-height: 1; }
.stat-value.total { font-size: 28px; color: #4a7cf7; }
.stat-title { font-size: 13px; color: #8a7b6b; margin-top: 4px; }

.clickable { cursor: pointer; transition: transform 0.15s ease; }
.clickable:hover { transform: translateY(-2px); }

/* Row 2 flex 等分：桌面端 5 等分 */
.count-row {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  flex-wrap: wrap;
}
.count-cell {
  flex: 1 1 calc(20% - 16px);
  min-width: 160px;
}

.pending-card :deep(.el-card__header) { padding: 12px 16px; font-size: 14px; font-weight: 600; }
.pending-card :deep(.el-card__body) { padding: 8px; }

.wish-cell {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 12px;
  line-height: 1.5;
  color: #555;
}

.chart-header { display: flex; justify-content: space-between; align-items: center; }
.chart-hint { font-size: 12px; color: #aaa; }

/* 小屏：5 列数据卡变成更合理的栅格 */
@media (max-width: 992px) {
  .stat-card--compact .stat-value { font-size: 18px; }
  .stat-card--compact .stat-value.total { font-size: 20px; }
}
</style>
