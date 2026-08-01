import { ref, computed } from 'vue'

// Lightweight client-side auth state. A real backend would issue a session
// token; here we persist a minimal user object to localStorage so the login
// state survives reloads and the Checkout route guard can rely on it.
const STORAGE_KEY = 'auth_user'

const load = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (_) {
    return null
  }
}

// Shared singleton state — every component sees the same user.
const user = ref(load())

const persist = () => {
  try {
    if (user.value) localStorage.setItem(STORAGE_KEY, JSON.stringify(user.value))
    else localStorage.removeItem(STORAGE_KEY)
  } catch (_) {}
}

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)

  /** Mark the visitor as signed in. `identity` is an email or phone number. */
  const login = (identity, method = 'password') => {
    user.value = { identity: identity || 'member', method, since: Date.now() }
    persist()
  }

  const logout = () => {
    user.value = null
    persist()
  }

  return { user, isAuthenticated, login, logout }
}
