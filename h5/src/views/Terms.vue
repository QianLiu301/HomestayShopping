<template>
  <div class="legal-page">
    <div class="legal-container">
      <button class="back-btn" @click="$router.back()">← {{ t('common.back') }}</button>
      <h1>{{ t('legal.termsTitle') }}</h1>
      <p class="update-date">{{ t('legal.lastUpdated') }}: 2026-03-12</p>

      <section>
        <h2>{{ t('legal.terms.acceptTitle') }}</h2>
        <p>{{ t('legal.terms.acceptContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.serviceTitle') }}</h2>
        <p>{{ t('legal.terms.serviceContent') }}</p>
        <ul>
          <li>{{ t('legal.terms.serviceTransfer') }}</li>
          <li>{{ t('legal.terms.serviceShop') }}</li>
        </ul>
      </section>

      <section>
        <h2>{{ t('legal.terms.orderTitle') }}</h2>
        <p>{{ t('legal.terms.orderContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.paymentTitle') }}</h2>
        <p>{{ t('legal.terms.paymentContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.cancelTitle') }}</h2>
        <p>{{ t('legal.terms.cancelTransfer') }}</p>
        <p>{{ t('legal.terms.cancelShop') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.liabilityTitle') }}</h2>
        <p>{{ t('legal.terms.liabilityFlight') }}</p>
        <p>{{ t('legal.terms.liabilityForce') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.disputeTitle') }}</h2>
        <p>{{ t('legal.terms.disputeContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.updateTitle') }}</h2>
        <p>{{ t('legal.terms.updateContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.terms.contactTitle') }}</h2>
        <p>{{ t('legal.terms.contactContent') }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<style scoped>
.legal-page { min-height: 100vh; background: var(--bg); padding: 80px 0 60px; }
.legal-container { max-width: 800px; margin: 0 auto; padding: 0 24px; }
.back-btn { background: none; border: none; color: var(--accent); font-size: 14px; cursor: pointer; padding: 8px 0; margin-bottom: 20px; font-family: var(--font-body); }
.back-btn:hover { text-decoration: underline; }
h1 { font-family: var(--font-display); font-size: 32px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
.update-date { font-size: 13px; color: var(--text-light); margin-bottom: 40px; }
section { margin-bottom: 32px; }
h2 { font-size: 18px; font-weight: 600; color: var(--text); margin-bottom: 12px; }
p { font-size: 14px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 12px; }
ul { padding-left: 20px; margin-bottom: 12px; }
li { font-size: 14px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 4px; }
@media (max-width: 768px) {
  .legal-page { padding: 70px 0 40px; }
  h1 { font-size: 24px; }
}
</style>
