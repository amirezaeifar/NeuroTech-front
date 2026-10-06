import { apiRequest } from './client.js'

const localeQuery = (locale) => new URLSearchParams({ locale }).toString()

const collectionApi = (publicPath, adminPath) => ({
  list: (locale = 'en') => apiRequest(`${publicPath}?${localeQuery(locale)}`),
  detail: (slug, locale = 'en') => apiRequest(`${publicPath}/${encodeURIComponent(slug)}?${localeQuery(locale)}`),
  adminList: () => apiRequest(adminPath),
  create: (body) => apiRequest(adminPath, { method: 'POST', body }),
  update: (id, body) => apiRequest(`${adminPath}/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  publish: (id) => apiRequest(`${adminPath}/${encodeURIComponent(id)}/publish`, { method: 'POST' }),
  unpublish: (id) => apiRequest(`${adminPath}/${encodeURIComponent(id)}/unpublish`, { method: 'POST' }),
  archive: (id) => apiRequest(`${adminPath}/${encodeURIComponent(id)}`, { method: 'DELETE' }),
})

export const partnersApi = collectionApi('/partners', '/admin/partners')
export const tradeApi = collectionApi('/trade-documents', '/admin/trade-documents')

export const pageContentApi = {
  get: (pageKey, locale = 'en') => apiRequest(`/page-content/${encodeURIComponent(pageKey)}?${localeQuery(locale)}`),
  adminList: () => apiRequest('/admin/page-content'),
  save: (pageKey, translations) => apiRequest(`/admin/page-content/${encodeURIComponent(pageKey)}`, { method: 'PUT', body: { translations } }),
  publish: (pageKey) => apiRequest(`/admin/page-content/${encodeURIComponent(pageKey)}/publish`, { method: 'POST' }),
  unpublish: (pageKey) => apiRequest(`/admin/page-content/${encodeURIComponent(pageKey)}/unpublish`, { method: 'POST' }),
}
