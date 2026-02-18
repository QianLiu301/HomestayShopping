import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Locale } from 'vant'
import enUS from 'vant/es/locale/lang/en-US'
import 'vant/lib/index.css'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './styles/global.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

// Set Vant default locale
const savedLang = localStorage.getItem('lang') || 'zh'
if (savedLang !== 'zh') {
  Locale.use('en-US', enUS)
}

app.mount('#app')
