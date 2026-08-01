<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useAuth } from '../composables/useAuth.js'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()
const route = useRoute()
const router = useRouter()
const { isAuthenticated } = useAuth()

const eventType = computed(() => (route.params.type === 'onsite' ? 'onsite' : 'online'))
const eventItems = computed(() => tm(`events.${eventType.value}.items`))
const itemIndex = computed(() => Number(route.params.id))
const item = computed(() => eventItems.value[itemIndex.value])
const venueOrHost = computed(() => item.value?.host || item.value?.venue || '')

// ── Mock capacity (a real backend would supply these per session) ──
const capacity = 100
const filled = 75
const remaining = computed(() => Math.max(capacity - filled, 0))
const fillPct = computed(() => Math.round((filled / capacity) * 100))

// ── Confirm-reservation flow with an auth guard ──
// Logged in  → show the "Reservation Confirmed" modal.
// Logged out → bounce to /login, remembering this page so the user lands back
//              here after signing in and can confirm.
const showConfirm = ref(false)
const confirmReservation = () => {
  if (isAuthenticated.value) {
    showConfirm.value = true
  } else {
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
  }
}

useReveal()
</script>

<template>
  <div v-if="item">
    <section class="bg-ink py-16 md:py-24">
      <div class="max-w-5xl mx-auto px-8">
        <router-link to="/events" class="text-[11px] uppercase tracking-[0.25em] text-gold/80 hover:text-gold transition-colors inline-flex items-center gap-2">
          <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('events.reservation.backCta') }}
        </router-link>
        <p class="mt-8 text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light">{{ t('events.reservation.eyebrow') }}</p>
        <h1 class="mt-3 font-serif font-light text-parchment-light text-4xl md:text-5xl tracking-wide">{{ t('events.reservation.title') }}</h1>
        <p class="mt-4 max-w-xl text-sm text-parchment-light/70 font-light leading-relaxed">{{ t('events.reservation.intro') }}</p>
      </div>
    </section>

    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8 grid lg:grid-cols-3 gap-10 lg:gap-14 lg:items-start">
        <!-- ── Left: Event Info (1/3) ── -->
        <aside class="lg:col-span-1">
          <LuxeCard class="reveal" :title="t('events.reservation.infoTitle')">
            <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ item.tag }}</span>
            <h3 class="font-serif font-light text-xl text-ink mt-2 mb-3 leading-snug">{{ item.title }}</h3>

            <dl class="space-y-3.5 text-sm mt-5">
              <div class="flex items-start justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light shrink-0">{{ eventType === 'onsite' ? t('events.reservation.venueLabel') : t('events.reservation.hostLabel') }}</dt>
                <dd class="text-ink font-light text-right leading-snug">{{ venueOrHost }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light shrink-0">{{ t('events.reservation.dateLabel') }}</dt>
                <dd class="text-ink font-light text-right leading-snug">{{ item.date }}</dd>
              </div>
              <div class="flex items-start justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light shrink-0">{{ t('events.reservation.statusLabel') }}</dt>
                <dd class="text-ink font-light text-right leading-snug">{{ item.status }}</dd>
              </div>
            </dl>

            <!-- Capacity indicator -->
            <div class="mt-6 pt-5 border-t border-parchment-deep">
              <div class="flex items-center justify-between text-[11px] uppercase tracking-[0.15em] font-light">
                <span class="text-ink-muted">{{ t('events.reservation.capacityLabel') }}: <span class="text-ink tabular-nums">{{ capacity }}</span></span>
                <span class="text-ink-muted">{{ t('events.reservation.filledLabel') }}: <span class="text-gold-dark tabular-nums">{{ filled }}</span></span>
              </div>
              <div class="mt-3 h-2 w-full rounded-full bg-parchment-deep/60 overflow-hidden">
                <div class="h-full rounded-full bg-gold transition-all duration-700" :style="{ width: fillPct + '%' }"></div>
              </div>
              <p class="mt-2.5 text-[11px] text-ink-hint font-light italic">{{ t('events.reservation.spotsRemaining', { count: remaining }) }}</p>
            </div>
          </LuxeCard>
        </aside>

        <!-- ── Right: Event Description (2/3) + CTA ── -->
        <div class="lg:col-span-2">
          <SectionEyebrow :text="t('events.reservation.descriptionTitle')" />
          <div class="reveal mt-6 space-y-4 text-[15px] text-ink-soft font-light leading-loose">
            <p v-for="(para, i) in t('events.reservation.eventDesc').split('\n\n').filter(Boolean)" :key="i">{{ para }}</p>
          </div>

          <!-- Confirm Reservation — right-aligned, flush with the content's
               right (inline-end) edge above it. -->
          <div class="reveal mt-10 flex flex-col items-end">
            <button
              type="button"
              @click="confirmReservation"
              class="ml-auto inline-flex items-center justify-center gap-2.5 text-[11px] uppercase tracking-[0.3em] font-light px-8 py-4 rounded-md bg-ink text-parchment-light border border-ink hover:bg-gold hover:text-ink hover:border-gold transition-colors"
            >
              {{ t('events.reservation.submit') }} <span class="dir-arrow" aria-hidden="true"></span>
            </button>
            <p v-if="!isAuthenticated" class="mt-3 text-[11px] text-ink-muted font-light italic text-end">{{ t('events.reservation.signInHint') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Reservation Confirmed modal (logged-in path) ── -->
    <Transition name="modal-fade">
      <div v-if="showConfirm" class="reserve-modal" role="dialog" aria-modal="true" @click.self="showConfirm = false">
        <div class="reserve-modal-card">
          <div class="mx-auto w-14 h-14 rounded-full border border-gold/60 bg-gold/10 flex items-center justify-center text-gold-dark">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <h2 class="mt-6 font-serif font-light text-2xl text-ink">{{ t('events.reservation.modalTitle') }}</h2>
          <p class="mt-3 text-sm text-ink-soft font-light leading-relaxed">{{ t('events.reservation.modalBody', { title: item.title }) }}</p>
          <div class="mt-8 flex items-center justify-center gap-6 flex-wrap">
            <button type="button" class="text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1" @click="showConfirm = false">{{ t('events.reservation.modalClose') }}</button>
            <router-link to="/events" class="text-[11px] uppercase tracking-[0.25em] text-ink-muted hover:text-ink transition-colors border-b border-transparent hover:border-gold/40 pb-1">{{ t('events.reservation.backCta') }}</router-link>
          </div>
        </div>
      </div>
    </Transition>
  </div>

  <div v-else class="py-32 text-center">
    <button class="text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1" @click="router.push('/events')">
      {{ t('events.reservation.backCta') }}
    </button>
  </div>
</template>

<style scoped>
.reserve-modal {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(10, 8, 6, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.reserve-modal-card {
  width: 100%;
  max-width: 26rem;
  text-align: center;
  padding: 2.5rem 2rem;
  border-radius: 16px;
  background: rgb(var(--c-parchment));
  border: 1px solid rgb(var(--c-parchment-deep) / 0.7);
  box-shadow: 0 40px 90px -30px rgba(0, 0, 0, 0.6);
}

/* Modal fade + lift */
.modal-fade-enter-active { transition: opacity 240ms ease; }
.modal-fade-leave-active { transition: opacity 200ms ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .reserve-modal-card { transition: transform 320ms cubic-bezier(0.16, 1, 0.3, 1); }
.modal-fade-enter-from .reserve-modal-card { transform: translateY(16px) scale(0.97); }

@media (prefers-reduced-motion: reduce) {
  .modal-fade-enter-active .reserve-modal-card { transition: none; }
}
</style>
