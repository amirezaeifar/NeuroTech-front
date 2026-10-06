<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useLocale } from '../composables/useLocale.js'
import { useTheme } from '../composables/useTheme.js'
import { useAuth } from '../composables/useAuth.js'
import { useCart } from '../composables/useCart.js'
import { brandLogoUrl } from '../data/brandAssets.js'
import { resolveApiUrl } from '../api/client.js'

const { t } = useI18n()
const router = useRouter()
const { locale, setLocale, locales } = useLocale()
const { isDark, toggle: toggleTheme } = useTheme()
const { user, isAuthenticated, ensureSession, logout } = useAuth()
const {
  items: cartItems, count: cartCount, flashKey,
  remove: removeCartItem, updateQuantity,
} = useCart()
const cartOpen = ref(false)
const userOpen = ref(false)
const userShell = ref(null)
const accountLinks = [
  { key: 'courses', en: 'My courses', fa: 'دوره‌های من' },
  { key: 'orders', en: 'My orders', fa: 'سفارش‌های من' },
  { key: 'payments', en: 'Payment history', fa: 'تاریخچه پرداخت' },
  { key: 'favorites', en: 'Favorites', fa: 'علاقه‌مندی‌ها' },
  { key: 'profile', en: 'Profile', fa: 'پروفایل' },
]
const removingKeys = ref(new Set())

const money = (item) => {
  if (!item.price && item.price !== 0) return '—'
  return new Intl.NumberFormat(locale.value, {
    style: 'currency',
    currency: item.currency || (locale.value === 'fa' ? 'IRR' : 'USD'),
    maximumFractionDigits: item.currency === 'USD' ? 2 : 0,
  }).format(item.currency === 'USD' ? item.price / 100 : item.price)
}
const closeCart = () => { cartOpen.value = false }
const checkout = () => { closeCart(); router.push('/checkout') }
const cancelCartItem = (key) => {
  if (removingKeys.value.has(key)) return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    if (cartItems.value.length === 1) closeCart()
    removeCartItem(key)
    return
  }
  removingKeys.value = new Set([...removingKeys.value, key])
  const removingLastItem = cartItems.value.length === 1
  window.setTimeout(() => {
    if (removingLastItem) closeCart()
    else removeCartItem(key)
  }, 380)
  window.setTimeout(() => {
    if (removingLastItem) removeCartItem(key)
    const next = new Set(removingKeys.value)
    next.delete(key)
    removingKeys.value = next
  }, removingLastItem ? 900 : 430)
}

const onAuthClick = async () => {
  cartOpen.value = false
  langOpen.value = false
  // Finish any session restoration before deciding whether this is a guest.
  await ensureSession().catch(() => null)
  if (!isAuthenticated.value) {
    userOpen.value = false
    mobileOpen.value = false
    return router.push({ name: 'Login', query: { redirect: router.currentRoute.value.fullPath } })
  }
  userOpen.value = !userOpen.value
}
const signOut = async () => { userOpen.value = false; await logout(); router.push('/') }

const scrolled = ref(false)
const mobileOpen = ref(false)
const langOpen = ref(false)

const onScroll = () => { scrolled.value = window.scrollY > 60 }
const onOutsideClick = (event) => { if (userOpen.value && !userShell.value?.contains(event.target)) userOpen.value = false }
const onEscape = (event) => { if (event.key === 'Escape') userOpen.value = false }
onMounted(() => {
  ensureSession().catch(() => null)
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('pointerdown', onOutsideClick)
  document.addEventListener('keydown', onEscape)
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('pointerdown', onOutsideClick)
  document.removeEventListener('keydown', onEscape)
})

const closeMobile = () => { mobileOpen.value = false }

const links = [
  { to: '/', key: 'home' },
  { to: '/academy', key: 'academy' },
  { to: '/articles', key: 'articles' },
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
  <div class="main-nav-row max-w-7xl mx-auto px-8 min-h-[80px] h-20 flex items-center justify-between gap-6">
    <!-- Logo (left in LTR, right in RTL) -->
    <router-link
      to="/"
      :aria-label="t('brand')"
      @click="closeMobile"
      class="main-nav-brand shrink-0"
    >
      <span class="flex items-center gap-3 select-none">
        <img :src="brandLogoUrl" alt="" aria-hidden="true" class="brand-logo-img h-12 w-auto" />
        <!-- Two-line wordmark — typographically identical to the footer BrandLogo
             (Cormorant "Neuro Tech" over Inter "NEUROLOGY · CRAFTED" + hairline). -->
        <span class="brand-wordmark hidden xl:flex">
          <span class="brand-wordmark-name">Neuro Tech</span>
          <span class="brand-wordmark-sub">NEUROLOGY&nbsp;·&nbsp;CRAFTED</span>
        </span>
      </span>
    </router-link>

    <!-- Small physical left shift in both writing directions; mobile is unchanged. -->
    <nav class="main-nav-links hidden lg:flex flex-1 items-center justify-center gap-6 xl:gap-10">
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
        :aria-label="isDark ? t('common.lightMode') : t('common.darkMode')"
      >
        <svg v-if="!isDark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
          <path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Cart appears only after the first item is added. Its synaptic ripple
           gives that moment one memorable, product-specific motion beat. -->
      <Transition name="cart-arrive">
        <div v-if="cartCount" class="cart-shell">
          <button
            type="button"
            class="cart-trigger"
            :class="{ 'is-charged': flashKey }"
            :aria-label="`${t('cart.title')} (${cartCount})`"
            :aria-expanded="cartOpen"
            @click="cartOpen = !cartOpen; userOpen = false"
          >
            <span class="cart-orbit" aria-hidden="true"></span>
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/><path d="M2 3h2l2.4 12.4a2 2 0 0 0 2 1.6h8.6a2 2 0 0 0 2-1.6L22 7H6"/></svg>
            <span class="cart-count">{{ cartCount }}</span>
          </button>

          <Transition name="cart-panel" :duration="{ enter: 440, leave: 520 }">
            <div v-if="cartOpen" class="cart-preview" role="dialog" :aria-label="t('cart.title')">
              <div class="cart-preview__head">
                <div>
                  <p class="cart-preview__eyebrow">{{ t('cart.eyebrow') }}</p>
                  <h2 class="cart-preview__title">{{ t('cart.title') }}</h2>
                </div>
                <div class="cart-preview__head-actions">
                  <button type="button" class="cart-preview__close" :aria-label="t('cart.close')" @click="closeCart">×</button>
                </div>
              </div>
              <div class="cart-preview__items">
                <article v-for="item in cartItems" :key="item.key" class="cart-line" :class="{ 'is-removing': removingKeys.has(item.key) }">
                  <span class="cart-line__glyph" :class="{ 'is-course': item.type === 'course' }">
                    <svg v-if="item.type === 'course'" viewBox="0 0 24 24"><path d="M5 4h14v16H5zM8 8h8M8 12h6"/></svg>
                    <svg v-else viewBox="0 0 24 24"><path d="M12 3 20 7v10l-8 4-8-4V7zM4 7l8 4 8-4M12 11v10"/></svg>
                  </span>
                  <span class="cart-line__copy">
                    <strong>{{ item.title }}</strong>
                    <small>{{ item.type === 'course' ? t('cart.course') : t('cart.product') }} · {{ money(item) }}</small>
                    <span v-if="item.type === 'product'" class="cart-line__quantity" :aria-label="t('cart.quantity')">
                      <button type="button" :disabled="item.quantity <= 1" :aria-label="t('cart.decrease')" @click="updateQuantity(item.key, item.quantity - 1)">−</button>
                      <b>{{ item.quantity }}</b>
                      <button type="button" :disabled="item.quantity >= 99" :aria-label="t('cart.increase')" @click="updateQuantity(item.key, item.quantity + 1)">+</button>
                    </span>
                  </span>
                  <button type="button" class="cart-line__remove" :disabled="removingKeys.has(item.key)" :aria-label="t('cart.remove')" @click="cancelCartItem(item.key)">×</button>
                </article>
              </div>
              <button type="button" class="cart-preview__checkout" @click="checkout">
                {{ t('cart.checkout') }} <span class="dir-arrow" aria-hidden="true"></span>
              </button>
            </div>
          </Transition>
        </div>
      </Transition>

      <!-- Sign in / out -->
      <div ref="userShell" class="user-shell">
      <button
        type="button"
        @click="onAuthClick"
        :aria-label="isAuthenticated ? (locale === 'fa' ? 'منوی کاربر' : 'Account menu') : t('nav.login')"
        :aria-expanded="isAuthenticated ? userOpen : undefined"
        :aria-haspopup="isAuthenticated ? 'menu' : undefined"
        class="inline-flex items-center text-ink-muted hover:text-gold-dark transition-colors p-1"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0" stroke-linecap="round"/></svg>
      </button>
      <Transition name="cart-panel" :duration="{ enter: 440, leave: 520 }">
        <div v-if="userOpen && isAuthenticated" class="user-preview" role="menu" :aria-label="locale === 'fa' ? 'منوی کاربر' : 'Account menu'">
          <div class="user-preview__identity">
            <img v-if="user?.avatar_url" class="user-preview__avatar" :src="resolveApiUrl(user.avatar_url)" alt="" />
            <span v-else class="user-preview__avatar user-preview__initial" aria-hidden="true">{{ (user?.display_name || (locale === 'fa' ? 'م' : 'G')).trim().charAt(0) }}</span>
            <p class="user-preview__name" :title="user?.display_name || ''">{{ user?.display_name || (locale === 'fa' ? 'مهمان' : 'Guest') }}</p>
          </div>
          <router-link v-for="item in accountLinks" :key="item.key" :to="`/account/${item.key}`" role="menuitem" class="user-menu-link" @click="userOpen = false">{{ locale === 'fa' ? item.fa : item.en }}</router-link>
          <button v-if="isAuthenticated" type="button" role="menuitem" class="user-menu-link user-menu-logout" @click="signOut">{{ t('nav.logout') }}</button>
        </div>
      </Transition>
      </div>

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
        :aria-label="mobileOpen ? t('common.closeMenu') : t('common.openMenu')"
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
.main-nav-row { position: relative; left: -8px; }
@media (min-width: 1024px) { .main-nav-row { left: -2px; } }
.main-nav-links { position: relative; left: -12px; }
@media (min-width: 1024px) { .main-nav-brand { position: relative; left: -28px; } }
@media (min-width: 1360px) { .main-nav-row { left: -16px; }.main-nav-brand { left: -44px; } }
.user-shell { position: relative; }
.user-preview { position: absolute; top: calc(100% + 18px); inset-inline-end: 0; z-index: 60; width: min(18rem, 85vw); padding: .25rem 0 .5rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .8rem; background: rgb(var(--c-parchment-light)); box-shadow: 0 22px 60px rgb(0 0 0 / .16); transform-origin: top right; }
.user-preview__identity { display: flex; align-items: center; gap: .7rem; padding: .7rem 1rem .6rem; }
.user-preview__avatar { flex: none; width: 2rem; height: 2rem; border-radius: 50%; object-fit: cover; }
.user-preview__initial { display: grid; place-items: center; background: rgb(var(--c-gold) / .16); color: rgb(var(--c-gold-dark)); font-size: .85rem; }
.user-preview__name { overflow: hidden; color: rgb(var(--c-gold-dark)); font-size: .82rem; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.user-menu-link { display: block; width: 100%; padding: .72rem 1rem; color: rgb(var(--c-ink)); text-align: start; font-size: .78rem; transition: background 160ms ease, color 160ms ease; }
.user-menu-link:hover, .user-menu-link:focus-visible { background: rgb(var(--c-gold) / .12); color: rgb(var(--c-gold-dark)); outline: none; }
.user-menu-logout { margin-top: .25rem; border-top: 1px solid rgb(var(--c-parchment-deep)); }
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

.cart-shell { position: relative; }
.cart-trigger {
  position: relative;
  display: grid;
  place-items: center;
  width: 2.15rem;
  height: 2.15rem;
  color: rgb(var(--c-gold-dark));
  border: 1px solid rgb(var(--c-gold) / 0.45);
  border-radius: 999px;
  background: rgb(var(--c-gold) / 0.07);
}
.cart-count {
  position: absolute;
  inset-block-start: -0.42rem;
  inset-inline-end: -0.42rem;
  display: grid;
  place-items: center;
  min-width: 1.15rem;
  height: 1.15rem;
  padding-inline: 0.2rem;
  border-radius: 999px;
  background: rgb(var(--c-ink));
  color: rgb(var(--c-parchment-light));
  font-size: 0.61rem;
  font-variant-numeric: tabular-nums;
  box-shadow: 0 0 0 2px rgb(var(--c-parchment-light));
}
.cart-orbit { position: absolute; inset: -1px; border: 1px solid rgb(var(--c-gold) / 0.6); border-radius: inherit; opacity: 0; }
.cart-trigger.is-charged .cart-orbit { animation: cart-synapse 850ms cubic-bezier(.2,.9,.2,1); }
@keyframes cart-synapse {
  0% { opacity: .9; transform: scale(.55); box-shadow: 0 0 16px rgb(var(--c-gold) / .8); }
  65% { opacity: .25; transform: scale(1.8); }
  100% { opacity: 0; transform: scale(2.2); }
}
.cart-preview {
  position: absolute;
  inset-inline-end: 0;
  top: calc(100% + 1rem);
  width: min(22rem, calc(100vw - 2rem));
  padding: 1.15rem;
  border: 1px solid rgb(var(--c-gold) / .35);
  border-radius: .9rem;
  background: rgb(var(--c-parchment-light) / .96);
  box-shadow: 0 24px 60px -28px rgba(0,0,0,.55);
  backdrop-filter: blur(18px);
  z-index: 70;
}
.cart-preview__head { display: flex; align-items: center; justify-content: space-between; padding: .2rem .2rem .9rem; border-bottom: 1px solid rgb(var(--c-parchment-deep)); }
.cart-preview__head-actions { display: flex; align-items: center; }
.cart-preview__close { display: grid; place-items: center; width: 1.8rem; height: 1.8rem; border-radius: 999px; color: rgb(var(--c-ink-muted)); border: 1px solid rgb(var(--c-parchment-deep)); font-size: 1rem; transition: transform 220ms ease, color 220ms ease, border-color 220ms ease; }
.cart-preview__close:hover { color: rgb(var(--c-gold-dark)); border-color: rgb(var(--c-gold)); transform: rotate(90deg); }
.cart-preview__eyebrow { color: rgb(var(--c-gold-dark)); font-size: .58rem; letter-spacing: .25em; text-transform: uppercase; }
.cart-preview__title { margin-top: .2rem; color: rgb(var(--c-ink)); font-family: 'Cormorant Garamond', Georgia, serif; font-size: 1.35rem; font-weight: 400; }
.cart-preview__items { max-height: 17rem; overflow: auto; }
.cart-line { display: flex; align-items: center; gap: .75rem; padding: .9rem .15rem; border-bottom: 1px solid rgb(var(--c-parchment-deep) / .7); }
.cart-line.is-removing { pointer-events: none; animation: cart-line-cancel 400ms cubic-bezier(.55,0,1,.45) both; }
.cart-line__glyph { flex: none; display: grid; place-items: center; width: 2.4rem; height: 2.4rem; border-radius: .65rem; border: 1px solid rgb(var(--c-parchment-deep)); color: rgb(var(--c-ink-muted)); }
.cart-line__glyph.is-course { color: rgb(var(--c-gold-dark)); border-color: rgb(var(--c-gold) / .4); background: rgb(var(--c-gold) / .07); }
.cart-line__glyph svg { width: 1.15rem; height: 1.15rem; fill: none; stroke: currentColor; stroke-width: 1.3; }
.cart-line__copy { min-width: 0; flex: 1; display: flex; flex-direction: column; gap: .18rem; text-align: start; }
.cart-line__copy strong { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: rgb(var(--c-ink)); font-size: .78rem; font-weight: 400; }
.cart-line__copy small { color: rgb(var(--c-ink-muted)); font-size: .65rem; font-weight: 300; }
.cart-line__quantity { display: inline-flex; align-items: center; align-self: flex-start; margin-top: .35rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: 999px; overflow: hidden; }
.cart-line__quantity button { display: grid; place-items: center; width: 1.55rem; height: 1.4rem; color: rgb(var(--c-gold-dark)); font-size: .8rem; transition: background 160ms ease; }
.cart-line__quantity button:hover:not(:disabled) { background: rgb(var(--c-gold) / .12); }
.cart-line__quantity button:disabled { opacity: .3; cursor: not-allowed; }
.cart-line__quantity b { min-width: 1.25rem; color: rgb(var(--c-ink)); text-align: center; font-size: .63rem; font-weight: 500; font-variant-numeric: tabular-nums; }
.cart-line__remove { flex: none; color: rgb(var(--c-ink-muted)); font-size: 1.15rem; padding: .25rem; }
.cart-line__remove:hover { color: #a33; transform: rotate(90deg) scale(1.08); }
.cart-line__remove:disabled { cursor: default; }
.cart-preview__checkout { display: flex; align-items: center; justify-content: center; gap: .6rem; width: 100%; margin-top: 1rem; padding: .8rem; border-radius: .55rem; background: rgb(var(--c-ink)); color: rgb(var(--c-parchment-light)); font-size: .66rem; letter-spacing: .18em; text-transform: uppercase; }
.cart-arrive-enter-active { animation: cart-materialize 720ms cubic-bezier(.16,1,.3,1); }
.cart-arrive-leave-active { animation: cart-dematerialize 440ms cubic-bezier(.7,0,.84,0); }
@keyframes cart-materialize {
  0% { opacity: 0; transform: scale(.2) rotate(-22deg); filter: blur(8px); }
  55% { opacity: 1; transform: scale(1.14) rotate(4deg); filter: blur(0); }
  100% { transform: scale(1) rotate(0); }
}
@keyframes cart-dematerialize {
  0% { opacity: 1; transform: scale(1); filter: blur(0); }
  45% { opacity: .7; transform: scale(1.12) rotate(5deg); }
  100% { opacity: 0; transform: scale(.15) rotate(-20deg); filter: blur(7px); }
}
.cart-panel-enter-active { animation: cart-panel-open 440ms cubic-bezier(.16,1,.3,1); transform-origin: top right; }
.cart-panel-leave-active { animation: cart-panel-close 520ms cubic-bezier(.7,0,.84,0); transform-origin: top right; pointer-events: none; }
@keyframes cart-line-cancel {
  0% { opacity: 1; transform: translateX(0) scale(1); filter: blur(0); max-height: 6rem; }
  35% { opacity: .75; transform: translateX(8px) scale(.985); box-shadow: inset 3px 0 rgb(var(--c-gold) / .5); }
  100% { opacity: 0; transform: translateX(-26px) scale(.9); filter: blur(5px); max-height: 0; padding-block: 0; border-color: transparent; }
}
@keyframes cart-panel-open { from { opacity: 0; transform: translateY(-12px) scale(.9) rotate(1.5deg); filter: blur(6px); } to { opacity: 1; transform: none; filter: blur(0); } }
@keyframes cart-panel-close { 0% { opacity: 1; transform: none; filter: blur(0); } 35% { opacity: .8; transform: translateY(-3px) scale(.975) rotate(-.6deg); } 100% { opacity: 0; transform: translateY(-20px) scale(.78) rotate(-4deg); filter: blur(9px); } }
@media (prefers-reduced-motion: reduce) {
  .cart-arrive-enter-active, .cart-arrive-leave-active, .cart-line.is-removing, .cart-trigger.is-charged .cart-orbit { animation: none; }
  .cart-panel-enter-active, .cart-panel-leave-active { animation: none; transition: opacity 120ms ease; }
  .cart-panel-enter-from, .cart-panel-leave-to { opacity: 0; }
}
</style>

