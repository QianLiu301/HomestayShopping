<template>
  <a
    v-if="whatsappNumber"
    ref="fabRef"
    :href="link"
    target="_blank"
    rel="noopener"
    class="wa-fab"
    :class="{ 'wa-fab--dragging': isDragging, 'wa-fab--with-tabbar': hasTabbar && !position }"
    :style="positionStyle"
    :aria-label="t('whatsapp.fabLabel')"
    @click="onClick"
    @pointerdown="onPointerDown"
  >
    <svg class="wa-fab__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.967-.94 1.164-.173.198-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413"/>
    </svg>
  </a>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { buildWhatsAppUrl } from '../utils/whatsapp'

const props = defineProps({
  whatsappNumber: { type: String, default: '' },
  hasTabbar: { type: Boolean, default: false },
})

const route = useRoute()
const { t } = useI18n()

// ============ 拖动相关 ============
const STORAGE_KEY = 'wa_fab_position'
const DRAG_THRESHOLD_PX = 6   // 移动超过 6px 才算"拖动"，否则算"点击"
const FAB_SIZE = 50           // 按钮直径，与 CSS 同步
const EDGE_MARGIN = 8         // 距离视窗边缘最小留白

const fabRef = ref(null)
const position = ref(null)    // { x, y } 自定义位置；null = 用 CSS 默认位置（右下角）
const isDragging = ref(false)
const wasDragged = ref(false) // 这次 pointer up 后用于阻止 click

let pointerStart = null       // pointerdown 时的 client 坐标
let pointerOffset = null      // pointer 与按钮左上角的偏移

const positionStyle = computed(() => {
  if (!position.value) return {}
  return {
    left: position.value.x + 'px',
    top: position.value.y + 'px',
    right: 'auto',
    bottom: 'auto',
  }
})

function clampToViewport(pos) {
  return {
    x: Math.max(EDGE_MARGIN, Math.min(window.innerWidth - FAB_SIZE - EDGE_MARGIN, pos.x)),
    y: Math.max(EDGE_MARGIN, Math.min(window.innerHeight - FAB_SIZE - EDGE_MARGIN, pos.y)),
  }
}

function onPointerDown(e) {
  // 只响应主鼠标键 / 触摸 / 笔
  if (e.pointerType === 'mouse' && e.button !== 0) return
  if (!fabRef.value) return

  const rect = fabRef.value.getBoundingClientRect()
  pointerStart = { x: e.clientX, y: e.clientY }
  pointerOffset = { x: e.clientX - rect.left, y: e.clientY - rect.top }
  wasDragged.value = false

  document.addEventListener('pointermove', onPointerMove, { passive: false })
  document.addEventListener('pointerup', onPointerUp)
  document.addEventListener('pointercancel', onPointerUp)
}

function onPointerMove(e) {
  if (!pointerStart) return
  const dx = e.clientX - pointerStart.x
  const dy = e.clientY - pointerStart.y

  // 移动超过阈值进入拖动模式
  if (!isDragging.value && Math.sqrt(dx * dx + dy * dy) > DRAG_THRESHOLD_PX) {
    isDragging.value = true
    wasDragged.value = true
  }

  if (isDragging.value) {
    e.preventDefault() // 拖动时禁止页面滚动
    const newPos = {
      x: e.clientX - pointerOffset.x,
      y: e.clientY - pointerOffset.y,
    }
    position.value = clampToViewport(newPos)
  }
}

function onPointerUp() {
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', onPointerUp)
  document.removeEventListener('pointercancel', onPointerUp)

  if (isDragging.value) {
    // 保存位置到 localStorage，下次访问保持
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(position.value))
    } catch {}
    // 延迟取消 isDragging，让本次 click 事件能被 onClick 中的 wasDragged 拦截
    setTimeout(() => { isDragging.value = false }, 50)
  }

  pointerStart = null
  pointerOffset = null
}

function onResize() {
  if (position.value) {
    position.value = clampToViewport(position.value)
  }
}

// ============ 预填消息 + 跳转 ============
const prefillMessage = computed(() => {
  const path = route.path || ''
  const meta = route.meta || {}
  const query = route.query || {}

  if (path.startsWith('/order-result') || path.startsWith('/ticket-order-result')) {
    if (query.orderNo) return t('whatsapp.messageOrder', { orderNo: query.orderNo })
  }
  if (path.startsWith('/product/')) {
    const name = meta.productName || document.title || ''
    if (name) return t('whatsapp.messageProduct', { name })
  }
  if (path.startsWith('/tickets/') && path !== '/tickets') {
    const name = meta.attractionName || document.title || ''
    if (name) return t('whatsapp.messageTicket', { name })
  }
  if (path.startsWith('/transfer')) return t('whatsapp.messageTransfer')
  return t('whatsapp.messageGeneral')
})

const link = computed(() => buildWhatsAppUrl(props.whatsappNumber, prefillMessage.value))

function onClick(e) {
  // 如果刚刚结束的是一次拖动，不要触发跳转
  if (wasDragged.value) {
    e.preventDefault()
    wasDragged.value = false
    return
  }
  if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
    window.gtag('event', 'click_whatsapp_fab', {
      page_path: route.path,
      has_order: route.query?.orderNo ? true : false,
    })
  }
}

// ============ 生命周期 ============
onMounted(() => {
  // 恢复上次保存的位置
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (parsed && typeof parsed.x === 'number' && typeof parsed.y === 'number') {
        position.value = clampToViewport(parsed)
      }
    }
  } catch {}
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', onPointerUp)
  document.removeEventListener('pointercancel', onPointerUp)
})
</script>

<style scoped>
.wa-fab {
  position: fixed;
  right: 14px;
  bottom: 20px;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #25d366;
  color: #fff;
  box-shadow: 0 6px 16px rgba(37, 211, 102, 0.4);
  text-decoration: none;
  transition: box-shadow 0.2s ease, transform 0.15s ease;
  animation: wa-pop 0.4s ease;
  -webkit-tap-highlight-color: transparent;
  cursor: grab;
  touch-action: none; /* 关键：禁用浏览器默认手势（滚动/缩放），让我们能完全控制拖动 */
  user-select: none;
}

.wa-fab:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 10px 22px rgba(37, 211, 102, 0.5);
}

.wa-fab:active {
  transform: scale(0.95);
}

/* 拖动中：放大一点 + 强阴影 + 手型变化 */
.wa-fab--dragging {
  cursor: grabbing;
  transform: scale(1.1);
  box-shadow: 0 14px 28px rgba(37, 211, 102, 0.6);
  transition: none; /* 拖动时跟手，不要动画 */
}

/* 没自定义位置时，避开底部 tabbar */
.wa-fab--with-tabbar {
  bottom: 72px;
}

.wa-fab__icon {
  width: 24px;
  height: 24px;
  pointer-events: none; /* SVG 不拦截事件，避免 pointer 事件目标不一致 */
}

@keyframes wa-pop {
  from { opacity: 0; transform: translateY(20px) scale(0.6); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

@media (min-width: 1024px) {
  .wa-fab {
    right: 24px;
    bottom: 24px;
    width: 50px;
    height: 50px;
  }
  .wa-fab__icon {
    width: 28px;
    height: 28px;
  }
}
</style>
