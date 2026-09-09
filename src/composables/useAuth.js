import { computed, ref } from 'vue'
import { authApi } from '../api/auth.js'

export const ROLES = Object.freeze({ USER: 'user', SPECIALIST: 'specialist', ADMIN: 'admin' })

const user = ref(null)
const initialized = ref(false)
let initialization = null

const acceptSession = (response) => {
  user.value = response?.data?.user || null
  return user.value
}

export function useAuth() {
  const isAuthenticated = computed(() => Boolean(user.value))
  const role = computed(() => user.value?.role || null)
  const isAdmin = computed(() => role.value === ROLES.ADMIN)
  const isStaff = computed(() => [ROLES.ADMIN, ROLES.SPECIALIST].includes(role.value))

  const ensureSession = async () => {
    if (initialized.value) return user.value
    if (initialization) return initialization

    initialization = (async () => {
      try {
        return acceptSession(await authApi.me())
      } catch (problem) {
        if (problem.status !== 401) throw problem
        try {
          await authApi.refresh()
          return acceptSession(await authApi.me())
        } catch (_) {
          user.value = null
          return null
        }
      } finally {
        initialized.value = true
        initialization = null
      }
    })()
    return initialization
  }

  const loginPassword = async (email, password) => {
    const response = await authApi.loginPassword({ email, password })
    initialized.value = true
    return acceptSession(response)
  }

  const registerPassword = (displayName, email, password) => authApi.registerPassword({
    display_name: displayName,
    email,
    password,
  })

  const verifyEmail = (token) => authApi.verifyEmail(token)

  const acceptInvitation = async (token, displayName, password) => {
    const response = await authApi.acceptInvitation({
      token,
      display_name: displayName,
      password,
    })
    initialized.value = true
    return acceptSession(response)
  }

  const requestOtp = async (phone, mode) => {
    return mode === 'register'
      ? authApi.requestRegistrationOtp(phone)
      : authApi.requestLoginOtp(phone)
  }

  const verifyOtp = async ({ phone, code, challengeId, displayName, mode }) => {
    const common = { phone, code, challenge_id: challengeId }
    const response = mode === 'register'
      ? await authApi.verifyRegistrationOtp({ ...common, display_name: displayName })
      : await authApi.verifyLoginOtp(common)
    initialized.value = true
    return acceptSession(response)
  }

  const logout = async () => {
    try {
      if (user.value) await authApi.logout()
    } finally {
      user.value = null
      initialized.value = true
    }
  }

  return {
    user,
    role,
    isAuthenticated,
    isAdmin,
    isStaff,
    ensureSession,
    loginPassword,
    registerPassword,
    verifyEmail,
    acceptInvitation,
    requestOtp,
    verifyOtp,
    logout,
  }
}
