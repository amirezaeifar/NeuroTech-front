import { ref, computed } from 'vue'

// Lightweight client-side auth + RBAC state. A real backend would issue a signed
// session token carrying the caller's role; here we persist a minimal user object
// (identity, sign-in method and role) to localStorage so both the login state and
// the access level survive reloads and every route guard can rely on them.
//
// This is a mock "store" in the same shape the rest of the app uses (a shared
// singleton composable, à la useTheme) rather than Pinia/Vuex — no extra
// dependency, identical ergonomics, and the reactive state is genuinely shared.
const STORAGE_KEY = 'auth_user'

/** The three access levels understood across the app. */
export const ROLES = Object.freeze({
  ADMIN: 'admin',
  SPECIALIST: 'specialist',
  USER: 'user',
})

const VALID_ROLES = Object.values(ROLES)

// Ordered from least to most privileged — handy for "at least this level" checks.
const ROLE_RANK = { [ROLES.USER]: 0, [ROLES.SPECIALIST]: 1, [ROLES.ADMIN]: 2 }

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

const normaliseRole = (r) => (VALID_ROLES.includes(r) ? r : ROLES.USER)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)

  /** Active role, or null when signed out. */
  const role = computed(() => user.value?.role || null)

  const isAdmin = computed(() => role.value === ROLES.ADMIN)
  const isSpecialist = computed(() => role.value === ROLES.SPECIALIST)
  const isUser = computed(() => role.value === ROLES.USER)

  // Admin Panel is open to privileged roles only. `admin` gets everything;
  // `specialist` gets the educational/clinical subset (see per-route meta.roles).
  const canAccessAdmin = computed(() => isAdmin.value || isSpecialist.value)

  /** True when the active role is one of `roles` (array or rest args). */
  const hasRole = (...roles) => roles.flat().includes(role.value)

  /** True when the active role is at least as privileged as `min`. */
  const atLeast = (min) => (ROLE_RANK[role.value] ?? -1) >= (ROLE_RANK[min] ?? 99)

  /** Mark the visitor as signed in. `identity` is an email or phone number. */
  const login = (identity, method = 'password', roleName = ROLES.USER) => {
    user.value = {
      identity: identity || 'member',
      method,
      role: normaliseRole(roleName),
      since: Date.now(),
    }
    persist()
  }

  /** Change the active role in place (mock role-switching / promotion). */
  const setRole = (roleName) => {
    if (!user.value) return
    user.value = { ...user.value, role: normaliseRole(roleName) }
    persist()
  }

  const logout = () => {
    user.value = null
    persist()
  }

  return {
    user,
    isAuthenticated,
    role,
    isAdmin,
    isSpecialist,
    isUser,
    canAccessAdmin,
    hasRole,
    atLeast,
    login,
    setRole,
    logout,
  }
}
