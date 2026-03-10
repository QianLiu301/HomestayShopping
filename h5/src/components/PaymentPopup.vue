<template>
  <van-overlay :show="show" @click="onClickOverlay" z-index="1000">
    <div class="payment-popup" @click.stop>
      <div class="popup-header">
        <h3>{{ t('payment.title') }}</h3>
        <van-icon name="cross" size="20" class="close-btn" @click="onCancel" />
      </div>

      <div class="amount-display">
        <span class="amount-label">{{ t('payment.amountToPay') }}</span>
        <span class="amount-value">¥{{ amount }}</span>
      </div>

      <!-- Payment method tabs -->
      <div class="method-tabs">
        <div
          v-if="method === 'wechat' || method === 'alipay'"
          class="method-tab active"
          :class="method"
        >
          <van-icon :name="method === 'wechat' ? 'chat-o' : 'balance-o'" size="18" />
          <span>{{ method === 'wechat' ? t('checkout.wechat') : t('checkout.alipay') }}</span>
        </div>
      </div>

      <!-- QR Code display -->
      <div class="qr-section">
        <div v-if="loading" class="qr-loading">
          <van-loading size="24" />
        </div>
        <div v-else-if="qrUrl" class="qr-container">
          <img :src="qrUrl" class="qr-image" :alt="method === 'wechat' ? 'WeChat Pay' : 'Alipay'" />
        </div>
        <div v-else class="qr-empty">
          <van-icon name="photo-o" size="48" color="#ccc" />
          <p>{{ t('payment.qrNotSet') }}</p>
        </div>
        <p class="scan-tip">{{ t('payment.scanTip') }}</p>
      </div>

      <!-- Action buttons -->
      <div class="popup-actions">
        <van-button
          round
          block
          type="success"
          size="large"
          :loading="confirming"
          @click="onConfirmPaid"
        >
          {{ t('payment.confirmPaid') }}
        </van-button>
        <van-button
          round
          block
          plain
          size="large"
          style="margin-top: 10px"
          @click="onCancel"
        >
          {{ t('payment.cancelOrder') }}
        </van-button>
      </div>
    </div>
  </van-overlay>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getPaymentQRCodes, confirmPaid } from '../api'

const { t } = useI18n()

const props = defineProps({
  show: { type: Boolean, default: false },
  method: { type: String, default: 'wechat' },
  amount: { type: [String, Number], default: '0' },
  orderNo: { type: String, default: '' }
})

const emit = defineEmits(['update:show', 'paid', 'cancel'])

const loading = ref(false)
const confirming = ref(false)
const wechatQr = ref('')
const alipayQr = ref('')

const qrUrl = computed(() => {
  if (props.method === 'wechat') return wechatQr.value
  if (props.method === 'alipay') return alipayQr.value
  return ''
})

watch(() => props.show, async (val) => {
  if (val && !wechatQr.value && !alipayQr.value) {
    loading.value = true
    try {
      const res = await getPaymentQRCodes()
      console.log('PaymentQRCodes API response:', JSON.stringify(res))
      wechatQr.value = res.data?.wechat_qr_url || ''
      alipayQr.value = res.data?.alipay_qr_url || ''
      console.log('QR URLs - wechat:', wechatQr.value, 'alipay:', alipayQr.value)
    } catch (e) {
      console.error('Failed to load QR codes', e)
    } finally {
      loading.value = false
    }
  }
}, { immediate: true })

function onClickOverlay() {
  // don't close on overlay click
}

async function onConfirmPaid() {
  if (!props.orderNo) return
  confirming.value = true
  try {
    await confirmPaid({ order_no: props.orderNo })
    emit('paid')
    emit('update:show', false)
  } catch (e) {
    console.error(e)
  } finally {
    confirming.value = false
  }
}

function onCancel() {
  emit('cancel')
  emit('update:show', false)
}
</script>

<style scoped>
.payment-popup {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 16px 16px 0 0;
  padding: 20px 20px calc(env(safe-area-inset-bottom, 0px) + 16px);
  max-height: 90vh;
  overflow-y: auto;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.popup-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  cursor: pointer;
  padding: 4px;
  color: #999;
}

.amount-display {
  text-align: center;
  padding: 16px 0;
  border-top: 1px solid #f5f5f5;
  border-bottom: 1px solid #f5f5f5;
}

.amount-label {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.amount-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
}

.method-tabs {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px;
}

.method-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.method-tab.wechat {
  background: #f0faf0;
  color: #07c160;
}

.method-tab.alipay {
  background: #f0f5ff;
  color: #1677ff;
}

.qr-section {
  text-align: center;
  padding: 16px 0;
}

.qr-loading {
  padding: 40px 0;
}

.qr-container {
  display: inline-block;
  padding: 12px;
  background: #fff;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
}

.qr-image {
  width: 200px;
  height: 200px;
  object-fit: contain;
  display: block;
}

.qr-empty {
  padding: 30px 0;
  color: #999;
  font-size: 13px;
}

.qr-empty p {
  margin-top: 8px;
}

.scan-tip {
  margin-top: 12px;
  font-size: 13px;
  color: #999;
}

.popup-actions {
  padding-top: 16px;
}
</style>
