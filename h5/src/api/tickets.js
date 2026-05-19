import api from './index'

// ==================== Tickets ====================
// H5 Public ticket APIs — these mirror the endpoints in app/api/tickets.py

export const getTicketAttractions = (params) => api.get('/tickets/attractions', { params })
export const getTicketAttraction = (id) => api.get(`/tickets/attractions/${id}`)
export const getTicketPackages = (params) => api.get('/tickets/packages', { params })
export const getTicketTransportOptions = (params) => api.get('/tickets/transport-options', { params })
export const createTicketOrder = (data) => api.post('/tickets/orders', data)
export const queryTicketOrders = (data) => api.post('/tickets/orders/query', data)
export const getTicketOrder = (orderNo) => api.get(`/tickets/orders/${orderNo}`)
export const getTicketCities = () => api.get('/tickets/cities')
export const confirmTicketPaid = (data) => api.post('/orders/confirm-paid', data)
