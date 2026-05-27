<template>
  <div class="page-container product-detail-page">
    <van-nav-bar :title="product?.name || ''" left-arrow @click-left="$router.back()" />

    <div v-if="loading" style="text-align: center; padding: 60px;">
      <van-loading size="24" />
    </div>

    <template v-else-if="product">
      <!-- Product Images with Thumbnails -->
      <div class="product-media-section">
        <div class="main-image-wrap" :class="{ empty: !currentImage }">
          <img
            v-if="currentImage"
            :src="$resolveUrl(currentImage)"
            class="main-image"
            @click="onImageClick"
          />
          <div v-else class="image-placeholder">{{ product.name?.charAt(0) }}</div>
          <button
            v-if="product.images?.length > 1"
            class="nav-btn prev"
            @click.stop="prevImage"
          >‹</button>
          <button
            v-if="product.images?.length > 1"
            class="nav-btn next"
            @click.stop="nextImage"
          >›</button>
          <span v-if="imageList.length > 1" class="image-counter">{{ activeImage + 1 }} / {{ imageList.length }}</span>
        </div>

        <div v-if="imageList.length > 1" class="thumbnail-list">
          <div
            v-for="(img, i) in imageList"
            :key="i"
            class="thumbnail-item"
            :class="{ active: activeImage === i }"
            @click="onThumbnailClick(i)"
          >
            <img :src="$resolveUrl(img)" class="thumbnail-img" />
          </div>
        </div>
      </div>

      <!-- Price & Basic Info -->
      <div class="card info-card">
        <h2 class="detail-name">{{ product.name }}</h2>

        <div class="price-section">
          <div class="price-main">
            <span class="detail-price">¥{{ selectedPrice }}</span>
            <span v-if="product.original_price" class="detail-original">¥{{ product.original_price }}</span>
          </div>
          <div v-if="usdReferencePrice" class="price-usd">≈ {{ usdReferencePrice }}</div>
        </div>

        <div v-if="productRating.review_count > 0 || product?.sales_count > 0" class="rating-row">
          <template v-if="productRating.review_count > 0">
            <van-rate v-model="productRating.avg_rating" readonly allow-half size="14" />
            <span class="rating-text">{{ productRating.avg_rating }} ({{ productRating.review_count }} {{ t('shop.reviews') || '评价' }})</span>
          </template>
          <span v-if="product?.sales_count > 0" class="rating-text">{{ t('shop.soldCount', { count: product.sales_count }) }}</span>
        </div>
      </div>

      <!-- Specs Selection -->
      <div v-if="product.specs?.length" class="card specs-card">
        <div class="card-title">{{ t('shop.specs') || '规格' }}</div>
        <div class="spec-list">
          <div
            v-for="spec in product.specs"
            :key="spec.name"
            class="spec-tag"
            :class="{ active: selectedSpec?.name === spec.name }"
            @click="selectedSpec = spec"
          >
            <div class="spec-content">
              <span class="spec-name">{{ spec.name }}</span>
              <span v-if="spec.price !== product.price" class="spec-price">¥{{ spec.price }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Product Description -->
      <div v-if="productDescription" class="card desc-card">
        <div class="card-title">{{ t('shop.desc') || '商品详情' }}</div>
        <div class="detail-desc-box">
          <div class="detail-desc-text">{{ productDescription }}</div>
        </div>
      </div>

      <!-- Bottom Action Bar -->
      <van-action-bar>
        <van-action-bar-icon
          icon="cart-o"
          :text="t('common.cart') || '购物车'"
          :badge="cartCount || undefined"
          @click="$router.push('/cart')"
        />
        <van-action-bar-button
          type="warning"
          :text="t('shop.addToCart') || '加入购物车'"
          @click="onAddToCart"
        />
        <van-action-bar-button
          type="danger"
          :text="t('shop.buyNow') || '立即购买'"
          @click="onBuyNow"
        />
      </van-action-bar>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ImagePreview, showToast } from 'vant'
import { getProduct, getProductRating, resolveUrl } from '../api'
import { useCartStore } from '../stores/cart'
import { formatUsdReference } from '../utils/currency'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const cart = useCartStore()

const product = ref(null)
const loading = ref(true)
const selectedSpec = ref(null)
const productRating = ref({ avg_rating: 0, review_count: 0 })
const activeImage = ref(0)

const cartCount = computed(() => cart.totalCount)
const selectedPrice = computed(() => selectedSpec.value?.price ?? product.value?.price)
const imageList = computed(() => (product.value?.images?.length ? product.value.images : []))
const currentImage = computed(() => imageList.value[activeImage.value] || '')
const usdReferencePrice = computed(() => formatUsdReference(selectedPrice.value))

const productDescription = computed(() => {
  const data = product.value
  if (!data) return ''

  const currentLang = locale.value || localStorage.getItem('lang') || 'en'
  const langField = `desc_${currentLang}`
  const value = data[langField] ?? data.desc

  if (typeof value !== 'string') return ''
  return value.replace(/\r\n/g, '\n').trim()
})

onMounted(async () => {
  try {
    const res = await getProduct(route.params.id)
    product.value = res.data

    activeImage.value = 0
    if (product.value?.specs?.length) {
      selectedSpec.value = product.value.specs[0]
    }

    const ratingRes = await getProductRating(route.params.id)
    if (ratingRes.data) productRating.value = ratingRes.data
  } catch (e) {
    showToast(e.message)
  } finally {
    loading.value = false
  }
})

function prevImage() {
  if (!imageList.value.length) return
  activeImage.value = activeImage.value === 0 ? imageList.value.length - 1 : activeImage.value - 1
}

function nextImage() {
  if (!imageList.value.length) return
  activeImage.value = activeImage.value === imageList.value.length - 1 ? 0 : activeImage.value + 1
}

function onImageClick() {
  if (!imageList.value.length) return
  // 用项目统一的 resolveUrl 把相对路径补成完整 URL（生产环境图片在不同子域名/R2 上）
  ImagePreview({
    images: imageList.value.map(img => resolveUrl(img)),
    startPosition: activeImage.value,
    closeable: true,
    showIndex: true,
    maxZoom: 5,   // 显式声明最大放大倍数，确保双指捏合可放大
    minZoom: 1 / 3
  })
}

function onThumbnailClick(index) {
  // 点击未选中的缩略图：切换为主图；点击当前选中的缩略图：打开放大预览
  if (activeImage.value === index) {
    onImageClick()
  } else {
    activeImage.value = index
  }
}

function onAddToCart() {
  cart.addItem(product.value, selectedSpec.value)
  showToast(t('shop.added'))
}

function onBuyNow() {
  cart.addItem(product.value, selectedSpec.value)
  router.push('/checkout')
}
</script>

<style scoped>
.product-media-section {
  margin: 12px;
  padding: 12px;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.06);
}

.main-image-wrap {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  background: linear-gradient(180deg, #f7f8fa 0%, #eef2f6 100%);
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  aspect-ratio: 1 / 1;
}

.main-image {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  cursor: zoom-in;
}

.image-counter {
  position: absolute;
  right: 12px;
  bottom: 10px;
  z-index: 2;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  pointer-events: none;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: rgba(0, 0, 0, 0.15);
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  font-size: 22px;
  line-height: 34px;
  text-align: center;
}

.nav-btn.prev {
  left: 10px;
}

.nav-btn.next {
  right: 10px;
}

.thumbnail-list {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.thumbnail-list::-webkit-scrollbar {
  display: none;
}

.thumbnail-item {
  flex: 0 0 68px;
  height: 68px;
  padding: 3px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: #f7f8fa;
  transition: all 0.2s ease;
}

.thumbnail-item.active {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(255, 87, 34, 0.12);
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  border-radius: 9px;
  object-fit: cover;
}

.product-detail-page {
  padding-top: 0;
  padding-bottom: 70px;
}

.info-card,
.specs-card,
.desc-card {
  margin-top: 12px;
  margin-bottom: 12px;
}

.desc-card {
  margin-bottom: 24px;
}

.detail-name {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.6;
  color: var(--text-primary);
}

.price-section {
  margin-bottom: 12px;
}

.price-main {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 6px;
}

.detail-price {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.1;
}

.detail-original {
  font-size: 16px;
  color: var(--text-light);
  text-decoration: line-through;
}

.price-usd {
  font-size: 13px;
  line-height: 1.35;
  color: #9b9388;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.rating-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.spec-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.spec-tag {
  padding: 12px;
  border: 1px solid #eceff3;
  border-radius: 14px;
  background: #f9fafc;
  transition: all 0.2s ease;
}

.spec-tag.active {
  border-color: var(--accent);
  background: rgba(255, 87, 34, 0.08);
}

.spec-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.spec-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.spec-price {
  color: var(--accent);
  font-size: 13px;
  font-weight: 600;
}

.detail-desc-box {
  padding: 14px 16px;
  border-radius: 12px;
  background: #faf6ef;
  border: 1px solid #eee2d3;
}

.detail-desc-text {
  margin: 0;
  display: block;
  width: 100%;
  min-height: 24px;
  font-size: 15px;
  font-family: inherit;
  color: #4a3728;
  line-height: 1.9;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

:deep(.van-action-bar) {
  padding-bottom: env(safe-area-inset-bottom);
}

:deep(.van-action-bar-button--warning) {
  background: linear-gradient(90deg, #ffb54d 0%, #ff9800 100%);
}

:deep(.van-action-bar-button--danger) {
  background: linear-gradient(90deg, #ff6b3d 0%, #ff4d1f 100%);
}

@media (max-width: 768px) {
  .nav-btn {
    width: 30px;
    height: 30px;
    font-size: 18px;
    line-height: 30px;
  }
  .image-counter {
    font-size: 11px;
    padding: 2px 8px;
  }
}
</style>
