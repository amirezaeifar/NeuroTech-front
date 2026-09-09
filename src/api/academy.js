import { apiRequest } from './client.js'

const query = (values) => {
  const params = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') params.set(key, value)
  })
  return params.toString()
}

export const academyApi = {
  list: (options = {}) => apiRequest(`/courses?${query(options)}`),
  detail: (slug, locale = 'en') => apiRequest(`/courses/${encodeURIComponent(slug)}?${query({ locale })}`),
  enroll: (slug) => apiRequest(`/courses/${encodeURIComponent(slug)}/enroll`, { method: 'POST' }),
  access: (slug, locale = 'en') => apiRequest(`/courses/${encodeURIComponent(slug)}/access?${query({ locale })}`),
  saveProgress: (lessonId, body) => apiRequest(`/me/lessons/${encodeURIComponent(lessonId)}/progress`, { method: 'PUT', body }),
  comments: (slug) => apiRequest(`/courses/${encodeURIComponent(slug)}/comments`),
  addComment: (slug, body) => apiRequest(`/courses/${encodeURIComponent(slug)}/comments`, { method: 'POST', body: { body } }),
  pathway: (locale = 'en') => apiRequest(`/me/pathway?${query({ locale })}`),
  adminList: () => apiRequest('/admin/courses'),
  adminCreate: (body) => apiRequest('/admin/courses', { method: 'POST', body }),
  adminUpdate: (id, body) => apiRequest(`/admin/courses/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  adminPublish: (id) => apiRequest(`/admin/courses/${encodeURIComponent(id)}/publish`, { method: 'POST' }),
  adminUnpublish: (id) => apiRequest(`/admin/courses/${encodeURIComponent(id)}/unpublish`, { method: 'POST' }),
  adminArchive: (id) => apiRequest(`/admin/courses/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  adminReplaceContent: (id, body) => apiRequest(`/admin/courses/${encodeURIComponent(id)}/content`, { method: 'PUT', body }),
  adminReorder: (courseIds) => apiRequest('/admin/courses/order', { method: 'PUT', body: { course_ids: courseIds } }),
  pendingComments: () => apiRequest('/admin/comments/pending'),
  moderateComment: (id, decision, reason = null) => apiRequest(`/admin/comments/${encodeURIComponent(id)}/moderate`, { method: 'POST', body: { decision, reason } }),
}
