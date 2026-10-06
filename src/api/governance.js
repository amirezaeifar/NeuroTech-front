import { apiRequest } from './client.js'

export const governanceApi = {
  approvals: (status = 'pending') => apiRequest(`/admin/approvals?status=${status}`),
  review: (id, decision, note = '') => apiRequest(`/admin/approvals/${id}/review`, {
    method: 'POST',
    body: { decision, note },
  }),
  blogs: () => apiRequest('/admin/blog'),
  createBlog: (body) => apiRequest('/admin/blog', { method: 'POST', body }),
  updateBlog: (id, body) => apiRequest(`/admin/blog/${id}`, { method: 'PATCH', body }),
  publishBlog: (id) => apiRequest(`/admin/blog/${id}/publish`, { method: 'POST' }),
  unpublishBlog: (id) => apiRequest(`/admin/blog/${id}/unpublish`, { method: 'POST' }),
  deleteBlog: (id) => apiRequest(`/admin/blog/${id}`, { method: 'DELETE' }),
  settings: () => apiRequest('/admin/settings'),
  saveSettings: (body) => apiRequest('/admin/settings', { method: 'PUT', body }),
}
