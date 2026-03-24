<template>
  <van-overlay :show="show" @click="onClickOverlay" z-index="1000">
    <div class="payment-popup" @click.stop>
      <div class="popup-header">
        <h3>{{ t('payment.title') }}</h3>
        <van-icon name="cross" size="20" class="close-btn" @click="onCancel" />
      </div>

      <!-- Step 1: Scan QR -->
      <template v-if="step === 1">
        <div class="amount-display">
          <span class="amount-label">{{ t('payment.amountToPay') }}</span>
          <span class="amount-value">¥{{ amount }}</span>
        </div>

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

        <div class="qr-section">
          <div v-if="loading" class="qr-loading">
            <van-loading size="24" />
          </div>
          <div v-else-if="qrUrl" class="qr-container">
            <img :src="$resolveUrl(qrUrl)" class="qr-image" :alt="method === 'wechat' ? 'WeChat Pay' : 'Alipay'" />
          </div>
          <div v-else class="qr-empty">
            <van-icon name="photo-o" size="48" color="#ccc" />
            <p>{{ t('payment.qrNotSet') }}</p>
          </div>
          <p class="scan-tip">{{ t('payment.scanTip') }}</p>
          <p class="scan-tip" style="color:#e8a87c;font-weight:500">{{ t('payment.remarkTip') }}</p>
        </div>

        <div class="popup-actions">
          <van-button round block type="success" size="large" @click="step = 2">
            {{ t('payment.nextStepProof') }}
          </van-button>
          <van-button round block plain size="large" style="margin-top: 10px" @click="onCancel">
            {{ t('payment.cancelOrder') }}
          </van-button>
        </div>
      </template>

      <!-- Step 2: Upload proof -->
      <template v-if="step === 2">
        <div class="proof-section">
          <p class="proof-title">{{ t('payment.proofTitle') }}</p>
          <p class="proof-subtitle">{{ t('payment.proofSubtitle') }}</p>

          <!-- Toggle: screenshot vs transaction ID -->
          <div class="proof-tabs">
            <div class="proof-tab" :class="{ active: proofType === 'screenshot' }" @click="proofType = 'screenshot'">
              {{ t('payment.uploadScreenshot') }}
            </div>
            <div class="proof-tab" :class="{ active: proofType === 'txid' }" @click="proofType = 'txid'">
              {{ t('payment.inputTxId') }}
            </div>
          </div>

          <!-- Screenshot upload -->
          <div v-if="proofType === 'screenshot'" class="upload-area">
            <div v-if="screenshotUrl" class="screenshot-preview">
              <img :src="screenshotUrl" />
              <van-icon name="close" class="remove-btn" @click="screenshotUrl = ''" />
            </div>
            <div v-else class="upload-placeholder" @click="triggerUpload">
              <van-icon name="photograph" size="36" color="#ccc" />
              <span>{{ t('payment.clickUpload') }}</span>
              <van-loading v-if="uploading" size="20" style="margin-top:8px" />
            </div>
            <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFileChange" />
          </div>

          <!-- Transaction ID input -->
          <div v-if="proofType === 'txid'" class="txid-area">
            <van-field
              v-model="transactionId"
              :placeholder="t('payment.txIdPlaceholder')"
              clearable
              maxlength="64"
            />
          </div>
        </div>

        <div class="popup-actions">
          <van-button
            round block type="success" size="large"
            :loading="confirming"
            :disabled="!proofValid"
            @click="onConfirmPaid"
          >
            {{ t('payment.confirmPaid') }}
          </van-button>
          <van-button round block plain size="large" style="margin-top: 10px" @click="step = 1">
            {{ t('common.back') }}
          </van-button>
        </div>
      </template>
    </div>
  </van-overlay>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getPaymentQRCodes, confirmPaid, uploadFile } from '../api'

const { t } = useI18n()

const props = defineProps({
  show: { type: Boolean, default: false },
  method: { type: String, default: 'wechat' },
  amount: { type: [String, Number], default: '0' },
  orderNo: { type: String, default: '' }
})

const emit = defineEmits(['update:show', 'paid', 'cancel'])

const step = ref(1)
const loading = ref(false)
const confirming = ref(false)
const uploading = ref(false)
const wechatQr = ref('')
const alipayQr = ref('')

// Proof fields
const proofType = ref('screenshot')
const screenshotUrl = ref('')
const transactionId = ref('')
const fileInput = ref(null)

const qrUrl = computed(() => {
  if (props.method === 'wechat') return wechatQr.value
  if (props.method === 'alipay') return alipayQr.value
  return ''
})

const proofValid = computed(() => {
  if (proofType.value === 'screenshot') return !!screenshotUrl.value
  return !!transactionId.value.trim()
})

watch(() => props.show, async (val) => {
  if (val && !wechatQr.value && !alipayQr.value) {
    loading.value = true
    try {
      const res = await getPaymentQRCodes()
      wechatQr.value = res.data?.wechat_qr_url || ''
      alipayQr.value = res.data?.alipay_qr_url || ''
    } catch (e) {
      console.error('Failed to load QR codes', e)
    } finally {
      loading.value = false
    }
  }
  if (!val) {
    step.value = 1
    screenshotUrl.value = ''
    transactionId.value = ''
    proofType.value = 'screenshot'
  }
}, { immediate: true })

function onClickOverlay() {}

function triggerUpload() {
  fileInput.value?.click()
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const res = await uploadFile(file)
    screenshotUrl.value = res.data?.url || ''
  } catch (err) {
    showToast({ message: t('payment.uploadFailed'), position: 'top' })
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function onConfirmPaid() {
  if (!props.orderNo || !proofValid.value) return
  confirming.value = true

  const payload = { order_no: props.orderNo }
  if (proofType.value === 'screenshot') {
    payload.payment_screenshot = screenshotUrl.value
  } else {
    payload.transaction_id = transactionId.value.trim()
  }

  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      await confirmPaid(payload)
      emit('paid')
      emit('update:show', false)
      return
    } catch (e) {
      console.error(`confirmPaid attempt ${attempt} failed:`, e)
      if (attempt < 3) {
        await new Promise(r => setTimeout(r, 1000 * attempt))
      } else {
        showToast({ message: t('payment.confirmFailed'), position: 'top', duration: 3000 })
        emit('paid')
        emit('update:show', false)
      }
    }
  }
  confirming.value = false
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

/* Step 2 styles */
.proof-section {
  padding: 8px 0 16px;
}

.proof-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 4px;
}

.proof-subtitle {
  font-size: 13px;
  color: #999;
  margin: 0 0 16px;
}

.proof-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.proof-tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-size: 14px;
  cursor: pointer;
  background: #fafafa;
  color: #666;
  transition: all 0.2s;
}

.proof-tab.active {
  background: #8b6f47;
  color: #fff;
  font-weight: 500;
}

.upload-area {
  display: flex;
  justify-content: center;
}

.upload-placeholder {
  width: 100%;
  height: 140px;
  border: 2px dashed #d0d0d0;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #999;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-placeholder:active {
  border-color: #8b6f47;
}

.screenshot-preview {
  position: relative;
  width: 100%;
  max-height: 200px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #eee;
}

.screenshot-preview img {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  display: block;
}

.remove-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  background: rgba(0,0,0,0.5);
  color: #fff;
  border-radius: 50%;
  padding: 4px;
  font-size: 16px;
  cursor: pointer;
}

.txid-area {
  margin-bottom: 8px;
}
</style>
