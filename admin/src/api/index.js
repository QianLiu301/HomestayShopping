import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const http = axios.create({ baseURL: (import.meta.env.VITE_API_URL || '') + '/api', timeout: 15000 })

http.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  res => res.data,
  err => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem('admin_token')
      router.push('/login')
      ElMessage.error('Login expired, please login again')
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
  return http.post('/admin/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
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
