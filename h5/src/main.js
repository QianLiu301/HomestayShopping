import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Locale } from 'vant'
import enUS from 'vant/es/locale/lang/en-US'
import 'vant/lib/index.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { resolveUrl } from './api'
import './styles/global.css'

const app = createApp(App)
app.config.globalProperties.$resolveUrl = resolveUrl

app.use(createPinia())
app.use(router)
app.use(i18n)

// Default to English for Vant components
const savedLang = localStorage.getItem('lang') || 'en'
if (savedLang !== 'zh') {
  Locale.use('en-US', enUS)
}

app.mount('#app')
