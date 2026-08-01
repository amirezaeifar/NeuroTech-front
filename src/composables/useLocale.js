import { watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'

// The site ships exclusively in Persian (RTL) and English (LTR). Other locales
// were retired; re-adding one means restoring its entry here, its messages
// import in main.js, and its JSON file under src/locales.
export const SUPPORTED_LOCALES = [
  { code: 'fa', label: 'فارسی', dir: 'rtl' },
  { code: 'en', label: 'English', dir: 'ltr' },
]

const RTL_LOCALES = ['fa']

const FONT_STACKS = {
  fa: "'YekanBakh', sans-serif",
}
const DEFAULT_FONT_STACK = "'Inter', sans-serif"

export function useLocale() {
  const { locale } = useI18n()

  watchEffect(() => {
    const html = document.documentElement
    const code = locale.value
    const isRtl = RTL_LOCALES.includes(code)

    html.setAttribute('dir', isRtl ? 'rtl' : 'ltr')
    html.setAttribute('lang', code)
    html.style.fontFamily = FONT_STACKS[code] || DEFAULT_FONT_STACK

    localStorage.setItem('locale', code)
  })

  const setLocale = (code) => {
    if (SUPPORTED_LOCALES.some((l) => l.code === code)) {
      locale.value = code
    }
  }

  // Cycles to the next supported locale — kept for any compact toggle UI.
  const toggleLocale = () => {
    const codes = SUPPORTED_LOCALES.map((l) => l.code)
    const idx = codes.indexOf(locale.value)
    locale.value = codes[(idx + 1) % codes.length]
  }

  return { locale, toggleLocale, setLocale, locales: SUPPORTED_LOCALES }
}
