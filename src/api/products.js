import { apiRequest } from './client.js'

const query = (values) => {
  const params = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') params.set(key, value)
  })
  return params.toString()
}

export const productsApi = {
  list: (options = {}) => apiRequest(`/products?${query(options)}`),
  categories: (locale = 'en') => apiRequest(`/product-categories?${query({ locale })}`),
  detail: (slug, locale = 'en') => apiRequest(`/products/${encodeURIComponent(slug)}?${query({ locale })}`),
  cart: (locale = 'en') => apiRequest(`/cart?${query({ locale })}`),
  setCartItem: (productId, quantity) => apiRequest(`/cart/items/${encodeURIComponent(productId)}`, {
    method: 'PUT',
    body: { quantity },
  }),
  removeCartItem: (productId) => apiRequest(`/cart/items/${encodeURIComponent(productId)}`, { method: 'DELETE' }),
  createOrder: (currency, shippingAddress) => apiRequest('/product-orders', {
    method: 'POST',
    body: { currency, shipping_address: shippingAddress },
  }),
  order: (orderId) => apiRequest(`/product-orders/${encodeURIComponent(orderId)}`),
  adminList: () => apiRequest('/admin/products'),
  adminCategories: () => apiRequest('/admin/product-categories'),
  createCategory: (body) => apiRequest('/admin/product-categories', { method: 'POST', body }),
  archiveCategory: (id) => apiRequest(`/admin/product-categories/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  adminCreate: (body) => apiRequest('/admin/products', { method: 'POST', body }),
  adminUpdate: (id, body) => apiRequest(`/admin/products/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  adminPublish: (id) => apiRequest(`/admin/products/${encodeURIComponent(id)}/publish`, { method: 'POST' }),
  adminUnpublish: (id) => apiRequest(`/admin/products/${encodeURIComponent(id)}/unpublish`, { method: 'POST' }),
  adminArchive: (id) => apiRequest(`/admin/products/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  upload: (file, isPublic = true) => {
    const body = new FormData()
    body.set('file', file)
    body.set('is_public', String(isPublic))
    return apiRequest('/admin/files', { method: 'POST', body, rawBody: true })
  },
  deleteFile: (id) => apiRequest(`/admin/files/${encodeURIComponent(id)}`, { method: 'DELETE' }),
}
