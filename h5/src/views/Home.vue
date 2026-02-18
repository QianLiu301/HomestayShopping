<template>
  <div class="page-container page-with-tabbar">
    <!-- Header -->
    <div class="home-header">
      <div class="header-top">
        <h1 class="logo">Homestay</h1>
        <LangSwitch />
      </div>
      <div class="banner">
        <div class="banner-content">
          <h2>{{ t('home.banner') }}</h2>
          <p>{{ t('home.bannerSub') }}</p>
        </div>
      </div>
    </div>

    <!-- Service entries -->
    <div class="service-grid">
      <div class="service-card transfer-card" @click="$router.push('/transfer')">
        <van-icon name="logistics" size="28" color="#1a73e8" />
        <div class="service-info">
          <h3>{{ t('home.transferEntry') }}</h3>
          <p>{{ t('home.transferDesc') }}</p>
        </div>
        <van-icon name="arrow" color="#999" />
      </div>
      <div class="service-card shop-card" @click="$router.push('/shop')">
        <van-icon name="gift-o" size="28" color="#ff6b35" />
        <div class="service-info">
          <h3>{{ t('home.shopEntry') }}</h3>
          <p>{{ t('home.shopDesc') }}</p>
        </div>
        <van-icon name="arrow" color="#999" />
      </div>
    </div>

    <!-- Categories -->
    <div v-if="categories.length" class="categories-section">
      <div class="section-header">
        <span class="section-title">{{ t('shop.allCategories') }}</span>
      </div>
      <div class="category-scroll">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="category-item"
          @click="$router.push({ path: '/shop', query: { category: cat.id } })"
        >
          <div class="category-icon">{{ cat.icon || '🛍️' }}</div>
          <span>{{ cat.name }}</span>
        </div>
      </div>
    </div>

    <!-- Featured Products -->
    <div class="section-header">
      <span class="section-title">{{ t('home.featured') }}</span>
      <span class="section-more" @click="$router.push('/shop')">{{ t('common.viewMore') }} ›</span>
    </div>

    <div v-if="loading" style="text-align: center; padding: 40px;">
      <van-loading size="24" />
    </div>

    <div v-else-if="featured.length" class="product-grid">
      <div
        v-for="product in featured"
        :key="product.id"
        class="product-card"
        @click="$router.push(`/product/${product.id}`)"
      >
        <img
          v-if="product.images?.length"
          :src="product.images[0]"
          :alt="product.name"
          class="product-image"
        />
        <div v-else class="placeholder-img">{{ product.name?.charAt(0) }}</div>
        <div class="product-info">
          <div class="product-name">{{ product.name }}</div>
          <div class="product-price">
            ¥{{ product.price }}
            <span v-if="product.original_price" class="original">¥{{ product.original_price }}</span>
          </div>
        </div>
      </div>
    </div>

    <van-empty v-else :description="t('common.noData')" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getFeaturedProducts, getCategories } from '../api'
import LangSwitch from '../components/LangSwitch.vue'

const { t } = useI18n()

const featured = ref([])
const categories = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [featRes, catRes] = await Promise.all([
      getFeaturedProducts(6),
      getCategories()
    ])
    featured.value = featRes.data || []
    categories.value = catRes.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-header {
  background: linear-gradient(135deg, #1a73e8 0%, #4a9eff 100%);
  padding: 0 0 20px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
}

.banner {
  padding: 20px 16px 0;
}

.banner-content {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 24px 20px;
  backdrop-filter: blur(10px);
}

.banner-content h2 {
  font-size: 24px;
  color: #fff;
  font-weight: 700;
  margin-bottom: 6px;
}

.banner-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.service-grid {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: -10px;
}

.service-card {
  background: var(--white);
  border-radius: var(--radius);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s;
}

.service-card:active {
  transform: scale(0.98);
}

.service-info {
  flex: 1;
}

.service-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.service-info p {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 2px;
}

.categories-section {
  margin-bottom: 4px;
}

.category-scroll {
  display: flex;
  overflow-x: auto;
  padding: 0 12px 12px;
  gap: 16px;
  -webkit-overflow-scrolling: touch;
}

.category-scroll::-webkit-scrollbar {
  display: none;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-width: 64px;
  cursor: pointer;
}

.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.category-item span {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.product-grid {
  padding-bottom: 16px;
}
</style>
