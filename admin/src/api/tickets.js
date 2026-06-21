import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const API_BASE = import.meta.env.VITE_API_URL || ''
const http = axios.create({ baseURL: API_BASE + '/api', timeout: 15000 })

http.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isLoggingOut = false

http.interceptors.response.use(
  res => res.data,
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

// Ticket Attractions
export const getTicketAttractions = params => http.get('/admin/ticket-attractions', { params })
export const createTicketAttraction = data => http.post('/admin/ticket-attractions', data)
export const updateTicketAttraction = (id, data) => http.put(`/admin/ticket-attractions/${id}`, data)
export const deleteTicketAttraction = id => http.delete(`/admin/ticket-attractions/${id}`)

// Ticket Packages
export const getTicketPackages = params => http.get('/admin/ticket-packages', { params })
export const createTicketPackage = data => http.post('/admin/ticket-packages', data)
export const updateTicketPackage = (id, data) => http.put(`/admin/ticket-packages/${id}`, data)
export const deleteTicketPackage = id => http.delete(`/admin/ticket-packages/${id}`)

// Ticket Transport Pricing
export const getTicketTransportPricing = params => http.get('/admin/ticket-transport-pricing', { params })
export const createTicketTransportPrice = data => http.post('/admin/ticket-transport-pricing', data)
export const updateTicketTransportPrice = (id, data) => http.put(`/admin/ticket-transport-pricing/${id}`, data)
export const deleteTicketTransportPrice = id => http.delete(`/admin/ticket-transport-pricing/${id}`)

// Ticket Orders
export const getTicketOrders = params => http.get('/admin/ticket-orders', { params })
export const getTicketOrder = id => http.get(`/admin/ticket-orders/${id}`)
export const updateTicketOrderStatus = (id, data) => http.put(`/admin/ticket-orders/${id}/status`, data)
export const confirmTicketOrderPayment = (id, data = {}) => http.put(`/admin/ticket-orders/${id}/payment`, data)

export const uploadTicketVoucher = (orderId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return http.post(`/admin/ticket-orders/${orderId}/voucher`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000
  })
}
export const deleteTicketVoucher = (orderId, voucherId) =>
  http.delete(`/admin/ticket-orders/${orderId}/voucher?voucher_id=${voucherId}`)
export const sendTicketVoucher = orderId => http.post(`/admin/ticket-orders/${orderId}/send-voucher`)
export const batchDeleteTicketOrders = ids => http.post('/admin/ticket-orders/batch-delete', { ids })
