<template>
  <div class="guide-detail-page">
    <van-nav-bar :title="t('guides.detailTitle')" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="detail-loading">
      <van-loading size="24px">{{ t('common.loading') }}</van-loading>
    </div>

    <template v-else-if="guide">
      <div v-if="guide.cover_image" class="detail-cover">
        <img :src="$resolveUrl(guide.cover_image)" :alt="guide.title" />
      </div>

      <div class="detail-body">
        <div class="detail-meta">
          <span v-if="guide.category" class="detail-cat">{{ t(`guides.cat_${guide.category}`) }}</span>
          <span class="detail-free">{{ t('guides.freeTag') }}</span>
        </div>

        <h1 class="detail-title">{{ guide.title }}</h1>

        <p v-if="guide.summary" class="detail-summary">{{ guide.summary }}</p>

        <div class="detail-content" v-html="guide.content"></div>

        <div v-if="guide.attraction" class="detail-ticket-cta" @click="goToAttraction">
          <div class="cta-left">
            <span class="cta-icon">🎫</span>
            <div>
              <div class="cta-title">{{ guide.attraction.name }}</div>
              <div class="cta-hint">{{ t('guides.buyTicketHint') }}</div>
            </div>
          </div>
          <span class="cta-arrow">→</span>
        </div>
      </div>
    </template>

    <div v-else class="detail-empty">
      <p>{{ t('common.noData') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getGuide } from '../api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const guide = ref(null)
const loading = ref(true)

function goToAttraction() {
  if (guide.value?.attraction_id) {
    router.push(`/tickets/${guide.value.attraction_id}`)
  }
}

onMounted(async () => {
  try {
    const res = await getGuide(route.params.id)
    guide.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.guide-detail-page {
  min-height: 100vh;
  background: #fff;
}

.detail-loading, .detail-empty {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-light, #9b9388);
}

.detail-cover {
  width: 100%;
  aspect-ratio: 16/9;
  overflow: hidden;
  background: var(--warm-bg, #faf6ef);
}
.detail-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-body {
  padding: 20px 20px 40px;
  max-width: 800px;
  margin: 0 auto;
}

.detail-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.detail-cat {
  padding: 3px 10px;
  border-radius: 4px;
  background: var(--accent-light, #f5efe6);
  color: var(--accent, #c8a97e);
  font-size: 12px;
  font-weight: 600;
}
.detail-free {
  padding: 3px 10px;
  border-radius: 4px;
  background: #e8f5e9;
  color: #2e7d32;
  font-size: 12px;
  font-weight: 600;
}

.detail-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--text, #3b2b1f);
  margin: 0 0 12px;
  line-height: 1.3;
}

.detail-summary {
  font-size: 15px;
  color: var(--text-secondary, #8d7b67);
  line-height: 1.7;
  margin: 0 0 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(200, 169, 126, 0.2);
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text, #3b2b1f);
  word-break: break-word;
}

.detail-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 12px 0;
}

.detail-content :deep(h2),
.detail-content :deep(h3) {
  margin: 24px 0 12px;
  color: var(--text, #3b2b1f);
}

.detail-content :deep(p) {
  margin: 0 0 12px;
}

.detail-ticket-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 32px;
  padding: 16px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #fff7e6, #fef3e0);
  border: 1px solid rgba(200, 169, 126, 0.3);
  cursor: pointer;
  transition: transform 0.2s;
}
.detail-ticket-cta:active {
  transform: scale(0.98);
}

.cta-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cta-icon {
  font-size: 28px;
}

.cta-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text, #3b2b1f);
}

.cta-hint {
  font-size: 12px;
  color: var(--accent, #c8a97e);
  margin-top: 2px;
}

.cta-arrow {
  font-size: 20px;
  color: var(--accent, #c8a97e);
  font-weight: 700;
}
</style>
