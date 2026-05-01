<template>
  <div class="page-container page-with-tabbar shop-page">
    <van-nav-bar :title="t('shop.title')" left-arrow @click-left="$router.back()">
      <template #right>
        <LangSwitch />
      </template>
    </van-nav-bar>

    <section class="shop-hero">
      <div class="shop-hero__content">
        <p class="shop-hero__eyebrow">Airport Transfer Service</p>
        <h1 class="shop-hero__title">机场接送服务</h1>
        <p class="shop-hero__subtitle">浦东 · 虹桥 ｜ 接机 · 送机 · 往返均可</p>
        <p class="shop-hero__desc">选择车型后在预订页面指定服务类型，当前展示价格为车型参考起步价，便于快速比较不同车型的空间与舒适度。</p>
      </div>
    </section>

    <section class="service-note-card">
      <div class="service-note-card__header">
        <div>
          <div class="service-note-card__title">预订说明</div>
          <div class="service-note-card__text">价格为参考起价，具体将根据服务类型、机场路线、时段与附加费用确认。</div>
        </div>
        <div class="service-note-card__badge">支持接机 / 送机 / 往返</div>
      </div>
      <div class="service-note-list">
        <span class="service-note-pill">浦东 / 虹桥均可安排</span>
        <span class="service-note-pill">预订页选择服务类型</span>
        <span class="service-note-pill">车型图片已优化展示</span>
      </div>
    </section>

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
              v-for="(product, index) in products"
              :key="product.id"
              class="product-card shop-card"
              @click="$router.push(`/product/${product.id}`)"
            >
              <div class="shop-card__media">
                <span v-if="product.original_price || index === 0" class="shop-card__flag">
                  {{ index === 0 ? '推荐车型' : '透明报价' }}
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
                  <span class="shop-card__badge">机场接送</span>
                  <span class="shop-card__badge shop-card__badge--muted">浦东 / 虹桥</span>
                </div>

                <div class="product-name shop-card__name">{{ product.name }}</div>
                <div class="shop-card__meta">适合提前对比车型空间、舒适度与预算区间</div>

                <div class="shop-card__price-row">
                  <div class="product-price shop-card__price">
                    ¥{{ product.price }}
                    <span class="shop-card__price-suffix">起 / 单程参考</span>
                  </div>
                  <span v-if="product.original_price" class="original shop-card__original">¥{{ product.original_price }}</span>
                </div>

                <div class="shop-card__desc">
                  价格以预订页最终确认为准，可根据服务类型、机场路线及时段产生差异。
                </div>

                <div class="shop-card__footer">
                  <div class="shop-card__tips">
                    <span>支持接机</span>
                    <span>支持送机</span>
                    <span>往返可选</span>
                  </div>
                  <button class="shop-card__cta" type="button">
                    立即预订
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
  background:
    radial-gradient(circle at top, rgba(201, 169, 126, 0.12), transparent 28%),
    #f8f4ee;
}

.shop-hero {
  padding: 18px 16px 8px;
}

.shop-hero__content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 26px 22px;
  border: 1px solid rgba(201, 169, 126, 0.18);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(249, 243, 234, 0.96));
  box-shadow: 0 12px 30px rgba(74, 55, 40, 0.06);
}

.shop-hero__eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #b08b57;
}

.shop-hero__title {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
  color: #3b2b1f;
}

.shop-hero__subtitle {
  margin: 10px 0 0;
  font-size: 16px;
  color: #6d5740;
  font-weight: 600;
}

.shop-hero__desc {
  margin: 12px 0 0;
  max-width: 780px;
  font-size: 14px;
  line-height: 1.8;
  color: #7b6b5d;
}

.service-note-card {
  max-width: 1200px;
  margin: 12px auto 0;
  padding: 18px 20px;
  border: 1px solid rgba(201, 169, 126, 0.16);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 10px 26px rgba(74, 55, 40, 0.04);
}

.service-note-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.service-note-card__title {
  font-size: 18px;
  font-weight: 700;
  color: #3b2b1f;
}

.service-note-card__text {
  margin-top: 6px;
  font-size: 14px;
  line-height: 1.7;
  color: #7b6b5d;
}

.service-note-card__badge {
  flex-shrink: 0;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(201, 169, 126, 0.12);
  color: #9f7740;
  font-size: 12px;
  font-weight: 700;
}

.service-note-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.service-note-pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f6efe5;
  color: #775b38;
  font-size: 12px;
}

.shop-tabs {
  margin-top: 14px;
}

.shop-grid-wrap {
  max-width: 1280px;
  margin: 0 auto;
  padding: 16px;
}

.shop-grid {
  padding: 0;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 24px;
}

.shop-card {
  border: 1px solid rgba(201, 169, 126, 0.22);
  border-radius: 24px;
  background: #fffdf9;
  box-shadow: 0 14px 34px rgba(74, 55, 40, 0.06);
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
  padding: 18px 18px 0;
}

.shop-card__flag {
  position: absolute;
  top: 30px;
  left: 30px;
  z-index: 1;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(59, 43, 31, 0.86);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.shop-card__image,
.shop-card__placeholder {
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: 18px;
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
  padding: 18px 18px 20px;
}

.shop-card__topline {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.shop-card__badge {
  padding: 5px 10px;
  border-radius: 999px;
  background: #f4eadb;
  color: #8a6635;
  font-size: 12px;
  font-weight: 600;
}

.shop-card__badge--muted {
  background: #f7f7f5;
  color: #7d766f;
}

.shop-card__name {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.25;
  color: #3b2b1f;
}

.shop-card__meta {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #7b6b5d;
}

.shop-card__price-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
}

.shop-card__price {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
  margin-top: 0;
  font-size: 30px;
  color: #b98745;
}

.shop-card__price-suffix {
  font-size: 12px;
  font-weight: 500;
  color: #8d7b67;
}

.shop-card__original {
  font-size: 14px;
  color: #a49b90;
}

.shop-card__desc {
  margin-top: 14px;
  font-size: 13px;
  line-height: 1.75;
  color: #8a7c6e;
}

.shop-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
}

.shop-card__tips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.shop-card__tips span {
  padding: 6px 10px;
  border-radius: 999px;
  background: #faf6f0;
  color: #6f614f;
  font-size: 12px;
}

.shop-card__cta {
  min-width: 120px;
  padding: 12px 18px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 12px 22px rgba(174, 123, 67, 0.22);
}

@media (max-width: 1024px) {
  .shop-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .shop-card__name {
    font-size: 24px;
  }
}

@media (max-width: 768px) {
  .shop-hero {
    padding: 14px 12px 6px;
  }

  .shop-hero__content,
  .service-note-card {
    padding: 18px 16px;
    border-radius: 18px;
  }

  .shop-hero__title {
    font-size: 26px;
  }

  .service-note-card__header,
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
