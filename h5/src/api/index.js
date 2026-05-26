import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || ''

// 将相对路径图片 URL 转为完整 URL
export const resolveUrl = (path) => {
  if (!path) return ''

  const value = String(path).trim()
  if (!value) return ''

  if (value.startsWith('http://') || value.startsWith('https://')) return value
  if (value.startsWith('//')) return window.location.protocol + value
  if (value.startsWith('/api/images/') || value.startsWith('/uploads/')) return API_BASE + value
  if (value.startsWith('/')) return API_BASE + value

  // 兼容数据库中仅保存文件名的历史数据
  return API_BASE + `/api/images/${value}`
}

const api = axios.create({
  baseURL: API_BASE + '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// Add language param to every request
api.interceptors.request.use(config => {
  const lang = localStorage.getItem('lang') || 'zh'
  config.params = { ...config.params, lang }
  return config
})

// Extract response data
api.interceptors.response.use(
  res => res.data,
  err => {
    const msg = err.response?.data?.message || 'Network error'
    return Promise.reject(new Error(msg))
  }
)

// ==================== Products ====================
export const getProducts = (params) => api.get('/products', { params })
export const getProduct = (id) => api.get(`/products/${id}`)
export const getFeaturedProducts = (limit = 6) => api.get('/products/featured', { params: { limit } })

// ==================== Categories ====================
export const getCategories = () => api.get('/categories')

// ==================== Vehicles ====================
export const getVehicles = () => api.get('/vehicles')

// ==================== Locations ====================
export const getLocations = () => api.get('/locations')
export const getDistricts = () => api.get('/districts')

// ==================== Transfer ====================
export const getTransferPrice = () => api.get('/transfer/price')
export const createTransferOrder = (data) => api.post('/transfer/orders', data)

// ==================== Shop Orders ====================
export const createShopOrder = (data) => api.post('/shop/orders', data)

// ==================== Order Query ====================
export const queryOrder = (data) => api.post('/orders/query', data)

// ==================== Contact Info ====================
export const getContactInfo = () => api.get('/contact-info')

// ==================== Payment ====================
export const getPaymentQRCodes = () => api.get('/payment/qrcodes')
export const confirmPaid = (data) => api.post('/orders/confirm-paid', data)
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}

// ==================== Refund ====================
export const requestRefund = (data) => api.post('/orders/refund', data)

// ==================== Reviews ====================
export const submitReview = (data) => api.post('/reviews', data)
export const getProductRating = (productId) => api.get(`/products/${productId}/rating`)

// ==================== Coupons ====================
export const verifyCoupon = (data) => api.post('/coupons/verify', data)

// ==================== Wishes (许愿池) ====================
export const submitWish = (data) => api.post('/wishes', data)

export default api
