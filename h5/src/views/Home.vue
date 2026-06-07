<template>
  <div class="home-page">
    <!-- ===== SECTION 1: HERO ===== -->
    <section class="hero" :style="heroStyle">
      <div class="hero-content">
        <p class="hero-label fade-in-up">{{ t('home.heroLabel') }}</p>
        <h1 class="hero-title fade-in-up delay-1">{{ t('home.heroTitle') }}</h1>
        <p class="hero-subtitle fade-in-up delay-2">{{ t('home.heroSubtitle') }}</p>
        <div class="hero-actions fade-in-up delay-3">
          <a href="#services" class="btn btn-primary hero-action-btn hero-action-btn--primary">
            <span class="hero-action-btn__title">{{ t('home.bookTransfer') }}</span>
            <span class="hero-action-btn__hint">{{ t('home.transferCtaHint') }}</span>
          </a>
          <a href="#shop" class="btn btn-outline hero-action-btn hero-action-btn--outline">
            <span class="hero-action-btn__title">{{ t('home.exploreShop') }}</span>
            <span class="hero-action-btn__hint">{{ t('home.shopCtaHint') }}</span>
          </a>
          <button type="button" class="btn btn-outline hero-action-btn hero-action-btn--outline hero-ticket-btn" @click="goToTickets">
            <span class="hero-action-btn__title">{{ t('home.ticketsTitle') }}</span>
            <span class="hero-action-btn__hint">{{ t('home.ticketsCtaHint') }}</span>
          </button>
        </div>
      </div>
      <div class="hero-scroll-hint">
        <span>{{ t('home.scrollDown') }}</span>
        <div class="scroll-arrow"></div>
      </div>
    </section>

    <!-- ===== SECTION 2: SERVICES ===== -->
    <section id="services" class="section services-section">
      <div class="section-container">
        <div class="section-label">{{ t('nav.services') }}</div>
        <h2 class="section-title-lg">{{ homeTransportMode === 'train' ? t('home.trainServicesTitle') : t('home.servicesTitle') }}</h2>
        <p class="section-subtitle">{{ homeTransportMode === 'train' ? t('home.trainServicesSubtitle') : t('home.servicesSubtitle') }}</p>

        <div class="transport-mode-toggle">
          <button type="button" class="mode-btn" :class="{ active: homeTransportMode === 'flight' }" @click="homeTransportMode = 'flight'">
            <span class="mode-icon">✈️</span>
            <span class="mode-label">{{ t('transfer.flightMode') }}</span>
          </button>
          <button type="button" class="mode-btn" :class="{ active: homeTransportMode === 'train' }" @click="homeTransportMode = 'train'">
            <span class="mode-icon">🚄</span>
            <span class="mode-label">{{ t('transfer.trainMode') }}</span>
          </button>
        </div>

        <div class="service-types">
          <div class="service-type" v-for="svc in serviceTypes" :key="svc.type" :class="{ active: activeService === svc.type }" @click="activeService = svc.type; goToTransfer(svc.type)">
            <div class="svc-icon">{{ svc.icon }}</div>
            <div class="svc-name">{{ t(svc.label) }}</div>
          </div>
        </div>

        <div class="vehicle-grid">
          <div v-for="v in vehicles" :key="v.id" class="vehicle-card" @click="goToTransfer(activeService, v.id)">
            <div class="vc-image">
              <img v-if="v.image" :src="$resolveUrl(v.image)" :alt="v.name" />
              <svg v-else width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/><path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/><path d="M5 17H3v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0H9m-6-6h15m-6 0V6"/></svg>
            </div>
            <div class="vc-info">
              <h3 class="vc-name">{{ v.name }}</h3>
              <p class="vc-desc">{{ t('transfer.seats', { n: v.seats }) }} · {{ t('transfer.luggage', { n: v.luggage_capacity }) }}</p>
              <div class="vc-bottom">
                <span class="vc-price">{{ vehicleServicePriceLabel(v, activeService) }}</span>
                <span class="vc-book">{{ t('home.bookNow') }} →</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!vehicles.length && !loading" class="empty-placeholder">
          <p>{{ t('home.servicesComingSoon') }}</p>
        </div>
      </div>
    </section>

    <!-- ===== SECTION 2.5: WISH POOL ===== -->
    <section id="wish-pool" class="wish-section">
      <div class="section-container">
        <div class="wish-section__header">
          <div class="section-label">{{ t('wish.sectionLabel') }}</div>
          <h2 class="wish-section__title">{{ t('wish.title') }}</h2>
          <p class="wish-section__subtitle">{{ t('wish.subtitle') }}</p>
        </div>

        <div class="wish-card">
          <div v-if="!wishSubmitted" class="wish-form">
            <div class="wish-notice">⏰ {{ t('wish.tipNotice') }} <span class="wish-hint-inline">💡 {{ t('wish.contactHint') }}</span></div>

            <!-- 横向 4 列：姓名 | 电话 | 邮箱 | 期望时间 -->
            <div class="wish-row wish-row--4col">
              <div class="wish-field">
                <label class="wish-label">{{ t('wish.contactName') }} <span class="wish-required">*</span></label>
                <input
                  v-model="wishForm.contact_name"
                  type="text"
                  class="wish-input"
                  :placeholder="t('wish.contactNamePlaceholder')"
                  maxlength="50"
                />
              </div>
              <div class="wish-field">
                <label class="wish-label">{{ t('wish.contactPhone') }}</label>
                <input
                  v-model="wishForm.contact_phone"
                  type="tel"
                  class="wish-input"
                  :placeholder="t('wish.contactPhonePlaceholder')"
                  maxlength="30"
                />
              </div>
              <div class="wish-field">
                <label class="wish-label">{{ t('wish.contactEmail') }}</label>
                <input
                  v-model="wishForm.contact_email"
                  type="email"
                  class="wish-input"
                  :placeholder="t('wish.contactEmailPlaceholder')"
                  maxlength="100"
                />
              </div>
              <div class="wish-field">
                <label class="wish-label">{{ t('wish.expectedDate') }} <span class="wish-required">*</span></label>
                <input
                  :value="wishExpectedDisplay"
                  type="text"
                  class="wish-input wish-input--picker"
                  :placeholder="t('wish.expectedDatePlaceholder')"
                  readonly
                  @click="openWishPicker"
                />
              </div>
            </div>

            <!-- 日期 + 时间选择弹层（用 Vant 的多语言友好选择器） -->
            <van-popup v-model:show="wishPickerVisible" position="bottom" round teleport="body">
              <van-picker-group
                :title="t('wish.expectedDate')"
                :tabs="[t('wish.tabDate') || 'Date', t('wish.tabTime') || 'Time']"
                @confirm="onWishPickerConfirm"
                @cancel="wishPickerVisible = false"
              >
                <van-date-picker
                  v-model="wishPickerDate"
                  :min-date="wishMinJsDate"
                />
                <van-time-picker
                  v-model="wishPickerTime"
                  :columns-type="['hour', 'minute']"
                />
              </van-picker-group>
            </van-popup>

            <!-- 需求描述：全宽 -->
            <div class="wish-field">
              <label class="wish-label">{{ t('wish.content') }} <span class="wish-required">*</span></label>
              <textarea
                v-model="wishForm.content"
                rows="2"
                class="wish-textarea"
                :placeholder="t('wish.contentPlaceholder')"
                maxlength="2000"
              />
            </div>

            <!-- 底部：预算 + 提交按钮，横向排列 -->
            <div class="wish-footer">
              <div class="wish-budget-field">
                <label class="wish-label">{{ t('wish.budget') }}</label>
                <div class="wish-budget-row">
                  <input
                    v-model.number="wishForm.budget"
                    type="number"
                    min="0"
                    step="0.01"
                    class="wish-input"
                    :placeholder="t('wish.budgetPlaceholder')"
                  />
                  <span v-if="wishForm.budget" class="wish-budget-ref">{{ wishBudgetUsdRef }}</span>
                </div>
              </div>

              <button
                type="button"
                class="btn btn-primary wish-submit"
                :disabled="wishSubmitting"
                @click="onSubmitWish"
              >
                {{ wishSubmitting ? t('wish.submitting') : t('wish.submit') }}
              </button>
            </div>

            <div v-if="wishError" class="wish-error">{{ wishError }}</div>
          </div>

          <div v-else class="wish-success">
            <div class="wish-success-icon">✓</div>
            <h3 class="wish-success-title">{{ t('wish.successTitle') }}</h3>
            <p class="wish-success-desc">{{ t('wish.successDesc') }}</p>
            <button type="button" class="btn btn-outline" @click="resetWishForm">
              {{ t('wish.submitAnother') }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== SECTION 3: SHOP ===== -->
    <section id="shop" class="section shop-section">
      <div class="section-container">
        <div class="section-label">{{ t('nav.shop') }}</div>
        <h2 class="section-title-lg">{{ t('home.shopTitle') }}</h2>
        <p class="section-subtitle">{{ t('home.shopSubtitle') }}</p>

        <div class="shop-toolbar-row">
          <div class="shop-toolbar" aria-label="homepage-shop-sort">
            <button
              v-for="item in homeShopSortOptions"
              :key="item.value"
              type="button"
              class="shop-sort-chip"
              :class="{ 'shop-sort-chip--active': homeShopSort === item.value }"
              @click="onHomeShopSortChange(item.value)"
            >
              {{ item.label }}
            </button>
          </div>

          <button class="shop-toolbar-entry" type="button" @click="goToShop">
            <span class="shop-toolbar-entry__title">{{ t('home.enterShopNow') }}</span>
            <span class="shop-toolbar-entry__hint">{{ t('home.viewAllProducts') }}</span>
          </button>
        </div>

        <div class="shop-grid">
          <div v-for="product in products" :key="product.id" class="shop-item" @click="$router.push(`/product/${product.id}`)">
            <div class="si-image">
              <img v-if="product.images?.length" :src="$resolveUrl(product.images[0])" :alt="product.name" loading="lazy" decoding="async" />
              <div v-else class="si-placeholder">{{ product.name?.charAt(0) }}</div>
              <div class="si-overlay"><span class="si-view">{{ t('common.viewMore') }}</span></div>
            </div>
            <div class="si-info">
              <h3>{{ product.name }}</h3>

              <!-- 评分 + 销量小标 -->
              <div v-if="product.avg_rating || product.sales_count > 0" class="si-stats">
                <span v-if="product.avg_rating" class="si-rating">
                  ⭐ {{ product.avg_rating }}<span v-if="product.review_count" class="si-rating-count"> ({{ product.review_count }})</span>
                </span>
                <span v-if="product.sales_count > 0" class="si-sales">{{ t('shop.soldCount', { count: product.sales_count }) }}</span>
              </div>

              <div class="si-price-wrap">
                <p class="si-price">¥{{ product.price }}</p>
                <p v-if="product.price" class="si-price-ref">≈ {{ formatUsdReference(product.price) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="products.length" class="shop-cta-row">
          <button class="shop-more-btn" type="button" @click="goToShop">
            {{ t('home.viewAllProducts') }}
          </button>
        </div>

        <div v-if="!products.length && !loadingProducts" class="empty-placeholder"><p>{{ t('home.productsComingSoon') }}</p></div>
        
        <!-- 加载更多提示 -->
        <div v-if="loadingProducts && products.length" class="products-status products-status-loading">
          <span class="status-line"></span>
          <span class="status-text">
            <span class="status-dot"></span>
            {{ t('common.loading') }}
          </span>
          <span class="status-line"></span>
        </div>
        <div v-else-if="hasMoreProducts && products.length" class="load-more-trigger" ref="loadMoreTrigger">
          <!-- 滚动到此处自动加载 -->
        </div>
      </div>
    </section>

    <!-- ===== SECTION 4: HOW IT WORKS ===== -->
    <section id="how-it-works" class="section how-section">
      <div class="section-container">
        <div class="section-label">{{ t('home.howLabel') }}</div>
        <h2 class="section-title-lg">{{ t('home.howTitle') }}</h2>
        <div class="steps-grid">
          <button class="step" v-for="(step, i) in steps" :key="i" type="button" @click="goToStep(step.action)">
            <div class="step-number">{{ String(i + 1).padStart(2, '0') }}</div>
            <h3 class="step-title">{{ t(step.title) }}</h3>
            <p class="step-desc">{{ t(step.desc) }}</p>
          </button>
        </div>
      </div>
    </section>

    <!-- ===== SECTION 5: ORDER QUERY ===== -->
    <section id="orders" class="section orders-section">
      <div class="section-container">
        <div v-if="isMobile" class="orders-mobile-card">
          <div>
            <div class="section-label orders-mobile-label">{{ t('nav.orders') }}</div>
            <h2 class="section-title-lg orders-mobile-title">{{ t('home.ordersTitle') }}</h2>
            <p class="orders-mobile-subtitle">{{ t('home.ordersSubtitle') }}</p>
          </div>
          <div class="orders-mobile-form">
            <input
              v-model="queryContact"
              type="text"
              :placeholder="t('order.inputContact')"
              class="orders-mobile-input"
              autocomplete="off"
            />
            <input
              v-model="queryOrderNo"
              type="text"
              :placeholder="t('order.orderNoOptional')"
              class="orders-mobile-input"
              autocomplete="off"
            />
            <button class="btn btn-primary orders-mobile-btn" @click="onQueryOrder">
              {{ t('order.query') }} →
            </button>
          </div>
        </div>

        <div v-else class="orders-card">
          <div class="oc-left">
            <div class="section-label" style="color:rgba(255,255,255,0.7)">{{ t('nav.orders') }}</div>
            <h2 class="section-title-lg" style="color:#fff">{{ t('home.ordersTitle') }}</h2>
            <p style="color:rgba(255,255,255,0.7);margin-bottom:24px">{{ t('home.ordersSubtitle') }}</p>
          </div>
          <div class="oc-right">
            <div class="oc-form">
              <input v-model="queryContact" type="text" :placeholder="t('order.inputContact')" class="oc-input" />
              <input v-model="queryOrderNo" type="text" :placeholder="t('order.orderNoOptional')" class="oc-input" />
              <button class="btn btn-primary" style="width:100%" @click="onQueryOrder">{{ t('order.query') }}</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== SECTION 6: FOOTER ===== -->
    <footer id="contact" class="footer-section">
      <div class="section-container">
        <div class="footer-grid">
          <div class="footer-brand">
            <h3 class="footer-logo">HOMESTAY</h3>
            <p class="footer-tagline">{{ t('home.footerTagline') }}</p>
          </div>
          <div class="footer-links">
            <h4>{{ t('home.quickLinks') }}</h4>
            <a href="#services">{{ t('nav.services') }}</a>
            <a href="#shop">{{ t('nav.shop') }}</a>
            <a href="#orders">{{ t('nav.orders') }}</a>
          </div>
          <div class="footer-links">
            <h4>{{ t('nav.contact') }}</h4>
            <p>Shanghai, China</p>
            <p>
              <a
                href="mailto:support@shanghai-tour-guide.com"
                class="email-link"
                @click.prevent="openSupportEmail"
              >
                support@shanghai-tour-guide.com
              </a>
            </p>
          </div>
          <div class="footer-links">
            <h4>{{ t('legal.termsTitle') }}</h4>
            <router-link to="/privacy">{{ t('legal.privacyPolicy') }}</router-link>
            <router-link to="/terms">{{ t('legal.termsOfService') }}</router-link>
          </div>
        </div>
        <div class="footer-bottom"><p>© 2026 Homestay. All rights reserved.</p></div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getProducts, getVehicles, queryOrder, submitWish } from '../api'
import { useCartStore } from '../stores/cart'
import { formatUsdReference } from '../utils/currency'

const { t } = useI18n()
const router = useRouter()
const cart = useCartStore()

const openSupportEmail = () => {
  window.location.href = 'mailto:support@shanghai-tour-guide.com'
}

// 本地静态资源 hero 背景图
const HERO_BG_DESKTOP = '/hero-bg.jpg'
const HERO_BG_MOBILE = '/hero-bg-mobile.jpg'
const isMobile = ref(window.innerWidth <= 768)

const heroStyle = computed(() => {
  const bg = isMobile.value
    ? HERO_BG_MOBILE
    : HERO_BG_DESKTOP
  return {
    backgroundImage: `url('${bg}')`,
    backgroundSize: 'cover',
    backgroundPosition: isMobile.value ? 'center top' : 'center center',
    backgroundRepeat: 'no-repeat'
  }
})

const products = ref([])
const vehicles = ref([])
const homeShopSort = ref('default')
const loading = ref(true)
const loadingProducts = ref(false)
const HOMEPAGE_PRODUCTS_PER_PAGE_DESKTOP = 300
const HOMEPAGE_PRODUCTS_PER_PAGE_MOBILE = 24
const currentPage = ref(1)
const totalPages = ref(1)
const hasMoreProducts = computed(() => currentPage.value < totalPages.value)
const loadMoreTrigger = ref(null)
const activeService = ref('pickup')
const homeTransportMode = ref('flight')
const queryOrderNo = ref('')
const queryContact = ref('')

const serviceTypes = computed(() => {
  const isTrain = homeTransportMode.value === 'train'
  return [
    { type: 'pickup', icon: isTrain ? '🚄' : '✈️', label: isTrain ? 'transfer.trainPickup' : 'transfer.pickup' },
    { type: 'dropoff', icon: isTrain ? '🚃' : '🛫', label: isTrain ? 'transfer.trainDropoff' : 'transfer.dropoff' },
    { type: 'combo', icon: '🔄', label: isTrain ? 'transfer.trainCombo' : 'transfer.combo' }
  ]
})

const homeShopSortOptions = computed(() => ([
  { value: 'default', label: t('shop.sortDefault') },
  { value: 'sales_desc', label: t('shop.sortSales') },
  { value: 'price_asc', label: t('shop.sortPriceAsc') },
  { value: 'price_desc', label: t('shop.sortPriceDesc') },
  { value: 'newest', label: t('shop.sortNewest') }
]))

function vehicleServicePrice(vehicle, serviceType = activeService.value) {
  if (!vehicle) return 0
  if (serviceType === 'pickup') return Number(vehicle.pickup_price || 0)
  if (serviceType === 'dropoff') return Number(vehicle.dropoff_price || 0)
  return Number(vehicle.combo_price || 0)
}

function vehicleServicePriceLabel(vehicle, serviceType = activeService.value) {
  const price = vehicleServicePrice(vehicle, serviceType)
  return price > 0 ? `¥${price}` : t('transfer.priceToConfirm')
}

const steps = [
  { title: 'home.step1Title', desc: 'home.step1Desc', action: 'shop' },
  { title: 'home.step2Title', desc: 'home.step2Desc', action: 'order-lookup' },
  { title: 'home.step3Title', desc: 'home.step3Desc', action: 'orders' },
  { title: 'home.step4Title', desc: 'home.step4Desc', action: 'orders' }
]

function goToTransfer(serviceType, vehicleId = null) {
  const query = { service_type: serviceType, transport_mode: homeTransportMode.value }
  if (vehicleId) query.vehicle_id = String(vehicleId)
  router.push({ path: '/transfer', query })
}

function goToTickets() {
  router.push('/tickets')
}

function goToShop() {
  router.push('/shop')
}

function goToStep(action) {
  if (action === 'shop') {
    router.push('/shop')
    return
  }

  if (action === 'order-lookup') {
    const target = document.getElementById('orders')
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      return
    }
    router.push('/order-query')
    return
  }

  if (action === 'orders') {
    router.push('/order-query')
  }
}

async function onQueryOrder() {
  if (!queryContact.value) return showToast(t('order.inputContact'))
  const query = { contact: queryContact.value.trim() }
  if (queryOrderNo.value.trim()) query.orderNo = queryOrderNo.value.trim()
  router.push({ path: '/order-query', query })
}

const onResize = () => { isMobile.value = window.innerWidth <= 768 }

async function fetchProducts(page = 1) {
  if (loadingProducts.value) return
  loadingProducts.value = true
  try {
    const perPage = isMobile.value ? HOMEPAGE_PRODUCTS_PER_PAGE_MOBILE : HOMEPAGE_PRODUCTS_PER_PAGE_DESKTOP
    const res = await getProducts({ page, per_page: perPage, sort: homeShopSort.value })
    const list = res.data?.list || []

    if (page === 1) {
      products.value = list
    } else {
      products.value.push(...list)
    }

    currentPage.value = res.data?.page || 1
    totalPages.value = res.data?.pages || 1
  } catch (e) {
    console.error(e)
  } finally {
    loadingProducts.value = false
    await nextTick()
    setupObserver()
  }
}

async function loadMoreProducts() {
  if (!hasMoreProducts.value || loadingProducts.value) return
  await fetchProducts(currentPage.value + 1)
}

async function reloadHomepageProducts() {
  currentPage.value = 1
  totalPages.value = 1
  products.value = []
  teardownObserver()
  await fetchProducts(1)
}

async function onHomeShopSortChange(sortValue) {
  if (loadingProducts.value || homeShopSort.value === sortValue) return
  homeShopSort.value = sortValue
  await reloadHomepageProducts()
}

let observer = null

function teardownObserver() {
  if (observer) {
    observer.disconnect()
    observer = null
  }
}

function setupObserver() {
  teardownObserver()

  if (!loadMoreTrigger.value || !hasMoreProducts.value || loadingProducts.value) return

  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting) {
        teardownObserver()
        loadMoreProducts()
      }
    },
    { rootMargin: '1200px 0px' }
  )

  observer.observe(loadMoreTrigger.value)
}

onMounted(async () => {
  window.addEventListener('resize', onResize)

  try {
    const vehRes = await getVehicles()
    vehicles.value = vehRes.data || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }

  await fetchProducts(1)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  teardownObserver()
})

// ============ 许愿池 ============
const wishForm = ref({
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  content: '',
  expected_date: '',  // 格式: 'YYYY-MM-DDTHH:MM'，发给后端
  budget: null,
})
const wishSubmitting = ref(false)
const wishSubmitted = ref(false)
const wishError = ref('')

// Vant date/time picker 状态
const wishPickerVisible = ref(false)
const _pad = n => String(n).padStart(2, '0')

// 最早可选时间：当前时间 + 24 小时
function _wishDefaultPickerDate() {
  const d = new Date(Date.now() + 24 * 60 * 60 * 1000)
  return [
    String(d.getFullYear()),
    _pad(d.getMonth() + 1),
    _pad(d.getDate()),
  ]
}
function _wishDefaultPickerTime() {
  const d = new Date(Date.now() + 24 * 60 * 60 * 1000)
  return [_pad(d.getHours()), _pad(d.getMinutes())]
}

// 当前打开 picker 时显示的值（YYYY/MM/DD 字符串数组 + HH/MM 字符串数组）
const wishPickerDate = ref(_wishDefaultPickerDate())
const wishPickerTime = ref(_wishDefaultPickerTime())

// 最小日期（Vant 用原生 Date）
const wishMinJsDate = computed(() => new Date(Date.now() + 24 * 60 * 60 * 1000))

// 输入框里显示的"已选时间"字符串（多语言友好，纯数字格式）
const wishExpectedDisplay = computed(() => {
  if (!wishForm.value.expected_date) return ''
  // expected_date 形如 '2026-05-28T14:30'
  return wishForm.value.expected_date.replace('T', ' ')
})

function openWishPicker() {
  // 如果用户没选过，重置到默认值（now+24h）
  if (!wishForm.value.expected_date) {
    wishPickerDate.value = _wishDefaultPickerDate()
    wishPickerTime.value = _wishDefaultPickerTime()
  }
  wishPickerVisible.value = true
}

function onWishPickerConfirm() {
  const [y, m, d] = wishPickerDate.value
  const [h, mi] = wishPickerTime.value
  wishForm.value.expected_date = `${y}-${m}-${d}T${h}:${mi}`
  wishPickerVisible.value = false
}

const wishBudgetUsdRef = computed(() => {
  const v = Number(wishForm.value.budget)
  if (!v || v <= 0) return ''
  return t('wish.budgetRef', { usd: formatUsdReference(v) })
})

function resetWishForm() {
  wishForm.value = {
    contact_name: '',
    contact_phone: '',
    contact_email: '',
    content: '',
    expected_date: '',
    budget: null,
  }
  wishSubmitted.value = false
  wishError.value = ''
}

async function onSubmitWish() {
  wishError.value = ''
  const f = wishForm.value
  if (!f.contact_name?.trim()) {
    wishError.value = t('wish.errContactRequired')
    return
  }
  if (!f.contact_phone?.trim() && !f.contact_email?.trim()) {
    wishError.value = t('wish.errContactWay')
    return
  }
  if (!f.content?.trim() || f.content.trim().length < 10) {
    wishError.value = t('wish.errContentTooShort')
    return
  }
  if (!f.expected_date) {
    wishError.value = t('wish.errExpectedTooSoon')
    return
  }
  const expectedMs = new Date(f.expected_date).getTime()
  if (isNaN(expectedMs) || expectedMs < Date.now() + 24 * 60 * 60 * 1000 - 60_000) {
    wishError.value = t('wish.errExpectedTooSoon')
    return
  }

  wishSubmitting.value = true
  try {
    await submitWish({
      contact_name: f.contact_name.trim(),
      contact_phone: f.contact_phone?.trim() || '',
      contact_email: f.contact_email?.trim() || '',
      content: f.content.trim(),
      expected_date: f.expected_date,
      budget: f.budget || null,
      budget_currency: 'CNY',
      lang: localStorage.getItem('lang') || 'zh',
    })
    wishSubmitted.value = true
  } catch (e) {
    wishError.value = e?.message || 'Submit failed'
    showToast(wishError.value)
  } finally {
    wishSubmitting.value = false
  }
}
</script>

<style scoped>
/* ===== HERO ===== */
.hero { position: relative; height: 100vh; min-height: 600px; display: flex; align-items: center; justify-content: center; overflow: hidden; text-align: center; color: #fff; background-color: var(--dark-bg); }
.hero::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(74,55,40,0.7) 0%, rgba(92,70,51,0.55) 40%, rgba(60,45,30,0.5) 100%); z-index: 1; }
.hero-content { position: relative; z-index: 2; padding: 0 24px; max-width: 800px; }
.hero-scroll-hint { z-index: 2; }
.hero-label { font-size: 13px; letter-spacing: 4px; text-transform: uppercase; color: #e8d5b8; margin-bottom: 20px; opacity: 0; }
.hero-title { font-family: var(--font-display); font-size: clamp(36px, 7vw, 72px); font-weight: 700; line-height: 1.1; margin-bottom: 20px; opacity: 0; }
.hero-subtitle { font-size: 18px; color: rgba(255,255,255,0.8); line-height: 1.6; margin-bottom: 34px; max-width: 500px; margin-left: auto; margin-right: auto; opacity: 0; }
.hero-actions { display: flex; gap: 18px; justify-content: center; align-items: stretch; flex-wrap: wrap; opacity: 0; }
.hero-actions .btn { min-width: 220px; }
.hero-action-btn {
  white-space: normal;
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  text-align: center;
  padding-top: 10px;
  padding-bottom: 10px;
}
.hero-action-btn__title { display: block; font-size: 16px; font-weight: 700; line-height: 1.1; }
.hero-action-btn__hint { display: block; font-size: 11px; line-height: 1.35; color: rgba(255,255,255,0.72); letter-spacing: 0.02em; }
.hero-action-btn--primary .hero-action-btn__hint { color: rgba(255,255,255,0.86); }
.hero-action-btn--outline:hover,
.hero-action-btn--outline:focus-visible,
.hero-action-btn--outline:active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(200,169,126,0.4);
}
.hero-action-btn--outline:hover .hero-action-btn__hint,
.hero-action-btn--outline:focus-visible .hero-action-btn__hint,
.hero-action-btn--outline:active .hero-action-btn__hint {
  color: rgba(255,255,255,0.86);
}
.hero-scroll-hint { position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); text-align: center; color: rgba(255,255,255,0.5); font-size: 12px; letter-spacing: 2px; }
.scroll-arrow { width: 1px; height: 40px; background: rgba(255,255,255,0.3); margin: 12px auto 0; position: relative; }
.scroll-arrow::after { content: ''; position: absolute; bottom: 0; left: -3px; width: 7px; height: 7px; border-right: 1px solid rgba(255,255,255,0.5); border-bottom: 1px solid rgba(255,255,255,0.5); transform: rotate(45deg); }

/* ===== SERVICES ===== */
.services-section { background: var(--white); }
.transport-mode-toggle { display: flex; gap: 12px; padding: 4px; background: #f5f5f5; border-radius: 12px; margin: 30px 0 0; max-width: 400px; }
.mode-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 16px; border: none; border-radius: 10px; background: transparent; font-size: 15px; font-weight: 500; color: #666; cursor: pointer; transition: all 0.25s ease; }
.mode-btn.active { background: #fff; color: var(--accent, #1a73e8); font-weight: 700; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.mode-icon { font-size: 20px; }
.mode-label { font-size: 14px; }
.service-types { display: flex; gap: 16px; margin: 36px 0 28px; flex-wrap: wrap; }
.service-type { flex: 1; min-width: 160px; padding: 18px 20px; border: 2px solid var(--border); border-radius: 16px; text-align: center; cursor: pointer; transition: all 0.3s; background: var(--white); }
.service-type:hover { border-color: var(--accent); background: var(--accent-light); }
.service-type.active { border-color: var(--accent); background: var(--accent-light); }
.svc-icon { font-size: 24px; margin-bottom: 4px; line-height: 1; }
.svc-name { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.25; }
.svc-price { font-size: 20px; font-weight: 700; color: var(--accent); margin-top: 2px; }

.vehicle-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; margin-top: 16px; }
.vehicle-card { border: 1px solid var(--border); border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s; background: var(--white); }
.vehicle-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(74,55,40,0.1); }
.vc-image { height: 220px; background: linear-gradient(135deg, var(--accent-light), var(--warm-bg)); display: flex; align-items: center; justify-content: center; color: var(--accent); overflow: hidden; padding: 12px; }
.vc-image img { width: 100%; height: 100%; object-fit: contain; border-radius: 12px; background: #fff; }
.vc-info { padding: 20px; }
.vc-name { font-family: var(--font-display); font-size: 20px; font-weight: 600; margin-bottom: 6px; }
.vc-desc { font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.vc-bottom { display: flex; justify-content: space-between; align-items: center; }
.vc-price { font-size: 14px; font-weight: 600; color: var(--accent); }
.vc-book { font-size: 13px; font-weight: 600; color: var(--text); }
.vehicle-card:hover .vc-book { color: var(--accent); }

/* ===== SHOP ===== */
.shop-section { background: var(--bg); padding-bottom: 40px; }
.shop-toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 26px;
}
.shop-toolbar {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 0;
}
.shop-sort-chip {
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid rgba(200, 169, 126, 0.42);
  background: rgba(255, 252, 247, 0.92);
  color: #4a3728;  /* 显式声明深色文字，防止被继承覆盖 */
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: all 0.25s ease;
  -webkit-tap-highlight-color: transparent;  /* 禁用 iOS 默认点击高亮闪烁 */
  -webkit-appearance: none;
  appearance: none;
}
.shop-sort-chip:hover {
  border-color: rgba(200, 169, 126, 0.72);
  background: #fff;
  color: #4a3728;  /* hover 时保持深色 */
  transform: translateY(-1px);
}
.shop-sort-chip--active {
  color: #fff;
  border-color: var(--accent);
  /* 同时声明 background-color 作为渐变 fallback，防止白底白字 */
  background-color: #b98745;
  background-image: linear-gradient(135deg, #c69a62, #ae7b43);
  box-shadow: 0 10px 24px rgba(174, 123, 67, 0.16);
}
/* 移动端：active + hover 同时存在时（点击后焦点保持）确保对比度 */
.shop-sort-chip--active:hover,
.shop-sort-chip--active:focus {
  color: #fff;
  background-color: #b98745;
  background-image: linear-gradient(135deg, #c69a62, #ae7b43);
}
.shop-toolbar-entry {
  flex: 0 0 auto;
  display: inline-flex;
  flex-direction: column;
  justify-content: center;
  gap: 3px;
  min-width: 180px;
  padding: 12px 18px;
  border: 1px solid rgba(200, 169, 126, 0.45);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 252, 247, 0.98), rgba(248, 241, 231, 0.98));
  color: var(--text);
  box-shadow: 0 10px 24px rgba(74, 55, 40, 0.06);
  cursor: pointer;
  transition: all 0.25s ease;
}
.shop-toolbar-entry:hover {
  transform: translateY(-2px);
  border-color: rgba(200, 169, 126, 0.72);
  box-shadow: 0 14px 30px rgba(74, 55, 40, 0.1);
}
.shop-toolbar-entry__title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-dark);
}
.shop-toolbar-entry__hint {
  font-size: 12px;
  color: var(--text-secondary);
}
.shop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-top: 28px; }
.shop-item { background: var(--white); border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s; }
.shop-item:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(74,55,40,0.1); }
.si-image { position: relative; aspect-ratio: 1; overflow: hidden; background: var(--warm-bg); }
.si-image img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.shop-item:hover .si-image img { transform: scale(1.05); }
.si-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 48px; font-family: var(--font-display); color: var(--accent); background: linear-gradient(135deg, var(--accent-light), var(--warm-bg)); }
.si-overlay { position: absolute; inset: 0; background: rgba(74,55,40,0.45); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s; }
.shop-item:hover .si-overlay { opacity: 1; }
.si-view { color: #fff; font-size: 14px; font-weight: 600; letter-spacing: 1px; padding: 10px 24px; border: 1.5px solid #fff; border-radius: 50px; }
.si-info { padding: 16px 20px; }
.si-info h3 { font-size: 15px; font-weight: 500; line-height: 1.4; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.si-stats {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  flex-wrap: wrap;
}
.si-rating {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #fff7e6;
  color: #d97706;
  font-weight: 600;
}
.si-rating-count { color: #8a6635; font-weight: 500; }
.si-sales { color: #9b9388; }
.si-price-wrap { display: flex; flex-direction: column; gap: 4px; }
.si-price { margin: 0; font-size: 18px; font-weight: 700; color: var(--accent); }
.si-price-ref { margin: 0; font-size: 12px; line-height: 1.25; color: #9b9388; }
.shop-cta-row {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}
.shop-more-btn {
  min-width: 180px;
  padding: 12px 28px;
  border-radius: 999px;
  border: 1px solid rgba(200, 169, 126, 0.45);
  background: rgba(255, 252, 247, 0.92);
  color: var(--text);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 10px 24px rgba(74, 55, 40, 0.06);
}
.shop-more-btn:hover {
  color: var(--accent-dark);
  border-color: rgba(200, 169, 126, 0.72);
  background: #fff;
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(74, 55, 40, 0.1);
}

/* ===== HOW IT WORKS ===== */
.how-section { background: var(--warm-bg); padding-top: 56px; padding-bottom: 84px; }
.steps-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 40px; margin-top: 42px; }
.step {
  text-align: center;
  padding: 24px 16px;
  border-radius: 18px;
  transition: background 0.28s, transform 0.22s, box-shadow 0.28s, border-color 0.28s;
  border: 1px solid transparent;
  width: 100%;
  background: transparent;
  cursor: pointer;
}
.step:hover,
.step:focus-visible,
.step:active {
  background: rgba(255, 252, 247, 0.78);
  border-color: rgba(200, 169, 126, 0.24);
  box-shadow: 0 16px 36px rgba(74, 55, 40, 0.08);
  transform: translateY(-4px);
}
.step:focus-visible { outline: none; }
.step-number {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 700;
  color: var(--accent);
  opacity: 0.4;
  line-height: 1;
  margin-bottom: 16px;
  transition: color 0.28s, opacity 0.28s, transform 0.28s;
}
.step-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  transition: color 0.28s;
}
.step-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  transition: color 0.28s;
}
.step:hover .step-number,
.step:focus-visible .step-number,
.step:active .step-number {
  color: var(--accent-dark);
  opacity: 0.82;
  transform: translateY(-2px);
}
.step:hover .step-title,
.step:focus-visible .step-title,
.step:active .step-title {
  color: var(--accent-dark);
}
.step:hover .step-desc,
.step:focus-visible .step-desc,
.step:active .step-desc {
  color: var(--text);
}

/* ===== ORDER QUERY ===== */
.orders-section { background: var(--warm-bg); padding: 80px 0; }
.orders-card, .orders-mobile-card { background: linear-gradient(135deg, var(--dark-bg) 0%, var(--warm-hero) 100%); }
.orders-card { border-radius: 24px; padding: 60px; display: flex; gap: 60px; align-items: center; }
.orders-mobile-card { border-radius: 20px; padding: 28px 20px; }
.oc-left { flex: 1; }
.oc-right { flex: 0 0 360px; }
.oc-form { display: flex; flex-direction: column; gap: 12px; }
.oc-input { width: 100%; padding: 14px 20px; border: 1.5px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.1); color: #fff; font-size: 14px; font-family: var(--font-body); outline: none; transition: border-color 0.2s; }
.oc-input::placeholder { color: rgba(255,255,255,0.4); }
.oc-input:focus { border-color: var(--accent); }
.orders-mobile-label { color: rgba(255,255,255,0.7); margin-bottom: 14px; }
.orders-mobile-title { color: #fff; margin-bottom: 10px; font-size: 28px; }
.orders-mobile-subtitle { color: rgba(255,255,255,0.72); margin-bottom: 18px; line-height: 1.7; font-size: 14px; }
.orders-mobile-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.orders-mobile-input {
  width: 100%;
  padding: 12px 16px;
  border: 1.5px solid rgba(255, 255, 255, 0.22);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 14px;
  font-family: var(--font-body);
  outline: none;
  transition: border-color 0.2s;
  -webkit-appearance: none;
  appearance: none;
  box-sizing: border-box;
}
.orders-mobile-input::placeholder { color: rgba(255, 255, 255, 0.45); }
.orders-mobile-input:focus { border-color: var(--accent); }
.orders-mobile-btn { width: 100%; margin-top: 4px; }

/* ===== FOOTER ===== */
.footer-section { background: var(--dark-bg); color: #fff; padding: 80px 0 30px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 60px; margin-bottom: 60px; }
.footer-logo { font-family: var(--font-display); font-size: 24px; font-weight: 700; letter-spacing: 2px; margin-bottom: 12px; color: var(--accent); }
.footer-tagline { color: rgba(255,255,255,0.6); font-size: 14px; line-height: 1.7; max-width: 300px; }
.footer-links h4 { font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 20px; color: var(--accent); }
.footer-links a, .footer-links p { display: block; font-size: 14px; color: rgba(255,255,255,0.55); text-decoration: none; margin-bottom: 12px; transition: color 0.2s; }
.footer-links a:hover { color: var(--accent); }
.email-link { display: inline-block; color: inherit; text-decoration: underline !important; cursor: pointer; word-break: break-word; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px; text-align: center; font-size: 13px; color: rgba(255,255,255,0.3); }
.empty-placeholder { text-align: center; padding: 60px 20px; color: var(--text-light); font-size: 15px; }

/* 加载更多和无更多商品提示 */
.products-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 28px;
  padding: 8px 0 4px;
  color: var(--text-light);
}

.status-line {
  flex: 1;
  max-width: 120px;
  height: 1px;
  background: linear-gradient(90deg, rgba(216, 161, 102, 0), rgba(216, 161, 102, 0.35), rgba(216, 161, 102, 0));
}

.status-text {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  letter-spacing: 0.08em;
  color: var(--text-light);
  white-space: nowrap;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--accent);
  box-shadow: 0 0 0 6px rgba(216, 161, 102, 0.12);
  animation: statusPulse 1.4s ease-in-out infinite;
}

.products-status-finished .status-text {
  color: var(--text-secondary);
}

.load-more-trigger {
  height: 1px;
  visibility: hidden;
}

@keyframes statusPulse {
  0%, 100% {
    opacity: 0.55;
    transform: scale(0.9);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  /* Hero mobile */
  .hero { min-height: 100vh; }
  .hero-content { padding: 0 20px; max-width: 100%; }
  .hero-title { font-size: 32px; }
  .hero-subtitle { font-size: 15px; margin-bottom: 24px; }
  .hero-actions { flex-direction: column; align-items: center; gap: 12px; }
  .hero-actions .btn { width: min(220px, 100%); min-width: 0; padding: 12px 28px; font-size: 13px; }
  .hero-action-btn { gap: 3px; padding-top: 11px; padding-bottom: 11px; }
  .hero-action-btn__title { font-size: 15px; }
  .hero-action-btn__hint { font-size: 10px; line-height: 1.3; }
 
  .shop-section { padding-bottom: 24px; }
  .how-section { padding-top: 36px; padding-bottom: 48px; }
 
  /* Services mobile */
  .transport-mode-toggle { max-width: 100%; margin-top: 20px; }
  .service-types { flex-direction: column; gap: 10px; margin: 24px 0 20px; }
  .service-type { min-width: unset; padding: 16px; display: flex; align-items: center; gap: 12px; text-align: left; border-radius: 12px; }
  .service-type .svc-icon { font-size: 24px; margin-bottom: 0; }
  .service-type .svc-name { font-size: 13px; flex: 1; line-height: 1.3; }
  .service-type .svc-price { font-size: 16px; margin-top: 0; }
  .vehicle-grid { grid-template-columns: 1fr; }
  .vc-image { height: 180px; padding: 10px; }

  /* Shop mobile */
  .shop-toolbar-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    margin-top: 20px;
  }
  .shop-toolbar {
    gap: 8px;
    margin-top: 0;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 4px;
    -webkit-overflow-scrolling: touch;
  }
  .shop-toolbar::-webkit-scrollbar { display: none; }
  .shop-sort-chip {
    flex: 0 0 auto;
    padding: 8px 12px;
    font-size: 12px;
  }
  .shop-toolbar-entry {
    width: 100%;
    min-width: 0;
    padding: 12px 14px;
    border-radius: 16px;
  }
  .shop-toolbar-entry__title {
    font-size: 13px;
  }
  .shop-toolbar-entry__hint {
    font-size: 11px;
  }
  .shop-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 24px;
  }
  .si-info { padding: 12px; }
  .si-info h3 { font-size: 13px; }
  .si-price { font-size: 15px; }
  .si-price-ref { font-size: 11px; }
  .products-status {
    gap: 10px;
    margin-top: 20px;
    padding-bottom: 0;
  }
  .status-line { max-width: none; }
  .status-text {
    font-size: 12px;
    letter-spacing: 0.04em;
  }

  .shop-cta-row { margin-top: 20px; }
  .shop-more-btn {
    width: 100%;
    max-width: 220px;
    padding: 11px 20px;
    font-size: 13px;
  }

  /* Steps mobile - 2 columns */
  .steps-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 32px; }
  .step { padding: 16px 12px; }
  .step:first-child {
    background: rgba(255, 252, 247, 0.82);
    border-color: rgba(200, 169, 126, 0.28);
    box-shadow: 0 12px 28px rgba(74, 55, 40, 0.07);
  }
  .step:first-child .step-number {
    color: var(--accent-dark);
    opacity: 0.82;
  }
  .step:first-child .step-title { color: var(--accent-dark); }
  .step:first-child .step-desc { color: var(--text); }
  .step-number { font-size: 36px; margin-bottom: 10px; }
  .step-title { font-size: 15px; margin-bottom: 6px; }
  .step-desc { font-size: 13px; }

  /* Orders mobile */
  .orders-section { padding: 40px 0 20px; }
  .orders-mobile-card { margin-bottom: 8px; }
  .orders-mobile-title { font-size: 24px; }

  /* Footer mobile */
  .footer-section { padding: 48px 0 24px; }
  .footer-grid { grid-template-columns: 1fr; gap: 28px; margin-bottom: 32px; }

  /* Wish mobile */
  .wish-section {
    margin-top: -20px;
    padding: 8px 0 24px;
  }
  .wish-card { padding: 14px; border-radius: 12px; }
  .wish-row--4col { grid-template-columns: 1fr; gap: 10px; }
  .wish-footer { grid-template-columns: 1fr; gap: 12px; }
  .wish-submit { width: 100%; min-width: 0; }
  .wish-section__title { font-size: 22px; }
  .wish-section__subtitle { font-size: 13px; }
  .wish-section__header :deep(.section-label) {
    font-size: 15px;
    letter-spacing: 3px;
  }
}

/* ============ 许愿池（横幅版） ============ */
.wish-section {
  background: var(--white);
  /* 上移：负 margin 抵消上一 section 的 100px 底部 padding */
  margin-top: -70px;
  padding: 12px 0 32px;
  position: relative;
}

.wish-section__header {
  text-align: center;
  margin-bottom: 18px;
}

/* "许愿池" 三个字单独加大、加粗 */
.wish-section__header :deep(.section-label) {
  font-size: 18px;
  letter-spacing: 4px;
  gap: 14px;
}

.wish-section__header :deep(.section-label::after) {
  width: 56px;
  height: 2px;
}

.wish-section__title {
  font-family: var(--font-display);
  font-size: 30px;
  line-height: 1.25;
  margin: 12px 0 8px;
  color: var(--text);
}

.wish-section__subtitle {
  font-size: 15px;
  line-height: 1.55;
  color: var(--text-secondary);
  margin: 0 auto;
  max-width: 620px;
}

/* 横幅卡片：稍微大一点 */
.wish-card {
  max-width: 1020px;
  margin: 16px auto 0;
  padding: 22px 26px;
  border-radius: 16px;
  background: var(--bg);
  border: 1px solid rgba(201, 169, 126, 0.18);
  box-shadow: 0 8px 22px rgba(74, 55, 40, 0.05);
}

/* 可点击的"时间选择"输入框 */
.wish-input--picker {
  cursor: pointer;
  background: #fff url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%238d7b67' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'%3E%3C/rect%3E%3Cline x1='16' y1='2' x2='16' y2='6'%3E%3C/line%3E%3Cline x1='8' y1='2' x2='8' y2='6'%3E%3C/line%3E%3Cline x1='3' y1='10' x2='21' y2='10'%3E%3C/line%3E%3C/svg%3E") no-repeat right 10px center;
  padding-right: 32px;
}

.wish-notice {
  margin-bottom: 12px;
  padding: 8px 14px;
  border-radius: 8px;
  background: #fff7e6;
  color: #a06b1f;
  /* 字稍大 */
  font-size: 13px;
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
}

.wish-hint-inline {
  color: #8d7b67;
}

.wish-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 4 列横向布局 */
.wish-row--4col {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.wish-field {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.wish-label {
  display: block;
  margin-bottom: 5px;
  /* 字稍大 */
  font-size: 13px;
  font-weight: 600;
  color: #4a3728;
}

.wish-required {
  color: #d9534f;
  margin-left: 2px;
}

.wish-input,
.wish-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(201, 169, 126, 0.35);
  border-radius: 8px;
  background: #fff;
  /* 输入文字加大 */
  font-size: 14px;
  color: #3b2b1f;
  font-family: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.wish-input:focus,
.wish-textarea:focus {
  outline: none;
  border-color: #c69a62;
  box-shadow: 0 0 0 3px rgba(198, 154, 98, 0.12);
}

.wish-textarea {
  resize: vertical;
  line-height: 1.55;
  min-height: 60px;
}

/* 底部：预算（左） + 提交按钮（右） */
.wish-footer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  align-items: end;
}

.wish-budget-field {
  display: flex;
  flex-direction: column;
}

.wish-budget-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.wish-budget-row .wish-input {
  flex: 1;
}

.wish-budget-ref {
  flex-shrink: 0;
  font-size: 13px;
  color: #8d7b67;
  font-weight: 500;
  white-space: nowrap;
}

.wish-error {
  padding: 9px 12px;
  border-radius: 8px;
  background: #fef0f0;
  color: #d9534f;
  font-size: 13px;
}

.wish-submit {
  min-width: 150px;
  height: 42px;
  padding: 0 24px;
  /* 按钮字加大 */
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
}

.wish-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.wish-success {
  text-align: center;
  padding: 16px 0;
}

.wish-success-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #c69a62, #ae7b43);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
}

.wish-success-title {
  margin: 0 0 6px;
  font-size: 17px;
  color: #3b2b1f;
}

.wish-success-desc {
  margin: 0 0 16px;
  font-size: 13px;
  color: #6e5f51;
  line-height: 1.55;
}

/* 中等屏幕：4 列变 2 列 */
@media (max-width: 900px) {
  .wish-card { max-width: 720px; }
  .wish-row--4col { grid-template-columns: 1fr 1fr; }
}
</style>
