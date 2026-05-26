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

// ---- 部署后的 stale chunk 自动恢复 ----
// 当用户的浏览器里缓存了旧版本的 index.html，新部署后旧 chunk 文件已被
// 删除，懒加载的路由组件会抛出 "Failed to fetch dynamically imported
// module"。此时强制刷新一次，让浏览器拿到最新的 index.html 与新 chunk。
const STALE_CHUNK_KEY = 'sw_stale_chunk_reload_at'
function isStaleChunkError(err) {
  const msg = (err && (err.message || err.toString())) || ''
  return (
    msg.includes('Failed to fetch dynamically imported module') ||
    msg.includes('error loading dynamically imported module') ||
    msg.includes('Importing a module script failed')
  )
}
function reloadOnce() {
  // 防止死循环刷新：10 秒内不重复刷新
  const last = Number(sessionStorage.getItem(STALE_CHUNK_KEY) || 0)
  if (Date.now() - last < 10000) return
  sessionStorage.setItem(STALE_CHUNK_KEY, String(Date.now()))
  window.location.reload()
}

router.onError((err) => {
  if (isStaleChunkError(err)) reloadOnce()
})

window.addEventListener('unhandledrejection', (event) => {
  if (isStaleChunkError(event.reason)) {
    event.preventDefault()
    reloadOnce()
  }
})

app.mount('#app')
