<template>
  <a
    v-if="whatsappNumber"
    :href="link"
    target="_blank"
    rel="noopener"
    class="wa-fab"
    :class="{ 'wa-fab--with-tabbar': hasTabbar }"
    :aria-label="t('whatsapp.fabLabel')"
    @click="onClick"
  >
    <svg class="wa-fab__icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.967-.94 1.164-.173.198-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413"/>
    </svg>
  </a>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { buildWhatsAppUrl } from '../utils/whatsapp'

const props = defineProps({
  // 客服 WhatsApp 号（从 settings 取的）
  whatsappNumber: { type: String, default: '' },
  // 是否页面底部有 TabBar，需要让按钮上浮一点不被遮
  hasTabbar: { type: Boolean, default: false },
})

const route = useRoute()
const { t } = useI18n()

// 根据当前路由生成上下文相关的预填消息
const prefillMessage = computed(() => {
  const path = route.path || ''
  const meta = route.meta || {}
  const query = route.query || {}

  // 订单结果页：带上订单号
  if (path.startsWith('/order-result') || path.startsWith('/ticket-order-result')) {
    if (query.orderNo) return t('whatsapp.messageOrder', { orderNo: query.orderNo })
  }
  // 商品详情：带商品名（meta.productName 或 document title）
  if (path.startsWith('/product/')) {
    const name = meta.productName || document.title || ''
    if (name) return t('whatsapp.messageProduct', { name })
  }
  // 门票详情
  if (path.startsWith('/tickets/') && path !== '/tickets') {
    const name = meta.attractionName || document.title || ''
    if (name) return t('whatsapp.messageTicket', { name })
  }
  // 接送页
  if (path.startsWith('/transfer')) return t('whatsapp.messageTransfer')

  // 默认
  return t('whatsapp.messageGeneral')
})

const link = computed(() => buildWhatsAppUrl(props.whatsappNumber, prefillMessage.value))

function onClick() {
  // 给 GA4 一个事件：方便统计 WhatsApp 按钮的点击转化
  if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
    window.gtag('event', 'click_whatsapp_fab', {
      page_path: route.path,
      has_order: route.query?.orderNo ? true : false,
    })
  }
}
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
  background: #25d366;       /* WhatsApp 品牌绿 */
  color: #fff;
  box-shadow: 0 6px 16px rgba(37, 211, 102, 0.4);
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: wa-pop 0.4s ease;
  -webkit-tap-highlight-color: transparent;
}

.wa-fab:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 10px 22px rgba(37, 211, 102, 0.5);
}

.wa-fab:active {
  transform: scale(0.95);
}

/* 底部 tabbar 高度约 56px，留出 12px 间隙 */
.wa-fab--with-tabbar {
  bottom: 72px;
}

.wa-fab__icon {
  width: 24px;
  height: 24px;
}

/* 出现动画：从下方弹出 */
@keyframes wa-pop {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.6);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 桌面端稍微大一点 */
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
