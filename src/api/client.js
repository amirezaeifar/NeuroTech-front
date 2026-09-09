export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api/v1').replace(/\/$/, '')

export const resolveApiUrl = (path) => new URL(path, `${new URL(API_BASE_URL).origin}/`).toString()

export class ApiProblem extends Error {
  constructor(problem, response) {
    super(problem?.detail || problem?.title || `Request failed with status ${response.status}`)
    this.name = 'ApiProblem'
    this.problem = problem || {}
    this.status = response.status
    this.retryAfter = response.headers.get('Retry-After')
  }
}

const cookieValue = (name) => {
  const prefix = `${encodeURIComponent(name)}=`
  const item = document.cookie.split('; ').find((part) => part.startsWith(prefix))
  return item ? decodeURIComponent(item.slice(prefix.length)) : null
}

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers)
  const method = (options.method || 'GET').toUpperCase()
  const body = options.body === undefined ? undefined : JSON.stringify(options.body)

  if (body !== undefined) headers.set('Content-Type', 'application/json')
  headers.set('Accept', 'application/json, application/problem+json')

  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const csrf = cookieValue(options.refresh ? 'csrf_refresh_token' : 'csrf_access_token')
    if (csrf) headers.set('X-CSRF-TOKEN', csrf)
  }

  let response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    method,
    body,
    headers,
    credentials: 'include',
  })

  if (response.status === 401 && !options.refresh && !options._retried && !path.startsWith('/auth/')) {
    try {
      await apiRequest('/auth/refresh', { method: 'POST', refresh: true, _retried: true })
      return apiRequest(path, { ...options, _retried: true })
    } catch (_) {
      // Preserve the original 401 so callers receive the protected resource problem.
    }
  }

  if (response.status === 204) return null
  const payload = await response.json().catch(() => null)
  if (!response.ok) throw new ApiProblem(payload, response)
  return payload
}
