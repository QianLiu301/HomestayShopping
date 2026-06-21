<template>
  <div class="guides-page">
    <div class="guides-header">
      <h1 class="guides-title">{{ t('guides.title') }}</h1>
      <p class="guides-subtitle">{{ t('guides.subtitle') }}</p>
    </div>

    <div class="guides-categories">
      <button
        v-for="cat in categories"
        :key="cat.value"
        type="button"
        class="cat-chip"
        :class="{ 'cat-chip--active': activeCategory === cat.value }"
        @click="activeCategory = cat.value; loadGuides()"
      >
        {{ cat.label }}
      </button>
    </div>

    <div v-if="loading && !guides.length" class="guides-loading">
      <van-loading size="24px">{{ t('common.loading') }}</van-loading>
    </div>

    <div v-else-if="!guides.length" class="guides-empty">
      <p>{{ t('common.noData') }}</p>
    </div>

    <div v-else class="guides-list">
      <div
        v-for="guide in guides"
        :key="guide.id"
        class="guide-card"
        @click="$router.push(`/guides/${guide.id}`)"
      >
        <div class="guide-cover">
          <img v-if="guide.cover_image" :src="$resolveUrl(guide.cover_image)" :alt="guide.title" loading="lazy" />
          <div v-else class="guide-cover-placeholder">{{ guide.title?.charAt(0) }}</div>
          <span v-if="guide.category" class="guide-cat-badge">{{ t(`guides.cat_${guide.category}`) }}</span>
        </div>
        <div class="guide-info">
          <h3 class="guide-card-title">{{ guide.title }}</h3>
          <p v-if="guide.summary" class="guide-card-summary">{{ guide.summary }}</p>
          <div class="guide-card-footer">
            <span class="guide-free-tag">{{ t('guides.freeTag') }}</span>
            <span v-if="guide.attraction" class="guide-ticket-link">{{ t('guides.hasTicket') }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="hasMore && guides.length" class="guides-load-more">
      <van-loading v-if="loading" size="20px" />
      <button v-else type="button" class="load-more-btn" @click="loadMore">{{ t('guides.loadMore') }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getGuides } from '../api'

const { t } = useI18n()

const guides = ref([])
const loading = ref(false)
const activeCategory = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const hasMore = computed(() => currentPage.value < totalPages.value)

const categories = computed(() => [
  { value: '', label: t('common.all') },
  { value: 'attraction', label: t('guides.cat_attraction') },
  { value: 'food', label: t('guides.cat_food') },
  { value: 'entertainment', label: t('guides.cat_entertainment') },
  { value: 'shopping', label: t('guides.cat_shopping') },
])

async function loadGuides(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: 12 }
    if (activeCategory.value) params.category = activeCategory.value
    const res = await getGuides(params)
    const list = res.data?.list || []
    if (page === 1) {
      guides.value = list
    } else {
      guides.value.push(...list)
    }
    currentPage.value = res.data?.page || 1
    totalPages.value = res.data?.pages || 1
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function loadMore() {
  if (hasMore.value && !loading.value) {
    loadGuides(currentPage.value + 1)
  }
}

onMounted(() => loadGuides())
</script>

<style scoped>
.guides-page {
  min-height: 100vh;
  background: var(--bg, #faf6ef);
  padding-bottom: 24px;
}

.guides-header {
  padding: 48px 20px 20px;
  text-align: center;
}

.guides-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--text, #3b2b1f);
  margin: 0 0 8px;
}

.guides-subtitle {
  font-size: 14px;
  color: var(--text-secondary, #8d7b67);
  margin: 0;
  line-height: 1.6;
}

.guides-categories {
  display: flex;
  gap: 10px;
  padding: 0 20px 16px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.guides-categories::-webkit-scrollbar { display: none; }

.cat-chip {
  flex: 0 0 auto;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid rgba(200, 169, 126, 0.4);
  background: rgba(255, 252, 247, 0.92);
  color: #4a3728;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}
.cat-chip--active {
  color: #fff;
  border-color: var(--accent, #c8a97e);
  background: linear-gradient(135deg, #c69a62, #ae7b43);
}

.guides-loading, .guides-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-light, #9b9388);
}

.guides-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  padding: 0 16px;
  max-width: 800px;
  margin: 0 auto;
}

.guide-card {
  display: flex;
  gap: 14px;
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.guide-card:active {
  transform: scale(0.98);
}

.guide-cover {
  position: relative;
  width: 120px;
  min-height: 120px;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--accent-light, #f5efe6), var(--warm-bg, #faf6ef));
}
.guide-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.guide-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: var(--accent, #c8a97e);
  font-weight: 700;
}

.guide-cat-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(0,0,0,0.55);
  color: #fff;
  font-size: 11px;
  font-weight: 500;
}

.guide-info {
  flex: 1;
  padding: 14px 14px 14px 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.guide-card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text, #3b2b1f);
  margin: 0 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.guide-card-summary {
  font-size: 13px;
  color: var(--text-secondary, #8d7b67);
  margin: 0 0 10px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.guide-card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.guide-free-tag {
  padding: 2px 8px;
  border-radius: 4px;
  background: #e8f5e9;
  color: #2e7d32;
  font-size: 11px;
  font-weight: 600;
}

.guide-ticket-link {
  font-size: 11px;
  color: var(--accent, #c8a97e);
  font-weight: 500;
}

.guides-load-more {
  text-align: center;
  padding: 20px;
}

.load-more-btn {
  padding: 10px 32px;
  border-radius: 999px;
  border: 1px solid rgba(200, 169, 126, 0.45);
  background: rgba(255, 252, 247, 0.92);
  color: var(--text, #3b2b1f);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.load-more-btn:active {
  background: #f0e8dc;
}

@media (min-width: 600px) {
  .guides-list {
    grid-template-columns: repeat(2, 1fr);
  }
  .guide-card {
    flex-direction: column;
  }
  .guide-cover {
    width: 100%;
    height: 180px;
    min-height: auto;
  }
  .guide-info {
    padding: 14px 16px 16px;
  }
}
</style>
