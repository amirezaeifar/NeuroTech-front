<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useAuth } from '../composables/useAuth.js'
import { useReveal } from '../composables/useReveal.js'
import { eventsApi } from '../api/events.js'

const { t, tm, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const { isAuthenticated, ensureSession } = useAuth()

const apiEvent = ref(null), myReservation = ref(null), reserving = ref(false)
const showConfirm = ref(false), reservationError = ref('')
const eventType = computed(() => apiEvent.value?.kind || (route.params.type === 'onsite' ? 'onsite' : 'online'))
let timer, sequence = 0, stopped = false
const loadEvent = async () => {
  const request = ++sequence
  try {
    const { data } = await eventsApi.detail(route.params.id, locale.value)
    if (request !== sequence || stopped) return
    apiEvent.value = { ...data, tag: data.kind, host: data.host_label, date: new Intl.DateTimeFormat(locale.value, { dateStyle: 'medium', timeStyle: 'short', timeZone: data.timezone }).format(new Date(data.starts_at)) }
    if (isAuthenticated.value) {
      const response = await eventsApi.reservation(data.slug)
      if (request === sequence && !stopped) myReservation.value = response.data
    } else myReservation.value = null
  } catch (problem) { if (!stopped && request === sequence) reservationError.value = problem.message }
}
onMounted(async () => { try { await ensureSession() } catch (problem) { reservationError.value = problem.message }; if (stopped) return; await loadEvent(); if (!stopped) timer = window.setInterval(() => { if (!document.hidden) loadEvent() }, 10000) })
onUnmounted(() => { stopped = true; sequence++; clearInterval(timer) })
watch([() => route.params.id, locale], loadEvent)
const item = computed(() => apiEvent.value)
const venueOrHost = computed(() => eventType.value === 'onsite' ? item.value?.venue : item.value?.host)
const capacity = computed(() => apiEvent.value?.capacity ?? '∞')
const filled = computed(() => apiEvent.value?.reserved ?? 0)
const remaining = computed(() => apiEvent.value?.remaining ?? '∞')
const fillPct = computed(() => typeof capacity.value === 'number' ? Math.min(100, Math.round(filled.value / capacity.value * 100)) : 0)
const isReserved = computed(() => myReservation.value?.status === 'confirmed')
const awaitingEmail = computed(() => myReservation.value?.status === 'pending_email')
const closed = computed(() => !['upcoming', 'live'].includes(item.value?.status) || new Date(item.value?.ends_at).getTime() <= Date.now())
const confirmReservation = async () => {
  if (reserving.value) return
  reserving.value = true; reservationError.value = ''
  try {
    await ensureSession()
    if (!isAuthenticated.value) { router.push({ name: 'Login', query: { redirect: route.fullPath } }); return }
    if (!apiEvent.value) return
    if (isReserved.value) showConfirm.value = true
    else { myReservation.value = (await eventsApi.reserve(apiEvent.value.slug)).data; showConfirm.value = true; if (isReserved.value) await loadEvent() }
  } catch (problem) { reservationError.value = problem.message }
  finally { reserving.value = false }
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
            <p v-for="(para, i) in (apiEvent?.description || t('events.reservation.eventDesc')).split('\n\n').filter(Boolean)" :key="i">{{ para }}</p>
          </div>

          <!-- Confirm Reservation — right-aligned, flush with the content's
               right (inline-end) edge above it. -->
          <div class="reveal mt-10 flex flex-col items-end">
            <button
              type="button"
              @click="confirmReservation" :disabled="reserving || (!isReserved && (remaining === 0 || closed))"
              class="ml-auto inline-flex items-center justify-center gap-2.5 text-[11px] uppercase tracking-[0.3em] font-light px-8 py-4 rounded-md bg-ink text-parchment-light border border-ink hover:bg-gold hover:text-ink hover:border-gold transition-colors"
            >
              {{ isReserved ? t('events.reservation.modalTitle') : awaitingEmail ? (locale === 'fa' ? 'ارسال دوباره ایمیل' : 'Resend email') : t('events.reservation.submit') }} <span class="dir-arrow" aria-hidden="true"></span>
            </button>
            <p v-if="reservationError" class="mt-3 text-xs text-red-700" role="alert">{{ reservationError }}</p>
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
          <h2 class="mt-6 font-serif font-light text-2xl text-ink">{{ isReserved ? t('events.reservation.modalTitle') : (locale === 'fa' ? 'ایمیل تأیید ارسال شد' : 'Confirmation email sent') }}</h2>
          <p class="mt-3 text-sm text-ink-soft font-light leading-relaxed">{{ isReserved ? t('events.reservation.modalBody', { title: item.title }) : (locale === 'fa' ? 'برای ثبت رزرو و ورود به لایو، روی لینک ارسالی به ایمیل تأییدشده خود کلیک کنید.' : 'Click the link sent to your verified email to confirm your reservation and enter the live event.') }}</p>
          <div class="mt-8 flex items-center justify-center gap-6 flex-wrap">
            <button type="button" class="text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1" @click="showConfirm = false">{{ t('events.reservation.modalClose') }}</button>
            <router-link to="/events" class="text-[11px] uppercase tracking-[0.25em] text-ink-muted hover:text-ink transition-colors border-b border-transparent hover:border-gold/40 pb-1">{{ t('events.reservation.backCta') }}</router-link>
            <router-link v-if="isReserved && apiEvent?.status === 'live'" :to="`/events/live/${apiEvent.slug}`" class="text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold pb-1">{{ locale === 'fa' ? 'ورود به لایو' : 'Enter live room' }}</router-link>
          </div>
        </div>
      </div>
    </Transition>
  </div>

  <div v-else class="py-32 text-center">
    <p v-if="reservationError" role="alert" class="mb-5 text-sm text-red-700">{{ reservationError }}</p>
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

