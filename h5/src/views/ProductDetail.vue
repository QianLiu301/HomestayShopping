<template>
  <div class="page-container">
    <van-nav-bar :title="product?.name || ''" left-arrow @click-left="$router.back()" />

    <div v-if="loading" style="text-align: center; padding: 60px;">
      <van-loading size="24" />
    </div>

    <template v-else-if="product">
      <!-- Product Images -->
      <van-swipe :autoplay="3000" lazy-render class="product-swipe">
        <van-swipe-item v-for="(img, i) in product.images" :key="i">
          <img :src="img" class="swipe-img" />
        </van-swipe-item>
        <van-swipe-item v-if="!product.images?.length">
          <div class="swipe-placeholder">{{ product.name?.charAt(0) }}</div>
        </van-swipe-item>
      </van-swipe>

      <!-- Price & Name -->
      <div class="card">
        <div class="price-row">
          <span class="detail-price">¥{{ selectedPrice }}</span>
          <span v-if="product.original_price" class="detail-original">¥{{ product.original_price }}</span>
        </div>
        <h2 class="detail-name">{{ product.name }}</h2>
        <div v-if="productRating.review_count > 0" class="rating-row">
          <van-rate v-model="productRating.avg_rating" readonly allow-half size="14" />
          <span class="rating-text">{{ productRating.avg_rating }} ({{ productRating.review_count }})</span>
        </div>
      </div>

      <!-- Specs -->
      <div v-if="product.specs?.length" class="card">
        <div class="card-title">{{ t('shop.specs') }}</div>
        <div class="spec-list">
          <div
            v-for="spec in product.specs"
            :key="spec.name"
            class="spec-tag"
            :class="{ active: selectedSpec?.name === spec.name }"
            @click="selectedSpec = spec"
          >
            {{ spec.name }}
            <span v-if="spec.price !== product.price" class="spec-price">¥{{ spec.price }}</span>
          </div>
        </div>
      </div>

      <!-- Description -->
      <div v-if="product.desc" class="card">
        <div class="card-title">{{ t('shop.desc') }}</div>
        <div class="detail-desc" v-html="product.desc"></div>
      </div>

      <!-- Bottom bar -->
      <van-action-bar>
        <van-action-bar-icon icon="cart-o" :text="t('common.cart')" :badge="cartCount || undefined" @click="$router.push('/cart')" />
        <van-action-bar-button type="warning" :text="t('shop.addToCart')" @click="onAddToCart" />
        <van-action-bar-button type="danger" :text="t('shop.buyNow')" @click="onBuyNow" />
      </van-action-bar>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getProduct, getProductRating } from '../api'
import { useCartStore } from '../stores/cart'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const cart = useCartStore()

const product = ref(null)
const loading = ref(true)
const selectedSpec = ref(null)
const productRating = ref({ avg_rating: 0, review_count: 0 })

const cartCount = computed(() => cart.totalCount)
const selectedPrice = computed(() => selectedSpec.value?.price ?? product.value?.price)

onMounted(async () => {
  try {
    const res = await getProduct(route.params.id)
    product.value = res.data
    if (product.value?.specs?.length) {
      selectedSpec.value = product.value.specs[0]
    }
    // 加载评分
    const ratingRes = await getProductRating(route.params.id)
    if (ratingRes.data) productRating.value = ratingRes.data
  } catch (e) {
    showToast(e.message)
  } finally {
    loading.value = false
  }
})

function onAddToCart() {
  cart.addItem(product.value, selectedSpec.value)
  showToast({ message: t('shop.added'), icon: 'success' })
}

function onBuyNow() {
  cart.addItem(product.value, selectedSpec.value)
  router.push('/checkout')
}
</script>

<style scoped>
.product-swipe {
  height: 375px;
  background: #f8f8f8;
}

.swipe-img {
  width: 100%;
  height: 375px;
  object-fit: cover;
}

.swipe-placeholder {
  width: 100%;
  height: 375px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: var(--text-light);
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.detail-price {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
}

.detail-original {
  font-size: 14px;
  color: var(--text-light);
  text-decoration: line-through;
}

.detail-name {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.5;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
}

.rating-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.spec-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.spec-tag {
  padding: 8px 16px;
  border-radius: 20px;
  background: #f5f5f5;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.spec-tag.active {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 500;
}

.spec-price {
  margin-left: 4px;
  color: var(--accent);
  font-weight: 500;
}

.detail-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.8;
}

:deep(.van-action-bar) {
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
