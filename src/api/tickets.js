import { apiRequest } from './client.js'

export const ticketsApi = {
  create: (body) => apiRequest('/tickets', { method: 'POST', body }),
  track: (token) => apiRequest(`/tickets/track/${encodeURIComponent(token)}`),
  list: (query = {}) => apiRequest(`/admin/tickets?${new URLSearchParams(Object.entries(query).filter(([, value]) => value !== ''))}`),
  detail: (id) => apiRequest(`/admin/tickets/${encodeURIComponent(id)}`),
  update: (id, body) => apiRequest(`/admin/tickets/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
}
