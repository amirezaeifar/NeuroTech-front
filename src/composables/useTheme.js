import { ref } from 'vue'

const STORAGE_KEY = 'theme'
const isDark = ref(false)

const apply = (dark) => {
  isDark.value = dark
  const root = document.documentElement
  root.classList.toggle('dark', dark)
  try { localStorage.setItem(STORAGE_KEY, dark ? 'dark' : 'light') } catch (_) {}
}

/** Read saved preference (or OS preference) and apply it. Call once at startup. */
export function initTheme() {
  let saved = null
  try { saved = localStorage.getItem(STORAGE_KEY) } catch (_) {}
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  apply(saved ? saved === 'dark' : prefersDark)
}

export function useTheme() {
  const toggle = () => apply(!isDark.value)
  const setDark = (v) => apply(!!v)
  return { isDark, toggle, setDark }
}
