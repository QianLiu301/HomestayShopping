<template>
  <div class="legal-page">
    <div class="legal-container">
      <button class="back-btn" @click="$router.back()">← {{ t('common.back') }}</button>
      <h1>{{ t('legal.privacyTitle') }}</h1>
      <p class="update-date">{{ t('legal.lastUpdated') }}: 2026-03-12</p>

      <section>
        <h2>{{ t('legal.privacy.introTitle') }}</h2>
        <p>{{ t('legal.privacy.introContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.privacy.collectTitle') }}</h2>
        <p>{{ t('legal.privacy.collectIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.collectName') }}</li>
          <li>{{ t('legal.privacy.collectPhone') }}</li>
          <li>{{ t('legal.privacy.collectEmail') }}</li>
          <li>{{ t('legal.privacy.collectFlight') }}</li>
          <li>{{ t('legal.privacy.collectAddress') }}</li>
          <li>{{ t('legal.privacy.collectPayment') }}</li>
          <li>{{ t('legal.privacy.collectOrder') }}</li>
        </ul>
      </section>

      <section>
        <h2>{{ t('legal.privacy.useTitle') }}</h2>
        <p>{{ t('legal.privacy.useIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.useService') }}</li>
          <li>{{ t('legal.privacy.useContact') }}</li>
          <li>{{ t('legal.privacy.usePayment') }}</li>
          <li>{{ t('legal.privacy.useImprove') }}</li>
        </ul>
      </section>

      <section>
        <h2>{{ t('legal.privacy.shareTitle') }}</h2>
        <p>{{ t('legal.privacy.shareContent') }}</p>
        <ul>
          <li>{{ t('legal.privacy.shareDriver') }}</li>
          <li>{{ t('legal.privacy.shareLegal') }}</li>
        </ul>
      </section>

      <section>
        <h2>{{ t('legal.privacy.storeTitle') }}</h2>
        <p>{{ t('legal.privacy.storeContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.privacy.rightsTitle') }}</h2>
        <p>{{ t('legal.privacy.rightsIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.rightsAccess') }}</li>
          <li>{{ t('legal.privacy.rightsCorrect') }}</li>
          <li>{{ t('legal.privacy.rightsDelete') }}</li>
        </ul>
        <p>{{ t('legal.privacy.rightsContact') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.privacy.cookieTitle') }}</h2>
        <p>{{ t('legal.privacy.cookieContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.privacy.updateTitle') }}</h2>
        <p>{{ t('legal.privacy.updateContent') }}</p>
      </section>

      <section>
        <h2>{{ t('legal.privacy.contactTitle') }}</h2>
        <p>{{ t('legal.privacy.contactContent') }}</p>
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
