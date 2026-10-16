import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const checkHealth = () => api.get('/health')
export const getDashboard = () => api.get('/dashboard')
export const getExpenses = () => api.get('/receipts')
export const uploadReceipt = (formData) => api.post('/receipts/upload', formData)
export const confirmReceipt = (data) => api.post('/receipts/confirm', data)
export const getInvoices = () => api.get('/invoices')
export const createInvoice = (data) => api.post('/invoices', data)
export const updateInvoice = (id, data) => api.patch(`/invoices/${id}`, data)
export const getMonthlyReport = (month) => api.get(`/reports/monthly?month=${month}`)
export const exportCSV = (month) => api.get(`/reports/export?month=${month}`, { responseType: 'blob' })
