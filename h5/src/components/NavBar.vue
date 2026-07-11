<template>
  <nav class="navbar" :class="{ scrolled: isScrolled, 'dark-mode': !isScrolled && isHome }">
    <div class="nav-inner">
      <div class="nav-logo" @click="scrollToTop">HOMESTAY</div>

      <div class="nav-links" :class="{ open: menuOpen }">
        <a v-for="item in navItems" :key="item.id" :href="item.href" class="nav-link" @click="onNavClick(item, $event)">{{ t(item.label) }}</a>
        <div class="nav-link mobile-lang" @click.stop="showLang = !showLang">
          <div class="mobile-lang__trigger">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            <span>{{ langLabels[currentLang] }}</span>
          </div>
          <div v-if="showLang" class="mobile-lang__dropdown">
            <div v-for="l in langs" :key="l.value" class="lang-item" :class="{ active: currentLang === l.value }" @click="switchLang(l.value)">{{ l.name }}</div>
          </div>
        </div>
      </div>

      <div class="nav-right">
        <div class="lang-btn desktop-lang" @click.stop="showLang = !showLang">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          <span>{{ langLabels[currentLang] }}</span>
          <div v-if="showLang" class="lang-dropdown">
            <div v-for="l in langs" :key="l.value" class="lang-item" :class="{ active: currentLang === l.value }" @click.stop="switchLang(l.value)">{{ l.name }}</div>
          </div>
        </div>


        <div class="cart-btn" @click="$router.push('/cart')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
          <span v-if="cartCount" class="cart-badge">{{ cartCount }}</span>
        </div>

        <div class="hamburger" @click="menuOpen = !menuOpen">
          <span :class="{ open: menuOpen }"></span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '../stores/cart'
import { useLangStore } from '../stores/lang'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const langStore = useLangStore()

const isScrolled = ref(false)
const menuOpen = ref(false)
const showLang = ref(false)
const currentLang = computed(() => langStore.current)

const isHome = computed(() => route.path === '/')
const cartCount = computed(() => cart.totalCount || 0)

const langLabels = { zh: '中文', en: 'EN', ru: 'РУ', es: 'ES' }
const langs = [
  { name: 'English', value: 'en' },
  { name: '中文', value: 'zh' },
  { name: 'Русский', value: 'ru' },
  { name: 'Español', value: 'es' }
]

const navItems = [
  { id: 'services', label: 'nav.services', href: '#services' },
  { id: 'shop', label: 'nav.shop', href: '#shop' },
  { id: 'how', label: 'nav.howItWorks', href: '#how-it-works' },
  { id: 'checkin', label: 'nav.checkin', href: '/checkin', route: true },
  { id: 'orders', label: 'nav.orders', href: '#orders' },
  { id: 'contact', label: 'nav.contact', href: '#contact' }
]

function onNavClick(item, e) {
  menuOpen.value = false
  if (item.route) {
    e.preventDefault()
    router.push(item.href)
    return
  }
  if (route.path !== '/') {
    e.preventDefault()
    router.push('/' + item.href)
  }
}

function scrollToTop() {
  if (route.path !== '/') router.push('/')
  else window.scrollTo({ top: 0, behavior: 'smooth' })
}

function switchLang(lang) {
  showLang.value = false
  menuOpen.value = false
  if (lang !== currentLang.value) langStore.setLang(lang)
}

function onScroll() { isScrolled.value = window.scrollY > 50 }
function closeDropdowns(e) {
  if (!e.target.closest('.lang-btn') && !e.target.closest('.mobile-lang')) showLang.value = false
}

onMounted(() => { window.addEventListener('scroll', onScroll); document.addEventListener('click', closeDropdowns); onScroll() })
onUnmounted(() => { window.removeEventListener('scroll', onScroll); document.removeEventListener('click', closeDropdowns) })
</script>

<style scoped>
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  transition: all 0.3s ease;
  background: var(--white);
  box-shadow: 0 1px 10px rgba(74,55,40,0.06);
}
.navbar.dark-mode { background: transparent; box-shadow: none; color: #fff; }
.navbar.scrolled { background: rgba(255,252,247,0.97); backdrop-filter: blur(20px); box-shadow: 0 1px 20px rgba(74,55,40,0.08); color: var(--text); }

.nav-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; height: var(--nav-height); display: flex; align-items: center; justify-content: space-between; }
.nav-logo { font-family: var(--font-display); font-size: 22px; font-weight: 700; letter-spacing: 2px; cursor: pointer; color: inherit; }

.nav-links { display: flex; align-items: center; gap: 32px; }
.nav-link { font-size: 13px; font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; text-decoration: none; color: inherit; transition: color 0.2s; cursor: pointer; }
.nav-link:hover { color: var(--accent); }
.mobile-lang { display: none; }

.nav-right { display: flex; align-items: center; gap: 16px; }
.lang-btn { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 13px; font-weight: 500; color: inherit; position: relative; }
.mobile-lang-btn { display: none; }
.lang-dropdown { position: absolute; top: 100%; right: 0; margin-top: 12px; background: var(--white); border-radius: 10px; box-shadow: 0 8px 30px rgba(74,55,40,0.12); overflow: hidden; min-width: 140px; }
.lang-item { padding: 12px 20px; font-size: 14px; color: var(--text); cursor: pointer; transition: background 0.2s; }
.lang-item:hover, .lang-item.active { background: var(--accent-light); color: var(--accent-dark); }

.cart-btn { position: relative; cursor: pointer; color: inherit; display: flex; align-items: center; }
.cart-badge { position: absolute; top: -6px; right: -8px; background: var(--accent); color: #fff; font-size: 10px; font-weight: 700; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }

.hamburger { display: none; width: 24px; height: 20px; cursor: pointer; position: relative; }
.hamburger span, .hamburger span::before, .hamburger span::after { display: block; width: 100%; height: 2px; background: currentColor; position: absolute; transition: all 0.3s; }
.hamburger span { top: 50%; transform: translateY(-50%); }
.hamburger span::before { content: ''; top: -7px; }
.hamburger span::after { content: ''; top: 7px; }
.hamburger span.open { background: transparent; }
.hamburger span.open::before { top: 0; transform: rotate(45deg); }
.hamburger span.open::after { top: 0; transform: rotate(-45deg); }

@media (max-width: 768px) {
  .nav-links {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    z-index: 998;
    height: calc(100dvh - var(--nav-height));
    max-height: calc(100dvh - var(--nav-height));
    padding: 20px 24px calc(28px + env(safe-area-inset-bottom));
    background: rgba(255, 252, 247, 0.98);
    backdrop-filter: blur(16px);
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;
    gap: 0;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    transform: translateY(-8px);
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    transition: opacity 0.25s ease, transform 0.25s ease, visibility 0.25s ease;
  }
  .nav-links.open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
  }
  .nav-links .nav-link {
    width: 100%;
    padding: 14px 0;
    font-size: 16px;
    color: var(--text);
    letter-spacing: 0.08em;
    border-bottom: 1px solid rgba(74, 55, 40, 0.08);
  }
  .mobile-lang {
    display: block;
    position: relative;
    width: 100%;
    padding: 14px 0 0;
    border-bottom: 1px solid rgba(74, 55, 40, 0.08);
  }
  .mobile-lang__trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    width: 100%;
    font-size: 16px;
    color: var(--text);
    letter-spacing: 0.08em;
  }
  .mobile-lang__trigger span {
    flex: 1;
  }
  .mobile-lang__dropdown {
    margin-top: 12px;
    background: var(--bg);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(74, 55, 40, 0.08);
  }
  .mobile-lang__dropdown .lang-item {
    padding: 12px 16px;
  }
  .hamburger { display: block; }
  .desktop-lang { display: none; }
  .mobile-lang-btn { display: none; }
}
</style>
