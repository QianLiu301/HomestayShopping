<template>
  <div class="page-container page-with-tabbar">
    <van-nav-bar :title="t('order.queryTitle')" />

    <!-- Search form -->
    <div class="card">
      <van-field
        v-model="orderNo"
        :label="t('order.orderNo')"
        :placeholder="t('order.inputOrderNo')"
        clearable
      />
      <van-field
        v-model="contact"
        :label="t('checkout.contact')"
        :placeholder="t('order.inputContact')"
        clearable
      />
      <div style="padding: 12px 0 4px;">
        <van-button round block type="primary" :loading="loading" @click="onQuery">
          {{ t('order.query') }}
        </van-button>
      </div>
    </div>

    <!-- Result -->
    <template v-if="result">
      <div class="card">
        <div class="order-type-tag" :class="result.type">
          {{ t(`order.type.${result.type}`) }}
        </div>

        <div class="order-detail">
          <div class="detail-row">
            <span>{{ t('order.orderNo') }}</span>
            <span class="mono">{{ result.order.order_no }}</span>
          </div>
          <div class="detail-row">
            <span>{{ t('order.status') }}</span>
            <van-tag :type="statusTagType(result.order.status)" size="medium">
              {{ t(`order.statusMap.${result.order.status}`) }}
            </van-tag>
          </div>
          <div class="detail-row">
            <span>{{ t('order.amount') }}</span>
            <span class="amount">¥{{ result.order.total_price }}</span>
          </div>

          <!-- Transfer specific -->
          <template v-if="result.type === 'transfer'">
            <div v-if="result.order.service_type" class="detail-row">
              <span>{{ t('transfer.title') }}</span>
              <span>{{ t(`transfer.${result.order.service_type}`) }}</span>
            </div>
            <div v-if="result.order.flight_no" class="detail-row">
              <span>{{ t('transfer.flightNo') }}</span>
              <span>{{ result.order.flight_no }}</span>
            </div>
            <div v-if="result.order.vehicle" class="detail-row">
              <span>{{ t('transfer.selectVehicle') }}</span>
              <span>{{ result.order.vehicle.name }}</span>
            </div>
          </template>

          <!-- Shop specific -->
          <template v-if="result.type === 'shop' && result.order.items?.length">
            <div class="items-section">
              <div v-for="item in result.order.items" :key="item.id" class="query-item">
                <span class="qi-name">{{ item.product_name }}</span>
                <span class="qi-qty">x{{ item.quantity }}</span>
                <span class="qi-price">¥{{ item.subtotal }}</span>
              </div>
            </div>
          </template>

          <div class="detail-row">
            <span>{{ t('transfer.contactName') }}</span>
            <span>{{ result.order.contact_name }}</span>
          </div>
          <div v-if="result.order.created_at" class="detail-row">
            <span>{{ t('common.home') }}</span>
            <span>{{ formatTime(result.order.created_at) }}</span>
          </div>
        </div>
      </div>
    </template>

    <van-empty v-if="searched && !result" :description="t('common.noData')" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { queryOrder } from '../api'

const { t } = useI18n()
const route = useRoute()

const orderNo = ref('')
const contact = ref('')
const loading = ref(false)
const result = ref(null)
const searched = ref(false)

function statusTagType(status) {
  const map = { 0: 'warning', 1: 'primary', 2: 'primary', 3: 'success', 4: 'default' }
  return map[status] || 'default'
}

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function onQuery() {
  if (!orderNo.value || !contact.value) {
    return showToast(t('order.inputOrderNo'))
  }

  loading.value = true
  searched.value = true
  result.value = null

  try {
    const res = await queryOrder({
      order_no: orderNo.value.trim(),
      contact: contact.value.trim()
    })
    result.value = res.data
  } catch (e) {
    showToast(e.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // If navigated from home page with pre-fetched data
  if (route.query.data) {
    try {
      result.value = JSON.parse(route.query.data)
      searched.value = true
      // Pre-fill form fields from the result
      if (result.value?.order) {
        orderNo.value = result.value.order.order_no || ''
        contact.value = result.value.order.contact_email || result.value.order.contact_phone || ''
      }
    } catch (e) {
      console.error('Failed to parse query data', e)
    }
  }
  // If navigated with orderNo and contact as query params
  if (route.query.orderNo) orderNo.value = route.query.orderNo
  if (route.query.contact) contact.value = route.query.contact
})
</script>

<style scoped>
.order-type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 12px;
}

.order-type-tag.shop {
  background: #e8f0fe;
  color: #1a73e8;
}

.order-type-tag.transfer {
  background: #fff7f0;
  color: #ff6b35;
}

.order-detail {
  display: flex;
  flex-direction: column;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row span:first-child {
  color: var(--text-secondary);
}

.mono {
  font-family: monospace;
  letter-spacing: 0.5px;
}

.amount {
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
}

.items-section {
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.query-item {
  display: flex;
  padding: 6px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.qi-name {
  flex: 1;
}

.qi-qty {
  width: 40px;
  text-align: center;
}

.qi-price {
  width: 60px;
  text-align: right;
  color: var(--text);
}
</style>
