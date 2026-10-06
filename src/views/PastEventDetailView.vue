<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useReveal } from '../composables/useReveal.js'
import { eventsApi } from '../api/events.js'
import { resolveApiUrl } from '../api/client.js'
import EventStream from '../components/EventStream.vue'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

// Writing direction — drives native RTL chevron glyphs (no scaleX mirroring)
// and the keyboard arrow mapping.
const isRtl = computed(() => locale.value === 'fa')
// Chevron pointing toward the gallery's start / end edge in the current
// direction. In LTR the start edge is the left; in RTL it is the right.
const chevronToStart = computed(() => (isRtl.value ? 'M9 6l6 6-6 6' : 'M15 6l-6 6 6 6'))
const chevronToEnd = computed(() => (isRtl.value ? 'M15 6l-6 6 6 6' : 'M9 6l6 6-6 6'))

const apiEvent = ref(null)
let loadSequence = 0
const loadEvent = async () => {
  const sequence = ++loadSequence
  try {
    const { data } = await eventsApi.detail(route.params.id, locale.value)
    if (sequence !== loadSequence) return
    apiEvent.value = { ...data, date: new Intl.DateTimeFormat(locale.value, { dateStyle: 'medium', timeZone: data.timezone }).format(new Date(data.starts_at)) }
    activeImg.value = 0
    lightboxOpen.value = false
  } catch { if (sequence === loadSequence) apiEvent.value = null }
}
onMounted(loadEvent)
watch([() => route.params.id, locale], loadEvent)
const item = computed(() => apiEvent.value)
const content = computed(() => item.value?.content || {})
const agenda = computed(() => content.value.agenda || [])
const faq = computed(() => content.value.faq || [])
const assetUrl = (url) => url?.startsWith('/api/') ? resolveApiUrl(url) : url
const documents = computed(() => (content.value.documents || []).map(d => ({ ...d, url: assetUrl(d.url) })))
const videos = computed(() => content.value.videos || [])
const docIcon = (type) => (type === 'XLSX'
  ? 'M7 3h10l4 4v14H7z M9 12l4 4 M13 12l-4 4'
  : 'M7 3h7l4 4v14H7z M14 3v4h4 M9 13h6 M9 16h4')

// Q&A accordion — one panel open at a time.
const openFaq = ref(0)
const toggleFaq = (i) => { openFaq.value = openFaq.value === i ? -1 : i }

const gallery = computed(() => (content.value.gallery || []).map(g => ({ ...g, url: assetUrl(g.url), caption: g.name })))
const coverImage = computed(() => assetUrl(item.value?.cover_url))

const activeImg = ref(0)
const count = computed(() => gallery.value.length)
const next = () => { activeImg.value = (activeImg.value + 1) % (count.value || 1) }
const prev = () => { activeImg.value = (activeImg.value - 1 + count.value) % (count.value || 1) }
const goTo = (i) => { activeImg.value = i }
const pad = (n) => String(n).padStart(2, '0')
const trackStyle = computed(() => ({ transform: `translateX(-${activeImg.value * 100}%)` }))

// ── Lightbox (fullscreen) ──
const lightboxOpen = ref(false)
const openLightbox = () => { lightboxOpen.value = true }
const closeLightbox = () => { lightboxOpen.value = false }

// Lock body scroll while the lightbox is open.
watch(lightboxOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

const onKey = (e) => {
  if (!lightboxOpen.value) return
  if (e.key === 'Escape') closeLightbox()
  // Physical arrow keys map to logical direction: in RTL, ArrowLeft advances.
  else if (e.key === 'ArrowRight') isRtl.value ? prev() : next()
  else if (e.key === 'ArrowLeft') isRtl.value ? next() : prev()
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => { window.removeEventListener('keydown', onKey); document.body.style.overflow = '' })

useReveal()
</script>

<template>
  <div v-if="item">
    <section class="bg-ink py-16 md:py-24">
      <div class="max-w-4xl mx-auto px-8">
        <router-link to="/events" class="text-[11px] uppercase tracking-[0.25em] text-gold/80 hover:text-gold transition-colors inline-flex items-center gap-2">
          <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('events.pastDetail.back') }}
        </router-link>
        <p class="mt-8 text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light">{{ t('events.pastDetail.eyebrow') }} · {{ t('events.sections.completedEvent') }}</p>
        <h1 class="mt-3 font-serif font-light text-parchment-light text-4xl md:text-5xl tracking-wide leading-snug">{{ item.title }}</h1>
        <p class="mt-4 text-sm text-parchment-light/70 uppercase tracking-[0.2em] font-light">{{ item.date }}</p>
        <img v-if="coverImage" :src="coverImage" :alt="item.title" class="mt-8 max-h-96 w-full rounded-xl object-cover" />
      </div>
    </section>

    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-4xl mx-auto px-8">
        <p class="reveal font-serif italic font-light text-2xl text-ink-soft leading-relaxed max-w-2xl">{{ item.summary }}</p>

        <!-- ── General Description ── -->
        <div class="mt-14">
          <SectionEyebrow :text="t('events.pastDetail.descriptionTitle')" />
          <div class="reveal mt-7 max-w-2xl">
            <p class="text-[15px] text-ink-soft font-light leading-loose whitespace-pre-line">{{ item.description }}</p>
          </div>
        </div>

        <!-- ── Interactive gallery ── -->
        <div v-if="gallery.length" class="mt-20">
          <SectionEyebrow :text="t('events.pastDetail.galleryTitle')" />

          <div v-if="gallery.length" class="gal mt-7 reveal">
            <!-- Main viewport -->
            <div class="gal-stage">
              <div class="gal-track" :style="trackStyle">
                <button
                  v-for="(g, i) in gallery"
                  :key="i"
                  type="button"
                  class="gal-slide"
                  
                  @click="openLightbox"
                  :aria-label="t('events.pastDetail.viewFull')"
                >
                  <img :src="g.url" :alt="g.caption" class="absolute inset-0 h-full w-full object-cover" loading="lazy"><span class="gal-plate-no relative">{{ pad(i + 1) }}</span>
                  <span class="gal-caption relative bg-black/40 px-3 py-1 rounded">{{ g.caption }}</span>
                </button>
              </div>

              <!-- Prev / Next -->
              <button type="button" class="gal-arrow gal-arrow--prev" @click="prev" :aria-label="t('events.pastDetail.prevImage')">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path :d="chevronToStart" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
              <button type="button" class="gal-arrow gal-arrow--next" @click="next" :aria-label="t('events.pastDetail.nextImage')">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path :d="chevronToEnd" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>

              <!-- Counter + fullscreen toggle -->
              <span class="gal-counter">{{ pad(activeImg + 1) }} / {{ pad(count) }}</span>
              <button type="button" class="gal-full" @click="openLightbox" :aria-label="t('events.pastDetail.viewFull')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M21 16v3a2 2 0 0 1-2 2h-3M3 16v3a2 2 0 0 0 2 2h3" stroke-linecap="round"/></svg>
              </button>
            </div>

            <!-- Thumbnail strip -->
            <div class="gal-thumbs">
              <button
                v-for="(g, i) in gallery"
                :key="'t' + i"
                type="button"
                class="gal-thumb"
                :class="{ 'is-active': i === activeImg }"
                
                @click="goTo(i)"
                :aria-label="`${t('events.pastDetail.galleryTitle')} ${pad(i + 1)}`"
              >
                <img :src="g.url" :alt="g.caption" class="absolute inset-0 h-full w-full object-cover" loading="lazy"><span class="relative">{{ pad(i + 1) }}</span>
              </button>
            </div>
          </div>
        </div>

        <div v-for="video in videos" :key="video.url" class="mt-8"><h3 class="font-serif text-xl text-ink mb-3">{{ video.name }}</h3><div class="aspect-video rounded-xl overflow-hidden bg-black"><EventStream :url="video.url" :title="video.name" /></div></div>
        <!-- ── Syllabus & Agenda ── -->
        <div v-if="agenda.length" class="mt-20">
          <SectionEyebrow :text="t('events.pastDetail.agendaTitle')" />
          <ol class="mt-9 relative">
            <li v-for="(a, i) in agenda" :key="i" class="reveal relative flex gap-5 pb-8 last:pb-0" :style="{ transitionDelay: `${i * 50}ms` }">
              <!-- rail -->
              <span v-if="i < agenda.length - 1" class="absolute top-7 bottom-0 w-px bg-parchment-deep" style="inset-inline-start: 3.25rem;"></span>
              <span class="shrink-0 w-[3.25rem] pt-0.5 text-end font-serif font-light text-gold-dark text-sm tabular-nums">{{ a.time }}</span>
              <span class="relative z-10 mt-1.5 shrink-0 w-3 h-3 rounded-full border-2 border-gold bg-parchment-light"></span>
              <div class="flex-1 -mt-0.5">
                <p class="font-serif font-light text-lg text-ink leading-snug">{{ a.title }}</p>
                <p class="mt-1 text-sm text-ink-soft font-light leading-relaxed">{{ a.detail }}</p>
              </div>
            </li>
          </ol>
        </div>

        <!-- ── Key Q&A (accordion) ── -->
        <div v-if="faq.length" class="mt-20">
          <SectionEyebrow :text="t('events.pastDetail.faqTitle')" />
          <div class="mt-9 space-y-3">
            <div
              v-for="(f, i) in faq" :key="i"
              class="reveal rounded-xl border border-parchment-deep/70 bg-parchment overflow-hidden lux-card"
              :style="{ transitionDelay: `${i * 50}ms` }"
            >
              <button
                type="button"
                class="w-full flex items-center justify-between gap-4 px-6 py-5 text-start"
                :aria-expanded="openFaq === i"
                @click="toggleFaq(i)"
              >
                <span class="font-serif font-light text-lg text-ink leading-snug" :class="openFaq === i ? 'text-gold-dark' : ''">{{ f.q }}</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
                     class="shrink-0 text-gold-dark transition-transform duration-300" :class="openFaq === i ? 'rotate-45' : ''">
                  <path d="M12 5v14M5 12h14" stroke-linecap="round"/>
                </svg>
              </button>
              <Transition name="faq">
                <div v-if="openFaq === i" class="faq-panel">
                  <p class="px-6 pb-6 -mt-1 text-sm text-ink-soft font-light leading-relaxed">{{ f.a }}</p>
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <!-- ── Documents & Resources ── -->
        <div v-if="documents.length" class="mt-20">
          <SectionEyebrow :text="t('events.pastDetail.resourcesTitle')" />
          <div class="mt-9 grid sm:grid-cols-2 gap-4">
            <a
              v-for="(d, i) in documents" :key="i"
              :href="d.url + (d.url.includes('?' ) ? '&' : '?') + 'download=1'" target="_blank" rel="noopener noreferrer"
              
              class="reveal group flex items-center gap-4 rounded-xl border border-parchment-deep/70 bg-parchment px-5 py-4 lux-card hover:border-gold/50"
              :style="{ transitionDelay: `${i * 50}ms` }"
            >
              <span class="shrink-0 grid place-items-center w-11 h-11 rounded-lg border border-gold/40 text-gold-dark">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path :d="docIcon(d.type)" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
              <span class="min-w-0 flex-1">
                <span class="block text-sm text-ink font-light leading-snug group-hover:text-gold-dark transition-colors">{{ d.name }}</span>
                <span class="block mt-0.5 text-[10px] uppercase tracking-[0.15em] text-ink-hint font-light">{{ d.type }} · {{ d.size }}</span>
              </span>
              <span class="shrink-0 inline-flex items-center gap-1.5 text-[10px] uppercase tracking-[0.2em] text-ink-muted group-hover:text-gold-dark transition-colors">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <span class="hidden sm:inline">{{ t('events.pastDetail.downloadLabel') }}</span>
              </span>
            </a>
          </div>
        </div>

        <!-- Closing note -->
        <LuxeCard v-if="content.closing_note" class="reveal mt-20">
          <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('events.pastDetail.infoLabel') }}</span>
          <p class="mt-2.5 text-sm text-ink-soft font-light leading-relaxed">{{ content.closing_note }}</p>
        </LuxeCard>
      </div>
    </section>

    <!-- ── Lightbox overlay ── -->
    <Transition name="lb-fade">
      <div v-if="lightboxOpen && gallery[activeImg]" class="lb" role="dialog" aria-modal="true" @click.self="closeLightbox">
        <button type="button" class="lb-close" @click="closeLightbox" :aria-label="t('events.pastDetail.closeImage')">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
        </button>

        <button type="button" class="lb-arrow lb-arrow--prev" @click="prev" :aria-label="t('events.pastDetail.prevImage')">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path :d="chevronToStart" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>

        <figure class="lb-stage relative"><img :src="gallery[activeImg].url" :alt="gallery[activeImg].caption" class="absolute inset-0 h-full w-full object-contain">
          <span class="lb-plate-no">{{ pad(activeImg + 1) }}</span>
          <figcaption class="lb-caption">{{ gallery[activeImg].caption }}</figcaption>
        </figure>

        <button type="button" class="lb-arrow lb-arrow--next" @click="next" :aria-label="t('events.pastDetail.nextImage')">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path :d="chevronToEnd" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>

        <span class="lb-counter">{{ pad(activeImg + 1) }} / {{ pad(count) }}</span>
      </div>
    </Transition>
  </div>

  <div v-else class="py-32 text-center">
    <button class="text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1" @click="router.push('/events')">
      {{ t('events.pastDetail.back') }}
    </button>
  </div>
</template>

<style scoped>
/* ───────────────────────── Q&A accordion ───────────────────────── */
.faq-enter-active, .faq-leave-active {
  transition: opacity 260ms ease, max-height 320ms ease;
  overflow: hidden;
  max-height: 260px;
}
.faq-enter-from, .faq-leave-to { opacity: 0; max-height: 0; }
@media (prefers-reduced-motion: reduce) {
  .faq-enter-active, .faq-leave-active { transition: opacity 200ms ease; }
}

/* ───────────────────────── Inline gallery ───────────────────────── */
.gal-stage {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgb(var(--c-parchment-deep) / 0.7);
  box-shadow: 0 24px 60px -30px rgba(0, 0, 0, 0.55);
  background: rgb(var(--c-ink));
}
.gal-track {
  display: flex;
  /* LTR so prev/next stay consistent across locales. */
  direction: ltr;
  will-change: transform;
  transition: transform 620ms cubic-bezier(0.22, 1, 0.36, 1);
}
.gal-slide {
  position: relative;
  flex: 0 0 100%;
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: zoom-in;
}
.gal-plate-no {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: clamp(3rem, 9vw, 5.5rem);
  line-height: 1;
  color: rgba(250, 247, 242, 0.22);
}
.gal-caption {
  margin-top: 0.75rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.28em;
  font-weight: 300;
  color: rgba(250, 247, 242, 0.8);
}

/* Flanking arrows */
.gal-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px;
  color: #f6f3ec;
  background: rgba(10, 8, 6, 0.42);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(246, 243, 236, 0.25);
  transition: background 220ms ease, transform 220ms ease, border-color 220ms ease;
}
.gal-arrow:hover { background: rgba(10, 8, 6, 0.7); border-color: rgba(246, 243, 236, 0.5); }
.gal-arrow--prev { inset-inline-start: 0.85rem; }
.gal-arrow--next { inset-inline-end: 0.85rem; }

.gal-counter {
  position: absolute;
  bottom: 0.9rem;
  inset-inline-start: 1rem;
  font-size: 11px;
  letter-spacing: 0.18em;
  font-weight: 300;
  color: rgba(246, 243, 236, 0.85);
  background: rgba(10, 8, 6, 0.42);
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  font-variant-numeric: tabular-nums;
}
.gal-full {
  position: absolute;
  bottom: 0.9rem;
  inset-inline-end: 1rem;
  display: grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 8px;
  color: #f6f3ec;
  background: rgba(10, 8, 6, 0.42);
  border: 1px solid rgba(246, 243, 236, 0.25);
  transition: background 220ms ease, border-color 220ms ease;
}
.gal-full:hover { background: rgba(10, 8, 6, 0.7); border-color: rgba(246, 243, 236, 0.5); }

/* Thumbnails */
.gal-thumbs {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.85rem;
  flex-wrap: wrap;
}
.gal-thumb { position: relative; overflow: hidden;
  position: relative;
  width: 4.5rem;
  height: 3rem;
  border-radius: 7px;
  overflow: hidden;
  border: 1px solid transparent;
  opacity: 0.55;
  transition: opacity 220ms ease, border-color 220ms ease, transform 220ms ease;
}
.gal-thumb span {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 300;
  color: rgba(250, 247, 242, 0.65);
  font-variant-numeric: tabular-nums;
}
.gal-thumb:hover { opacity: 0.85; }
.gal-thumb.is-active {
  opacity: 1;
  border-color: rgb(var(--c-gold));
  transform: translateY(-2px);
}

/* ───────────────────────── Lightbox ───────────────────────── */
.lb {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.5rem, 3vw, 2rem);
  padding: clamp(1rem, 5vw, 3.5rem);
  background: rgba(8, 6, 5, 0.92);
  backdrop-filter: blur(6px);
}
.lb-stage {
  position: relative;
  width: min(100%, 1100px);
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 40px 120px -30px rgba(0, 0, 0, 0.8);
}
.lb-plate-no {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: clamp(4rem, 14vw, 9rem);
  line-height: 1;
  color: rgba(250, 247, 242, 0.25);
}
.lb-caption {
  margin-top: 1rem;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.32em;
  font-weight: 300;
  color: rgba(250, 247, 242, 0.85);
}
.lb-close {
  position: absolute;
  top: clamp(1rem, 3vw, 2rem);
  inset-inline-end: clamp(1rem, 3vw, 2rem);
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px;
  color: #f6f3ec;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(246, 243, 236, 0.25);
  transition: background 220ms ease, border-color 220ms ease;
}
.lb-close:hover { background: rgba(255, 255, 255, 0.16); border-color: rgba(246, 243, 236, 0.5); }
.lb-arrow {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 9999px;
  color: #f6f3ec;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(246, 243, 236, 0.22);
  transition: background 220ms ease, border-color 220ms ease, transform 220ms ease;
}
.lb-arrow:hover { background: rgba(255, 255, 255, 0.16); border-color: rgba(246, 243, 236, 0.5); transform: scale(1.05); }
.lb-counter {
  position: absolute;
  bottom: clamp(1rem, 3vw, 2rem);
  inset-inline-start: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  letter-spacing: 0.2em;
  font-weight: 300;
  color: rgba(246, 243, 236, 0.8);
  font-variant-numeric: tabular-nums;
}

/* Lightbox open/close fade */
.lb-fade-enter-active, .lb-fade-leave-active { transition: opacity 260ms ease; }
.lb-fade-enter-from, .lb-fade-leave-to { opacity: 0; }
.lb-fade-enter-active .lb-stage { transition: transform 320ms cubic-bezier(0.16, 1, 0.3, 1); }
.lb-fade-enter-from .lb-stage { transform: scale(0.96); }

@media (prefers-reduced-motion: reduce) {
  .gal-track { transition: none; }
  .lb-fade-enter-active .lb-stage { transition: none; }
}
</style>

