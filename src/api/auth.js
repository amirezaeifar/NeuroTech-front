import { apiRequest } from './client.js'

export const authApi = {
  me: () => apiRequest('/me'),
  registerPassword: (body) => apiRequest('/auth/register/password', { method: 'POST', body }),
  verifyEmail: (token) => apiRequest('/auth/email/verify', { method: 'POST', body: { token } }),
  resendEmail: (email) => apiRequest('/auth/email/resend', { method: 'POST', body: { email } }),
  acceptInvitation: (body) => apiRequest('/auth/invitations/accept', { method: 'POST', body }),
  loginPassword: (body) => apiRequest('/auth/login/password', { method: 'POST', body }),
  requestRegistrationOtp: (phone) => apiRequest('/auth/register/phone/request-otp', { method: 'POST', body: { phone } }),
  verifyRegistrationOtp: (body) => apiRequest('/auth/register/phone/verify-otp', { method: 'POST', body }),
  requestLoginOtp: (phone) => apiRequest('/auth/login/otp/request', { method: 'POST', body: { phone } }),
  verifyLoginOtp: (body) => apiRequest('/auth/login/otp/verify', { method: 'POST', body }),
  refresh: () => apiRequest('/auth/refresh', { method: 'POST', refresh: true }),
  logout: () => apiRequest('/auth/logout', { method: 'POST' }),
  logoutAll: () => apiRequest('/auth/logout-all', { method: 'POST' }),
  adminUsers: () => apiRequest('/admin/users'),
  updateUser: (userId, body) => apiRequest(`/admin/users/${userId}`, { method: 'PATCH', body }),
  invite: (body) => apiRequest('/admin/invitations', { method: 'POST', body }),
  updateRole: (userId, role) => apiRequest(`/admin/users/${userId}/role`, {
    method: 'PATCH',
    body: { role },
  }),
}
