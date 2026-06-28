<template>
  <div class="guide-detail-page">
    <van-nav-bar :title="t('guides.detailTitle')" left-arrow @click-left="$router.back()" />

    <div v-if="loading" class="detail-loading">
      <van-loading size="24px">{{ t('common.loading') }}</van-loading>
    </div>

    <template v-else-if="guide">
      <div v-if="guideImages.length > 1" class="detail-gallery">
        <van-swipe :autoplay="4000" lazy-render class="gallery-swipe" indicator-color="#c8a97e">
          <van-swipe-item v-for="(img, idx) in guideImages" :key="idx">
            <div class="gallery-slide">
              <img :src="$resolveUrl(img)" :alt="`${guide.title} - ${idx + 1}`" class="gallery-img" />
            </div>
          </van-swipe-item>
          <template #indicator="{ active, total }">
            <div class="gallery-bottom">
              <div class="gallery-dots">
                <span v-for="i in total" :key="i" :class="['dot', { active: i - 1 === active }]" />
              </div>
              <div class="gallery-counter">{{ active + 1 }} / {{ total }}</div>
            </div>
          </template>
        </van-swipe>
        <div class="swipe-hint">{{ t('guides.swipeHint') }}</div>
      </div>
      <div v-else-if="guideImages.length === 1" class="detail-cover">
        <img :src="$resolveUrl(guideImages[0])" :alt="guide.title" />
      </div>

      <div class="detail-body">
        <div class="detail-meta">
          <span v-if="guide.category" class="detail-cat">{{ t(`guides.cat_${guide.category}`) }}</span>
          <span class="detail-free">{{ t('guides.freeTag') }}</span>
        </div>

        <h1 class="detail-title">{{ guide.title }}</h1>

        <p v-if="guide.summary" class="detail-summary">{{ guide.summary }}</p>

        <div class="detail-content" v-html="renderedContent" @click="onContentClick"></div>

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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getGuide } from '../api'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const guide = ref(null)
const loading = ref(true)

const guideImages = computed(() => {
  if (!guide.value) return []
  if (guide.value.images?.length) return guide.value.images
  if (guide.value.cover_image) return [guide.value.cover_image]
  return []
})

const renderedContent = computed(() => {
  if (!guide.value?.content) return ''
  const hint = t('guides.buyTicketHint')
  return guide.value.content.replace(
    /\{\{ticket:(\d+):([^}]+)\}\}/g,
    (_, id, name) =>
      `<div class="inline-ticket-cta" data-ticket-id="${id}">` +
        `<div class="cta-left"><span class="cta-icon">🎫</span>` +
        `<div><div class="cta-title">${name}</div>` +
        `<div class="cta-hint">${hint}</div></div></div>` +
        `<span class="cta-arrow">→</span></div>`
  )
})

function onContentClick(e) {
  const cta = e.target.closest('.inline-ticket-cta')
  if (cta) {
    const id = cta.dataset.ticketId
    if (id) router.push(`/tickets/${id}`)
  }
}

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

.detail-gallery {
  width: 100%;
  background: var(--warm-bg, #faf6ef);
}

.gallery-swipe {
  width: 100%;
  height: 280px;
}

.gallery-slide {
  width: 100%;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--warm-bg, #faf6ef);
}

.gallery-img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
}

.gallery-bottom {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.gallery-dots {
  display: flex;
  gap: 6px;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transition: all 0.3s;
}

.dot.active {
  width: 18px;
  border-radius: 3px;
  background: var(--accent, #c8a97e);
}

.gallery-counter {
  padding: 2px 10px;
  font-size: 12px;
  color: #fff;
  background: rgba(0, 0, 0, 0.45);
  border-radius: 10px;
}

.swipe-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-light, #9b9388);
  padding: 6px 0;
}

.detail-cover {
  width: 100%;
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--warm-bg, #faf6ef);
}
.detail-cover img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
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
  white-space: pre-wrap;
}

.detail-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text, #3b2b1f);
  word-break: break-word;
  white-space: pre-wrap;
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

<style>
.detail-content .inline-ticket-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 16px 0;
  padding: 14px 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #fff7e6, #fef3e0);
  border: 1px solid rgba(200, 169, 126, 0.3);
  cursor: pointer;
  transition: transform 0.2s;
  white-space: normal;
}
.detail-content .inline-ticket-cta:active {
  transform: scale(0.98);
}
.detail-content .inline-ticket-cta .cta-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.detail-content .inline-ticket-cta .cta-icon {
  font-size: 28px;
}
.detail-content .inline-ticket-cta .cta-title {
  font-size: 15px;
  font-weight: 600;
  color: #3b2b1f;
}
.detail-content .inline-ticket-cta .cta-hint {
  font-size: 12px;
  color: #c8a97e;
  margin-top: 2px;
}
.detail-content .inline-ticket-cta .cta-arrow {
  font-size: 20px;
  color: #c8a97e;
  font-weight: 700;
}
</style>
