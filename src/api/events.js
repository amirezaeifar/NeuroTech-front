import { apiRequest } from './client.js'

const query = (values) => {
  const params = new URLSearchParams()
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') params.set(key, value)
  })
  return params.toString()
}

export const eventsApi = {
  list: (options = {}) => apiRequest(`/events?${query(options)}`),
  detail: (slug, locale = 'en') => apiRequest(`/events/${encodeURIComponent(slug)}?${query({ locale })}`),
  reserve: (slug) => apiRequest(`/events/${encodeURIComponent(slug)}/reservations`, { method: 'POST' }),
  confirmReservation: (token) => apiRequest('/events/reservations/confirm', { method: 'POST', body: { token } }),
  cancelReservation: (slug) => apiRequest(`/events/${encodeURIComponent(slug)}/reservations/me`, { method: 'DELETE' }),
  reservation: (slug) => apiRequest(`/events/${encodeURIComponent(slug)}/reservations/me`),
  attendees: (id) => apiRequest(`/admin/events/${encodeURIComponent(id)}/reservations`),
  cancelAttendee: (id, userId) => apiRequest(`/admin/events/${encodeURIComponent(id)}/reservations/${encodeURIComponent(userId)}`, { method: 'DELETE' }),
  liveControl: (slug, body) => apiRequest(`/events/${encodeURIComponent(slug)}/live/control`, { method: 'PATCH', body }),
  liveDelete: (slug, kind, id) => apiRequest(`/events/${encodeURIComponent(slug)}/live/${kind}/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  live: (slug, locale = 'en') => apiRequest(`/events/${encodeURIComponent(slug)}/live?locale=${encodeURIComponent(locale)}`),
  liveMessage: (slug, body) => apiRequest(`/events/${encodeURIComponent(slug)}/live/messages`, { method: 'POST', body: { body } }),
  liveQuestion: (slug, body) => apiRequest(`/events/${encodeURIComponent(slug)}/live/questions`, { method: 'POST', body: { body } }),
  liveVote: (slug, id) => apiRequest(`/events/${encodeURIComponent(slug)}/live/questions/${encodeURIComponent(id)}/vote`, { method: 'POST' }),
  liveAnswer: (slug, id) => apiRequest(`/events/${encodeURIComponent(slug)}/live/questions/${encodeURIComponent(id)}/answer`, { method: 'POST' }),
  liveStep: (slug, step) => apiRequest(`/events/${encodeURIComponent(slug)}/live/step`, { method: 'POST', body: { step } }),
  adminList: () => apiRequest('/admin/events'),
  speakerOptions: (q = '') => apiRequest(`/admin/events/speakers?${query({ q })}`),
  adminCreate: (body) => apiRequest('/admin/events', { method: 'POST', body }),
  adminUpdate: (id, body) => apiRequest(`/admin/events/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  adminPublish: (id) => apiRequest(`/admin/events/${encodeURIComponent(id)}/publish`, { method: 'POST' }),
  adminUnpublish: (id) => apiRequest(`/admin/events/${encodeURIComponent(id)}/unpublish`, { method: 'POST' }),
  adminArchive: (id) => apiRequest(`/admin/events/${encodeURIComponent(id)}`, { method: 'DELETE' }),
}
