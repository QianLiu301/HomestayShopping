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
        <div class="contact-methods">
          <div class="contact-item">
            <van-icon name="chat-o" size="20" color="#07c160" />
            <div class="contact-detail">
              <span class="contact-label">{{ t('order.wechatLabel') }}</span>
              <span class="contact-value">homestay_shanghai</span>
            </div>
            <van-button size="mini" plain type="success" @click="copyText('homestay_shanghai')">{{ t('order.copy') }}</van-button>
          </div>
          <div class="contact-item">
            <van-icon name="phone-o" size="20" color="#1a73e8" />
            <div class="contact-detail">
              <span class="contact-label">{{ t('order.phoneLabel') }}</span>
              <span class="contact-value">+86 138-0000-0000</span>
            </div>
            <van-button size="mini" plain type="primary" @click="copyText('+8613800000000')">{{ t('order.copy') }}</van-button>
          </div>
          <div class="contact-item">
            <van-icon name="envelop-o" size="20" color="#e6a23c" />
            <div class="contact-detail">
              <span class="contact-label">{{ t('order.emailLabel') }}</span>
              <span class="contact-value">info@homestay.com</span>
            </div>
            <van-button size="mini" plain type="warning" @click="copyText('info@homestay.com')">{{ t('order.copy') }}</van-button>
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
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'

const { t } = useI18n()
const route = useRoute()

const orderNo = route.query.orderNo || ''
const amount = route.query.amount || '0'

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
