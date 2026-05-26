import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './styles/global.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// ---- 部署后的 stale chunk 自动恢复 ----
// 部署新版本后，浏览器里缓存的旧 index.html 仍引用已被删除的旧 chunk
// 文件名，懒加载会抛出 "Failed to fetch dynamically imported module"。
// 此处自动刷新一次，让浏览器拿到最新的 index.html。
const STALE_CHUNK_KEY = 'admin_stale_chunk_reload_at'
function isStaleChunkError(err) {
  const msg = (err && (err.message || err.toString())) || ''
  return (
    msg.includes('Failed to fetch dynamically imported module') ||
    msg.includes('error loading dynamically imported module') ||
    msg.includes('Importing a module script failed')
  )
}
function reloadOnce() {
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
