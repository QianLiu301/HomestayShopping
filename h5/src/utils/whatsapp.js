/**
 * WhatsApp click-to-chat 工具
 *
 * 通过 https://wa.me/<PHONE>?text=<MESSAGE> 跳转 WhatsApp。
 * - 移动端：直接唤起 WhatsApp App
 * - 桌面端：打开 WhatsApp Web
 */

/**
 * 把任意手机号字符串清理成 wa.me 接受的格式（纯数字，去掉 +、空格、横线等）
 * @param {string} raw 形如 +86 138 1234 5678 / +1-555-0100 / 8613812345678
 * @returns {string} 纯数字，如 8613812345678
 */
export function normalizePhone(raw) {
  if (!raw) return ''
  return String(raw).replace(/\D+/g, '')
}

/**
 * 生成 WhatsApp 点击跳转链接
 * @param {string} phone 客服 WhatsApp 号（带不带 + 都行）
 * @param {string} [text] 预填消息（可选）
 * @returns {string} 形如 https://wa.me/8613812345678?text=Hi%20...
 */
export function buildWhatsAppUrl(phone, text) {
  const num = normalizePhone(phone)
  if (!num) return ''
  const base = `https://wa.me/${num}`
  if (!text) return base
  return `${base}?text=${encodeURIComponent(text)}`
}

/**
 * 在新窗口打开 WhatsApp（会自动按桌面/移动端切换）
 */
export function openWhatsApp(phone, text) {
  const url = buildWhatsAppUrl(phone, text)
  if (!url) return false
  window.open(url, '_blank', 'noopener')
  return true
}
