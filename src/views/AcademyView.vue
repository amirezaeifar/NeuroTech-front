<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SpecimenPlate from '../components/SpecimenPlate.vue'
import logo from '../assets/logo.png'
import NeuralProgressTree from '../components/NeuralProgressTree.vue'
import { courseCode } from '../utils/catalog.js'
import { courseMediaAt } from '../data/courseMedia.js'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()

const statusFilters = [
  { key: 'all', label: 'academy.filters.all' },
  { key: 'free', label: 'academy.filters.free' },
  { key: 'premium', label: 'academy.filters.premium' },
]
const fieldFilters = [
  { key: 'all', label: 'academy.fields.all' },
  { key: 'clinicalNeurology', label: 'academy.fields.clinicalNeurology' },
  { key: 'neuroimaging', label: 'academy.fields.neuroimaging' },
  { key: 'neurosurgery', label: 'academy.fields.neurosurgery' },
  { key: 'neuroscience', label: 'academy.fields.neuroscience' },
  { key: 'neurocriticalCare', label: 'academy.fields.neurocriticalCare' },
  { key: 'brainAnatomy', label: 'academy.fields.brainAnatomy' },
]

const activeStatus = ref('all')
const activeField = ref('all')

// Tier CTAs filter the library to the matching tier and scroll to it.
const scrollToCourses = (tier) => {
  activeStatus.value = tier
  const el = document.getElementById('library')
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const courses = computed(() => tm('academy.courses'))
const courseIndex = (course) => courses.value.indexOf(course)
const filtered = computed(() => courses.value.filter((c) =>
  (activeStatus.value === 'all' || c.tier === activeStatus.value) &&
  (activeField.value === 'all' || c.field === activeField.value)
))

useReveal()
</script>

<template>
  <div class="academy-page">
    <!-- ───────────────────────── Hero ───────────────────────── -->
    <section class="academy-hero relative overflow-hidden py-24 md:py-32">
      <!-- Depth layers: faint hairline grid, amber light-pool, brand watermark -->
      <div class="academy-hero-grid pointer-events-none absolute inset-0"></div>
      <div class="academy-hero-glow pointer-events-none absolute inset-0"></div>
      <img
        :src="logo"
        alt=""
        aria-hidden="true"
        class="academy-hero-logo pointer-events-none absolute -top-16 w-[420px] h-auto opacity-[0.05] hidden md:block"
        style="inset-inline-end: -3rem;"
      />

      <div class="relative max-w-5xl mx-auto px-8 text-center">
        <p class="academy-hero-eyebrow text-[11px] uppercase tracking-[0.35em] text-[#EDC071] font-light mb-6">
          {{ t('academy.hero.eyebrow') }}
        </p>
        <h1 class="academy-hero-title font-serif font-light text-[#F6F3EC] text-5xl md:text-6xl tracking-wide">
          {{ t('academy.hero.title') }}
        </h1>

        <!-- Diamond rule — a touch more crafted than a plain line -->
        <div class="academy-hero-rule mt-10 flex items-center justify-center gap-4">
          <span class="h-px w-16 bg-gradient-to-r from-transparent to-[#EDC071]/70"></span>
          <span class="academy-hero-diamond text-[#EDC071] text-[9px] tracking-widest">◆</span>
          <span class="h-px w-16 bg-gradient-to-l from-transparent to-[#EDC071]/70"></span>
        </div>
      </div>
    </section>

    <!-- ─────────────── Preamble: pull-quote + access tiers ─────────────── -->
    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8">
        <figure class="reveal relative max-w-2xl mx-auto text-center">
          <span aria-hidden="true" class="block font-serif text-gold/30 text-6xl leading-none mb-2 select-none">&ldquo;</span>
          <p class="font-serif italic font-light text-2xl text-ink-soft leading-relaxed">
            {{ t('academy.intro') }}
          </p>
        </figure>

        <!-- Tiers -->
        <div class="mt-16 grid md:grid-cols-2 gap-8">
          <!-- Free -->
          <LuxeCard class="reveal group relative overflow-hidden lux-card hover:-translate-y-0.5 hover:border-gold/50">
            <div class="flex items-center gap-3">
              <span class="grid place-items-center h-9 w-9 rounded-full border border-gold/40 text-gold-dark">
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6.5A2 2 0 0 1 5 5h5a2 2 0 0 1 2 2v12a1.5 1.5 0 0 0-1.5-1.5H5A2 2 0 0 1 3 15.5z"/><path d="M21 6.5A2 2 0 0 0 19 5h-5a2 2 0 0 0-2 2v12a1.5 1.5 0 0 1 1.5-1.5H19a2 2 0 0 0 2-1.5z"/></svg>
              </span>
              <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('academy.tiers.free.name') }}</span>
            </div>
            <p class="mt-5 text-sm text-ink-soft font-light leading-relaxed">{{ t('academy.tiers.free.desc') }}</p>
            <button
              type="button"
              class="mt-7 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1"
              @click="scrollToCourses('free')"
            >
              {{ t('academy.tiers.free.cta') }}
              <span aria-hidden="true" class="transition-transform duration-300 group-hover:translate-y-0.5">↓</span>
            </button>
          </LuxeCard>

          <!-- Premium -->
          <LuxeCard class="reveal group relative overflow-hidden lux-card hover:-translate-y-0.5 hover:border-gold/50" style="transition-delay: 80ms;">
            <div class="flex items-center justify-between gap-4">
              <div class="flex items-center gap-3">
                <span class="grid place-items-center h-9 w-9 rounded-full border border-gold/40 text-gold-dark">
                  <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 6.5v5c0 4.5 3.2 7.8 8 9 4.8-1.2 8-4.5 8-9v-5z"/><path d="m9 12 2 2 4-4.5"/></svg>
                </span>
                <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('academy.tiers.premium.name') }}</span>
              </div>
              <span class="text-[10px] uppercase tracking-[0.22em] text-gold border border-gold/50 px-2.5 py-1 font-light whitespace-nowrap">{{ t('academy.tiers.premium.badge') }}</span>
            </div>
            <p class="mt-5 text-sm text-ink-soft font-light leading-relaxed">{{ t('academy.tiers.premium.desc') }}</p>
            <button
              type="button"
              class="mt-7 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1"
              @click="scrollToCourses('premium')"
            >
              {{ t('academy.tiers.premium.cta') }}
              <span aria-hidden="true" class="transition-transform duration-300 group-hover:translate-y-0.5">↓</span>
            </button>
          </LuxeCard>
        </div>
      </div>
    </section>

    <!-- ───────────── Course library — Neural rail + plates ───────────── -->
    <section class="library-section bg-parchment border-t border-parchment-deep">
      <!-- The grid is the scroll-track: its height drives the neural currents. -->
      <div class="lib-grid" data-progress-track>
        <!-- ONE sticky wrapper — a direct grid child — holding BOTH the halo and
             the tree. They lock together (sticky; bottom:20px) and scroll away
             together when the library section ends. -->
        <div class="neural-rail">
          <!-- Halo: absolute INSIDE the sticky wrapper, so it's bound to the tree. -->
          <div class="neural-glow" aria-hidden="true"></div>
          <!-- Tree: stacked above the halo. -->
          <div class="neural-underlay">
            <NeuralProgressTree :sticky="false" />
          </div>
        </div>

        <!-- Field: editorial control header, then the specimen plates -->
        <div class="lib-field">
        <header id="library" class="scroll-mt-24">
          <h2 class="font-serif font-light text-3xl md:text-4xl text-ink">{{ t('academy.filterTitle') }}</h2>
          <div class="mt-5 h-px w-16 bg-gold/50"></div>

          <!-- Two-level filters: status, then field (start-aligned, editorial) -->
          <div class="mt-9 flex flex-wrap gap-x-9 gap-y-3">
            <button
              v-for="f in statusFilters"
              :key="f.key"
              @click="activeStatus = f.key"
              :class="[
                'relative text-[11px] uppercase tracking-[0.25em] font-light pb-1 transition-colors',
                activeStatus === f.key ? 'text-ink' : 'text-ink-muted hover:text-ink'
              ]"
            >
              {{ t(f.label) }}
              <span
                class="absolute inset-inline-0 -bottom-px h-px bg-gold transition-transform duration-200"
                :class="activeStatus === f.key ? 'scale-x-100' : 'scale-x-0'"
                style="inset-inline-start:0; inset-inline-end:0;"
              ></span>
            </button>
          </div>

          <div class="mt-4 flex flex-wrap gap-x-6 gap-y-2.5">
            <button
              v-for="f in fieldFilters"
              :key="f.key"
              @click="activeField = f.key"
              :class="[
                'text-[10px] uppercase tracking-[0.2em] font-light px-3 py-1.5 border rounded-full transition-colors whitespace-nowrap',
                activeField === f.key ? 'text-gold-dark border-gold/60 bg-gold/5' : 'text-ink-muted border-parchment-deep hover:text-ink hover:border-gold/40'
              ]"
            >{{ t(f.label) }}</button>
          </div>
        </header>

        <!-- The editorial plate stack -->
        <div class="mt-12 md:mt-16">
          <SpecimenPlate
            v-for="(c, i) in filtered"
            :key="courseIndex(c)"
            :section-id="`plate-${courseIndex(c)}`"
            :code="courseCode(courses, courseIndex(c))"
            :course="c"
            :cover="courseMediaAt(courseIndex(c))?.cover || ''"
            :to="`/academy/course/${courseIndex(c)}`"
            :field-label="t(`academy.fields.${c.field}`)"
            :tier-label="t(`academy.filters.${c.tier}`)"
            :flip="i % 2 === 1"
          />
        </div>

        <p v-if="!filtered.length" class="mt-16 text-sm text-ink-muted font-light italic">
          {{ t('academy.fields.all') }} — {{ t('academy.filters.all') }}
        </p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ── Library: living neural rail + specimen plates ─────────────────────────── */
.lib-grid {
  display: grid;
  grid-template-columns: 1fr;              /* mobile: rail stacked above the list */
  column-gap: clamp(2rem, 6vw, 5rem);
  row-gap: clamp(1rem, 4vw, 2rem);
  width: 100%;
  max-width: 84rem;
  margin-inline: auto;
  padding-inline: clamp(1.5rem, 5vw, 4rem);
}

.lib-field {
  min-width: 0;                            /* let plates shrink inside the grid */
  padding-top: clamp(3rem, 8vh, 7rem);
  padding-bottom: clamp(3rem, 8vh, 7rem);
}

.library-section { position: relative; }
.lib-grid { position: relative; z-index: 0; }

/* ── The single sticky wrapper (tree + halo) ───────────────────────────────────
   A direct child of the grid, so it's bound to the library section: it scrolls
   away naturally when the section ends. `position: relative` here also makes it
   the containing block for the absolute halo within it. */
.neural-rail {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: clamp(2rem, 6vh, 4rem);      /* mobile: a slim accent above the list */
}

/* The network sits clearly ABOVE the halo. */
.neural-underlay {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 340px;
  display: flex;
  justify-content: center;
}
.neural-underlay > * { position: relative; z-index: 10; }

/* ── Enormous, BOUND halo — absolute inside the sticky wrapper ──────────────────
   Locks exactly when the tree locks and scrolls out with it when the section
   ends. A very soft radial pool, densest behind the tree and melting to 0 toward
   the page centre. No border, no hard shadow.

   LIGHT MODE (default): a faint metallic-gold aura (#EBBC73) — the charcoal
   neuron reads as a sleek dark ink structure on the light page, wrapped in a warm
   gold glow that echoes its gold neural currents.
   DARK MODE: a deeper shade of the charcoal theme (#323A45 → #212833) so the
   luminous white neuron pops against it. */
.neural-glow {
  position: absolute;
  top: 50%;
  left: -10vw;
  transform: translateY(-50%);
  width: 70vw;
  height: 150vh;
  z-index: 0;
  pointer-events: none;
  background: radial-gradient(
    ellipse 46% 42% at 38% 50%,
    rgba(235, 188, 115, 0.26) 0%,
    rgba(235, 188, 115, 0.16) 24%,
    rgba(235, 188, 115, 0.09) 44%,
    rgba(235, 188, 115, 0.035) 62%,
    rgba(235, 188, 115, 0) 80%
  );
  filter: blur(12px);                        /* extra atmospheric softness */
}
/* DARK MODE halo (charcoal pool) lives in the global stylesheet
   (src/style.css, `html.dark .neural-glow`) for reliable cross-component theming. */

@media (min-width: 1024px) {
  .lib-grid {
    /* Wider rail so the (much larger) neuron reads as a prominent visual anchor. */
    grid-template-columns: minmax(300px, 4.6fr) minmax(0, 7.4fr);
    /* A large, prominent tree (~30–40% bigger than before). Sized so the WHOLE
       thing still fits in the viewport when it locks — prerequisite for the
       "fully visible, uncut" lock. Capped at 1100px on tall screens; otherwise
       it tracks the viewport minus 160px (room for navbar + top/bottom gaps). */
    --neuron-h: min(1100px, calc(100vh - 160px));
    /* Initial offset so the TOP of the tree starts just below the field row
       ("All fields / Neurology / Psychiatric Emergency / General"). */
    --neuron-start: clamp(11rem, 7vh + 11.9rem, 18rem);
  }

  /* ── THE STICKY LOCK on the sticky wrapper ────────────────────────────────────
     `align-self: start` stops the grid item from stretching to the full row, so
     it keeps its own height and has room to travel; the tall grid (= the plate
     list) is its sticky containing block.

     We pin with `top`, NOT `bottom`. A `bottom` inset shifts a sticky box UP
     toward the TOP of its containing block — but this box sits near that top
     edge (it's offset down only by `--neuron-start`), so a bottom inset has
     almost no room to shift into and releases immediately, tracking the scroll
     1:1 (this was the long-standing "sticky doesn't work" bug). A `top` inset
     is the correct model: the tree slides up with the cards and LOCKS once its
     top reaches the inset — by which point the whole tree (sized to fit) is on
     screen — then holds while the cards scroll, releasing at the section ends.

     The inset clears the 81px sticky navbar and otherwise vertically centres the
     neuron in the leftover viewport height, biased ~50–90px downward so it sits
     comfortably mid-viewport (never cut off at the top) when locked. */
  .neural-rail {
    align-self: start;
    position: sticky;
    top: clamp(140px, calc((100vh - var(--neuron-h)) / 2 + 45px), 320px);
    height: var(--neuron-h);
    margin-top: var(--neuron-start);
    padding-top: 0;
  }

  .neural-underlay {
    width: 100%;
    max-width: none;
    height: 100%;
    align-items: center;
  }
  /* Drive the SVG by HEIGHT so it matches --neuron-h exactly (overrides the
     component's width-driven aspect-ratio). */
  .neural-underlay :deep(.npt__svg) {
    height: var(--neuron-h);
    width: auto;
    max-width: 100%;
    aspect-ratio: auto;
  }

  /* Cards stay crisp above the halo's right-side bleed. */
  .lib-field { position: relative; z-index: 1; }
}
</style>
