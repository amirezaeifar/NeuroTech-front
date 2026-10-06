import { computed, ref } from 'vue'

const STORAGE_KEY = 'neurotech-cart-v1'
const readItems = () => {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(value) ? value : []
  } catch (_) {
    return []
  }
}

const items = ref(typeof window === 'undefined' ? [] : readItems())
const flashKey = ref('')
let flashTimer = null

const persist = () => {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(items.value)) } catch (_) { /* memory-only fallback */ }
}

export function useCart() {
  const count = computed(() => items.value.reduce((sum, item) => sum + (item.quantity || 1), 0))

  const add = (item) => {
    const key = `${item.type}:${item.id || item.slug}`
    const existing = items.value.find((entry) => entry.key === key)
    if (existing) existing.quantity = item.type === 'course' ? 1 : Math.min(99, existing.quantity + 1)
    else items.value.push({ ...item, key, quantity: item.quantity || 1 })
    flashKey.value = key
    window.clearTimeout(flashTimer)
    flashTimer = window.setTimeout(() => { flashKey.value = '' }, 900)
    persist()
  }

  const remove = (key) => {
    items.value = items.value.filter((item) => item.key !== key)
    persist()
  }

  const updateQuantity = (key, quantity) => {
    const item = items.value.find((entry) => entry.key === key)
    if (!item || item.type !== 'product') return
    item.quantity = Math.max(1, Math.min(99, Number(quantity) || 1))
    persist()
  }

  const clearType = (type) => {
    items.value = items.value.filter((item) => item.type !== type)
    persist()
  }

  return { items, count, flashKey, add, remove, updateQuantity, clearType }
}
