<template>
  <div class="home-page">
    <!-- ===== SECTION 1: HERO ===== -->
    <section class="hero">
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
          <div class="service-type" v-for="svc in serviceTypes" :key="svc.type" :class="{ active: activeService === svc.type }" @click="activeService = svc.type">
            <div class="svc-icon">{{ svc.icon }}</div>
            <div class="svc-name">{{ t(svc.label) }}</div>
            <div class="svc-price">{{ svc.priceLabel }}</div>
          </div>
        </div>

        <div class="vehicle-grid">
          <div v-for="v in vehicles" :key="v.id" class="vehicle-card" @click="$router.push('/transfer')">
            <div class="vc-image">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/><path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"/><path d="M5 17H3v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0H9m-6-6h15m-6 0V6"/></svg>
            </div>
            <div class="vc-info">
              <h3 class="vc-name">{{ v.name }}</h3>
              <p class="vc-desc">{{ t('transfer.seats', { n: v.seats }) }} · {{ t('transfer.luggage', { n: v.luggage_capacity }) }}</p>
              <div class="vc-bottom">
                <span class="vc-price">{{ v.extra_price > 0 ? t('transfer.extraPrice', { price: v.extra_price }) : t('transfer.noExtra') }}</span>
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

        <div class="shop-grid">
          <div v-for="product in featured" :key="product.id" class="shop-item" @click="$router.push(`/product/${product.id}`)">
            <div class="si-image">
              <img v-if="product.images?.length" :src="product.images[0]" :alt="product.name" />
              <div v-else class="si-placeholder">{{ product.name?.charAt(0) }}</div>
              <div class="si-overlay"><span class="si-view">{{ t('common.viewMore') }}</span></div>
            </div>
            <div class="si-info">
              <h3>{{ product.name }}</h3>
              <p class="si-price">¥{{ product.price }}</p>
            </div>
          </div>
        </div>

        <div v-if="!featured.length && !loading" class="empty-placeholder"><p>{{ t('home.productsComingSoon') }}</p></div>
        <div class="shop-cta"><button class="btn btn-dark" @click="$router.push('/shop')">{{ t('home.viewAllProducts') }} →</button></div>
      </div>
    </section>

    <!-- ===== SECTION 4: HOW IT WORKS ===== -->
    <section id="how-it-works" class="section how-section">
      <div class="section-container">
        <div class="section-label">{{ t('home.howLabel') }}</div>
        <h2 class="section-title-lg">{{ t('home.howTitle') }}</h2>
        <div class="steps-grid">
          <div class="step" v-for="(step, i) in steps" :key="i">
            <div class="step-number">{{ String(i + 1).padStart(2, '0') }}</div>
            <h3 class="step-title">{{ t(step.title) }}</h3>
            <p class="step-desc">{{ t(step.desc) }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== SECTION 5: ORDER QUERY ===== -->
    <section id="orders" class="section orders-section">
      <div class="section-container">
        <div class="orders-card">
          <div class="oc-left">
            <div class="section-label" style="color:rgba(255,255,255,0.7)">{{ t('nav.orders') }}</div>
            <h2 class="section-title-lg" style="color:#fff">{{ t('home.ordersTitle') }}</h2>
            <p style="color:rgba(255,255,255,0.7);margin-bottom:24px">{{ t('home.ordersSubtitle') }}</p>
          </div>
          <div class="oc-right">
            <div class="oc-form">
              <input v-model="queryOrderNo" type="text" :placeholder="t('order.inputOrderNo')" class="oc-input" />
              <input v-model="queryContact" type="text" :placeholder="t('order.inputContact')" class="oc-input" />
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
            <p>info@homestay.com</p>
          </div>
        </div>
        <div class="footer-bottom"><p>© 2024 Homestay. All rights reserved.</p></div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { showToast } from 'vant'
import { getFeaturedProducts, getVehicles, getTransferPrice, queryOrder } from '../api'

const { t } = useI18n()
const router = useRouter()

const featured = ref([])
const vehicles = ref([])
const pricing = ref(null)
const loading = ref(true)
const activeService = ref('combo')
const queryOrderNo = ref('')
const queryContact = ref('')

const serviceTypes = computed(() => {
  const p = pricing.value
  return [
    { type: 'pickup', icon: '✈️', label: 'transfer.pickup', priceLabel: p ? `¥${p.pickup_price}` : '' },
    { type: 'dropoff', icon: '🛫', label: 'transfer.dropoff', priceLabel: p ? `¥${p.dropoff_price}` : '' },
    { type: 'combo', icon: '🔄', label: 'transfer.combo', priceLabel: p ? `¥${p.combo_price}` : '' }
  ]
})

const steps = [
  { title: 'home.step1Title', desc: 'home.step1Desc' },
  { title: 'home.step2Title', desc: 'home.step2Desc' },
  { title: 'home.step3Title', desc: 'home.step3Desc' },
  { title: 'home.step4Title', desc: 'home.step4Desc' }
]

async function onQueryOrder() {
  if (!queryOrderNo.value || !queryContact.value) return showToast(t('order.inputOrderNo'))
  try {
    const res = await queryOrder({ order_no: queryOrderNo.value.trim(), contact: queryContact.value.trim() })
    router.push({ path: '/order-query', query: { data: JSON.stringify(res.data) } })
  } catch (e) { showToast(e.message) }
}

onMounted(async () => {
  try {
    const [featRes, vehRes, priceRes] = await Promise.all([getFeaturedProducts(6), getVehicles(), getTransferPrice()])
    featured.value = featRes.data || []
    vehicles.value = vehRes.data || []
    pricing.value = priceRes.data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.hero { position: relative; height: 100vh; min-height: 600px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%); overflow: hidden; text-align: center; color: #fff; }
.hero::before { content: ''; position: absolute; top: -50%; right: -20%; width: 600px; height: 600px; border-radius: 50%; background: radial-gradient(circle, rgba(200,169,126,0.15) 0%, transparent 70%); }
.hero-content { position: relative; z-index: 2; padding: 0 24px; max-width: 800px; }
.hero-label { font-size: 13px; letter-spacing: 4px; text-transform: uppercase; color: var(--accent); margin-bottom: 20px; opacity: 0; }
.hero-title { font-family: var(--font-display); font-size: clamp(36px, 7vw, 72px); font-weight: 700; line-height: 1.1; margin-bottom: 20px; opacity: 0; }
.hero-subtitle { font-size: 18px; color: rgba(255,255,255,0.7); line-height: 1.6; margin-bottom: 40px; max-width: 500px; margin-left: auto; margin-right: auto; opacity: 0; }
.hero-actions { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; opacity: 0; }
.hero-scroll-hint { position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%); text-align: center; color: rgba(255,255,255,0.5); font-size: 12px; letter-spacing: 2px; }
.scroll-arrow { width: 1px; height: 40px; background: rgba(255,255,255,0.3); margin: 12px auto 0; position: relative; }
.scroll-arrow::after { content: ''; position: absolute; bottom: 0; left: -3px; width: 7px; height: 7px; border-right: 1px solid rgba(255,255,255,0.5); border-bottom: 1px solid rgba(255,255,255,0.5); transform: rotate(45deg); }

.services-section { background: var(--white); }
.service-types { display: flex; gap: 16px; margin: 40px 0 32px; flex-wrap: wrap; }
.service-type { flex: 1; min-width: 160px; padding: 24px 20px; border: 2px solid var(--border); border-radius: 16px; text-align: center; cursor: pointer; transition: all 0.3s; }
.service-type:hover { border-color: var(--accent); }
.service-type.active { border-color: var(--accent); background: var(--accent-light); }
.svc-icon { font-size: 28px; margin-bottom: 8px; }
.svc-name { font-size: 14px; font-weight: 600; color: var(--text); }
.svc-price { font-size: 20px; font-weight: 700; color: var(--accent); margin-top: 4px; }

.vehicle-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; margin-top: 16px; }
.vehicle-card { border: 1px solid var(--border); border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s; }
.vehicle-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.08); }
.vc-image { height: 180px; background: linear-gradient(135deg, #f8f6f3, #ede8e1); display: flex; align-items: center; justify-content: center; color: var(--accent); }
.vc-info { padding: 20px; }
.vc-name { font-family: var(--font-display); font-size: 20px; font-weight: 600; margin-bottom: 6px; }
.vc-desc { font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.vc-bottom { display: flex; justify-content: space-between; align-items: center; }
.vc-price { font-size: 14px; font-weight: 600; color: var(--accent); }
.vc-book { font-size: 13px; font-weight: 600; color: var(--text); }
.vehicle-card:hover .vc-book { color: var(--accent); }

.shop-section { background: var(--bg); }
.shop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; margin-top: 40px; }
.shop-item { background: var(--white); border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s; }
.shop-item:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.08); }
.si-image { position: relative; aspect-ratio: 1; overflow: hidden; background: #f5f5f5; }
.si-image img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
.shop-item:hover .si-image img { transform: scale(1.05); }
.si-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 48px; font-family: var(--font-display); color: var(--accent); background: linear-gradient(135deg, #f8f6f3, #ede8e1); }
.si-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s; }
.shop-item:hover .si-overlay { opacity: 1; }
.si-view { color: #fff; font-size: 14px; font-weight: 600; letter-spacing: 1px; padding: 10px 24px; border: 1.5px solid #fff; border-radius: 50px; }
.si-info { padding: 16px 20px; }
.si-info h3 { font-size: 15px; font-weight: 500; line-height: 1.4; margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.si-price { font-size: 18px; font-weight: 700; color: var(--accent); }
.shop-cta { text-align: center; margin-top: 48px; }

.how-section { background: var(--white); }
.steps-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 40px; margin-top: 50px; }
.step { text-align: center; padding: 0 16px; }
.step-number { font-family: var(--font-display); font-size: 48px; font-weight: 700; color: var(--accent); opacity: 0.4; line-height: 1; margin-bottom: 16px; }
.step-title { font-size: 18px; font-weight: 600; margin-bottom: 10px; }
.step-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }

.orders-section { background: var(--bg); padding: 80px 0; }
.orders-card { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 24px; padding: 60px; display: flex; gap: 60px; align-items: center; }
.oc-left { flex: 1; }
.oc-right { flex: 0 0 360px; }
.oc-form { display: flex; flex-direction: column; gap: 12px; }
.oc-input { width: 100%; padding: 14px 20px; border: 1.5px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.1); color: #fff; font-size: 14px; font-family: var(--font-body); outline: none; transition: border-color 0.2s; }
.oc-input::placeholder { color: rgba(255,255,255,0.4); }
.oc-input:focus { border-color: var(--accent); }

.footer-section { background: #111; color: #fff; padding: 80px 0 30px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 60px; margin-bottom: 60px; }
.footer-logo { font-family: var(--font-display); font-size: 24px; font-weight: 700; letter-spacing: 2px; margin-bottom: 12px; }
.footer-tagline { color: rgba(255,255,255,0.5); font-size: 14px; line-height: 1.7; max-width: 300px; }
.footer-links h4 { font-size: 14px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 20px; color: rgba(255,255,255,0.7); }
.footer-links a, .footer-links p { display: block; font-size: 14px; color: rgba(255,255,255,0.5); text-decoration: none; margin-bottom: 12px; transition: color 0.2s; }
.footer-links a:hover { color: var(--accent); }
.footer-bottom { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 24px; text-align: center; font-size: 13px; color: rgba(255,255,255,0.3); }
.empty-placeholder { text-align: center; padding: 60px 20px; color: var(--text-light); font-size: 15px; }

@media (max-width: 768px) {
  .hero-actions { flex-direction: column; align-items: center; }
  .orders-card { flex-direction: column; padding: 36px 24px; gap: 32px; }
  .oc-right { flex: none; width: 100%; }
  .footer-grid { grid-template-columns: 1fr; gap: 32px; }
  .vehicle-grid { grid-template-columns: 1fr; }
  .shop-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .si-info { padding: 12px; }
  .si-info h3 { font-size: 13px; }
  .si-price { font-size: 15px; }
}
</style>
