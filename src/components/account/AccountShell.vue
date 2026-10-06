<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth.js'
import { resolveApiUrl } from '../../api/client.js'
import { brandLogoUrl } from '../../data/brandAssets.js'

const props = defineProps({ section: { type: String, required: true } })
const { locale } = useI18n()
const { user } = useAuth()
const labels = {
  courses: ['My courses', 'دوره‌های من'],
  orders: ['My orders', 'سفارش‌های من'],
  payments: ['Payment history', 'تاریخچه پرداخت'],
  favorites: ['Favorites', 'علاقه‌مندی‌ها'],
  profile: ['Profile', 'پروفایل'],
}
const title = (key) => labels[key][locale.value === 'fa' ? 1 : 0]
const name = computed(() => user.value?.display_name || (locale.value === 'fa' ? 'کاربر' : 'Member'))
const initial = computed(() => name.value.trim().charAt(0).toLocaleUpperCase(locale.value))
const avatar = computed(() => user.value?.avatar_url ? resolveApiUrl(user.value.avatar_url) : '')
</script>

<template>
  <section class="account-space">
    <div class="account-container">
      <header class="account-hero">
        <img class="account-logo-shadow" :src="brandLogoUrl" alt="" aria-hidden="true" />
        <div class="account-hero-content">
          <div class="account-avatar" aria-hidden="true"><img v-if="avatar" :src="avatar" alt="" /> <span v-else>{{ initial }}</span></div>
          <div>
            <p class="account-kicker">{{ locale === 'fa' ? 'فضای شخصی شما' : 'PERSONAL SPACE' }}</p>
            <h1 class="account-name">{{ name }}</h1>
            <p class="account-subtitle">{{ locale === 'fa' ? 'دوره‌ها، خریدها و اطلاعاتتان در یک نگاه' : 'Your learning, orders and details in one place' }}</p>
          </div>
        </div>
      </header>

      <nav class="account-nav" :aria-label="locale === 'fa' ? 'بخش‌های فضای شخصی' : 'Personal space sections'">
        <router-link v-for="key in Object.keys(labels)" :key="key" :to="`/account/${key}`" class="account-nav-link" :class="{ 'is-current': props.section === key }" :aria-current="props.section === key ? 'page' : undefined">
          {{ title(key) }}<span class="account-nav-arrow" aria-hidden="true">↗</span>
        </router-link>
      </nav>

      <div class="account-content">
        <div class="account-section-heading"><span class="account-section-rule" aria-hidden="true"></span><h2>{{ title(props.section) }}</h2></div>
        <slot />
      </div>
    </div>
  </section>
</template>

<style scoped>
.account-space { min-height: 75vh; padding: clamp(1.1rem, 2.5vw, 2.2rem) 1rem 4.5rem; background: radial-gradient(circle at 12% 16%, rgb(var(--c-gold) / .06), transparent 25rem), rgb(var(--c-parchment-light)); color: rgb(var(--c-ink)); }
.account-container { max-width: 67rem; margin: auto; }
.account-hero { position: relative; overflow: hidden; min-height: 11.5rem; border: 1px solid rgb(var(--c-gold) / .2); border-radius: .85rem; background: linear-gradient(115deg, #202a33, #303c45 72%, #263039); color: #f6f3ec; box-shadow: 0 17px 38px -31px #111b25a8; }
.account-logo-shadow { position: absolute; right: 0; top: -22%; width: 40%; height: 145%; object-fit: contain; opacity: .18; mix-blend-mode: screen; filter: drop-shadow(0 0 28px #d5ad6980); -webkit-mask-image: radial-gradient(circle at 58% 50%, #000 33%, transparent 75%); mask-image: radial-gradient(circle at 58% 50%, #000 33%, transparent 75%); pointer-events: none; }
.account-hero-content { position: relative; z-index: 1; display: flex; align-items: center; gap: clamp(.9rem, 2.5vw, 1.5rem); width: 60%; min-height: 11.5rem; margin-left: 0; margin-right: auto; padding: clamp(1.25rem, 3vw, 2rem); }
.account-avatar { display: grid; flex: none; place-items: center; overflow: hidden; width: 3.7rem; height: 3.7rem; border: 1px solid #d5ad6977; border-radius: 50%; background: #e3b97918; color: #efd09a; font: 400 1.8rem/1 Georgia,serif; }
.account-avatar img { width: 100%; height: 100%; object-fit: cover; }
.account-kicker { margin-bottom: .55rem; color: #dfba7c; font-size: .68rem; letter-spacing: .2em; text-transform: uppercase; }
.account-name { max-width: 33rem; overflow-wrap: anywhere; font: 400 clamp(1.8rem, 3.4vw, 2.8rem)/1.2 Georgia, 'YekanBakh', serif; }
.account-subtitle { margin-top: .55rem; color: #d6dbdd; font-size: .78rem; }
.account-nav { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: .5rem; margin-top: .9rem; }
.account-nav-link { display: flex; min-height: 3.5rem; align-items: center; justify-content: space-between; gap: .5rem; padding: .75rem .85rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .55rem; background: rgb(var(--c-parchment-light)); color: rgb(var(--c-ink)); font-size: .78rem; transition: border-color .2s, background .2s, transform .2s, box-shadow .2s; }
.account-nav-link:hover { transform: translateY(-2px); border-color: rgb(var(--c-gold)); box-shadow: 0 8px 22px #0000000e; }
.account-nav-link.is-current { border-color: rgb(var(--c-gold) / .75); background: rgb(var(--c-gold) / .1); color: rgb(var(--c-gold-dark)); font-weight: 600; }
.account-nav-link:focus-visible { outline: 2px solid rgb(var(--c-gold-dark)); outline-offset: 2px; }
.account-nav-arrow { color: rgb(var(--c-gold-dark)); font-size: 1rem; }
.account-content { margin-top: clamp(1.9rem, 3vw, 2.8rem); }
.account-section-heading { display: flex; align-items: center; gap: 1rem; }
.account-section-rule { width: 2.8rem; height: 1px; background: rgb(var(--c-gold-dark)); }
.account-section-heading h2 { font: 400 clamp(1.5rem, 2.5vw, 2rem)/1.2 Georgia, 'YekanBakh', serif; }
@media (max-width: 760px) { .account-nav { grid-template-columns: repeat(2, minmax(0,1fr)); } .account-hero-content { width: 100%; min-height: 12rem; align-items: flex-start; flex-direction: column; } .account-logo-shadow { opacity: .07; width: 70%; right: -17%; } }
@media (prefers-reduced-motion: reduce) { .account-nav-link { transition: none; } }
</style>
