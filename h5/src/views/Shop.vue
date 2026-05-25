<template>
  <div class="page-container page-with-tabbar shop-page">
    <van-nav-bar :title="t('shop.title')" left-arrow @click-left="$router.back()">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeCategory" sticky shrink class="shop-tabs" @change="onCategoryChange">
      <van-tab :title="t('common.all')" :name="0" />
      <van-tab
        v-for="cat in categories"
        :key="cat.id"
        :title="cat.name"
        :name="cat.id"
      />
    </van-tabs>

    <div class="shop-sort-bar">
      <div class="shop-sort-bar__inner">
        <div class="shop-sort-bar__chips">
          <button
            v-for="item in sortOptions"
            :key="item.value"
            type="button"
            class="shop-sort-chip"
            :class="{ 'shop-sort-chip--active': currentSort === item.value }"
            @click="onSortChange(item.value)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loadingMore"
        :finished="finished"
        :finished-text="products.length ? '' : ''"
        @load="loadMore"
      >
        <div class="shop-grid-wrap">
          <div class="product-grid shop-grid">
            <article
              v-for="product in products"
              :key="product.id"
              class="product-card shop-card"
              @click="$router.push(`/product/${product.id}`)"
            >
              <div class="shop-card__media">
                <span v-if="product.is_featured || product.original_price" class="shop-card__flag">
                  {{ product.is_featured ? t('shop.featuredFlag') : t('shop.priceFlag') }}
                </span>
                <img
                  v-if="product.images?.length"
                  :src="$resolveUrl(product.images[0])"
                  :alt="product.name"
                  class="product-image shop-card__image"
                  loading="lazy"
                />
                <div v-else class="placeholder-img shop-card__placeholder">{{ product.name?.charAt(0) }}</div>
              </div>

              <div class="product-info shop-card__content">
                <div class="shop-card__topline">
                  <span class="shop-card__badge">{{ t('shop.featuredBadge') }}</span>
                  <span v-if="product.original_price" class="shop-card__badge shop-card__badge--muted">{{ t('shop.limitedBadge') }}</span>
                </div>

                <div class="product-name shop-card__name">{{ product.name }}</div>
                <div class="shop-card__meta">
                  <span>{{ t('shop.meta') }}</span>
                  <span v-if="product.sales_count > 0" class="shop-card__sales">{{ t('shop.soldCount', { count: product.sales_count }) }}</span>
                </div>

                <div class="shop-card__price-row">
                  <div class="shop-card__price-stack">
                    <div class="shop-card__price-main">
                      <div class="product-price shop-card__price">
                        ¥{{ product.price }}
                      </div>
                      <span v-if="product.original_price" class="original shop-card__original">¥{{ product.original_price }}</span>
                    </div>
                    <div v-if="product.price" class="shop-card__price-ref">≈ {{ formatUsdReference(product.price) }}</div>
                  </div>
                </div>

                <div class="shop-card__desc">
                  {{ product.desc || t('shop.descFallback') }}
                </div>

                <div class="shop-card__footer">
                  <div class="shop-card__tips">
                    <span>{{ t('shop.tipOrder') }}</span>
                    <span>{{ t('shop.tipDetail') }}</span>
                    <span>{{ t('shop.tipQuality') }}</span>
                  </div>
                  <button class="shop-card__cta" type="button">
                    {{ t('shop.viewProduct') }}
                  </button>
                </div>
              </div>
            </article>
          </div>
        </div>

        <van-empty v-if="!loadingMore && !products.length" :description="t('common.noData')" />
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getProducts, getCategories } from '../api'
import LangSwitch from '../components/LangSwitch.vue'
import { formatUsdReference } from '../utils/currency'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const categories = ref([])
const products = ref([])
const activeCategory = ref(Number(route.query.category) || 0)
const currentSort = ref(String(route.query.sort || 'default'))
const page = ref(1)
const loadingMore = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const isFetching = ref(false)

const sortOptions = computed(() => [
  { value: 'default', label: t('shop.sortDefault') },
  { value: 'sales_desc', label: t('shop.sortSales') },
  { value: 'price_asc', label: t('shop.sortPriceAsc') },
  { value: 'price_desc', label: t('shop.sortPriceDesc') },
  { value: 'newest', label: t('shop.sortNewest') }
])

onMounted(async () => {
  try {
    const res = await getCategories()
    categories.value = res.data || []
  } catch (e) {
    console.error(e)
  }
})

async function loadMore() {
  if (isFetching.value || finished.value) return

  isFetching.value = true
  loadingMore.value = true
  const currentPage = page.value

  try {
    const params = { page: currentPage, per_page: 10, sort: currentSort.value }
    if (activeCategory.value) {
      params.category_id = activeCategory.value
    }
    const res = await getProducts(params)
    const list = res.data?.list || []

    if (currentPage === 1) {
      products.value = list
    } else {
      const merged = [...products.value, ...list]
      const uniqueMap = new Map()
      merged.forEach(item => {
        if (item?.id != null) uniqueMap.set(item.id, item)
      })
      products.value = Array.from(uniqueMap.values())
    }

    if (products.value.length >= (res.data?.total || 0) || !list.length) {
      finished.value = true
    } else {
      page.value = currentPage + 1
    }
  } catch (e) {
    finished.value = true
  } finally {
    isFetching.value = false
    loadingMore.value = false
    refreshing.value = false
  }
}

function updateRouteQuery() {
  const query = { ...route.query }
  if (activeCategory.value) query.category = String(activeCategory.value)
  else delete query.category

  if (currentSort.value && currentSort.value !== 'default') query.sort = currentSort.value
  else delete query.sort

  router.replace({ path: route.path, query })
}

function resetAndLoad() {
  page.value = 1
  finished.value = false
  products.value = []
  isFetching.value = false
  updateRouteQuery()
  loadMore()
}

function onCategoryChange() {
  resetAndLoad()
}

function onSortChange(sortValue) {
  if (currentSort.value === sortValue) return
  currentSort.value = sortValue
  resetAndLoad()
}

function onRefresh() {
  page.value = 1
  finished.value = false
  products.value = []
  isFetching.value = false
  loadMore()
}
</script>

<style scoped>
.shop-page {
  padding-top: 0;
  background: #f8f4ee;
}

.shop-tabs {
  margin-top: 0;
}

.shop-sort-bar {
  position: sticky;
  top: 44px;
  z-index: 12;
  padding: 10px 16px 12px;
  background: transparent;
}

.shop-sort-bar__inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 12px 14px;
  border: 1px solid rgba(201, 169, 126, 0.2);
  border-radius: 20px;
  background: rgba(248, 244, 238, 0.94);
  backdrop-filter: blur(14px);
  box-shadow: 0 12px 28px rgba(74, 55, 40, 0.08);
}

.shop-sort-bar__chips {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.shop-sort-bar__chips::-webkit-scrollbar {
  display: none;
}

.shop-sort-chip {
  flex: 0 0 auto;
  padding: 8px 14px;
  border: 1px solid rgba(201, 169, 126, 0.28);
  border-radius: 999px;
  background: #fffdf9;
  color: #6f614f;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.shop-sort-chip--active {
  color: #fff;
  border-color: #b98745;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  box-shadow: 0 8px 16px rgba(174, 123, 67, 0.16);
}

.shop-grid-wrap {
  max-width: 1440px;
  margin: 0 auto;
  padding: 12px 16px 16px;
}

.shop-grid {
  padding: 0;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.shop-card {
  border: 1px solid rgba(201, 169, 126, 0.18);
  border-radius: 18px;
  background: #fffdf9;
  box-shadow: 0 10px 22px rgba(74, 55, 40, 0.05);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  cursor: pointer;
}

.shop-card:hover {
  transform: translateY(-4px);
  border-color: rgba(201, 169, 126, 0.42);
  box-shadow: 0 18px 38px rgba(74, 55, 40, 0.1);
}

.shop-card__media {
  position: relative;
  padding: 12px 12px 0;
}

.shop-card__flag {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(59, 43, 31, 0.86);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

.shop-card__image,
.shop-card__placeholder {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 14px;
  background: linear-gradient(180deg, #f7f2ea 0%, #efe7db 100%);
}

.shop-card__image {
  object-fit: cover;
}

.shop-card__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: rgba(59, 43, 31, 0.25);
}

.shop-card__content {
  padding: 12px 14px 14px;
}

.shop-card__topline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.shop-card__badge {
  padding: 4px 8px;
  border-radius: 999px;
  background: #f4eadb;
  color: #8a6635;
  font-size: 11px;
  font-weight: 600;
}

.shop-card__badge--muted {
  background: #f7f7f5;
  color: #7d766f;
}

.shop-card__name {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.45;
  color: #3b2b1f;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.shop-card__meta {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  line-height: 1.5;
  color: #7b6b5d;
}

.shop-card__sales {
  color: #9b9388;
}

.shop-card__price-row {
  margin-top: 12px;
}

.shop-card__price-stack {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.shop-card__price-main {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
}

.shop-card__price {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px;
  margin-top: 0;
  font-size: 18px;
  color: #b98745;
}

.shop-card__price-ref {
  font-size: 12px;
  line-height: 1.25;
  color: #9b9388;
}

.shop-card__price-suffix {
  font-size: 12px;
  font-weight: 500;
  color: #8d7b67;
}

.shop-card__original {
  font-size: 12px;
  color: #a49b90;
}

.shop-card__desc {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.6;
  color: #8a7c6e;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.shop-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
}

.shop-card__tips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.shop-card__tips span {
  padding: 4px 8px;
  border-radius: 999px;
  background: #faf6f0;
  color: #6f614f;
  font-size: 11px;
}

.shop-card__cta {
  min-width: 96px;
  padding: 10px 14px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 8px 16px rgba(174, 123, 67, 0.18);
}

@media (max-width: 1280px) {
  .shop-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 1024px) {
  .shop-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .shop-card__name {
    font-size: 20px;
  }
}

@media (max-width: 768px) {
  .shop-card__footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .shop-sort-bar {
    top: 46px;
    padding: 8px 12px 10px;
  }

  .shop-sort-bar__inner {
    padding: 10px;
    border-radius: 16px;
  }

  .shop-sort-bar__chips {
    gap: 8px;
  }

  .shop-sort-chip {
    padding: 7px 12px;
    font-size: 12px;
  }

  .shop-grid-wrap {
    padding: 4px 12px 12px;
  }

  .shop-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .shop-card__content {
    padding: 12px;
  }

  .shop-card__name {
    font-size: 14px;
  }

  .shop-card__price {
    font-size: 16px;
  }

  .shop-card__price-ref {
    font-size: 11px;
  }

  .shop-card__cta {
    width: 100%;
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>
