import { formatValidationProblem } from '../utils/validation.js'
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

export const resolveApiUrl = (path) => new URL(path, `${new URL(API_BASE_URL, window.location.origin).origin}/`).toString()

export class ApiProblem extends Error {
  constructor(problem, response) {
    super(problem?.detail || problem?.title || `Request failed with status ${response.status}`)
    const validation = formatValidationProblem(problem)
    if (validation) this.message = validation
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

let refreshPromise = null

const refreshSession = () => {
  if (!refreshPromise) {
    refreshPromise = apiRequest('/auth/refresh', {
      method: 'POST',
      refresh: true,
      _retried: true,
    }).finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

export async function apiRequest(path, options = {}) {
  const { rawBody: _rawBody, refresh: _refresh, _retried: _wasRetried, ...fetchOptions } = options
  const headers = new Headers(options.headers)
  const method = (options.method || 'GET').toUpperCase()
  const body = options.body === undefined
    ? undefined
    : options.rawBody
      ? options.body
      : JSON.stringify(options.body)

  if (body !== undefined && !options.rawBody) headers.set('Content-Type', 'application/json')
  headers.set('Accept', 'application/json, application/problem+json')

  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    const csrf = cookieValue(options.refresh ? 'csrf_refresh_token' : 'csrf_access_token')
    if (csrf) headers.set('X-CSRF-TOKEN', csrf)
  }

  let response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    method,
    body,
    headers,
    credentials: 'include',
  })

  if (response.status === 401 && !options.refresh && !options._retried && !path.startsWith('/auth/')) {
    try {
      await refreshSession()
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
