import { apiRequest } from './client.js'

export const commerceApi = {
  createOrder: (courseSlug, currency) => apiRequest('/orders', {
    method: 'POST',
    body: { course_slug: courseSlug, currency },
  }),
  order: (orderId) => apiRequest(`/orders/${encodeURIComponent(orderId)}`),
}
