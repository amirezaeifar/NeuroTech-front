import { apiRequest } from './client.js'

export const articlesApi = {
  list: (locale, category) => apiRequest(`/blog?locale=${encodeURIComponent(locale)}${category ? `&category=${category}` : ''}`),
  detail: (slug, locale) => apiRequest(`/blog/${encodeURIComponent(slug)}?locale=${encodeURIComponent(locale)}`),
}
