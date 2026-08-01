import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'
import router from './router'
import en from './locales/en.json'
import fa from './locales/fa.json'
import './assets/fonts.css'
import './style.css'
import { initTheme } from './composables/useTheme.js'
import { MotionPlugin } from '@vueuse/motion'

initTheme()

const SUPPORTED = ['fa', 'en']
const saved = localStorage.getItem('locale')
// Visitors who previously selected a now-retired locale fall back to English.
const savedLocale = SUPPORTED.includes(saved) ? saved : 'en'

const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { en, fa },
})

const app = createApp(App)
app.use(router)
app.use(MotionPlugin)
app.use(i18n)
app.mount('#app')
