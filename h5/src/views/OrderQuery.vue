<template>
  <div class="page-container page-with-tabbar">
    <van-nav-bar :title="t('order.queryTitle')" />

    <!-- Search form -->
    <div class="card">
      <van-field
        v-model="contact"
        :label="t('order.contactLabel')"
        :placeholder="t('order.inputContact')"
        clearable
        required
      />
      <van-field
        v-model="orderNo"
        :label="t('order.orderNo')"
        :placeholder="t('order.orderNoOptional')"
        clearable
      />
      <div style="padding: 12px 0 4px;">
        <van-button round block type="primary" :loading="loading" @click="onQuery">
          {{ t('order.query') }}
        </van-button>
      </div>
    </div>

    <!-- Error banner -->
    <div v-if="errorMsg" class="error-banner">
      <van-icon name="warning-o" size="18" />
      <span>{{ errorMsg }}</span>
    </div>

    <!-- Results list -->
    <template v-if="results.length">
      <div class="results-header">{{ t('order.foundOrders', { count: results.length }) }}</div>
      <div v-for="(item, idx) in results" :key="idx" class="card order-card" @click="toggleDetail(idx)">
        <div class="order-card-header">
          <span class="order-type-tag" :class="item.type">
            {{ t(`order.type.${item.type}`) }}
          </span>
          <van-tag :type="statusTagType(item.order.status)" size="medium">
            {{ t(`order.statusMap.${item.order.status}`) }}
          </van-tag>
        </div>

        <div class="order-card-main">
          <div class="order-card-no">{{ item.order.order_no }}</div>
          <div class="order-card-amount">¥{{ item.order.total_price }}</div>
        </div>

        <div class="order-card-meta">
          <span>{{ formatTime(item.order.created_at) }}</span>
          <van-tag :type="item.order.payment_status === 1 ? 'success' : 'warning'" size="small" plain>
            {{ t(`order.paymentStatus.${item.order.payment_status}`) }}
          </van-tag>
        </div>

        <!-- Expandable detail -->
        <div v-if="expandedIdx === idx" class="order-detail">
          <!-- Transfer specific -->
          <template v-if="item.type === 'transfer'">
            <div v-if="item.order.service_type" class="detail-row">
              <span>{{ t('transfer.title') }}</span>
              <span>{{ t(`transfer.${item.order.service_type}`) }}</span>
            </div>
            <div v-if="item.order.flight_no" class="detail-row">
              <span>{{ t('transfer.flightNo') }}</span>
              <span>{{ item.order.flight_no }}</span>
            </div>
            <div v-if="item.order.vehicle" class="detail-row">
              <span>{{ t('transfer.selectVehicle') }}</span>
              <span>{{ item.order.vehicle.name }}</span>
            </div>
          </template>

          <!-- Shop specific -->
          <template v-if="item.type === 'shop' && item.order.items?.length">
            <div class="items-section">
              <div v-for="si in item.order.items" :key="si.id" class="query-item">
                <span class="qi-name">{{ si.product_name }}</span>
                <span class="qi-qty">x{{ si.quantity }}</span>
                <span class="qi-price">¥{{ si.subtotal }}</span>
              </div>
            </div>
          </template>

          <div class="detail-row">
            <span>{{ t('order.contactLabel') }}</span>
            <span>{{ item.order.contact_name }}</span>
          </div>
          <div v-if="item.order.booking_no" class="detail-row">
            <span>{{ t('checkout.bookingNo') }}</span>
            <span>{{ item.order.booking_no }}</span>
          </div>
        </div>

        <div class="expand-hint">
          <van-icon :name="expandedIdx === idx ? 'arrow-up' : 'arrow-down'" size="14" />
        </div>
      </div>
    </template>

    <van-empty v-if="searched && !results.length && !errorMsg" :description="t('common.noData')" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { queryOrder } from '../api'

const { t } = useI18n()
const route = useRoute()

const orderNo = ref('')
const contact = ref('')
const loading = ref(false)
const results = ref([])
const searched = ref(false)
const errorMsg = ref('')
const expandedIdx = ref(-1)

function statusTagType(status) {
  const map = { 0: 'warning', 1: 'primary', 2: 'primary', 3: 'success', 4: 'default' }
  return map[status] || 'default'
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function toggleDetail(idx) {
  expandedIdx.value = expandedIdx.value === idx ? -1 : idx
}

async function onQuery() {
  if (!contact.value.trim()) {
    errorMsg.value = t('order.inputContact')
    setTimeout(() => { errorMsg.value = '' }, 3000)
    return
  }

  loading.value = true
  searched.value = true
  results.value = []
  errorMsg.value = ''
  expandedIdx.value = -1

  try {
    const payload = { contact: contact.value.trim() }
    if (orderNo.value.trim()) payload.order_no = orderNo.value.trim()
    const res = await queryOrder(payload)
    results.value = res.data?.orders || []
  } catch (e) {
    errorMsg.value = e.message || t('common.noData')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (route.query.orderNo) orderNo.value = route.query.orderNo
  if (route.query.contact) contact.value = route.query.contact
  // Auto-query if params provided
  if (contact.value) onQuery()
})
</script>

<style scoped>
.results-header {
  padding: 12px 16px 4px;
  font-size: 13px;
  color: var(--text-light);
}

.order-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.order-card:active {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.order-type-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.order-type-tag.shop {
  background: #e8f0fe;
  color: #1a73e8;
}

.order-type-tag.transfer {
  background: #fff7f0;
  color: #ff6b35;
}

.order-card-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.order-card-no {
  font-family: monospace;
  font-size: 13px;
  color: var(--text-secondary);
  letter-spacing: 0.3px;
}

.order-card-amount {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
}

.order-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-light);
}

.order-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px solid #f8f8f8;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row span:first-child {
  color: var(--text-secondary);
}

.items-section {
  padding: 4px 0;
  border-bottom: 1px solid #f8f8f8;
}

.query-item {
  display: flex;
  padding: 4px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.qi-name { flex: 1; }
.qi-qty { width: 40px; text-align: center; }
.qi-price { width: 60px; text-align: right; color: var(--text); }

.expand-hint {
  text-align: center;
  padding-top: 6px;
  color: var(--text-light);
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 16px;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  color: #ff4d4f;
  font-size: 14px;
  font-weight: 500;
}
</style>
