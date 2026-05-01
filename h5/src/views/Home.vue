<template>
  <div class="home-page">
    <!-- ===== SECTION 1: HERO ===== -->
    <section class="hero" :style="heroStyle">
      <div class="hero-content">
        <p class="hero-label fade-in-up">{{ t('home.heroLabel') }}</p>
        <h1 class="hero-title fade-in-up delay-1">{{ t('home.heroTitle') }}</h1>
        <p class="hero-subtitle fade-in-up delay-2">{{ t('home.heroSubtitle') }}</p>
        <div class="hero-actions fade-in-up delay-3">
          <a href="#services" class="btn btn-primary">{{ t('home.bookTransfer') }}</a>
          <a href="#shop" class="btn btn-outline">{{ t('home.exploreShop') }}</a>
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
        <h2 class="section-title-lg">{{ t('home.servicesTitle') }}</h2>
        <p class="section-subtitle">{{ t('home.servicesSubtitle') }}</p>

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

    <!-- ===== SECTION 3: SHOP ===== -->
    <section id="shop" class="section shop-section">
      <div class="section-container">
        <div class="section-label">{{ t('nav.shop') }}</div>
        <h2 class="section-title-lg">{{ t('home.shopTitle') }}</h2>
        <p class="section-subtitle">{{ t('home.shopSubtitle') }}</p>

        <div class="shop-grid" :class="{ 'shop-grid-mobile': isMobile }">
          <div v-for="product in products" :key="product.id" class="shop-item" @click="$router.push(`/product/${product.id}`)">
            <div class="si-image">
              <img v-if="product.images?.length" :src="$resolveUrl(product.images[0])" :alt="product.name" />
              <div v-else class="si-placeholder">{{ product.name?.charAt(0) }}</div>
              <div class="si-overlay"><span class="si-view">{{ t('common.viewMore') }}</span></div>
            </div>
            <div class="si-info">
              <h3>{{ product.name }}</h3>
              <p class="si-price">¥{{ product.price }}</p>
            </div>
          </div>
        </div>

        <div v-if="!products.length && !loading" class="empty-placeholder"><p>{{ t('home.productsComingSoon') }}</p></div>
        <div v-else-if="isMobile" class="shop-entry-mobile">
          <button class="shop-entry-link" @click="$router.push('/shop')">{{ t('home.viewAllProducts') }} →</button>
        </div>
        <div v-else class="shop-cta"><button class="btn btn-dark" @click="$router.push('/shop')">{{ t('home.viewAllProducts') }} →</button></div>
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
          <button class="btn btn-primary orders-mobile-btn" @click="router.push('/order-query')">
            {{ t('order.query') }} →
          </button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getProducts, getVehicles, queryOrder } from '../api'
import { useCartStore } from '../stores/cart'

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
const loading = ref(true)
const activeService = ref('pickup')
const queryOrderNo = ref('')
const queryContact = ref('')

const serviceTypes = computed(() => ([
  { type: 'pickup', icon: '✈️', label: 'transfer.pickup' },
  { type: 'dropoff', icon: '🛫', label: 'transfer.dropoff' },
  { type: 'combo', icon: '🔄', label: 'transfer.combo' }
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
  { title: 'home.step2Title', desc: 'home.step2Desc', action: 'checkout' },
  { title: 'home.step3Title', desc: 'home.step3Desc', action: 'orders' },
  { title: 'home.step4Title', desc: 'home.step4Desc', action: 'orders' }
]

function goToTransfer(serviceType, vehicleId = null) {
  const query = { service_type: serviceType }
  if (vehicleId) query.vehicle_id = String(vehicleId)
  router.push({ path: '/transfer', query })
}

function goToStep(action) {
  if (action === 'shop') {
    router.push('/shop')
    return
  }

  if (action === 'checkout') {
    if (cart.items?.length) {
      router.push('/checkout')
    } else {
      router.push('/shop')
    }
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

onMounted(async () => {
  window.addEventListener('resize', onResize)
  try {
    const [productRes, vehRes] = await Promise.all([
      getProducts({ page: 1, per_page: 1000 }),
      getVehicles()
    ])
    products.value = productRes.data?.list || []
    vehicles.value = vehRes.data || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

onUnmounted(() => { window.removeEventListener('resize', onResize) })
</script>

<style scoped>
/* ===== HERO ===== */
.hero { position: relative; height: 100vh; min-height: 600px; display: flex; align-items: center; justify-content: center; overflow: hidden; text-align: center; color: #fff; background-color: var(--dark-bg); }
.hero::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(74,55,40,0.7) 0%, rgba(92,70,51,0.55) 40%, rgba(60,45,30,0.5) 100%); z-index: 1; }
.hero-content { position: relative; z-index: 2; padding: 0 24px; max-width: 800px; }
.hero-scroll-hint { z-index: 2; }
.hero-label { font-size: 13px; letter-spacing: 4px; text-transform: uppercase; color: #e8d5b8; margin-bottom: 20px; opacity: 0; }
.hero-title { font-family: var(--font-display); font-size: clamp(36px, 7vw, 72px); font-weight: 700; line-height: 1.1; margin-bottom: 20px; opacity: 0; }
.hero-subtitle { font-size: 18px; color: rgba(255,255,255,0.8); line-height: 1.6; margin-bottom: 40px; max-width: 500px; margin-left: auto; margin-right: auto; opacity: 0; }
.hero-actions { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; opacity: 0; }
.hero-scroll-hint { position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); text-align: center; color: rgba(255,255,255,0.5); font-size: 12px; letter-spacing: 2px; }
.scroll-arrow { width: 1px; height: 40px; background: rgba(255,255,255,0.3); margin: 12px auto 0; position: relative; }
.scroll-arrow::after { content: ''; position: absolute; bottom: 0; left: -3px; width: 7px; height: 7px; border-right: 1px solid rgba(255,255,255,0.5); border-bottom: 1px solid rgba(255,255,255,0.5); transform: rotate(45deg); }

/* ===== SERVICES ===== */
.services-section { background: var(--white); }
.service-types { display: flex; gap: 16px; margin: 40px 0 32px; flex-wrap: wrap; }
.service-type { flex: 1; min-width: 160px; padding: 24px 20px; border: 2px solid var(--border); border-radius: 16px; text-align: center; cursor: pointer; transition: all 0.3s; background: var(--white); }
.service-type:hover { border-color: var(--accent); background: var(--accent-light); }
.service-type.active { border-color: var(--accent); background: var(--accent-light); }
.svc-icon { font-size: 28px; margin-bottom: 8px; }
.svc-name { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.35; }
.svc-price { font-size: 20px; font-weight: 700; color: var(--accent); margin-top: 4px; }

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
.shop-section { background: var(--bg); }
.shop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-top: 40px; }
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
.si-price { font-size: 18px; font-weight: 700; color: var(--accent); }
.shop-cta { text-align: center; margin-top: 48px; }
.shop-entry-mobile { display: none; }
.shop-entry-link { background: none; border: none; padding: 0; color: var(--accent-dark); font-size: 14px; font-weight: 600; cursor: pointer; }

/* ===== HOW IT WORKS ===== */
.how-section { background: var(--white); }
.steps-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 40px; margin-top: 50px; }
.step { text-align: center; padding: 24px 16px; border-radius: 16px; transition: background 0.3s, transform 0.2s; border: none; width: 100%; background: transparent; cursor: pointer; }
.step:hover { background: var(--accent-light); transform: translateY(-2px); }
.step-number { font-family: var(--font-display); font-size: 48px; font-weight: 700; color: var(--accent); opacity: 0.4; line-height: 1; margin-bottom: 16px; }
.step-title { font-size: 18px; font-weight: 600; margin-bottom: 10px; }
.step-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }

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
.orders-mobile-btn { width: 100%; }

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

@media (max-width: 768px) {
  /* Hero mobile */
  .hero { min-height: 100vh; }
  .hero-content { padding: 0 20px; max-width: 100%; }
  .hero-title { font-size: 32px; }
  .hero-subtitle { font-size: 15px; margin-bottom: 28px; }
  .hero-actions { flex-direction: column; align-items: center; gap: 12px; }
  .hero-actions .btn { width: 200px; padding: 12px 28px; font-size: 13px; }

  /* Services mobile */
  .service-types { flex-direction: column; gap: 10px; margin: 24px 0 20px; }
  .service-type { min-width: unset; padding: 16px; display: flex; align-items: center; gap: 12px; text-align: left; border-radius: 12px; }
  .service-type .svc-icon { font-size: 24px; margin-bottom: 0; }
  .service-type .svc-name { font-size: 13px; flex: 1; line-height: 1.3; }
  .service-type .svc-price { font-size: 16px; margin-top: 0; }
  .vehicle-grid { grid-template-columns: 1fr; }
  .vc-image { height: 180px; padding: 10px; }

  /* Shop mobile */
  .shop-grid-mobile {
    display: flex;
    gap: 12px;
    margin-top: 24px;
    overflow-x: auto;
    scroll-snap-type: x proximity;
    padding: 4px 16px 10px 0;
    grid-template-columns: none;
  }
  .shop-grid-mobile::-webkit-scrollbar { display: none; }
  .shop-grid-mobile .shop-item {
    flex: 0 0 72%;
    min-width: 72%;
    scroll-snap-align: start;
    box-shadow: 0 6px 20px rgba(74,55,40,0.08);
  }
  .si-info { padding: 12px; }
  .si-info h3 { font-size: 13px; }
  .si-price { font-size: 15px; }
  .shop-cta { display: none; }
  .shop-entry-mobile {
    display: flex;
    justify-content: flex-end;
    margin-top: 14px;
  }

  /* Steps mobile - 2 columns */
  .steps-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 32px; }
  .step { padding: 16px 12px; }
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
}
</style>
