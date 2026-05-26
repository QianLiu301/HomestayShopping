<template>
  <div class="page-container page-with-tabbar tickets-page">
    <van-nav-bar :title="t('tickets.title')" left-arrow @click-left="$router.back()">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <div v-if="loading" class="loading-wrap">
      <van-loading size="24" />
    </div>

    <template v-else>
      <section v-if="isDesktop" class="tickets-desktop section-container">
        <div class="tickets-desktop__hero">
          <div>
            <div class="tickets-desktop__eyebrow">{{ t('tickets.heroBadge') }}</div>
            <h1 class="tickets-desktop__title">{{ t('tickets.heroTitle') }}</h1>
            <p class="tickets-desktop__subtitle">{{ t('tickets.heroSubtitle') }}</p>
          </div>
          <div class="tickets-desktop__city">{{ t('tickets.shanghaiOnlyLabel') }}</div>
        </div>

        <div class="tickets-sort-bar">
          <button
            v-for="option in sortOptions"
            :key="option.value"
            type="button"
            class="tickets-sort-bar__item"
            :class="{ active: sortKey === option.value }"
            @click="sortKey = option.value"
          >
            {{ option.label }}
          </button>
        </div>

        <section class="tickets-desktop__list">
          <article
            v-for="(item, index) in sortedList"
            :key="item.id"
            class="ticket-desktop-card"
            @click="goDetail(item.id)"
          >
            <div class="ticket-desktop-card__image-wrap">
              <img
                v-if="item.cover_image"
                :src="resolveUrl(item.cover_image)"
                :alt="item.name"
                class="ticket-desktop-card__image"
              />
              <div v-else class="ticket-desktop-card__placeholder">{{ item.name?.charAt(0) || 'T' }}</div>
            </div>

            <div class="ticket-desktop-card__content">
              <div class="ticket-desktop-card__title-row">
                <div>
                  <h3 class="ticket-desktop-card__title">{{ item.name }}</h3>
                  <div class="ticket-desktop-card__meta">
                    <span class="ticket-desktop-card__city-tag">{{ t('tickets.cityShanghai') }}</span>
                    <span v-if="item.category" class="ticket-desktop-card__category">{{ item.category }}</span>
                    <span v-if="item.featured" class="ticket-desktop-card__featured">{{ t('tickets.featured') }}</span>
                  </div>
                </div>
              </div>

              <p class="ticket-desktop-card__desc">{{ item.subtitle || item.desc || t('tickets.desktopListFallback') }}</p>

              <div v-if="item.tags?.length" class="ticket-desktop-card__tags">
                <span v-for="tag in item.tags.slice(0, 4)" :key="tag" class="ticket-desktop-card__tag">{{ tag }}</span>
              </div>

              <div class="ticket-desktop-card__footer">
                <span class="ticket-desktop-card__rank">{{ t('tickets.comprehensiveSort') }} · {{ String(index + 1).padStart(2, '0') }}</span>
              </div>
            </div>

            <div class="ticket-desktop-card__side">
              <div class="ticket-desktop-card__price-block">
                <div class="ticket-desktop-card__price">
                  <template v-if="item.min_price">¥{{ item.min_price }}</template>
                  <template v-else>{{ t('tickets.priceToConfirm') }}</template>
                </div>
                <div v-if="item.min_price" class="ticket-desktop-card__price-ref">
                  {{ t('tickets.referenceUsdPrice', { price: formatUsdReference(item.min_price) }) }}
                </div>
              </div>
              <button class="ticket-desktop-card__cta" type="button">{{ t('tickets.viewDetail') }}</button>
            </div>
          </article>

          <van-empty v-if="!sortedList.length" :description="t('common.noData')" />
        </section>
      </section>

      <template v-else>
        <section class="tickets-hero">
          <div class="tickets-hero__badge">{{ t('tickets.heroBadge') }}</div>
          <h1 class="tickets-hero__title">{{ t('tickets.heroTitle') }}</h1>
          <p class="tickets-hero__subtitle">{{ t('tickets.heroSubtitle') }}</p>
        </section>

        <section class="tickets-filters card">
          <van-search
            v-model="keyword"
            shape="round"
            :placeholder="t('tickets.searchPlaceholder')"
            @search="onSearch"
            @clear="onSearch"
          />
        </section>

        <section class="tickets-list">
          <article
            v-for="item in sortedList"
            :key="item.id"
            class="ticket-card"
            @click="goDetail(item.id)"
          >
            <div class="ticket-card__media">
              <img
                v-if="item.cover_image"
                :src="resolveUrl(item.cover_image)"
                :alt="item.name"
                class="ticket-card__image"
              />
              <div v-else class="ticket-card__placeholder">{{ item.name?.charAt(0) || 'T' }}</div>

              <div class="ticket-card__badges">
                <span v-if="item.featured" class="badge badge-featured">{{ t('tickets.featured') }}</span>
                <span v-if="item.min_price" class="badge badge-price">{{ t('tickets.fromPrice', { price: item.min_price }) }}</span>
              </div>
            </div>

            <div class="ticket-card__content">
              <div class="ticket-card__top">
                <h3 class="ticket-card__name">{{ item.name }}</h3>
                <span class="ticket-card__city">{{ t('tickets.cityShanghai') }}</span>
              </div>

              <p v-if="item.subtitle" class="ticket-card__subtitle">{{ item.subtitle }}</p>
              <p v-else-if="item.desc" class="ticket-card__subtitle">{{ item.desc }}</p>

              <div v-if="item.tags?.length" class="ticket-card__tags">
                <span v-for="tag in item.tags" :key="tag" class="tag-chip">{{ tag }}</span>
              </div>

              <div class="ticket-card__bottom">
                <div>
                  <div class="ticket-card__price-label">{{ t('tickets.startingFrom') }}</div>
                  <div class="ticket-card__price">
                    <template v-if="item.min_price">¥{{ item.min_price }}</template>
                    <template v-else>{{ t('tickets.priceToConfirm') }}</template>
                  </div>
                </div>
                <button class="ticket-card__cta" type="button">{{ t('tickets.viewDetail') }}</button>
              </div>
            </div>
          </article>

          <van-empty v-if="!sortedList.length" :description="t('common.noData')" />
        </section>
      </template>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getTicketAttractions } from '../api/tickets'
import { resolveUrl } from '../api'
import LangSwitch from '../components/LangSwitch.vue'

const { t } = useI18n()
const router = useRouter()

const list = ref([])
const loading = ref(true)
const keyword = ref('')
const sortKey = ref('comprehensive')
const isDesktop = ref(window.innerWidth >= 1024)
const USD_CNY_RATE = 7.2
const usdCurrencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
})

const sortOptions = computed(() => ([
  { value: 'comprehensive', label: t('tickets.comprehensiveSort') },
  { value: 'price_asc', label: t('tickets.priceLowToHigh') },
  { value: 'price_desc', label: t('tickets.priceHighToLow') }
]))

const filteredList = computed(() => {
  const base = (list.value || []).filter(item => !item.city || item.city === '上海')
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return base
  return base.filter(item => {
    const haystack = [item.name, item.subtitle, item.desc, item.category, ...(item.tags || [])]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(kw)
  })
})

const sortedList = computed(() => {
  const source = filteredList.value.map((item, index) => ({ ...item, __index: index }))
  if (sortKey.value === 'price_asc') {
    return source.sort((a, b) => normalizedPrice(a) - normalizedPrice(b))
  }
  if (sortKey.value === 'price_desc') {
    return source.sort((a, b) => normalizedPrice(b) - normalizedPrice(a))
  }
  return source.sort((a, b) => {
    if (Number(b.featured) !== Number(a.featured)) return Number(b.featured) - Number(a.featured)
    return a.__index - b.__index
  })
})

function normalizedPrice(item) {
  const price = Number(item?.min_price)
  return Number.isFinite(price) && price > 0 ? price : Number.MAX_SAFE_INTEGER
}

function formatUsdReference(cnyPrice) {
  const price = Number(cnyPrice)
  if (!Number.isFinite(price) || price <= 0) return ''
  return usdCurrencyFormatter.format(price / USD_CNY_RATE)
}

function goDetail(id) {
  router.push(`/tickets/${id}`)
}

function onSearch() {
  if (isDesktop.value) return
}

async function loadData() {
  loading.value = true
  try {
    const params = { city: '上海' }
    if (keyword.value.trim() && !isDesktop.value) params.keyword = keyword.value.trim()
    const res = await getTicketAttractions(params)
    list.value = res.data || []
  } catch (error) {
    console.error(error)
    list.value = []
  } finally {
    loading.value = false
  }
}

function handleResize() {
  isDesktop.value = window.innerWidth >= 1024
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await loadData()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.tickets-page {
  padding-top: 0;
  padding-bottom: 76px;
  background: linear-gradient(180deg, #f7f2ea 0%, #f3ece0 100%);
}

.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 72px 0;
}

.tickets-desktop {
  padding-top: 16px;
  padding-bottom: 28px;
}

.tickets-desktop__hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 16px;
}

.tickets-desktop__eyebrow {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(200, 169, 126, 0.16);
  color: #8f6b3d;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.tickets-desktop__title {
  margin: 10px 0 0;
  font-size: 28px;
  line-height: 1.16;
  color: #2f2419;
}

.tickets-desktop__subtitle {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: #766555;
  max-width: 560px;
}

.tickets-desktop__city {
  flex-shrink: 0;
  padding: 9px 14px;
  border-radius: 12px;
  background: rgba(255, 252, 247, 0.82);
  border: 1px solid rgba(200, 169, 126, 0.34);
  color: #8f6b3d;
  font-size: 12px;
  font-weight: 700;
}

.tickets-sort-bar {
  display: inline-grid;
  grid-template-columns: repeat(3, minmax(0, 170px));
  max-width: 100%;
  border: 1px solid rgba(200, 169, 126, 0.28);
  background: rgba(255, 252, 247, 0.84);
  border-radius: 14px;
  overflow: hidden;
}

.tickets-sort-bar__item {
  height: 52px;
  border: none;
  border-right: 1px solid rgba(200, 169, 126, 0.22);
  background: transparent;
  color: #4a3728;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease;
}

.tickets-sort-bar__item:last-child {
  border-right: none;
}

.tickets-sort-bar__item.active {
  color: #8f6b3d;
  background: rgba(200, 169, 126, 0.14);
}

.tickets-desktop__list {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.ticket-desktop-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(200, 169, 126, 0.18);
  border-radius: 18px;
  background: rgba(255, 252, 247, 0.94);
  box-shadow: 0 10px 22px rgba(74, 55, 40, 0.045);
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.ticket-desktop-card:hover {
  transform: translateY(-3px);
  border-color: rgba(200, 169, 126, 0.4);
  box-shadow: 0 16px 32px rgba(74, 55, 40, 0.09);
}

.ticket-desktop-card__image-wrap {
  overflow: hidden;
  border-radius: 12px;
  background: linear-gradient(180deg, #f7f2ea 0%, #efe7db 100%);
  aspect-ratio: 16 / 10;
}

.ticket-desktop-card__image,
.ticket-desktop-card__placeholder {
  width: 100%;
  height: 100%;
}

.ticket-desktop-card__image {
  object-fit: cover;
}

.ticket-desktop-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 72px;
  color: rgba(59, 43, 31, 0.2);
}

.ticket-desktop-card__content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.ticket-desktop-card__title {
  margin: 0;
  font-size: 17px;
  line-height: 1.3;
  color: #2f2419;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ticket-desktop-card__meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.ticket-desktop-card__city-tag,
.ticket-desktop-card__category,
.ticket-desktop-card__featured,
.ticket-desktop-card__tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}

.ticket-desktop-card__city-tag,
.ticket-desktop-card__category,
.ticket-desktop-card__tag {
  background: #faf3e7;
  color: #7b6340;
}

.ticket-desktop-card__featured {
  background: rgba(200, 169, 126, 0.16);
  color: #8f6b3d;
}

.ticket-desktop-card__desc {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.55;
  color: #6e5f51;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ticket-desktop-card__tags {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ticket-desktop-card__footer {
  margin-top: auto;
  padding-top: 14px;
}

.ticket-desktop-card__rank {
  font-size: 12px;
  color: #7f715f;
}

.ticket-desktop-card__side {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid rgba(200, 169, 126, 0.18);
  margin-top: auto;
}

.ticket-desktop-card__price-block {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.ticket-desktop-card__price {
  font-size: 24px;
  line-height: 1;
  font-weight: 700;
  color: var(--accent-dark);
}

.ticket-desktop-card__price-ref {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.4;
  color: #9f988e;
}

.ticket-desktop-card__cta {
  flex: 0 0 auto;
  min-width: 96px;
  height: 38px;
  padding: 0 16px;
  border: none;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 8px 18px rgba(200,169,126,0.22);
  cursor: pointer;
}

.tickets-hero {
  margin: 12px 16px 0;
  padding: 24px 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, #3f2e20 0%, #73563d 100%);
  color: #fff;
}

.tickets-hero__badge {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.14);
  font-size: 12px;
  letter-spacing: 1px;
  margin-bottom: 10px;
}

.tickets-hero__title {
  margin: 0;
  font-size: 26px;
  line-height: 1.2;
}

.tickets-hero__subtitle {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255,255,255,0.78);
}

.tickets-filters {
  margin-top: 14px;
  padding: 12px;
}

.tickets-list {
  padding: 14px 16px 20px;
  display: grid;
  gap: 16px;
}

.ticket-card {
  overflow: hidden;
  border-radius: 20px;
  background: #fffdf9;
  box-shadow: 0 10px 24px rgba(74, 55, 40, 0.08);
}

.ticket-card__media {
  position: relative;
  aspect-ratio: 16 / 10;
  background: linear-gradient(180deg, #f7f2ea 0%, #efe7db 100%);
}

.ticket-card__image,
.ticket-card__placeholder {
  width: 100%;
  height: 100%;
}

.ticket-card__image {
  object-fit: cover;
}

.ticket-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44px;
  color: rgba(59, 43, 31, 0.25);
}

.ticket-card__badges {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.badge-featured {
  background: rgba(59, 43, 31, 0.86);
  color: #fff;
}

.badge-price {
  background: rgba(255,255,255,0.92);
  color: #8a6635;
}

.ticket-card__content {
  padding: 16px;
}

.ticket-card__top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.ticket-card__name {
  margin: 0;
  font-size: 18px;
  line-height: 1.45;
  color: #3b2b1f;
}

.ticket-card__city {
  flex-shrink: 0;
  padding: 4px 8px;
  border-radius: 999px;
  background: #f4eadb;
  color: #8a6635;
  font-size: 11px;
  font-weight: 600;
}

.ticket-card__subtitle {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.7;
  color: #7b6b5d;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ticket-card__tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 4px 8px;
  border-radius: 999px;
  background: #faf6f0;
  color: #6f614f;
  font-size: 11px;
}

.ticket-card__bottom {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
}

.ticket-card__price-label {
  font-size: 11px;
  color: #9a8c7f;
}

.ticket-card__price {
  margin-top: 4px;
  font-size: 22px;
  font-weight: 700;
  color: #b98745;
}

.ticket-card__cta {
  min-width: 104px;
  padding: 10px 14px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

@media (min-width: 1024px) {
  .tickets-page {
    padding-bottom: 40px;
  }

  .tickets-hero,
  .tickets-filters,
  .tickets-list {
    display: none;
  }
}

@media (max-width: 1023px) {
  .tickets-desktop {
    display: none;
  }
}
</style>
