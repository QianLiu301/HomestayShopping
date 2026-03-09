import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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

// ==================== Payment ====================
export const getPaymentQRCodes = () => api.get('/payment/qrcodes')
export const confirmPaid = (data) => api.post('/orders/confirm-paid', data)

// ==================== Coupons ====================
export const verifyCoupon = (data) => api.post('/coupons/verify', data)

export default api
