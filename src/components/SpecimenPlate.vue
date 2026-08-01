<script setup>
/**
 * SpecimenPlate — one course rendered as an editorial "atlas plate".
 *
 * A full-width, asymmetric two-column composition: a framed specimen panel
 * (stamped with the field prefix) paired with an editorial type block that uses
 * the three voices — serif display (title), sans (lede), and a mono/data voice
 * (catalog code, metadata strip). Generous whitespace; one floating plane.
 *
 * Courses are standalone, so the plate is addressed by a stable catalog code
 * (e.g. NRO-101) — never a sequential plate number. `flip` alternates the
 * composition (panel to the right column) for editorial rhythm.
 *
 * Scope note: the composition is authored LTR-first with physical CSS
 * properties. The one reading-direction-sensitive detail — the "view" arrow —
 * is made native-RTL-correct via flex order + a per-direction SVG path swap
 * (no scaleX mirroring); see `.plate__view-arrow-*` in the style block.
 */
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  /** DOM id the IndexSpine observes / jumps to (e.g. "plate-3"). */
  sectionId: { type: String, required: true },
  /** Stable catalog code for the course (e.g. "NRO-101"). */
  code: { type: String, required: true },
  /** Raw course object: { title, instructor, level, duration, tier, field, desc }. */
  course: { type: Object, required: true },
  /** Router target for the course. */
  to: { type: String, required: true },
  /** Course cover image (object-fit: cover with a subtle dark overlay). */
  cover: { type: String, default: '' },
  /** Pre-translated field label (e.g. "Neurology"). */
  fieldLabel: { type: String, default: '' },
  /** Pre-translated tier label (e.g. "Premium"). */
  tierLabel: { type: String, default: '' },
  /** Mirror the composition (panel to the right column). */
  flip: { type: Boolean, default: false },
})

/* Deterministic specimen tint per plate — stands in for course artwork.
   Keyed off the catalog code so it's stable without a sequential number. */
const palettes = [
  'from-gold/30 via-gold/5 to-transparent',
  'from-ink/65 via-ink/25 to-transparent',
  'from-gold-dark/25 via-gold/10 to-transparent',
  'from-ink-soft/45 via-ink/15 to-transparent',
  'from-gold/20 via-ink/15 to-transparent',
  'from-ink/55 via-gold/15 to-transparent',
]
const gradient = computed(() => {
  let h = 0
  for (const ch of props.code) h += ch.charCodeAt(0)
  return palettes[h % palettes.length]
})

/* The field prefix ("NRO" / "PSY" / "GEN") stamps the specimen panel. */
const stamp = computed(() => (props.code.split('-')[0] || '').toUpperCase())

const initial = computed(() =>
  (props.course.instructor || '')
    .replace(/^\s*(Dr\.|Eng\.|Prof\.)\s*/i, '')
    .trim()
    .charAt(0)
    .toUpperCase()
)
const isPremium = computed(() => props.course.tier === 'premium')

/* Metadata strip: "6 lessons · 3h 20m" → ["6 lessons", "3h 20m"], plus level. */
const metrics = computed(() => {
  const parts = (props.course.duration || '').split('·').map((s) => s.trim()).filter(Boolean)
  if (props.course.level) parts.push(props.course.level)
  return parts
})

/* ── Per-instance reveal (robust across filter re-renders) ─────────────── */
const root = ref(null)
const shown = ref(false)
let io = null
onMounted(() => {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    shown.value = true
    return
  }
  io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (e.isIntersecting) { shown.value = true; io.disconnect() }
      }
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  )
  io.observe(root.value)
})
onBeforeUnmount(() => io?.disconnect())
</script>

<template>
  <article
    :id="sectionId"
    ref="root"
    data-atlas-section
    class="plate"
    :class="{ 'plate--flip': flip, 'is-shown': shown }"
  >
    <router-link :to="to" class="plate__inner group">
      <!-- Specimen panel (the single floating plane) -->
      <figure class="plate__panel lux-card">
        <template v-if="cover">
          <img :src="cover" alt="" class="plate__cover" loading="lazy" />
          <span class="plate__cover-overlay" aria-hidden="true"></span>
        </template>
        <span v-else class="plate__panel-fill" :class="['bg-gradient-to-br', gradient]"></span>
        <span v-if="!cover" class="plate__stamp font-serif" aria-hidden="true">{{ stamp }}</span>
        <span class="plate__tag" :class="{ 'is-premium': isPremium }">
          <svg v-if="isPremium" viewBox="0 0 24 24" class="plate__tag-icon" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="1.5" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /></svg>
          {{ tierLabel }}
        </span>
      </figure>

      <!-- Editorial type block -->
      <div class="plate__body">
        <p class="plate__eyebrow tabular-nums">
          <span>{{ 'REF ' + code }}</span>
          <span class="plate__eyebrow-sep" aria-hidden="true">—</span>
          <span>{{ fieldLabel }}</span>
        </p>

        <h3 class="plate__title font-serif">{{ course.title }}</h3>

        <p class="plate__author">
          <span class="plate__author-mark">{{ initial }}</span>
          <span>{{ course.instructor }}</span>
        </p>

        <p class="plate__lede">{{ course.desc }}</p>

        <div class="plate__meta tabular-nums">
          <span v-for="(m, i) in metrics" :key="i" class="plate__metric">{{ m }}</span>
        </div>

        <span class="plate__view">
          <span class="plate__view-rule" aria-hidden="true"></span>
          <!-- Two arrowhead paths share one line; CSS draws whichever points
               along the reading direction (→ in LTR, ← in RTL). No scaleX. -->
          <svg class="plate__view-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path class="plate__view-arrow-ltr" d="M5 12h14M13 6l6 6-6 6" />
            <path class="plate__view-arrow-rtl" d="M5 12h14M11 6l-6 6 6 6" />
          </svg>
        </span>
      </div>
    </router-link>
  </article>
</template>

<style scoped>
/* var(--c-*) are the same triplets Tailwind reads (parchment / ink / gold),
   so the plate stays in lock-step with the theme + scoped #323A45 charcoal.
   LTR-only: physical properties throughout. */

/* ── Reveal ────────────────────────────────────────────────────────────── */
.plate {
  position: relative;
  opacity: 0;
  transform: translateY(22px);
  transition: opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1),
              transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.plate.is-shown { opacity: 1; transform: none; }

/* Hairline between consecutive plates — the editorial "rule". */
.plate + .plate { border-top: 1px solid rgb(var(--c-parchment-deep)); }

/* ── Composition ───────────────────────────────────────────────────────── */
.plate__inner {
  display: grid;
  grid-template-columns: 1fr;            /* mobile: stacked */
  gap: clamp(1.5rem, 4vw, 3rem);
  align-items: center;
  padding-top: clamp(2.5rem, 7vh, 5rem);
  padding-bottom: clamp(2.5rem, 7vh, 5rem);
  text-decoration: none;
  color: inherit;
}
@media (min-width: 768px) {
  .plate__inner {
    grid-template-columns: 1.05fr 1fr;
    gap: clamp(2rem, 5vw, 4.5rem);
  }
  /* Flip: panel travels to the right column. */
  .plate--flip .plate__panel { order: 2; }
}

/* ── Specimen panel ────────────────────────────────────────────────────── */
.plate__panel {
  position: relative;
  margin: 0;
  aspect-ratio: 5 / 4;
  overflow: hidden;
  border-radius: 12px;
  background: rgb(var(--c-ink));
  transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}
.group:hover .plate__panel { transform: translateY(-4px); }

.plate__panel-fill {
  position: absolute;
  inset: 0;
  transition: transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.group:hover .plate__panel-fill { transform: scale(1.05); }

/* Course cover — fills the panel without cropping the focal subject, under a
   subtle dark wash that keeps the gold tag and theme legible. */
.plate__cover {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.group:hover .plate__cover { transform: scale(1.05); }
.plate__cover-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(160deg, rgb(20 17 13 / 0.18) 0%, rgb(20 17 13 / 0.32) 60%, rgb(20 17 13 / 0.52) 100%);
}

/* Field stamp — a large, faint specimen mark. */
.plate__stamp {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-size: clamp(3.5rem, 9vw, 6rem);
  font-weight: 300;
  line-height: 1;
  letter-spacing: 0.12em;
  color: rgb(var(--c-parchment-light) / 0.15);
}

.plate__tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid rgb(var(--c-parchment-light) / 0.4);
  background: rgb(var(--c-ink) / 0.4);
  -webkit-backdrop-filter: blur(4px);
          backdrop-filter: blur(4px);
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: rgb(var(--c-parchment-light) / 0.92);
}
.plate__tag.is-premium {
  color: rgb(var(--c-gold));
  border-color: rgb(var(--c-gold) / 0.5);
}
.plate__tag-icon { width: 0.75rem; height: 0.75rem; }

/* ── Editorial body ────────────────────────────────────────────────────── */
.plate__body { min-width: 0; }

.plate__eyebrow {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0 0 1rem;
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.28em;
  color: rgb(var(--c-gold-dark));
}
.plate__eyebrow-sep { color: rgb(var(--c-parchment-deep)); }

.plate__title {
  margin: 0;
  font-size: clamp(1.6rem, 3vw, 2.35rem);
  font-weight: 300;
  line-height: 1.12;
  color: rgb(var(--c-ink));
  transition: color 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.group:hover .plate__title { color: rgb(var(--c-gold-dark)); }

.plate__author {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 1rem;
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: rgb(var(--c-ink-muted));
}
.plate__author-mark {
  display: grid;
  place-items: center;
  width: 1.6rem;
  height: 1.6rem;
  border: 1px solid rgb(var(--c-gold) / 0.4);
  border-radius: 9999px;
  font-size: 0.625rem;
  color: rgb(var(--c-gold-dark));
}

.plate__lede {
  margin-top: 1.25rem;
  max-width: 46ch;                /* disciplined editorial measure */
  font-size: 0.95rem;
  line-height: 1.7;
  font-weight: 300;
  color: rgb(var(--c-ink-soft));
}

.plate__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.3rem;
  margin-top: 1.5rem;
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: rgb(var(--c-ink-muted));
}
.plate__metric { position: relative; }
/* Hairline divider before each metric except the first. */
.plate__metric + .plate__metric::before {
  content: '';
  position: absolute;
  left: -0.68rem;
  top: 0.1em;
  bottom: 0.1em;
  width: 1px;
  background: rgb(var(--c-parchment-deep));
}

.plate__view {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.75rem;
  color: rgb(var(--c-gold-dark));
}
.plate__view-rule {
  width: 2rem;
  height: 1px;
  background: rgb(var(--c-gold) / 0.5);
  transition: width 0.4s cubic-bezier(0.22, 1, 0.36, 1),
              background-color 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.group:hover .plate__view-rule {
  width: 3.25rem;
  background: rgb(var(--c-gold));
}
.plate__view-arrow {
  width: 1rem;
  height: 1rem;
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.group:hover .plate__view-arrow { transform: translateX(3px); }

/* ── Direction-aware arrow — native RTL, no scaleX mirroring ─────────────────
   `.plate__view` is an inline-flex row, so its order already reverses under
   dir="rtl": the lead rule lands on the reading-start (right) edge and the
   arrow on the reading-end (left) edge. We only swap which arrowhead path is
   stroked so the head points along the reading direction — → in LTR, ← in RTL —
   and flip the hover nudge to the inline axis. */
.plate__view-arrow-rtl { display: none; }
html[dir='rtl'] .plate__view-arrow-ltr { display: none; }
html[dir='rtl'] .plate__view-arrow-rtl { display: inline; }
html[dir='rtl'] .group:hover .plate__view-arrow { transform: translateX(-3px); }

/* ── Reduced motion ────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .plate { opacity: 1; transform: none; transition: none; }
  .plate__panel,
  .plate__panel-fill,
  .plate__title,
  .plate__view-rule,
  .plate__view-arrow { transition: none; }
}
</style>
