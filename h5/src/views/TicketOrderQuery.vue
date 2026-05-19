<template>
  <div class="page-container page-with-tabbar ticket-query-page">
    <van-nav-bar :title="t('tickets.queryTitle')">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <div class="query-hero">
      <div class="query-badge">{{ t('tickets.ticketOrder') }}</div>
      <h1 class="query-title">{{ t('tickets.queryTitle') }}</h1>
      <p class="query-subtitle">{{ t('tickets.querySubtitle') }}</p>
    </div>

    <div class="card query-form-card">
      <van-field
        v-model="orderNo"
        :label="t('tickets.orderNo')"
        :placeholder="t('tickets.orderNoPlaceholder')"
        clearable
      />
      <van-field
        v-model="contactName"
        :label="t('tickets.contactName')"
        :placeholder="t('tickets.contactNamePlaceholder')"
        clearable
      />
      <van-field
        v-model="contactEmail"
        :label="t('tickets.contactEmail')"
        :placeholder="t('tickets.contactEmailPlaceholder')"
        clearable
      />
      <div class="query-actions">
        <van-button round block type="primary" :loading="loading" @click="onQuery">
          {{ t('tickets.queryTicketOrder') }}
        </van-button>
      </div>
    </div>

    <div v-if="errorMsg" class="error-banner">
      <van-icon name="warning-o" size="18" />
      <span>{{ errorMsg }}</span>
    </div>

    <div v-if="result" class="card result-card">
      <div class="result-header">
        <div>
          <div class="result-name">{{ result.attraction?.name || '-' }}</div>
          <div class="result-order">{{ result.order_no }}</div>
        </div>
        <van-tag :type="statusTagType(result.status)">{{ statusLabel(result.status) }}</van-tag>
      </div>

      <div class="detail-row">
        <span>{{ t('tickets.package') }}</span>
        <span>{{ packageNames }}</span>
      </div>
      <div class="detail-row">
        <span>{{ t('tickets.visitDate') }}</span>
        <span>{{ result.visit_date || '-' }}</span>
      </div>
      <div class="detail-row">
        <span>{{ t('tickets.totalPrice') }}</span>
        <span>¥{{ result.total_price }}</span>
      </div>
      <div class="detail-row">
        <span>{{ t('tickets.paymentStatus') }}</span>
        <span>{{ result.payment_status === 1 ? t('tickets.paid') : t('tickets.unpaid') }}</span>
      </div>
      <div class="detail-row">
        <span>{{ t('tickets.contactName') }}</span>
        <span>{{ result.contact_name }}</span>
      </div>
      <div v-if="result.contact_phone" class="detail-row">
        <span>{{ t('tickets.contactPhone') }}</span>
        <span>{{ result.contact_phone }}</span>
      </div>
      <div v-if="result.contact_email" class="detail-row">
        <span>{{ t('tickets.contactEmail') }}</span>
        <span>{{ result.contact_email }}</span>
      </div>
      <div v-if="result.booking_no" class="detail-row">
        <span>{{ t('tickets.bookingNo') }}</span>
        <span>{{ result.booking_no }}</span>
      </div>
      <div v-if="result.need_transfer" class="detail-row">
        <span>{{ t('tickets.transfer') }}</span>
        <span>{{ transferText }}</span>
      </div>
      <div v-if="result.vouchers?.length" class="voucher-section">
        <div class="voucher-title">{{ t('tickets.vouchers') }}</div>
        <a
          v-for="item in result.vouchers"
          :key="item.id"
          class="voucher-link"
          :href="$resolveUrl(item.file_url)"
          target="_blank"
        >
          {{ item.file_name || item.file_url }}
        </a>
      </div>

      <div v-if="result.payment_status !== 1" class="payment-box">
        <div v-if="paymentProofSubmitted" class="payment-proof-banner">
          {{ t('tickets.paymentProofSubmitted') }}
        </div>
        <template v-else></template>
      </div>
    </div>

    <PaymentPopup
      v-model:show="showPaymentPopup"
      :method="paymentMethod"
      :amount="result?.total_price || 0"
      :order-no="result?.order_no || ''"
      @paid="onPaid"
    />

    <van-empty v-if="searched && !result && !errorMsg" :description="t('common.noData')" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { queryTicketOrders, getTicketOrder, confirmTicketPaid } from '../api/tickets'
import LangSwitch from '../components/LangSwitch.vue'
import PaymentPopup from '../components/PaymentPopup.vue'

const { t } = useI18n()
const route = useRoute()

const orderNo = ref('')
const contactName = ref('')
const contactEmail = ref('')
const loading = ref(false)
const searched = ref(false)
const errorMsg = ref('')
const result = ref(null)
const showPaymentPopup = ref(false)
const paymentMethod = ref('wechat')
const paymentProofSubmitted = ref(false)

const packageNames = computed(() => {
  const list = result.value?.package_snapshot || []
  return list.map(item => `${item.package_name} x${item.quantity}`).join(', ') || '-'
})

const transferText = computed(() => {
  if (!result.value?.need_transfer) return t('tickets.noTransfer')
  return result.value?.transfer_vehicle?.name || result.value?.transfer_vehicle?.name_zh || t('tickets.needTransfer')
})

function statusLabel(status) {
  const map = {
    0: t('tickets.pending'),
    1: t('tickets.confirmed'),
    2: t('tickets.completed'),
    3: t('tickets.cancelled')
  }
  return map[status] || t('tickets.unknown')
}

function statusTagType(status) {
  const map = { 0: 'warning', 1: 'primary', 2: 'success', 3: 'default' }
  return map[status] || 'default'
}

function openPayment(method) {
  paymentMethod.value = method
  showPaymentPopup.value = true
}

async function onPaid() {
  paymentProofSubmitted.value = true
  await onQuery()
}

async function onQuery() {
  loading.value = true
  searched.value = true
  result.value = null
  errorMsg.value = ''

  try {
    if (orderNo.value.trim()) {
      const res = await getTicketOrder(orderNo.value.trim())
      result.value = res.data || null
      paymentProofSubmitted.value = !!(result.value?.transaction_id || result.value?.payment_screenshot)
    } else if (contactName.value.trim() && contactEmail.value.trim()) {
      const res = await queryTicketOrders({
        contact_name: contactName.value.trim(),
        contact_email: contactEmail.value.trim()
      })
      result.value = res.data || null
      paymentProofSubmitted.value = !!(result.value?.transaction_id || result.value?.payment_screenshot)
    } else {
      throw new Error(t('tickets.queryValidation'))
    }
  } catch (error) {
    errorMsg.value = error.message || t('common.noData')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (route.query.orderNo) orderNo.value = String(route.query.orderNo)
  if (route.query.contactName) contactName.value = String(route.query.contactName)
  if (route.query.contactEmail) contactEmail.value = String(route.query.contactEmail)
  if (orderNo.value || (contactName.value && contactEmail.value)) onQuery()
})
</script>

<style scoped>
.ticket-query-page {
  padding-top: 0;
  padding-bottom: 76px;
}

.query-hero {
  margin: 12px 16px 0;
  padding: 24px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #3f2e20 0%, #73563d 100%);
  color: #fff;
}

.query-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.14);
  font-size: 12px;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.query-title {
  font-size: 26px;
  line-height: 1.2;
  margin-bottom: 8px;
}

.query-subtitle {
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255,255,255,0.74);
}

.query-form-card {
  margin-top: 14px;
}

.query-actions {
  padding-top: 12px;
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

.result-card {
  margin-top: 14px;
}

.result-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.result-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
}

.result-order {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  font-family: monospace;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 14px;
}

.detail-row span:first-child {
  color: var(--text-secondary);
}

.payment-box {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #f0f0f0;
}

.payment-box__title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text);
}

.payment-proof-banner {
  padding: 12px 14px;
  border-radius: 10px;
  background: #f0f9eb;
  color: #67c23a;
  font-size: 14px;
  font-weight: 600;
}

.voucher-section {
  margin-top: 14px;
}

.voucher-title {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 10px;
}

.voucher-link {
  display: block;
  color: var(--accent);
  text-decoration: underline;
  margin-bottom: 8px;
  word-break: break-all;
}
</style>
