<script setup>
/**
 * PartnerProfileView — a dedicated Doctor / Partner profile page.
 *
 * Structurally inspired by LinkedIn (cover band → overlapping avatar → identity
 * header → stacked About / Experience / Education / Publications sections) but
 * dressed strictly in the house's flat 2D luxury system: parchment surfaces,
 * gold hairlines, ink typography — no drop shadows, no 3D lift. Everything is
 * built on the brand CSS tokens (--c-parchment-light / --c-ink / --c-gold …) so
 * it inverts cleanly in dark mode without any global overrides. The only
 * fixed-tone region is the "cover" band + avatar, which — like the hero stages —
 * are intentionally always-dark.
 *
 * Native RTL: layout uses logical Tailwind utilities (ms-/me-, text-start) and
 * the shared .dir-arrow glyph; no scaleX(-1) mirroring.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()
const route = useRoute()

const people = computed(() => tm('partners.people'))
const index = computed(() => Number(route.params.id))
const person = computed(() => people.value[index.value])

const initials = (name = '') => name
  .replace(/^(Dr\.|د\.|دکتر|Prof\.?|Eng\.|مهندس)\s*/i, '')
  .trim()
  .split(/\s+/)
  .map((w) => w[0])
  .slice(0, 2)
  .join('')
  .toUpperCase()

// ── Graceful fallbacks ───────────────────────────────────────────────────────
// Locales that carry the extended profile data (en / fa) render full sections;
// the remaining locales fall back to whatever the base directory provides, so
// every field degrades to something meaningful rather than rendering empty.
const title = computed(() => person.value?.title || person.value?.collaborations?.[0] || '')
const affiliation = computed(() => person.value?.affiliation || '')
const experience = computed(() => {
  const p = person.value
  if (!p) return []
  if (Array.isArray(p.experience) && p.experience.length) return p.experience
  return (p.collaborations || []).map((c) => ({ role: c, org: p.affiliation || '' }))
})
const education = computed(() => {
  const p = person.value
  if (!p) return []
  if (Array.isArray(p.education) && p.education.length) return p.education
  return p.qualification ? [{ degree: p.qualification }] : []
})
const publications = computed(() => (Array.isArray(person.value?.publications) ? person.value.publications : []))

// ── Educational-partner extensions (present only on content-provider profiles)
const expertise = computed(() => (Array.isArray(person.value?.expertise) ? person.value.expertise : []))
const methodology = computed(() => person.value?.methodology || '')
const impact = computed(() => person.value?.impact || '')
const coursesTaught = computed(() => (Array.isArray(person.value?.courses) ? person.value.courses : []))
const playlists = computed(() => (Array.isArray(person.value?.playlists) ? person.value.playlists : []))
const platform = computed(() => person.value?.platform || '')
const status = computed(() => person.value?.status || '')

// Aside: a generic placeholder schedule of upcoming clinical sessions.
const upcoming = computed(() => {
  const u = tm('partners.profile.upcoming')
  return Array.isArray(u) ? u : []
})

useReveal()
</script>

<template>
  <div class="profile-page bg-parchment-light min-h-screen pb-24">
    <div class="max-w-5xl mx-auto px-6 md:px-8">
      <!-- Back link -->
      <div class="pt-7">
        <router-link
          to="/partners"
          class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-gold-dark hover:text-gold font-light transition-colors"
        >
          <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('partners.profile.back') }}
        </router-link>
      </div>

      <template v-if="person">
        <!-- ── Hero / identity header ───────────────────────────────────────
             A LinkedIn-style cover band with an overlapping gold-ringed avatar,
             then the name / title / affiliation and a contact CTA. Flat — the
             cover is a single calm gradient, no shadow, no lift. -->
        <header class="profile-hero reveal mt-5 rounded-2xl border border-parchment-deep bg-parchment overflow-hidden">
          <div class="profile-cover" aria-hidden="true">
            <span class="profile-cover-aura"></span>
            <span class="profile-cover-grid"></span>
          </div>

          <div class="relative px-6 md:px-10 pb-8">
            <!-- Only the avatar overlaps the dark cover; ALL identity text sits
                 below it on the parchment card body, so contrast is correct in
                 both themes (this fixes the prior dark-on-dark light-mode bug). -->
            <div class="-mt-12 sm:-mt-14 flex justify-center sm:justify-start">
              <div class="profile-avatar grid place-items-center shrink-0">
                <span class="profile-initials font-serif font-light leading-none">{{ initials(person.name) }}</span>
              </div>
            </div>

            <div class="mt-5 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-5">
              <div class="min-w-0 text-center sm:text-start">
                <h1 class="font-serif font-light text-3xl md:text-4xl text-ink leading-tight">{{ person.name }}</h1>
                <p v-if="title" class="profile-title mt-1.5 text-sm md:text-base font-light tracking-wide">{{ title }}</p>
                <p v-if="affiliation" class="mt-1.5 inline-flex items-center gap-1.5 text-[13px] text-ink-muted font-light">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" class="shrink-0 text-gold-dark"><path d="M3 21h18M5 21V7l8-4 8 4v14M9 9h.01M9 13h.01M9 17h.01M15 9h.01M15 13h.01M15 17h.01" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  {{ t('partners.profile.affiliationLabel') }} · {{ affiliation }}
                </p>
              </div>
              <div class="shrink-0 flex justify-center sm:justify-end">
                <router-link to="/contact" class="btn-ghost-gold">
                  {{ t('partners.profile.contactCta') }} <span class="dir-arrow" aria-hidden="true"></span>
                </router-link>
              </div>
            </div>

            <!-- Credential strip -->
            <div class="mt-6 flex flex-wrap justify-center sm:justify-start gap-2.5">
              <span v-if="status" class="profile-chip profile-chip--status">
                <span class="profile-status-dot" aria-hidden="true"></span>{{ status }}
              </span>
              <span v-if="platform" class="profile-chip">
                {{ t('partners.profile.platformLabel') }} · {{ platform }}
              </span>
              <span v-if="person.councilNumber && person.councilNumber !== '—'" class="profile-chip">
                {{ t('partners.profile.councilLabel') }} · <span class="tabular-nums tracking-wide">{{ person.councilNumber }}</span>
              </span>
              <span v-for="(c, j) in person.collaborations" :key="j" class="profile-chip">{{ c }}</span>
            </div>
          </div>
        </header>

        <!-- ── Body: stacked sections + aside ─────────────────────────────── -->
        <div class="mt-8 grid lg:grid-cols-12 gap-8">
          <div class="lg:col-span-8 space-y-6">
            <!-- About — inverted to a light parchment panel in dark mode for a
                 striking editorial contrast against the charcoal surroundings. -->
            <section v-if="person.bio" class="profile-section profile-invert reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.aboutTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <p class="text-[15px] text-ink-soft font-light leading-relaxed">{{ person.bio }}</p>
            </section>

            <!-- Areas of Expertise (educational partners) -->
            <section v-if="expertise.length" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.expertiseTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <div class="flex flex-wrap gap-2">
                <span v-for="(x, j) in expertise" :key="j" class="profile-tag">{{ x }}</span>
              </div>
            </section>

            <!-- Teaching Methodology -->
            <section v-if="methodology" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.methodologyTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <p class="text-[15px] text-ink-soft font-light leading-relaxed">{{ methodology }}</p>
            </section>

            <!-- Educational Impact -->
            <section v-if="impact" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.impactTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <p class="text-[15px] text-ink-soft font-light leading-relaxed">{{ impact }}</p>
            </section>

            <!-- Courses Taught — linked to the Academy course pages -->
            <section v-if="coursesTaught.length" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.coursesTaughtTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <ul class="space-y-3">
                <li v-for="(c, j) in coursesTaught" :key="j">
                  <router-link :to="`/academy/course/${c.index}`" class="profile-course group">
                    <span class="shrink-0 w-8 h-8 rounded border border-gold/40 flex items-center justify-center text-gold-dark">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                    </span>
                    <span class="min-w-0 flex-1 text-[15px] text-ink font-light leading-snug group-hover:text-gold-dark transition-colors">{{ c.title }}</span>
                    <span class="dir-arrow shrink-0 text-gold-dark" aria-hidden="true"></span>
                  </router-link>
                </li>
              </ul>
            </section>

            <!-- Experience & Roles -->
            <section v-if="experience.length" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.experienceTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <ol class="profile-timeline">
                <li v-for="(e, j) in experience" :key="j" class="profile-entry">
                  <span class="profile-dot" aria-hidden="true"></span>
                  <div class="min-w-0">
                    <p class="text-[15px] text-ink font-normal leading-snug">{{ e.role }}</p>
                    <p v-if="e.org" class="text-[13px] text-gold-dark font-light mt-0.5">{{ e.org }}</p>
                    <p v-if="e.period" class="text-[11px] uppercase tracking-[0.18em] text-ink-muted font-light mt-1 tabular-nums">{{ e.period }}</p>
                  </div>
                </li>
              </ol>
            </section>

            <!-- Education -->
            <section v-if="education.length" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.educationTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <ol class="profile-timeline">
                <li v-for="(e, j) in education" :key="j" class="profile-entry">
                  <span class="profile-dot profile-dot--ring" aria-hidden="true"></span>
                  <div class="min-w-0">
                    <p class="text-[15px] text-ink font-normal leading-snug">{{ e.degree }}</p>
                    <p v-if="e.school" class="text-[13px] text-gold-dark font-light mt-0.5">{{ e.school }}</p>
                    <p v-if="e.period" class="text-[11px] uppercase tracking-[0.18em] text-ink-muted font-light mt-1 tabular-nums">{{ e.period }}</p>
                  </div>
                </li>
              </ol>
            </section>

            <!-- Publications & Projects -->
            <section v-if="publications.length" class="profile-section reveal">
              <h2 class="profile-section-title">{{ t('partners.profile.publicationsTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <ul class="space-y-4">
                <li v-for="(pub, j) in publications" :key="j" class="flex gap-3.5">
                  <span class="shrink-0 mt-0.5 w-8 h-8 rounded border border-gold/40 flex items-center justify-center text-gold-dark">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </span>
                  <div class="min-w-0">
                    <p class="text-[15px] text-ink font-light leading-snug">{{ pub.title }}</p>
                    <p v-if="pub.venue" class="text-[12px] text-ink-muted font-light mt-0.5">{{ pub.venue }}</p>
                  </div>
                </li>
              </ul>
            </section>
          </div>

          <!-- Aside -->
          <aside class="lg:col-span-4 space-y-6">
            <!-- Areas of collaboration — inverted light panel in dark mode. -->
            <section v-if="person.collaborations && person.collaborations.length" class="profile-section profile-invert reveal">
              <h2 class="profile-section-title text-base">{{ t('partners.labels.collaborations') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <div class="flex flex-wrap gap-2">
                <span v-for="(c, j) in person.collaborations" :key="j" class="profile-tag">{{ c }}</span>
              </div>
            </section>

            <!-- Associated Playlists (educational partners) — counts only, never
                 a source URL; lessons are internal learning resources. -->
            <section v-if="playlists.length" class="profile-section profile-invert reveal">
              <h2 class="profile-section-title text-base">{{ t('partners.profile.playlistsTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <ul class="space-y-3.5">
                <li v-for="(pl, j) in playlists" :key="j" class="flex gap-3">
                  <span class="shrink-0 mt-0.5 w-8 h-8 rounded border border-gold/40 flex items-center justify-center text-gold-dark">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M3 6h13M3 12h13M3 18h9M17 12l4 3-4 3z" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </span>
                  <div class="min-w-0">
                    <p class="text-[14px] text-ink font-light leading-snug">{{ pl.title }}</p>
                    <p class="text-[11px] text-ink-muted font-light mt-0.5 tabular-nums">{{ pl.lessons }} {{ t('partners.profile.lessonsLabel') }}</p>
                  </div>
                </li>
              </ul>
            </section>

            <!-- Contact card -->
            <section class="profile-contact reveal">
              <h2 class="font-serif font-light text-xl leading-snug">{{ t('partners.profile.contactTitle', { name: person.name }) }}</h2>
              <p class="mt-2.5 text-[13px] font-light leading-relaxed">{{ t('partners.profile.contactDesc') }}</p>
              <router-link to="/contact" class="btn-ghost-gold mt-5 inline-flex">
                {{ t('partners.profile.contactCta') }} <span class="dir-arrow" aria-hidden="true"></span>
              </router-link>
            </section>

            <!-- Upcoming Clinical Sessions -->
            <section v-if="upcoming.length" class="profile-section profile-invert reveal">
              <h2 class="profile-section-title text-base">{{ t('partners.profile.upcomingTitle') }}</h2>
              <span class="profile-rule" aria-hidden="true"></span>
              <ul class="space-y-3.5">
                <li v-for="(s, j) in upcoming" :key="j" class="flex gap-3">
                  <span class="shrink-0 mt-0.5 w-8 h-8 rounded border border-gold/40 flex items-center justify-center text-gold-dark">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18" stroke-linecap="round"/></svg>
                  </span>
                  <div class="min-w-0">
                    <p class="text-[11px] text-gold-dark font-light tabular-nums tracking-wide">{{ s.date }}</p>
                    <p class="text-[13px] text-ink font-light leading-snug">{{ s.title }}</p>
                    <p v-if="s.venue" class="text-[11px] text-ink-muted font-light mt-0.5">{{ s.venue }}</p>
                  </div>
                </li>
              </ul>
              <p class="mt-4 text-[11px] text-ink-hint font-light italic leading-relaxed">{{ t('partners.profile.upcomingNote') }}</p>
            </section>
          </aside>
        </div>
      </template>

      <!-- Unknown / out-of-range id -->
      <div v-else class="py-32 text-center">
        <p class="font-serif font-light text-2xl text-ink">{{ t('partners.profile.notFound') }}</p>
        <router-link
          to="/partners"
          class="mt-6 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1 hover:text-gold transition-colors"
        >
          {{ t('partners.profile.back') }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Cover band — always-dark, flat. A single calm charcoal gradient warmed by a
   gold aura in the upper-start corner + whisper-fine hairlines. No shadow. ── */
.profile-cover {
  position: relative;
  height: 6.5rem;
  background: linear-gradient(150deg, #2b2620 0%, #1a1714 58%, #100e0b 100%);
}
.profile-cover-aura {
  position: absolute;
  inset: 0;
  background: radial-gradient(60% 120% at 16% 0%, rgba(237, 192, 113, 0.18), transparent 60%);
}
.profile-cover-grid {
  position: absolute;
  inset: 0;
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent 63px, rgba(244, 215, 145, 0.04) 63px, rgba(244, 215, 145, 0.04) 64px);
  -webkit-mask-image: linear-gradient(180deg, #000, transparent 90%);
          mask-image: linear-gradient(180deg, #000, transparent 90%);
}

/* Overlapping avatar — fixed deep-charcoal disc with a gold ring + gold initials,
   theme-stable so it reads on the always-dark cover in both light and dark mode. */
.profile-avatar {
  width: 6rem;
  height: 6rem;
  border-radius: 9999px;
  background: #211d18;
  border: 2px solid rgb(var(--c-gold) / 0.7);
  /* a slim parchment keyline lifts the disc off the cover without any shadow */
  outline: 4px solid rgb(var(--c-parchment));
  outline-offset: 0;
}
@media (min-width: 640px) {
  .profile-avatar { width: 7rem; height: 7rem; }
}
.profile-initials {
  color: #edc071;
  font-size: 2rem;
  letter-spacing: 0.04em;
}

/* Credential chips on the header */
.profile-chip {
  font-size: 11px;
  font-weight: 300;
  color: rgb(var(--c-ink-soft));
  border: 1px solid rgb(var(--c-gold) / 0.35);
  background: rgb(var(--c-gold) / 0.06);
  border-radius: 9999px;
  padding-block: 0.25rem;
  padding-inline: 0.75rem;
}

/* Active-partner status chip — a small gold "live" dot on the standard chip. */
.profile-chip--status {
  color: rgb(var(--c-gold-dark));
  border-color: rgb(var(--c-gold) / 0.5);
}
.profile-status-dot {
  display: inline-block;
  width: 6px; height: 6px;
  margin-inline-end: 0.45rem;
  border-radius: 9999px;
  background: rgb(var(--c-gold));
  box-shadow: 0 0 0 3px rgb(var(--c-gold) / 0.18);
  vertical-align: middle;
}

/* Courses-taught rows — a flat gold-hairline link that warms on hover. */
.profile-course {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid rgb(var(--c-parchment-deep));
  border-radius: 0.6rem;
  transition: border-color 240ms ease, background-color 240ms ease;
}
.profile-course:hover {
  border-color: rgb(var(--c-gold) / 0.55);
  background: rgb(var(--c-gold) / 0.05);
}

/* ── Flat section cards ─────────────────────────────────────────────────── */
.profile-section {
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  border-radius: 0.75rem;
  padding: 1.5rem 1.6rem 1.75rem;
}
.profile-section-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: 1.4rem;
  color: rgb(var(--c-ink));
  line-height: 1.2;
}
html[lang='fa'] .profile-section-title { font-family: inherit; font-weight: 700; }
.profile-rule {
  display: block;
  width: 32px;
  height: 1px;
  margin-block: 0.75rem 1.25rem;
  background: rgb(var(--c-gold) / 0.6);
}
.profile-title { color: rgb(var(--c-gold-dark)); }

/* ── Experience / education timeline — a gold hairline rail with flat dots ── */
.profile-timeline {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.profile-entry {
  position: relative;
  display: flex;
  gap: 1rem;
  padding-inline-start: 1.25rem;
}
/* Continuous rail behind the dots, on the inline-start edge (RTL-safe). */
.profile-timeline::before {
  content: '';
  position: absolute;
  inset-block: 0.4rem 0.4rem;
  inset-inline-start: 4px;
  width: 1px;
  background: rgb(var(--c-gold) / 0.25);
}
.profile-dot {
  position: absolute;
  inset-inline-start: 0;
  top: 0.35rem;
  width: 9px;
  height: 9px;
  border-radius: 9999px;
  background: rgb(var(--c-gold));
}
.profile-dot--ring {
  background: rgb(var(--c-parchment));
  border: 2px solid rgb(var(--c-gold) / 0.7);
}

/* Collaboration tags in the aside */
.profile-tag {
  font-size: 11px;
  font-weight: 300;
  letter-spacing: 0.02em;
  color: rgb(var(--c-gold-dark));
  border: 1px solid rgb(var(--c-gold) / 0.45);
  background: rgb(var(--c-gold) / 0.06);
  border-radius: 9999px;
  padding-block: 0.2rem;
  padding-inline: 0.7rem;
}

/* Contact card — deep charcoal editorial slab, flat (mirrors the Partners CTA). */
.profile-contact {
  border-radius: 0.75rem;
  padding: 1.5rem 1.6rem 1.75rem;
  background: linear-gradient(155deg, #2b2620 0%, #1a1714 60%, #100e0b 100%);
  border: 1px solid rgba(237, 192, 113, 0.18);
}
.profile-contact h2 { color: #f7f2e9; }
.profile-contact p { color: rgba(217, 210, 197, 0.75); }

@media (prefers-reduced-motion: reduce) {
  .profile-hero, .profile-section, .profile-contact { transition: none; }
}
</style>
