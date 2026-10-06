import { apiRequest } from './client.js'

const query = (values = {}) => {
  const params = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value) params.set(key, value)
  })
  return params.toString()
}

export const ordersApi = {
  adminList: (filters = {}) => apiRequest(`/admin/orders?${query(filters)}`),
  advanceProduct: (orderId, status) => apiRequest(
    `/admin/orders/products/${encodeURIComponent(orderId)}/fulfillment`,
    { method: 'PATCH', body: { status } },
  ),
}
