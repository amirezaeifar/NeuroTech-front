<script setup>
/**
 * ProductsView — clean, minimal catalogue.
 *
 * A calm two-band layout: a deep-charcoal header ("Collection") above a warm
 * parchment catalogue of frosted-glass product cards. No animated particle
 * field, no drifting silhouettes, no decorative floating shapes — just the
 * product grid on quiet, static backgrounds. Dark-mode inverts the bands
 * (top-light / bottom-dark) via src/style.css.
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useReveal } from '../composables/useReveal.js'
import { deviceArt } from '../composables/useDeviceArt.js'

const { t, tm } = useI18n()

const filters = [
  { key: 'all', label: 'products.filters.all' },
  { key: 'eeg', label: 'products.filters.eeg' },
  { key: 'emg', label: 'products.filters.emg' },
  { key: 'neurostim', label: 'products.filters.neurostim' },
  { key: 'monitoring', label: 'products.filters.monitoring' },
]

const active = ref('all')
const products = computed(() => tm('products.items'))
const filtered = computed(() =>
  active.value === 'all' ? products.value : products.value.filter((p) => p.category === active.value)
)
const categoryLabel = (k) => t(`products.filters.${k}`)
const pad2 = (n) => String(n + 1).padStart(2, '0')
// Resolve a product's stable index in the full catalogue (the filtered loop
// index is not stable) so cards route to the correct detail page.
const productId = (p) => products.value.findIndex((x) => x.name === p.name)

useReveal()
</script>

<template>
  <div class="products-page">
    <!-- ── Header: COLLECTION / Maison Catalogue ─────────────────────────────── -->
    <section class="products-hero relative overflow-hidden py-24 md:py-36 text-center">
      <span class="products-hero-grid" aria-hidden="true"></span>
      <span class="products-hero-aura" aria-hidden="true"></span>
      <div class="relative max-w-5xl mx-auto px-8">
        <div class="flex items-center justify-center gap-4">
          <span class="products-hero-rule h-px w-10"></span>
          <span class="products-hero-eyebrow text-[11px] uppercase tracking-[0.4em] font-light">{{ t('products.hero.eyebrow') }}</span>
          <span class="products-hero-rule h-px w-10"></span>
        </div>
        <h1 class="products-hero-title font-serif font-light text-5xl md:text-7xl tracking-wide mt-8 leading-[1.05]">
          {{ t('products.hero.title') }}
        </h1>
      </div>
    </section>

    <!-- ── Stage: catalogue ──────────────────────────────────────────────────── -->
    <div class="products-stage">
      <div class="stage-content">
        <div class="mx-auto max-w-6xl px-8">
          <!-- Intro statement -->
          <div class="reveal text-center pt-20 md:pt-28 max-w-3xl mx-auto">
            <p class="stage-intro font-serif italic font-light text-2xl md:text-[2rem] leading-relaxed">
              {{ t('products.intro') }}
            </p>
            <div class="mx-auto mt-9 flex items-center justify-center gap-3 stage-intro-mark">
              <span class="h-px w-12"></span>
              <span class="text-xs">&#9670;</span>
              <span class="h-px w-12"></span>
            </div>
          </div>

          <!-- Filter tabs -->
          <div class="mt-16 flex flex-wrap justify-center gap-x-10 gap-y-3">
            <button
              v-for="f in filters"
              :key="f.key"
              type="button"
              @click="active = f.key"
              class="stage-tab"
              :class="{ 'is-active': active === f.key }"
            >
              {{ t(f.label) }}
              <span class="stage-tab-rule" :class="active === f.key ? 'scale-x-100' : 'scale-x-0'"></span>
            </button>
          </div>

          <!-- Premium glassmorphic product grid — each card is a single flat
               link: a framed device "render" up top, blueprint type below. -->
          <div class="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3 pb-28">
            <router-link
              v-for="(p, i) in filtered"
              :key="p.name + i"
              :to="`/products/${productId(p)}`"
              class="glass-card"
              :style="{ animationDelay: `${(i % 6) * 70}ms` }"
            >
              <!-- Top half — framed product imagery (flat line-art device) -->
              <div class="card-media">
                <span class="card-cat">{{ categoryLabel(p.category) }}</span>
                <span class="card-index">{{ pad2(i) }}</span>
                <svg
                  class="card-art"
                  viewBox="0 0 48 36"
                  fill="none"
                  stroke-width="1.1"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <g class="da-frame">
                    <path v-for="(d, k) in deviceArt(p.category).frame" :key="'f' + k" :d="d" />
                  </g>
                  <g class="da-signal">
                    <path v-for="(d, k) in deviceArt(p.category).signal" :key="'s' + k" :d="d" />
                  </g>
                </svg>
                <span class="card-media-tick" aria-hidden="true"></span>
              </div>

              <!-- Bottom half — blueprint typography -->
              <div class="card-body">
                <h3 class="card-name font-serif font-light">{{ p.name }}</h3>
                <span class="card-rule"></span>
                <p class="card-desc">{{ p.desc }}</p>
                <span class="card-inquire">
                  {{ t('products.viewCta') }}
                  <span class="dir-arrow" aria-hidden="true"></span>
                </span>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Page shell ─────────────────────────────────────────────────────────────
   A quiet two-band layout: charcoal header above a parchment catalogue. The
   dark-mode inversion lives in src/style.css (html.dark .products-hero / .products-stage). */
.products-page {
  position: relative;
  isolation: isolate;
}

/* ── Header band ───────────────────────────────────────────────────────────── */
.products-hero {
  background: #1a1714; /* light-mode header = deep charcoal */
  transition: background-color 300ms ease;
}
/* Static editorial hairlines, faded toward the foot of the band. */
.products-hero-grid {
  position: absolute;
  inset: 0;
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent 119px, rgba(244, 215, 145, 0.05) 119px, rgba(244, 215, 145, 0.05) 120px);
  -webkit-mask-image: linear-gradient(180deg, #000, transparent 92%);
          mask-image: linear-gradient(180deg, #000, transparent 92%);
}
.products-hero-aura {
  position: absolute;
  inset: 0;
  background: radial-gradient(60% 90% at 50% 0%, rgba(237, 192, 113, 0.16), transparent 70%);
}
.products-hero-eyebrow { color: rgb(237 192 113 / 0.8); }
.products-hero-rule { background: rgb(237 192 113 / 0.6); }
.products-hero-title { color: #f2ede4; }

/* ── Theme-adaptive catalogue stage (text + glass tokens) ───────────────────
   The light-mode palette lives here; the dark override lives in src/style.css
   (html.dark .products-stage …). */
.products-stage {
  position: relative;
  /* Empty drift zone below the catalogue so the last cards clear the fade. */
  padding-block-end: 7rem;
  /* light-mode catalogue = warm parchment + faint gold vignette */
  background-color: rgb(var(--c-parchment-light));
  background-image: radial-gradient(120% 60% at 50% 0%, rgba(138, 106, 26, 0.05), transparent 60%);
  transition: background-color 360ms ease;

  --stage-gold: #8a6a1a;
  --stage-text: #1a1714;
  --stage-muted: rgba(26, 23, 20, 0.62);
  --stage-faint: rgba(26, 23, 20, 0.42);
  --stage-rule: rgba(138, 106, 26, 0.55);
  --glass-bg: rgba(255, 255, 255, 0.5);
  --glass-bg-hover: rgba(255, 255, 255, 0.72);
  --glass-border: rgba(26, 23, 20, 0.1);
  --glass-sheen: rgba(255, 255, 255, 0.55);
  --media-bg: rgba(26, 23, 20, 0.035);
  --device-frame: rgba(26, 23, 20, 0.5);
  --device-signal: #8a6a1a;
}

.stage-content { position: relative; }

/* ── Intro statement ─────────────────────────────────────────────────────── */
.stage-intro { color: var(--stage-text); }
.stage-intro-mark { color: var(--stage-gold); }
.stage-intro-mark span:first-child,
.stage-intro-mark span:last-child { background: var(--stage-rule); }

/* ── Filter tabs ───────────────────────────────────────────────────────── */
.stage-tab {
  position: relative;
  padding-block-end: 0.25rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  font-weight: 300;
  color: var(--stage-faint);
  transition: color 200ms ease;
}
.stage-tab:hover,
.stage-tab.is-active { color: var(--stage-text); }
.stage-tab-rule {
  position: absolute;
  inset-inline: 0;
  bottom: -1px;
  height: 1px;
  background: var(--stage-gold);
  transition: transform 220ms ease;
}

/* ── Premium frosted-glass product cards ───────────────────────────────────
   Near-transparent fill + a strong backdrop blur. A framed device render tops
   the card; sharp blueprint type sits below. */
.glass-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  -webkit-backdrop-filter: blur(16px) saturate(1.2);
  backdrop-filter: blur(16px) saturate(1.2);
  overflow: hidden;
  /* A soft drop shadow lifts the card off the band; it floats a little higher
     on hover for a premium, tactile feel. */
  box-shadow: 0 8px 26px rgba(26, 23, 20, 0.1), 0 2px 6px rgba(26, 23, 20, 0.06);
  transition: background-color 360ms ease, border-color 360ms ease,
              transform 420ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 420ms ease;
  animation: card-in 600ms cubic-bezier(0.22, 1, 0.36, 1) both;
}
/* A whisper-fine gold top hairline catches the eye like a glass edge. */
.glass-card::after {
  content: '';
  position: absolute;
  inset-block-start: 0;
  inset-inline: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(237, 192, 113, 0.5), transparent);
  opacity: 0.6;
  pointer-events: none;
  z-index: 2;
}
.glass-card:hover {
  background: var(--glass-bg-hover);
  border-color: rgba(237, 192, 113, 0.5);
  transform: translateY(-5px);
  box-shadow: 0 18px 40px rgba(26, 23, 20, 0.16), 0 5px 12px rgba(26, 23, 20, 0.08);
}
@keyframes card-in {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: none; }
}

/* Top half — the framed product "render". Flat tinted panel, full device shown
   via object-fit:contain, divided from the body by a gold hairline. */
.card-media {
  position: relative;
  aspect-ratio: 4 / 3;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: var(--media-bg);
  border-block-end: 1px solid var(--glass-border);
}
/* Diagonal glass sheen — purely flat, adds depth without any 3D/shadow. */
.card-media::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(150deg, var(--glass-sheen), transparent 46%);
  opacity: 0.45;
}
.card-art {
  position: relative;
  width: 64%;
  height: 64%;
  object-fit: contain;
  transition: transform 500ms cubic-bezier(0.22, 1, 0.36, 1);
}
.glass-card:hover .card-art { transform: scale(1.04); }
.da-frame { stroke: var(--device-frame); }
.da-signal { stroke: var(--device-signal); }
/* A small gold corner tick — a clinical "registration mark". */
.card-media-tick {
  position: absolute;
  inset-block-start: 0.9rem;
  inset-inline-end: 0.9rem;
  width: 10px;
  height: 10px;
  border-top: 1px solid rgba(237, 192, 113, 0.6);
  border-inline-end: 1px solid rgba(237, 192, 113, 0.6);
}
.card-cat {
  position: absolute;
  inset-block-start: 1rem;
  inset-inline-start: 1.25rem;
  z-index: 1;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-weight: 400;
  color: var(--stage-gold);
}
.card-index {
  position: absolute;
  inset-block-end: 0.9rem;
  inset-inline-end: 1.25rem;
  z-index: 1;
  font-size: 11px;
  letter-spacing: 0.18em;
  font-weight: 400;
  color: var(--stage-faint);
  font-feature-settings: 'tnum' 1;
}

/* Bottom half — blueprint typography. */
.card-body {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  padding: 1.75rem 1.75rem 2rem;
}
.card-name {
  margin: 0;
  font-size: 1.6rem;
  line-height: 1.2;
  color: var(--stage-text);
}
.card-rule {
  display: block;
  width: 28px;
  height: 1px;
  margin-block: 1rem;
  background: var(--stage-rule);
}
.card-desc {
  flex: 1 1 auto;
  font-size: 0.875rem;
  line-height: 1.7;
  font-weight: 300;
  color: var(--stage-muted);
}
.card-inquire {
  align-self: flex-start;
  margin-block-start: 1.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  font-weight: 300;
  color: var(--stage-text);
  border-block-end: 1px solid var(--stage-rule);
  padding-block-end: 0.25rem;
  transition: color 220ms ease, border-color 220ms ease;
}
.card-inquire:hover,
.glass-card:hover .card-inquire {
  color: var(--stage-gold);
  border-block-end-color: var(--stage-gold);
}

/* ── Persian — neutralise Latin tracking; promote weights per the type system. */
html[lang='fa'] .products-hero-eyebrow,
html[lang='fa'] .stage-tab,
html[lang='fa'] .card-cat,
html[lang='fa'] .card-index,
html[lang='fa'] .card-inquire {
  letter-spacing: 0;
  text-transform: none;
}
html[lang='fa'] .card-cat,
html[lang='fa'] .card-inquire { font-weight: 700; }

@media (prefers-reduced-motion: reduce) {
  .glass-card { animation: none; }
  .glass-card:hover { transform: none; }
  .stage-tab-rule,
  .glass-card,
  .card-art,
  .card-inquire { transition: none; }
}
</style>
