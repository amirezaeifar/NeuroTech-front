<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t, tm } = useI18n()
const route = useRoute()
const router = useRouter()

// NOTE: access control is enforced by the router guard (meta.requiresAuth) in
// src/router/index.js — unauthenticated visitors are redirected to /login with a
// ?redirect back here, so by the time this view renders the user is signed in.

const courses = computed(() => tm('academy.courses'))
const courseIndex = computed(() => {
  const raw = route.query.course
  return raw !== undefined && raw !== null && courses.value[Number(raw)] ? Number(raw) : null
})
const course = computed(() => (courseIndex.value !== null ? courses.value[courseIndex.value] : null))
const itemName = computed(() => course.value?.title || t('academy.tiers.premium.name') + ' — ' + t('brand'))
const included = computed(() => tm('checkout.included'))

const stage = ref('form')      // form | processing | success
const step = ref('cart')        // cart | payment
const paymentMethod = ref('card')

// Keep the viewport exactly where it is when moving to the payment step — no
// scroll jump. The two steps occupy the same region, so the eye stays put.
const goToPayment = () => { step.value = 'payment' }
const goToCart = () => { step.value = 'cart' }

const submit = () => {
  stage.value = 'processing'
  window.setTimeout(() => { stage.value = 'success' }, 1400)
}

// Return to the course with the purchase confirmed — ?purchased=true unlocks the
// player and lesson list on the course page (mocks a post-payment redirect).
const goBack = () => {
  if (courseIndex.value !== null) {
    router.push({ path: `/academy/course/${courseIndex.value}`, query: { purchased: 'true' } })
  } else {
    router.push('/academy')
  }
}

// Entrance motion presets (subtle slide-up + fade, staggered by delay).
const rise = (delay = 0) => ({
  initial: { opacity: 0, y: 26 },
  enter: { opacity: 1, y: 0, transition: { duration: 600, delay, ease: 'easeOut' } },
})
</script>

<template>
  <div class="checkout-page">
    <!-- ── Hero (always-dark, premium band) ───────────────────────────── -->
    <section class="checkout-hero relative overflow-hidden py-16 md:py-24">
      <div class="checkout-hero-glow pointer-events-none absolute inset-0"></div>
      <div class="relative max-w-3xl mx-auto px-8 text-center">
        <p class="text-[11px] uppercase tracking-[0.35em] text-[#EDC071] font-light mb-5">{{ t('checkout.hero.eyebrow') }}</p>
        <h1 class="font-serif font-light text-[#F2EDE4] text-4xl md:text-5xl tracking-wide">{{ t('checkout.hero.title') }}</h1>
        <p class="mt-4 text-sm text-[#F2EDE4]/60 font-light">{{ t('checkout.heroSubtitle') }}</p>
      </div>
    </section>

    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-6 md:px-8">

        <!-- ── Success state ── -->
        <div v-if="stage === 'success'" class="text-center" v-motion v-bind="rise()">
          <div class="max-w-md mx-auto bg-parchment border border-parchment-deep/70 rounded-xl p-10 lux-card">
            <div class="mx-auto w-14 h-14 rounded-full border border-gold/60 bg-gold/10 flex items-center justify-center text-gold-dark">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <h2 class="mt-6 font-serif font-light text-2xl text-ink">{{ t('checkout.successTitle') }}</h2>
            <p class="mt-3 text-sm text-ink-soft font-light leading-relaxed">{{ t('checkout.successDesc') }}</p>
            <div class="mt-8 flex items-center justify-center gap-8 flex-wrap">
              <button class="text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1" @click="goBack">{{ t('checkout.backCta') }}</button>
              <router-link to="/academy" class="text-[11px] uppercase tracking-[0.25em] text-ink-muted hover:text-ink transition-colors border-b border-transparent hover:border-gold/40 pb-1">{{ t('checkout.continueCta') }}</router-link>
            </div>
          </div>
        </div>

        <!-- ── Checkout flow ── -->
        <div v-else>
          <!-- Step indicator -->
          <div class="mb-12 flex items-center justify-center gap-4 text-[11px] uppercase tracking-[0.2em] font-light" v-motion v-bind="rise()">
            <div class="flex items-center gap-2.5" :class="step === 'cart' ? 'text-gold-dark' : 'text-ink-muted'">
              <span class="flex items-center justify-center w-7 h-7 border rounded-full" :class="step === 'cart' ? 'border-gold text-gold-dark' : 'border-parchment-deep'">1</span>
              <span>{{ t('checkout.cartTitle') }}</span>
            </div>
            <span class="w-10 h-px bg-parchment-deep"></span>
            <div class="flex items-center gap-2.5" :class="step === 'payment' ? 'text-gold-dark' : 'text-ink-muted'">
              <span class="flex items-center justify-center w-7 h-7 border rounded-full" :class="step === 'payment' ? 'border-gold text-gold-dark' : 'border-parchment-deep'">2</span>
              <span>{{ t('checkout.paymentTitle') }}</span>
            </div>
          </div>

          <div class="grid lg:grid-cols-5 gap-8 lg:gap-12 items-start">
            <!-- Main column -->
            <div class="lg:col-span-3">
              <!-- Steps crossfade/slide into one another (mode out-in keeps a single
                   box in flow at a time, so its top stays flush with Order Summary). -->
              <Transition name="step-fade" mode="out-in">
              <!-- Step 1: Shopping cart -->
              <div v-if="step === 'cart'" key="cart">
                <div class="bg-parchment border border-parchment-deep/70 rounded-xl overflow-hidden lux-card">
                  <header class="flex items-center gap-3 px-7 py-5 border-b border-parchment-deep/70">
                    <span class="grid place-items-center h-9 w-9 rounded-full border border-gold/40 text-gold-dark">
                      <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/><path d="M2 3h2l2.4 12.4a2 2 0 0 0 2 1.6h8.6a2 2 0 0 0 2-1.6L22 7H6"/></svg>
                    </span>
                    <h2 class="font-serif font-light text-xl text-ink">{{ t('checkout.cartTitle') }}</h2>
                  </header>

                  <!-- Line item -->
                  <div class="flex items-start gap-5 px-7 py-6">
                    <div class="shrink-0 w-16 h-16 rounded-lg flex items-center justify-center text-gold-dark border border-gold/30" style="background: linear-gradient(135deg, rgb(var(--c-gold) / 0.12), rgb(var(--c-gold) / 0.03));">
                      <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6.5v5c0 4.5 3.2 7.8 8 9 4.8-1.2 8-4.5 8-9v-5z"/><path d="m9 12 2 2 4-4.5"/></svg>
                    </div>
                    <div class="min-w-0 flex-1">
                      <h3 class="font-serif font-light text-lg text-ink leading-snug">{{ itemName }}</h3>
                      <p class="mt-1 text-xs text-ink-muted font-light uppercase tracking-[0.15em]">{{ t('checkout.cartItemSubtitle') }}</p>
                      <span class="mt-3 inline-block text-[10px] uppercase tracking-[0.2em] text-gold border border-gold/50 px-2.5 py-1 font-light">{{ t('academy.filters.premium') }}</span>
                    </div>
                    <div class="shrink-0 text-end">
                      <p class="font-serif text-lg text-ink">{{ t('checkout.mockPrice') }}</p>
                    </div>
                  </div>

                  <!-- Included features -->
                  <div class="px-7 pb-7 pt-1">
                    <p class="text-[11px] uppercase tracking-[0.25em] text-ink-muted font-light mb-4">{{ t('checkout.includedTitle') }}</p>
                    <ul class="space-y-3">
                      <li v-for="(feat, i) in included" :key="i" class="flex items-start gap-3 text-sm text-ink-soft font-light">
                        <svg class="shrink-0 mt-0.5 text-gold-dark" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                        {{ feat }}
                      </li>
                    </ul>
                  </div>
                </div>

                <button
                  type="button"
                  @click="goToPayment"
                  class="mt-7 w-full inline-flex items-center justify-center gap-2.5 text-[11px] uppercase tracking-[0.3em] font-light px-6 py-4 rounded-md border border-gold/60 bg-ink text-parchment-light hover:bg-gold hover:text-ink hover:border-gold transition-colors"
                >
                  {{ t('checkout.proceedCta') }} <span class="dir-arrow" aria-hidden="true"></span>
                </button>
              </div>

              <!-- Step 2: Payment method -->
              <div v-else key="payment">
                <div class="bg-parchment border border-parchment-deep/70 rounded-xl p-7 md:p-8 lux-card">
                  <h2 class="font-serif font-light text-xl text-ink mb-6">{{ t('checkout.paymentTitle') }}</h2>
                  <form class="space-y-6" @submit.prevent="submit">
                    <div class="space-y-3">
                      <label
                        v-for="opt in ['card', 'bank']"
                        :key="opt"
                        class="flex items-center gap-4 px-5 py-4 border rounded-lg cursor-pointer transition-colors"
                        :class="paymentMethod === opt ? 'border-gold bg-gold/10' : 'border-parchment-deep hover:border-gold/40'"
                      >
                        <input v-model="paymentMethod" type="radio" name="paymentMethod" :value="opt" class="accent-gold" />
                        <span class="grid place-items-center h-9 w-9 rounded-md border border-parchment-deep text-ink-muted">
                          <svg v-if="opt === 'card'" viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.4"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></svg>
                          <svg v-else viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M4 10h16M5 10V7l7-4 7 4v3M6 10v8M10 10v8M14 10v8M18 10v8"/></svg>
                        </span>
                        <span class="text-sm font-light text-ink">{{ t(`checkout.paymentOptions.${opt}`) }}</span>
                      </label>
                    </div>

                    <div class="flex items-center gap-2.5 text-[11px] text-ink-muted font-light">
                      <svg class="shrink-0 text-gold-dark" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V8a4 4 0 0 1 8 0v3" stroke-linecap="round"/></svg>
                      {{ t('checkout.securedNote') }}
                    </div>

                    <div class="flex items-center gap-5 pt-1">
                      <button type="button" @click="goToCart" class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink-muted hover:text-ink transition-colors border-b border-transparent hover:border-gold/40 pb-1">
                        <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('checkout.back') }}
                      </button>
                      <button
                        type="submit"
                        :disabled="stage === 'processing'"
                        class="checkout-confirm flex-1 inline-flex items-center justify-center gap-2 text-[11px] uppercase tracking-[0.2em] font-normal px-7 py-3 rounded-lg border transition-all duration-300"
                        :class="stage === 'processing' ? 'border-parchment-deep text-ink-muted cursor-wait' : 'border-ink/80 bg-ink text-parchment-light shadow-sm hover:bg-gold hover:text-ink hover:border-gold hover:shadow-md hover:-translate-y-px'"
                      >
                        <svg v-if="stage === 'processing'" class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9" stroke-opacity="0.25" /><path d="M21 12a9 9 0 0 0-9-9" stroke-linecap="round" /></svg>
                        {{ stage === 'processing' ? t('checkout.processing') : t('checkout.submit') }}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
              </Transition>
            </div>

            <!-- Order summary (static sidebar — top edge sits flush with the main column) -->
            <aside class="lg:col-span-2" v-motion v-bind="rise(160)">
              <div class="bg-parchment border border-parchment-deep/70 rounded-xl p-7 lux-card">
                <h3 class="font-serif font-light text-lg text-ink mb-6">{{ t('checkout.summaryTitle') }}</h3>
                <dl class="space-y-4 text-sm">
                  <div class="flex items-start justify-between gap-4">
                    <dt class="text-ink-muted font-light">{{ t('checkout.itemLabel') }}</dt>
                    <dd class="text-ink font-light text-end leading-snug">{{ itemName }}</dd>
                  </div>
                  <div class="flex items-center justify-between gap-4">
                    <dt class="text-ink-muted font-light">{{ t('checkout.subtotalLabel') }}</dt>
                    <dd class="text-ink font-light">{{ t('checkout.mockPrice') }}</dd>
                  </div>
                  <div class="flex items-center justify-between gap-4">
                    <dt class="text-ink-muted font-light">{{ t('checkout.vatLabel') }}</dt>
                    <dd class="text-ink-muted font-light italic text-xs">{{ t('checkout.vatNote') }}</dd>
                  </div>
                  <div class="flex items-center justify-between gap-4 pt-4 mt-1 border-t border-parchment-deep">
                    <dt class="text-ink uppercase tracking-[0.15em] text-[11px] font-light">{{ t('checkout.totalLabel') }}</dt>
                    <dd class="text-ink font-serif text-xl">{{ t('checkout.mockPrice') }}</dd>
                  </div>
                </dl>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Always-dark hero band (fixed warm-charcoal so it never inverts with theme). */
.checkout-hero { background: linear-gradient(160deg, #14110E 0%, #1C1915 100%); }
.checkout-hero-glow { background: radial-gradient(60% 90% at 50% 0%, rgba(237, 192, 113, 0.14), transparent 70%); }

/* ── Step 1 → Step 2 transition ──────────────────────────────────────────────
   A gentle fade + slide as the cart hands off to the payment step. `out-in`
   means the leaving box fully clears before the next eases in, so there is no
   overlap jump and the top edge stays flush with the Order Summary. */
.step-fade-enter-active { transition: opacity 420ms ease, transform 480ms cubic-bezier(0.22, 1, 0.36, 1); }
.step-fade-leave-active { transition: opacity 240ms ease, transform 240ms ease; }
.step-fade-enter-from { opacity: 0; transform: translateX(22px); }
.step-fade-leave-to { opacity: 0; transform: translateX(-16px); }
:global(html[dir='rtl']) .step-fade-enter-from { transform: translateX(-22px); }
:global(html[dir='rtl']) .step-fade-leave-to { transform: translateX(16px); }
</style>
