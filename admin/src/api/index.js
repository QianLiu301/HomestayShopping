import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const API_BASE = import.meta.env.VITE_API_URL || ''
const http = axios.create({ baseURL: API_BASE + '/api', timeout: 15000 })

// 用于将相对路径的图片 URL 转为完整 URL（生产环境需要拼接 API 域名）
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

http.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 防止 401 弹出多次
let isLoggingOut = false

http.interceptors.response.use(
  res => {
    // 文件下载（blob）需要保留完整响应，以便读取 Content-Disposition 头里的文件名
    if (res.config?.responseType === 'blob') return res
    return res.data
  },
  err => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem('admin_token')
      if (!isLoggingOut) {
        isLoggingOut = true
        ElMessage.error('Login expired, please login again')
        router.push('/login').finally(() => {
          setTimeout(() => { isLoggingOut = false }, 2000)
        })
      }
    } else {
      ElMessage.error(err.response?.data?.message || 'Request failed')
    }
    return Promise.reject(err)
  }
)

// Auth
export const login = data => http.post('/auth/login', data)
export const getAdminInfo = () => http.get('/auth/info')

// Upload
export const uploadFile = file => {
  const formData = new FormData()
  formData.append('file', file)
  return http.post('/admin/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000   // 上传到 R2 需要更长超时
  })
}

// Products
export const getProducts = params => http.get('/admin/products', { params })
export const createProduct = data => http.post('/admin/products', data)
export const updateProduct = (id, data) => http.put(`/admin/products/${id}`, data)
export const deleteProduct = id => http.delete(`/admin/products/${id}`)

// Categories
export const getCategories = () => http.get('/admin/categories')
export const createCategory = data => http.post('/admin/categories', data)
export const updateCategory = (id, data) => http.put(`/admin/categories/${id}`, data)
export const deleteCategory = id => http.delete(`/admin/categories/${id}`)

// Vehicles
export const getVehicles = () => http.get('/admin/vehicles')
export const createVehicle = data => http.post('/admin/vehicles', data)
export const updateVehicle = (id, data) => http.put(`/admin/vehicles/${id}`, data)
export const deleteVehicle = id => http.delete(`/admin/vehicles/${id}`)

// Locations
export const getLocations = () => http.get('/admin/locations')
export const createLocation = data => http.post('/admin/locations', data)
export const updateLocation = (id, data) => http.put(`/admin/locations/${id}`, data)
export const deleteLocation = id => http.delete(`/admin/locations/${id}`)

// Analytics
export const getAnalytics = params => http.get('/admin/analytics', { params })
export const getTopProducts = params => http.get('/admin/analytics/top-products', { params })

// Orders
export const getShopOrders = params => http.get('/admin/orders/shop', { params })
export const updateShopOrder = (id, data) => http.put(`/admin/orders/shop/${id}`, data)
export const confirmShopPayment = id => http.post(`/admin/orders/shop/${id}/confirm-payment`)
export const getTransferOrders = params => http.get('/admin/orders/transfer', { params })
export const updateTransferOrder = (id, data) => http.put(`/admin/orders/transfer/${id}`, data)
export const confirmTransferPayment = id => http.post(`/admin/orders/transfer/${id}/confirm-payment`)
export const batchDeleteShopOrders = ids => http.post('/admin/orders/shop/batch-delete', { ids })
export const batchDeleteTransferOrders = ids => http.post('/admin/orders/transfer/batch-delete', { ids })
export const getCancelledOrders = params => http.get('/admin/orders/cancelled', { params })
export const updateRefundStatus = (orderType, orderId, data) => http.put(`/admin/orders/refund/${orderType}/${orderId}`, data)
export const exportCancelledOrdersUrl = params => {
  const search = new URLSearchParams()
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.append(key, value)
    }
  })
  const token = localStorage.getItem('admin_token')
  if (token) search.append('token', token)
  return `${API_BASE}/api/admin/orders/cancelled/export?${search.toString()}`
}

// Delivery
export const getDeliveryOrders = params => http.get('/admin/delivery/orders', { params })
export const startDelivery = ids => http.post('/admin/delivery/start', { ids })
export const completeDelivery = ids => http.post('/admin/delivery/complete', { ids })

// Coupons
export const getCoupons = params => http.get('/admin/coupons', { params })
export const createCoupon = data => http.post('/admin/coupons', data)
export const updateCoupon = (id, data) => http.put(`/admin/coupons/${id}`, data)
export const deleteCoupon = id => http.delete(`/admin/coupons/${id}`)

// Settings
export const getSettings = () => http.get('/admin/settings')
export const updateSettings = data => http.put('/admin/settings', data)

// Wishes (许愿池)
export const getWishes = params => http.get('/admin/wishes', { params })
export const updateWish = (id, data) => http.put(`/admin/wishes/${id}`, data)
export const deleteWish = id => http.delete(`/admin/wishes/${id}`)

// Reviews (评价管理：接送 / 门票 / 商城)
export const getAdminReviews = params => http.get('/admin/reviews', { params })
export const updateReview = (id, data) => http.put(`/admin/reviews/${id}`, data)
export const deleteReview = id => http.delete(`/admin/reviews/${id}`)

// Accounts (管理员账号管理 — 仅 owner)
export const getAccounts = params => http.get('/admin/accounts', { params })
export const createAccount = data => http.post('/admin/accounts', data)
export const updateAccount = (id, data) => http.put(`/admin/accounts/${id}`, data)
export const deleteAccount = id => http.delete(`/admin/accounts/${id}`)

// 导出原始 http 实例（用于特殊场景：blob 文件下载、自定义 headers 等）
export default http
