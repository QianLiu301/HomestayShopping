<template>
  <div class="page-container">
    <van-nav-bar :title="t('order.success')" />

    <div class="result-content">
      <div class="success-icon">
        <van-icon name="checked" size="64" color="#07c160" />
      </div>

      <h2 class="result-title">{{ t('order.success') }}</h2>

      <div class="result-card">
        <div class="result-row">
          <span class="result-label">{{ t('order.orderNo') }}</span>
          <span class="result-value order-no">{{ orderNo }}</span>
        </div>
        <div class="result-row">
          <span class="result-label">{{ t('order.amount') }}</span>
          <span class="result-value amount">¥{{ amount }}</span>
        </div>
        <div class="result-row">
          <span class="result-label">{{ t('order.status') }}</span>
          <span class="result-value">{{ t('order.statusMap.0') }}</span>
        </div>
      </div>

      <!-- Contact to pay -->
      <div class="contact-card">
        <div class="contact-header">
          <span class="contact-icon">📱</span>
          <span class="contact-title">{{ t('order.contactToPayTitle') }}</span>
        </div>
        <p class="contact-tip">{{ t('order.contactToPayTip') }}</p>

        <div v-if="contactLoading" style="text-align:center;padding:20px">
          <van-loading size="20" />
        </div>

        <div v-else class="contact-methods">
          <!-- WeChat -->
          <div v-if="contactInfo.contact_wechat_id" class="contact-item">
            <van-icon name="chat-o" size="20" color="#07c160" />
            <div class="contact-detail">
              <span class="contact-label">{{ t('order.wechatLabel') }}</span>
              <span class="contact-value">{{ contactInfo.contact_wechat_id }}</span>
            </div>
            <van-button size="mini" plain type="success" @click="copyText(contactInfo.contact_wechat_id)">{{ t('order.copy') }}</van-button>
          </div>
          <!-- WeChat QR -->
          <div v-if="contactInfo.contact_wechat_qr" class="contact-qr">
            <img :src="contactInfo.contact_wechat_qr" class="qr-image" :alt="t('order.wechatLabel')" />
          </div>

          <!-- WhatsApp -->
          <div v-if="contactInfo.contact_whatsapp" class="contact-item">
            <van-icon name="phone-o" size="20" color="#25d366" />
            <div class="contact-detail">
              <span class="contact-label">WhatsApp</span>
              <span class="contact-value">{{ contactInfo.contact_whatsapp }}</span>
            </div>
            <van-button size="mini" plain type="success" @click="copyText(contactInfo.contact_whatsapp)">{{ t('order.copy') }}</van-button>
          </div>
          <!-- WhatsApp QR -->
          <div v-if="contactInfo.contact_whatsapp_qr" class="contact-qr">
            <img :src="contactInfo.contact_whatsapp_qr" class="qr-image" :alt="'WhatsApp'" />
          </div>

          <!-- Fallback if nothing configured -->
          <div v-if="!contactInfo.contact_wechat_id && !contactInfo.contact_whatsapp" class="contact-empty">
            {{ t('order.contactNotSet') }}
          </div>
        </div>

        <p class="contact-note">{{ t('order.contactNote', { orderNo }) }}</p>
      </div>

      <div class="result-actions">
        <van-button round block type="primary" @click="$router.replace('/')">
          {{ t('order.backHome') }}
        </van-button>
        <van-button round block plain type="primary" @click="$router.replace('/shop')" style="margin-top: 10px;">
          {{ t('order.continueShopping') }}
        </van-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getContactInfo } from '../api'

const { t } = useI18n()
const route = useRoute()

const orderNo = route.query.orderNo || ''
const amount = route.query.amount || '0'

const contactLoading = ref(true)
const contactInfo = ref({
  contact_wechat_id: '',
  contact_whatsapp: '',
  contact_wechat_qr: '',
  contact_whatsapp_qr: ''
})

onMounted(async () => {
  try {
    const res = await getContactInfo()
    if (res.data) {
      contactInfo.value = res.data
    }
  } catch (e) {
    console.error('Failed to load contact info', e)
  } finally {
    contactLoading.value = false
  }
})

function copyText(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(t('order.copied'))
    }).catch(() => {
      fallbackCopy(text)
    })
  } else {
    fallbackCopy(text)
  }
}

function fallbackCopy(text) {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  try {
    document.execCommand('copy')
    showToast(t('order.copied'))
  } catch {
    showToast(t('order.copyFailed'))
  }
  document.body.removeChild(textarea)
}
</script>

<style scoped>
.result-content {
  text-align: center;
  padding: 40px 24px;
}

.success-icon {
  margin-bottom: 16px;
}

.result-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 24px;
}

.result-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 20px;
  text-align: left;
}

.result-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.result-row:last-child {
  border-bottom: none;
}

.result-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.result-value {
  font-size: 14px;
  font-weight: 500;
}

.order-no {
  font-family: monospace;
  letter-spacing: 0.5px;
}

.amount {
  color: var(--accent);
  font-size: 18px;
  font-weight: 700;
}

.contact-card {
  background: #fff7f0;
  border: 1px solid #ffe0c2;
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 24px;
  text-align: left;
}

.contact-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.contact-icon {
  font-size: 22px;
}

.contact-title {
  font-size: 16px;
  font-weight: 700;
  color: #d4710a;
}

.contact-tip {
  font-size: 13px;
  color: #a0522d;
  margin: 0 0 16px;
  line-height: 1.5;
}

.contact-methods {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff;
  border-radius: 10px;
  padding: 12px;
}

.contact-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.contact-label {
  font-size: 12px;
  color: #999;
}

.contact-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  word-break: break-all;
}

.contact-qr {
  display: flex;
  justify-content: center;
  padding: 8px;
  background: #fff;
  border-radius: 10px;
}

.qr-image {
  width: 180px;
  height: 180px;
  object-fit: contain;
  border-radius: 8px;
}

.contact-empty {
  text-align: center;
  padding: 16px;
  color: #999;
  font-size: 13px;
}

.contact-note {
  font-size: 12px;
  color: #a0522d;
  margin: 14px 0 0;
  padding: 10px;
  background: rgba(255,255,255,0.6);
  border-radius: 8px;
  line-height: 1.5;
}

.result-actions {
  max-width: 280px;
  margin: 0 auto;
}
</style>
