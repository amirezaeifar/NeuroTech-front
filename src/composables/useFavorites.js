import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from './useAuth.js'
import { userApi } from '../api/user.js'

const favorites = ref([])
let loading = null

export function useFavorites() {
  const route = useRoute()
  const router = useRouter()
  const { ensureSession, isAuthenticated } = useAuth()

  const refresh = async () => {
    if (loading) return loading
    loading = (async () => {
      await ensureSession()
      favorites.value = isAuthenticated.value ? (await userApi.favorites()).data : []
      return favorites.value
    })().finally(() => { loading = null })
    return loading
  }

  const toggle = async (type, id) => {
    await ensureSession()
    if (!isAuthenticated.value) {
      router.push({ name: 'Login', query: { redirect: route.fullPath } })
      return false
    }
    await refresh()
    const existing = favorites.value.find((item) => item.item_type === type && item.item_id === id)
    if (existing) {
      await userApi.removeFavorite(existing.id)
      favorites.value = favorites.value.filter((item) => item.id !== existing.id)
    } else {
      await userApi.addFavorite(type, id)
      await refresh()
    }
    return true
  }

  const isFavorite = (type, id) => computed(() => favorites.value.some((item) => item.item_type === type && item.item_id === id))
  return { favorites, refresh, toggle, isFavorite }
}
