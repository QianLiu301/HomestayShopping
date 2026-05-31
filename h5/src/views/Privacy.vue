<template>
  <div class="legal-page">
    <div class="legal-container">
      <button class="back-btn" @click="$router.back()">← {{ t('common.back') }}</button>
      <h1>{{ t('legal.privacyTitle') }}</h1>
      <p class="update-date">{{ t('legal.lastUpdated') }}: 2026-05-31</p>

      <!-- 1. 引言 -->
      <section>
        <h2>{{ t('legal.privacy.introTitle') }}</h2>
        <p>{{ t('legal.privacy.introContent') }}</p>
      </section>

      <!-- 2. 收集的信息 -->
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
          <li>{{ t('legal.privacy.collectTraveler') }}</li>
          <li>{{ t('legal.privacy.collectUGC') }}</li>
          <li>{{ t('legal.privacy.collectTechnical') }}</li>
          <li>{{ t('legal.privacy.collectLang') }}</li>
        </ul>
      </section>

      <!-- 3. 信息使用 -->
      <section>
        <h2>{{ t('legal.privacy.useTitle') }}</h2>
        <p>{{ t('legal.privacy.useIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.useService') }}</li>
          <li>{{ t('legal.privacy.useContact') }}</li>
          <li>{{ t('legal.privacy.usePayment') }}</li>
          <li>{{ t('legal.privacy.useTicketCheck') }}</li>
          <li>{{ t('legal.privacy.useImprove') }}</li>
          <li>{{ t('legal.privacy.useSecurity') }}</li>
          <li>{{ t('legal.privacy.useLegal') }}</li>
        </ul>
      </section>

      <!-- 4. 法律依据 (GDPR) -->
      <section>
        <h2>{{ t('legal.privacy.legalBasisTitle') }}</h2>
        <p>{{ t('legal.privacy.legalBasisIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.legalBasisContract') }}</li>
          <li>{{ t('legal.privacy.legalBasisConsent') }}</li>
          <li>{{ t('legal.privacy.legalBasisInterest') }}</li>
          <li>{{ t('legal.privacy.legalBasisCompliance') }}</li>
        </ul>
      </section>

      <!-- 5. 信息共享 -->
      <section>
        <h2>{{ t('legal.privacy.shareTitle') }}</h2>
        <p>{{ t('legal.privacy.shareContent') }}</p>
        <ul>
          <li>{{ t('legal.privacy.shareDriver') }}</li>
          <li>{{ t('legal.privacy.shareAttraction') }}</li>
          <li>{{ t('legal.privacy.shareLegal') }}</li>
        </ul>
        <p>{{ t('legal.privacy.shareProviders') }}</p>
        <ul>
          <li>{{ t('legal.privacy.shareDB') }}</li>
          <li>{{ t('legal.privacy.shareCDN') }}</li>
          <li>{{ t('legal.privacy.shareEmail') }}</li>
          <li>{{ t('legal.privacy.shareAnalytics') }}</li>
          <li>{{ t('legal.privacy.sharePayment') }}</li>
          <li>{{ t('legal.privacy.shareWhatsApp') }}</li>
        </ul>
      </section>

      <!-- 6. 跨境数据传输 -->
      <section>
        <h2>{{ t('legal.privacy.transferTitle') }}</h2>
        <p>{{ t('legal.privacy.transferContent') }}</p>
      </section>

      <!-- 7. 存储与安全 + 保留期限 -->
      <section>
        <h2>{{ t('legal.privacy.storeTitle') }}</h2>
        <p>{{ t('legal.privacy.storeContent') }}</p>

        <h3 class="sub-title">{{ t('legal.privacy.retentionTitle') }}</h3>
        <p>{{ t('legal.privacy.retentionIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.retentionOrder') }}</li>
          <li>{{ t('legal.privacy.retentionTraveler') }}</li>
          <li>{{ t('legal.privacy.retentionPayment') }}</li>
          <li>{{ t('legal.privacy.retentionLogs') }}</li>
          <li>{{ t('legal.privacy.retentionAnalytics') }}</li>
        </ul>
        <p>{{ t('legal.privacy.retentionAfter') }}</p>
      </section>

      <!-- 8. 您的权利 -->
      <section>
        <h2>{{ t('legal.privacy.rightsTitle') }}</h2>
        <p>{{ t('legal.privacy.rightsIntro') }}</p>
        <ul>
          <li>{{ t('legal.privacy.rightsAccess') }}</li>
          <li>{{ t('legal.privacy.rightsCorrect') }}</li>
          <li>{{ t('legal.privacy.rightsDelete') }}</li>
          <li>{{ t('legal.privacy.rightsPortable') }}</li>
          <li>{{ t('legal.privacy.rightsRestrict') }}</li>
          <li>{{ t('legal.privacy.rightsObject') }}</li>
          <li>{{ t('legal.privacy.rightsWithdraw') }}</li>
          <li>{{ t('legal.privacy.rightsComplain') }}</li>
        </ul>
        <p>{{ t('legal.privacy.rightsContact') }}</p>
      </section>

      <!-- 9. Cookie 详细说明 -->
      <section>
        <h2>{{ t('legal.privacy.cookieTitle') }}</h2>
        <p>{{ t('legal.privacy.cookieIntro') }}</p>

        <h3 class="sub-title">{{ t('legal.privacy.cookieEssentialTitle') }}</h3>
        <p>{{ t('legal.privacy.cookieEssentialContent') }}</p>

        <h3 class="sub-title">{{ t('legal.privacy.cookieAnalyticsTitle') }}</h3>
        <p>{{ t('legal.privacy.cookieAnalyticsContent') }}</p>
        <ul>
          <li>{{ t('legal.privacy.cookieGA') }}</li>
          <li>{{ t('legal.privacy.cookieClarity') }}</li>
        </ul>

        <p>{{ t('legal.privacy.cookieControl') }}</p>
      </section>

      <!-- 10. 儿童隐私 -->
      <section>
        <h2>{{ t('legal.privacy.childrenTitle') }}</h2>
        <p>{{ t('legal.privacy.childrenContent') }}</p>
      </section>

      <!-- 11. 政策更新 -->
      <section>
        <h2>{{ t('legal.privacy.updateTitle') }}</h2>
        <p>{{ t('legal.privacy.updateContent') }}</p>
      </section>

      <!-- 12. 联系我们 -->
      <section>
        <h2>{{ t('legal.privacy.contactTitle') }}</h2>
        <p>{{ t('legal.privacy.contactContent') }}</p>
        <p><strong>{{ t('legal.privacy.contactEmail') }}</strong></p>
        <p>{{ t('legal.privacy.contactResponse') }}</p>
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
h3.sub-title { font-size: 15px; font-weight: 600; color: var(--text); margin: 18px 0 8px; }
p { font-size: 14px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 12px; }
ul { padding-left: 20px; margin-bottom: 12px; }
li { font-size: 14px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 4px; }
@media (max-width: 768px) {
  .legal-page { padding: 70px 0 40px; }
  h1 { font-size: 24px; }
}
</style>
