<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()

const tabs = [
  { key: 'online', label: 'events.tabs.online' },
  { key: 'onsite', label: 'events.tabs.onsite' },
]
const active = ref('online')

const withIdx = (arr) => (Array.isArray(arr) ? arr : []).map((it, i) => ({ ...it, i }))
const onlineItems = computed(() => withIdx(tm('events.online.items')))
const onsiteItems = computed(() => withIdx(tm('events.onsite.items')))
const archiveItems = computed(() => tm('events.archive.items'))

const currentItems = computed(() => (active.value === 'online' ? onlineItems.value : onsiteItems.value))
const ongoing = computed(() => currentItems.value.filter((x) => x.phase === 'ongoing'))
const upcoming = computed(() => currentItems.value.filter((x) => (x.phase || 'upcoming') !== 'ongoing'))

const reserveLabel = computed(() => (active.value === 'online' ? t('events.online.watch') : t('events.onsite.register')))
const joinLabel = computed(() => (active.value === 'online' ? t('events.online.join') : t('events.onsite.join')))
const personOf = (item) => item.host || item.venue || ''

useReveal()
</script>

<template>
  <div>
    <section class="bg-ink py-20 md:py-28">
      <div class="max-w-5xl mx-auto px-8 text-center">
        <p class="text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light mb-6">
          {{ t('events.hero.eyebrow') }}
        </p>
        <h1 class="font-serif font-light text-parchment-light text-5xl md:text-6xl tracking-wide">
          {{ t('events.hero.title') }}
        </h1>
        <div class="mx-auto mt-10 h-px w-24 bg-gold"></div>
      </div>
    </section>

    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8">
        <p class="reveal max-w-2xl mx-auto text-center font-serif italic font-light text-2xl text-ink-soft leading-relaxed">
          {{ t('events.intro') }}
        </p>

        <!-- Prominent category toggle -->
        <div class="mt-12 flex justify-center">
          <div class="inline-flex p-1.5 rounded-full bg-parchment border border-parchment-deep/70 shadow-card">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              @click="active = tab.key"
              :class="[
                'px-9 sm:px-14 py-3.5 rounded-full text-sm sm:text-base uppercase tracking-[0.22em] transition-all duration-300',
                active === tab.key
                  ? 'bg-ink text-parchment-light font-normal shadow-soft'
                  : 'text-ink-muted hover:text-ink font-light'
              ]"
            >
              {{ t(tab.label) }}
            </button>
          </div>
        </div>

        <!-- ===================== ONGOING ===================== -->
        <div class="mt-16">
          <div class="flex items-center justify-center gap-3">
            <span class="relative flex h-2.5 w-2.5">
              <span class="absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-60 animate-ping"></span>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-red-500"></span>
            </span>
            <h2 class="font-serif font-light text-2xl md:text-3xl text-ink">{{ t('events.sections.ongoing') }}</h2>
          </div>
          <p class="mt-3 text-center text-sm text-ink-muted font-light max-w-lg mx-auto">{{ t('events.sections.ongoingDesc') }}</p>

          <div v-if="ongoing.length" class="mt-9 grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <article
              v-for="item in ongoing"
              :key="'ongoing-' + item.i"
              class="reveal relative rounded-lg border border-gold/40 bg-gradient-to-br from-gold/[0.07] to-transparent p-7 shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card-hover hover:border-gold/60"
            >
              <div class="flex items-center justify-between gap-3">
                <span class="inline-flex items-center gap-2 text-[10px] uppercase tracking-[0.25em] font-medium text-red-600 dark:text-red-400">
                  <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse-dot"></span>
                  {{ t('events.sections.liveNow') }}
                </span>
                <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ item.tag }}</span>
              </div>
              <h3 class="font-serif font-light text-xl text-ink mt-3 leading-snug">{{ item.title }}</h3>
              <p class="mt-1.5 text-xs text-ink-muted font-light">{{ personOf(item) }}</p>
              <p class="mt-1 text-xs text-ink-hint font-light uppercase tracking-[0.15em]">{{ item.date }}</p>

              <!-- Both online and on-site sessions stream into the same Live
                   Event hub. On-site sessions additionally surface the admin
                   broadcast ("Events messages") panel inside that hub. -->
              <router-link
                :to="`/events/active/${active}/${item.i}`"
                class="mt-6 inline-flex items-center justify-center gap-2.5 w-full text-[11px] uppercase tracking-[0.3em] font-light px-6 py-3.5 rounded-md bg-ink text-parchment-light hover:bg-gold-dark transition-colors"
              >
                {{ joinLabel }} <span class="dir-arrow" aria-hidden="true"></span>
              </router-link>
            </article>
          </div>
          <p v-else class="reveal mt-9 text-center text-sm text-ink-hint font-light italic">{{ t('events.sections.emptyOngoing') }}</p>
        </div>

        <!-- ===================== UPCOMING ===================== -->
        <div class="mt-20 max-w-3xl mx-auto">
          <SectionEyebrow :text="t('events.sections.upcoming')" />
          <p class="mt-3 text-center text-sm text-ink-muted font-light">{{ t('events.sections.upcomingDesc') }}</p>

          <div class="mt-9 space-y-6">
            <LuxeCard
              v-for="item in upcoming"
              :key="'upcoming-' + item.i"
              hover
              class="reveal flex flex-col md:flex-row md:items-center md:justify-between gap-5"
            >
              <div class="flex-1">
                <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ item.tag }}</span>
                <h3 class="font-serif font-light text-xl text-ink mt-2 mb-1 leading-snug">{{ item.title }}</h3>
                <p class="text-xs text-ink-muted font-light">{{ personOf(item) }}</p>
                <p class="mt-1 text-xs text-ink-hint font-light uppercase tracking-[0.15em]">{{ item.date }}</p>
              </div>
              <div class="flex flex-col items-start md:items-end gap-2 shrink-0">
                <span class="text-[11px] uppercase tracking-[0.2em] text-ink-muted font-light">{{ item.status }}</span>
                <router-link :to="`/events/reserve/${active}/${item.i}`" class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1">
                  {{ reserveLabel }} <span class="dir-arrow" aria-hidden="true"></span>
                </router-link>
              </div>
            </LuxeCard>
          </div>
        </div>

        <!-- ===================== PAST (Archive structure) ===================== -->
        <div class="mt-20">
          <SectionEyebrow :text="t('events.sections.past')" />
          <p class="mt-3 text-center text-sm text-ink-muted font-light max-w-lg mx-auto">{{ t('events.sections.pastDesc') }}</p>

          <div class="mt-10 grid md:grid-cols-2 gap-8">
            <router-link
              v-for="(item, i) in archiveItems"
              :key="'past-' + item.title + i"
              :to="`/events/archive/${i}`"
              class="reveal group block"
              :style="{ transitionDelay: `${(i % 6) * 60}ms` }"
            >
              <article class="bg-parchment border border-parchment-deep/70 rounded-lg p-8 md:p-10 shadow-card transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-card-hover group-hover:border-gold/50 flex gap-6 h-full">
                <div class="shrink-0 w-12 h-12 rounded-full border border-gold/40 flex items-center justify-center">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="text-gold">
                    <path d="M4 5h16v15H4z M4 9h16 M8 3v4 M16 3v4" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="flex items-baseline justify-between gap-3">
                    <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('events.sections.completedEvent') }}</span>
                    <span class="text-[11px] uppercase tracking-[0.2em] text-ink-hint font-light shrink-0">{{ item.date }}</span>
                  </div>
                  <h3 class="font-serif font-light text-lg text-ink mt-2 mb-2 leading-snug group-hover:text-gold-dark transition-colors">{{ item.title }}</h3>
                  <p class="text-sm text-ink-soft font-light leading-relaxed">{{ item.summary }}</p>
                  <span class="mt-4 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink group-hover:text-gold-dark transition-colors border-b border-gold/40 pb-1">
                    {{ t('events.archive.viewDetail') }} <span class="dir-arrow" aria-hidden="true"></span>
                  </span>
                </div>
              </article>
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
