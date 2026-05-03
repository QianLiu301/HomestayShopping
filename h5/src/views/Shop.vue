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
                  {{ product.is_featured ? '推荐商品' : '透明报价' }}
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
                  <span class="shop-card__badge">精品推荐</span>
                  <span v-if="product.original_price" class="shop-card__badge shop-card__badge--muted">限时好物</span>
                </div>

                <div class="product-name shop-card__name">{{ product.name }}</div>
                <div class="shop-card__meta">甄选品质商品，支持查看详情与在线下单</div>

                <div class="shop-card__price-row">
                  <div class="product-price shop-card__price">
                    ¥{{ product.price }}
                  </div>
                  <span v-if="product.original_price" class="original shop-card__original">¥{{ product.original_price }}</span>
                </div>

                <div class="shop-card__desc">
                  {{ product.desc || '精选商品展示，价格与规格请以商品详情页信息为准。' }}
                </div>

                <div class="shop-card__footer">
                  <div class="shop-card__tips">
                    <span>支持下单</span>
                    <span>查看详情</span>
                    <span>品质甄选</span>
                  </div>
                  <button class="shop-card__cta" type="button">
                    查看商品
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getProducts, getCategories } from '../api'
import LangSwitch from '../components/LangSwitch.vue'

const { t } = useI18n()
const route = useRoute()

const categories = ref([])
const products = ref([])
const activeCategory = ref(Number(route.query.category) || 0)
const page = ref(1)
const loadingMore = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const isFetching = ref(false)

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
    const params = { page: currentPage, per_page: 10 }
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

function onCategoryChange() {
  page.value = 1
  finished.value = false
  products.value = []
  isFetching.value = false
  loadMore()
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
  font-size: 12px;
  line-height: 1.5;
  color: #7b6b5d;
}

.shop-card__price-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
  margin-top: 12px;
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

  .shop-grid-wrap {
    padding: 12px;
  }

  .shop-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .shop-card__content {
    padding: 16px;
  }

  .shop-card__name {
    font-size: 22px;
  }

  .shop-card__price {
    font-size: 24px;
  }

  .shop-card__cta {
    width: 100%;
  }
}
</style>
