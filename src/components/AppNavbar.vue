<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useLocale } from '../composables/useLocale.js'
import { useTheme } from '../composables/useTheme.js'
import { useAuth } from '../composables/useAuth.js'
import logo from '../assets/logo.png'

const { t } = useI18n()
const router = useRouter()
const { locale, setLocale, locales } = useLocale()
const { isDark, toggle: toggleTheme } = useTheme()
const { isAuthenticated, logout } = useAuth()

const onAuthClick = () => {
  if (isAuthenticated.value) { logout(); router.push('/') }
  else { router.push('/login') }
}

const scrolled = ref(false)
const mobileOpen = ref(false)
const langOpen = ref(false)

const onScroll = () => { scrolled.value = window.scrollY > 60 }
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const closeMobile = () => { mobileOpen.value = false }

const links = [
  { to: '/', key: 'home' },
  { to: '/academy', key: 'academy' },
  { to: '/events', key: 'events' },
  { to: '/products', key: 'products' },
  { to: '/global-trade', key: 'globalTrade' },
  { to: '/partners', key: 'partners' },
]

const currentLabel = () => locales.find((l) => l.code === locale.value)?.label || locale.value.toUpperCase()
const pickLocale = (code) => { setLocale(code); langOpen.value = false }
</script>

<template>
<header
  :class="[
    'sticky top-0 z-50 w-full transition-all duration-300',
    scrolled
      ? 'bg-parchment-light/80 backdrop-blur-sm border-b border-parchment-deep'
      : 'bg-parchment-light border-b border-parchment-dark'
  ]"
>
  <div class="max-w-7xl mx-auto px-8 min-h-[80px] h-20 flex items-center justify-between gap-6">
    <!-- Logo (left in LTR, right in RTL) -->
    <router-link
      to="/"
      :aria-label="t('brand')"
      @click="closeMobile"
      class="shrink-0"
    >
      <span class="flex items-center gap-3 select-none">
        <img :src="logo" alt="" aria-hidden="true" class="brand-logo-img h-11 w-auto" />
        <!-- Two-line wordmark — typographically identical to the footer BrandLogo
             (Cormorant "Neuro Tech" over Inter "NEUROLOGY · CRAFTED" + hairline). -->
        <span class="brand-wordmark hidden xl:flex">
          <span class="brand-wordmark-name">Neuro Tech</span>
          <span class="brand-wordmark-sub">NEUROLOGY&nbsp;·&nbsp;CRAFTED</span>
        </span>
      </span>
    </router-link>

    <!-- Menu links — centred in the bar between the logo and the controls.
         flex-1 + justify-center keeps them evenly spaced and centred in any
         locale (LTR/RTL). Hidden below lg, where the mobile menu takes over. -->
    <nav class="hidden lg:flex flex-1 items-center justify-center gap-6 xl:gap-10">
      <router-link
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="nav-link whitespace-nowrap"
      >{{ t('nav.' + link.key) }}</router-link>
    </nav>

    <!-- Language selector + mobile toggle (right in LTR, left in RTL).
         shrink-0 + a fixed inline-start margin guarantee the mode toggle never
         touches the last nav tab, in any locale. -->
    <div class="flex items-center gap-5 shrink-0">
      <!-- Dark mode toggle -->
      <button
        type="button"
        @click="toggleTheme"
        class="text-ink-muted hover:text-gold-dark transition-colors p-1"
        :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
      >
        <svg v-if="!isDark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
          <path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Sign in / out -->
      <button
        type="button"
        @click="onAuthClick"
        :aria-label="isAuthenticated ? t('nav.logout') : t('nav.login')"
        :title="isAuthenticated ? t('nav.logout') : t('nav.login')"
        class="hidden sm:inline-flex items-center text-ink-muted hover:text-gold-dark transition-colors p-1"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0" stroke-linecap="round"/></svg>
      </button>

      <div class="relative">
        <button
          type="button"
          @click="langOpen = !langOpen"
          class="text-[11px] tracking-[0.25em] uppercase text-ink-muted hover:text-ink transition-colors font-light flex items-center gap-1.5"
        >
          <span>{{ currentLabel() }}</span>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" :class="['transition-transform', langOpen ? 'rotate-180' : '']">
            <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <Transition name="fade">
          <div
            v-if="langOpen"
            class="absolute end-0 mt-3 w-44 bg-parchment-light border border-parchment-deep shadow-lg py-2 z-50"
            style="direction: ltr;"
          >
            <button
              v-for="l in locales"
              :key="l.code"
              type="button"
              @click="pickLocale(l.code)"
              :class="[
                'w-full text-left px-4 py-2 text-xs tracking-[0.15em] uppercase font-light transition-colors',
                locale === l.code ? 'text-gold' : 'text-ink-muted hover:text-ink'
              ]"
            >{{ l.label }}</button>
          </div>
        </Transition>
      </div>

      <button
        type="button"
        class="lg:hidden text-ink p-1"
        @click="mobileOpen = !mobileOpen"
        :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
      >
        <svg v-if="!mobileOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M3 7h18M3 17h18" stroke-linecap="round" />
        </svg>
        <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M6 6l12 12M6 18L18 6" stroke-linecap="round" />
        </svg>
      </button>
    </div>
  </div>

  <Transition name="fade">
    <div v-if="mobileOpen" class="lg:hidden bg-parchment-light border-t border-parchment-deep">
      <nav class="px-8 py-6 flex flex-col gap-4">
        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="nav-link whitespace-nowrap"
          @click="closeMobile"
        >{{ t('nav.' + link.key) }}</router-link>
      </nav>

      <div class="px-8 pb-6 flex flex-wrap gap-2.5" style="direction: ltr;">
        <button
          v-for="l in locales"
          :key="l.code"
          type="button"
          @click="setLocale(l.code); closeMobile()"
          :class="[
            'text-[11px] tracking-[0.2em] uppercase font-light px-3 py-1.5 border transition-colors',
            locale === l.code ? 'text-gold border-gold/50' : 'text-ink-muted border-parchment-deep hover:text-ink'
          ]"
        >{{ l.label }}</button>
      </div>
    </div>
  </Transition>
</header>
</template>

<style scoped>
/* The navbar row is a strict `flex items-center` container (see the header
   markup). Every child — logo, wordmark, nav tabs, and the utility cluster
   (user, language, theme) — is vertically centred by flexbox alone. No
   per-item translate-y / margin nudges are used: any such offset is what threw
   the icons off the shared centre-line previously. */

/* Two-line wordmark — a faithful HTML/CSS rendition of the footer's BrandLogo
   SVG so the masthead and footer brand identities are pixel-for-pixel alike:
     · "Neuro Tech"         — Cormorant Garamond 300, ~0.083em tracking
     · "NEUROLOGY · CRAFTED" — Inter 300, 0.5em tracking, capitalised
     · a hairline rule beneath, exactly as in the footer mark.
   Always rendered LTR (English) regardless of locale, like the footer. */
.brand-wordmark {
  flex-direction: column;
  justify-content: center;
  line-height: 1;
  direction: ltr !important;
  unicode-bidi: isolate;
  text-align: start;
}
.brand-wordmark-name {
  font-family: 'Cormorant Garamond', Georgia, serif !important;
  font-size: 25px;
  font-weight: 300;
  letter-spacing: 0.083em;
  line-height: 1;
  color: var(--ink);
  font-feature-settings: 'liga' 1, 'dlig' 1;
}
.brand-wordmark-sub {
  font-family: 'Inter', sans-serif !important;
  font-size: 8.5px;
  font-weight: 300;
  letter-spacing: 0.5em;
  text-transform: uppercase;
  line-height: 1;
  color: var(--ink-muted);
  margin-top: 5px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgb(var(--c-ink) / 0.32);
}
</style>
