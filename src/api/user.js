import { API_BASE_URL, apiRequest } from './client.js'
import { authApi } from './auth.js'

export const userApi = {
  profile: () => apiRequest('/me/profile'),
  saveProfile: (body) => apiRequest('/me/profile', { method: 'PUT', body }),
  courses: () => apiRequest('/me/courses'),
  orders: () => apiRequest('/me/orders'),
  payments: () => apiRequest('/me/payments'),
  favorites: () => apiRequest('/me/favorites'),
  addFavorite: (item_type, item_id) => apiRequest('/me/favorites', { method: 'POST', body: { item_type, item_id } }),
  removeFavorite: (id) => apiRequest(`/me/favorites/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  uploadAvatar: (file) => {
    const body = new FormData()
    body.set('file', file)
    return apiRequest('/me/avatar', { method: 'POST', body, rawBody: true })
  },
  removeAvatar: () => apiRequest('/me/avatar', { method: 'DELETE' }),
  downloadInvoice: async (payment) => {
    const locale = document.documentElement.lang === 'fa' ? 'fa' : 'en'
    const path = `${API_BASE_URL}/me/payments/${encodeURIComponent(payment.id)}/invoice?type=${encodeURIComponent(payment.type)}&locale=${locale}`
    let response = await fetch(path, { credentials: 'include' })
    if (response.status === 401) {
      await authApi.refresh()
      response = await fetch(path, { credentials: 'include' })
    }
    if (!response.ok) throw new Error(response.status === 404 ? 'Invoice is available after a successful payment.' : 'Could not download the invoice.')
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `invoice-${payment.order_id}.html`
    document.body.append(link)
    link.click()
    link.remove()
    window.setTimeout(() => URL.revokeObjectURL(url), 60000)
  },
}
