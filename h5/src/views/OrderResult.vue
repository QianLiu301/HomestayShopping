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

      <p class="result-tips">{{ t('order.tips') }}</p>

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

const { t } = useI18n()
const route = useRoute()

const orderNo = route.query.orderNo || ''
const amount = route.query.amount || '0'
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

.result-tips {
  font-size: 13px;
  color: var(--text-light);
  line-height: 1.6;
  margin-bottom: 30px;
  padding: 0 8px;
}

.result-actions {
  max-width: 280px;
  margin: 0 auto;
}
</style>
