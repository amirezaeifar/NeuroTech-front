<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useReveal } from '../composables/useReveal.js'
import { deviceArt } from '../composables/useDeviceArt.js'

const { t, tm } = useI18n()
const route = useRoute()

const products = computed(() => tm('products.items'))
const index = computed(() => Number(route.params.id))
const product = computed(() => products.value[index.value])
const categoryLabel = (k) => t(`products.filters.${k}`)

const badges = computed(() => tm('products.detail.badges'))
const keyFeatures = computed(() => tm('products.detail.keyFeatures'))
const specs = computed(() => tm('products.detail.specs'))
const certs = computed(() => tm('products.detail.certs'))
const trials = computed(() => tm('products.detail.trials'))
const ecosystem = computed(() => tm('products.detail.ecosystem'))

const reviews = computed(() => tm('products.detail.reviews'))
const ratingAvg = computed(() => {
  const r = reviews.value
  if (!r || !r.length) return 0
  return r.reduce((sum, x) => sum + (Number(x.rating) || 0), 0) / r.length
})
const starFills = computed(() =>
  Array.from({ length: 5 }, (_, i) => Math.max(0, Math.min(1, ratingAvg.value - i)))
)

const sku = computed(() => 'NT-' + String(index.value + 1).padStart(3, '0'))
const pad2 = (n) => String(n + 1).padStart(2, '0')

// ── Gallery ──────────────────────────────────────────────────────────────────
// Four "views" of the device — same SVG art, different viewBox crops to simulate
// front / interface / signal / rear perspectives. No extra assets required.
const GALLERY_SLIDES = [
  { label: 'Front View',       viewBox: '0 0 48 36' },
  { label: 'Interface Panel',  viewBox: '8 5 32 26' },
  { label: 'Signal Output',    viewBox: '-2 2 44 32' },
  { label: 'Module Detail',    viewBox: '4 0 40 36' },
]
const activeSlide = ref(0)
const isFullscreen = ref(false)

// ── Review carousel (3-up group paging, direction-aware) ─────────────────────
// visibleReviews is a window of up to 3 reviews starting at reviewOffset.
// Direction is tracked so the Transition name switches between rv-next / rv-prev,
// giving the group of 3 cards a directional slide-in/slide-out when navigating.
const reviewOffset = ref(0)
const reviewDir = ref('next')

const visibleReviews = computed(() => {
  const r = reviews.value
  const n = r.length
  if (!n) return []
  return Array.from({ length: Math.min(3, n) }, (_, i) => {
    const idx = (reviewOffset.value + i + n) % n
    return { idx, rv: r[idx] }
  })
})

const prevReview = () => {
  const n = reviews.value.length
  if (!n) return
  reviewDir.value = 'prev'
  reviewOffset.value = (reviewOffset.value - 1 + n) % n
}
const nextReview = () => {
  const n = reviews.value.length
  if (!n) return
  reviewDir.value = 'next'
  reviewOffset.value = (reviewOffset.value + 1) % n
}

// Blueprint & ecosystem icons (unchanged)
const blueprintIcons = [
  ['M2 12h4l2-7 3 14 2-9 2 4 1-2h6'],
  ['M5 4h14v11H5z', 'M9 20h6', 'M12 15v5', 'M8 8h8', 'M8 11h5'],
  ['M7 18a4 4 0 1 1 .8-7.9 5.5 5.5 0 0 1 10.5 1.6A3.5 3.5 0 0 1 17 18z', 'M12 12v6', 'M9.5 15.5 12 18l2.5-2.5'],
  ['M12 2 21 7v10l-9 5-9-5V7z', 'M3.5 7.5 12 12l8.5-4.5', 'M12 12v9.5'],
]
const featureIcon = (i) => blueprintIcons[i % blueprintIcons.length]

const ecosystemIcons = [
  ['M4 5h16v11H4z', 'M4 20h16', 'M8 9v4', 'M12 7v6', 'M16 10v3'],
  ['M7 18a4 4 0 1 1 .8-7.9 5.5 5.5 0 0 1 10.5 1.6A3.5 3.5 0 0 1 17 18z', 'M12 21v-7', 'M9.5 16.5 12 14l2.5 2.5'],
  ['M6 3h9l3 3v15H6z', 'M9 8h6', 'M9 12h6', 'M9 16h4'],
  ['M9 8 5 12l4 4', 'M15 8l4 4-4 4', 'M13 6l-2 12'],
]
const ecoIcon = (i) => ecosystemIcons[i % ecosystemIcons.length]

useReveal()
</script>

<template>
  <div class="pdx-page bg-parchment-light">
    <template v-if="product">
      <!-- ── Breadcrumb ─────────────────────────────────────────────────────── -->
      <div class="max-w-6xl mx-auto px-6 md:px-10">
        <nav class="pt-7 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[11px] uppercase tracking-[0.22em] font-light text-ink-muted">
          <router-link to="/" class="hover:text-gold-dark transition-colors">{{ t('products.detail.home') }}</router-link>
          <span class="text-ink-hint">/</span>
          <router-link to="/products" class="hover:text-gold-dark transition-colors">{{ t('products.detail.products') }}</router-link>
          <span class="text-ink-hint">/</span>
          <span class="text-gold-dark normal-case tracking-[0.1em]">{{ product.name }}</span>
        </nav>
      </div>

      <!-- ── Split hero ─────────────────────────────────────────────────────── -->
      <section class="max-w-6xl mx-auto px-6 md:px-10 pt-8 md:pt-12">
        <div class="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">

          <!-- ── Image Gallery ───────────────────────────────────────────────── -->
          <div class="pdx-gallery reveal">
            <!-- Main display -->
            <figure class="pdx-gallery-main">
              <!-- Fullscreen toggle -->
              <button
                class="pdx-fs-btn"
                type="button"
                aria-label="View fullscreen"
                @click="isFullscreen = true"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
                  <path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/>
                </svg>
              </button>

              <span class="pdx-render-cat">{{ categoryLabel(product.category) }}</span>
              <span class="pdx-render-ref">{{ t('products.detail.skuLabel') }} · {{ sku }}</span>

              <!-- Slides stacked; CSS opacity + scale transition between them -->
              <div class="pdx-slides-wrap">
                <div
                  v-for="(slide, k) in GALLERY_SLIDES"
                  :key="k"
                  class="pdx-slide"
                  :class="{ 'is-active': activeSlide === k }"
                >
                  <svg
                    class="pdx-render-art"
                    :viewBox="slide.viewBox"
                    fill="none"
                    stroke-width="0.9"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    aria-hidden="true"
                  >
                    <g class="pdx-frame">
                      <path v-for="(d, m) in deviceArt(product.category).frame" :key="'f' + m" :d="d" />
                    </g>
                    <g class="pdx-signal">
                      <path v-for="(d, m) in deviceArt(product.category).signal" :key="'s' + m" :d="d" />
                    </g>
                  </svg>
                  <!-- Slide label chip -->
                  <span class="pdx-slide-label">{{ slide.label }}</span>
                </div>
              </div>

              <!-- Corner registration marks -->
              <span class="pdx-tick pdx-tick-tl" aria-hidden="true"></span>
              <span class="pdx-tick pdx-tick-br" aria-hidden="true"></span>
            </figure>

            <!-- Thumbnail strip -->
            <div class="pdx-thumbs" role="tablist" aria-label="Gallery views">
              <button
                v-for="(slide, k) in GALLERY_SLIDES"
                :key="k"
                type="button"
                role="tab"
                class="pdx-thumb"
                :class="{ 'is-active': activeSlide === k }"
                :aria-selected="activeSlide === k"
                @click="activeSlide = k"
              >
                <svg
                  :viewBox="slide.viewBox"
                  fill="none"
                  stroke-width="1.2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="pdx-thumb-art"
                  aria-hidden="true"
                >
                  <g class="pdx-frame">
                    <path v-for="(d, m) in deviceArt(product.category).frame" :key="'f' + m" :d="d" />
                  </g>
                  <g class="pdx-signal">
                    <path v-for="(d, m) in deviceArt(product.category).signal" :key="'s' + m" :d="d" />
                  </g>
                </svg>
              </button>
            </div>
          </div>

          <!-- Name · tagline · technical essence -->
          <div class="reveal">
            <p class="text-[11px] uppercase tracking-[0.38em] text-gold-dark font-light">{{ t('products.detail.brand') }}</p>
            <h1 class="mt-4 font-serif font-light text-[2.6rem] md:text-6xl text-ink leading-[1.04]">{{ product.name }}</h1>
            <p class="mt-5 font-serif italic font-light text-xl md:text-2xl text-ink-soft leading-relaxed">{{ t('products.detail.overviewLead') }}</p>

            <div class="mt-8">
              <div class="flex items-center gap-3">
                <span class="pdx-essence-rule"></span>
                <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('products.detail.essenceLabel') }}</span>
              </div>
              <p class="mt-4 text-[15px] text-ink-soft font-light leading-relaxed">{{ product.desc }}</p>
              <p class="mt-3 text-[15px] text-ink-soft font-light leading-relaxed">{{ t('products.detail.overviewBody') }}</p>
            </div>

            <!-- Badges -->
            <div class="mt-7 flex flex-wrap gap-2.5">
              <span v-for="(b, k) in badges" :key="k" class="pdx-badge">{{ b }}</span>
            </div>

            <!-- CTAs — high-end clinical glassmorphism buttons -->
            <div class="mt-9 flex flex-col sm:flex-row gap-3.5">
              <router-link to="/checkout" class="pdx-btn-primary">
                {{ t('products.detail.purchaseCta') }} <span class="dir-arrow" aria-hidden="true"></span>
              </router-link>
              <!-- Download Brochure — premium placeholder; no action wired. -->
              <a href="#" class="pdx-btn-ghost" @click.prevent>
                {{ t('products.detail.ctaSecondary') }}
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Technical Blueprint ────────────────────────────────────────────── -->
      <section class="pdx-blueprint">
        <div class="max-w-6xl mx-auto px-6 md:px-10">
          <div class="reveal flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <p class="text-[10px] uppercase tracking-[0.34em] text-gold-dark font-light">{{ t('products.detail.featuresTitle') }}</p>
              <h2 class="pdx-h2 mt-3">{{ t('products.detail.blueprintTitle') }}</h2>
            </div>
            <p class="font-serif italic font-light text-lg text-ink-muted max-w-sm md:text-end">{{ t('products.detail.blueprintLead') }}</p>
          </div>
          <span class="pdx-hairline reveal" aria-hidden="true"></span>

          <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-px pdx-grid reveal">
            <article v-for="(f, k) in keyFeatures" :key="k" class="pdx-cell">
              <div class="flex items-center justify-between">
                <span class="pdx-cell-no">{{ pad2(k) }}</span>
                <svg class="pdx-cell-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path v-for="(d, m) in featureIcon(k)" :key="m" :d="d" />
                </svg>
              </div>
              <p class="pdx-cell-text">{{ f }}</p>
            </article>
          </div>
        </div>
      </section>

      <!-- ── Clinical Validation & Certifications ───────────────────────────── -->
      <section class="max-w-6xl mx-auto px-6 md:px-10 pt-20 md:pt-24">
        <div class="reveal">
          <p class="text-[10px] uppercase tracking-[0.34em] text-gold-dark font-light">{{ t('products.detail.validationKicker') }}</p>
          <h2 class="pdx-h2 mt-3">{{ t('products.detail.validationTitle') }}</h2>
          <p class="mt-3 font-serif italic font-light text-lg text-ink-muted max-w-xl">{{ t('products.detail.validationLead') }}</p>
          <span class="pdx-hairline" aria-hidden="true"></span>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 reveal">
          <article v-for="(c, k) in certs" :key="k" class="pdx-cert">
            <span class="pdx-cert-mark">{{ c.mark }}</span>
            <div>
              <p class="pdx-cert-name">{{ c.name }}</p>
              <p class="pdx-cert-note">{{ c.note }}</p>
            </div>
          </article>
        </div>

        <div class="mt-6 flex items-center gap-3 reveal">
          <span class="pdx-essence-rule"></span>
          <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('products.detail.trialsLabel') }}</span>
        </div>
        <div class="mt-5 grid sm:grid-cols-3 gap-5 reveal">
          <article v-for="(tr, k) in trials" :key="k" class="pdx-trial">
            <p class="pdx-trial-stat">{{ tr.stat }}</p>
            <p class="pdx-trial-label">{{ tr.label }}</p>
            <p class="pdx-trial-note">{{ tr.note }}</p>
          </article>
        </div>
      </section>

      <!-- ── Software Ecosystem ─────────────────────────────────────────────── -->
      <section class="max-w-6xl mx-auto px-6 md:px-10 pt-20 md:pt-24">
        <div class="reveal flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <p class="text-[10px] uppercase tracking-[0.34em] text-gold-dark font-light">{{ t('products.detail.ecosystemKicker') }}</p>
            <h2 class="pdx-h2 mt-3">{{ t('products.detail.ecosystemTitle') }}</h2>
          </div>
          <p class="font-serif italic font-light text-lg text-ink-muted max-w-sm md:text-end">{{ t('products.detail.ecosystemLead') }}</p>
        </div>
        <span class="pdx-hairline reveal" aria-hidden="true"></span>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 reveal">
          <article v-for="(e, k) in ecosystem" :key="k" class="pdx-eco">
            <svg class="pdx-eco-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path v-for="(d, m) in ecoIcon(k)" :key="m" :d="d" />
            </svg>
            <p class="pdx-eco-name">{{ e.name }}</p>
            <p class="pdx-eco-desc">{{ e.desc }}</p>
          </article>
        </div>
        <p class="mt-6 text-[13px] text-ink-muted font-light reveal flex items-center gap-2.5">
          <span class="pdx-eco-dot" aria-hidden="true"></span>{{ t('products.detail.ecosystemNote') }}
        </p>
      </section>

      <!-- ── Specifications ─────────────────────────────────────────────────── -->
      <section class="max-w-6xl mx-auto px-6 md:px-10 pt-20 md:pt-24">
        <div class="reveal">
          <p class="text-[10px] uppercase tracking-[0.34em] text-gold-dark font-light">{{ t('products.detail.specsTitle') }}</p>
          <h2 class="pdx-h2 mt-3">{{ t('products.detail.specsTitle') }}</h2>
          <span class="pdx-hairline" aria-hidden="true"></span>
        </div>

        <dl class="pdx-specs reveal">
          <div v-for="(s, k) in specs" :key="k" class="pdx-spec-row">
            <dt>{{ s.label }}</dt>
            <dd>{{ s.value }}</dd>
          </div>
        </dl>
      </section>

      <!-- ── CTA band ───────────────────────────────────────────────────────── -->
      <section class="max-w-6xl mx-auto px-6 md:px-10 pt-20 md:pt-28 pb-16">
        <div class="pdx-cta reveal">
          <div class="pdx-cta-grid" aria-hidden="true"></div>
          <div class="relative">
            <p class="text-[10px] uppercase tracking-[0.34em] pdx-cta-eyebrow font-light">{{ t('products.detail.brand') }}</p>
            <h2 class="mt-4 font-serif font-light text-3xl md:text-5xl leading-[1.08] pdx-cta-title">{{ t('products.detail.overviewLead') }}</h2>
            <p class="mt-4 text-[14px] font-light leading-relaxed pdx-cta-note max-w-xl">{{ t('products.detail.priceNote') }}</p>
            <div class="mt-9 flex flex-col sm:flex-row gap-3.5">
              <router-link to="/checkout" class="pdx-cta-btn">
                {{ t('products.detail.purchaseCta') }} <span class="dir-arrow" aria-hidden="true"></span>
              </router-link>
              <span class="pdx-cta-meta">
                <span class="pdx-cta-dot"></span>{{ t('products.detail.availability') }} · {{ t('products.detail.leadTime') }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Reviews & Ratings — pinned to the very bottom, just above footer ── -->
      <section class="max-w-6xl mx-auto px-6 md:px-10 pt-16 md:pt-20 pb-24">
        <div class="reveal">
          <p class="text-[10px] uppercase tracking-[0.34em] text-gold-dark font-light">{{ t('products.detail.reviewsKicker') }}</p>
          <h2 class="pdx-h2 mt-3">{{ t('products.detail.reviewsTitle') }}</h2>
          <span class="pdx-hairline" aria-hidden="true"></span>
        </div>

        <!-- Rating summary -->
        <div class="pdx-rating-summary reveal">
          <div class="pdx-rating-score">
            <span class="pdx-rating-avg">{{ ratingAvg.toFixed(1) }}</span>
            <span class="pdx-rating-outof">/ 5</span>
          </div>
          <div class="pdx-rating-meta">
            <span class="pdx-stars" :style="{ '--fill': ratingAvg / 5 }" aria-hidden="true">
              <span class="pdx-stars-base">★★★★★</span>
              <span class="pdx-stars-fill">★★★★★</span>
            </span>
            <span class="pdx-rating-count">{{ reviews.length }} · {{ t('products.detail.ratingSuffix') }}</span>
          </div>
        </div>

        <!-- 3-up directional card carousel — the entire visible group transitions
             as a unit with a direction-aware slide. mode="out-in" ensures the
             outgoing group fully exits before the incoming group enters, keeping
             the grid stable with no overlap or layout pop. -->
        <Transition :name="`rv-${reviewDir}`" mode="out-in">
          <div class="pdx-review-grid" :key="reviewOffset">
            <article
              v-for="item in visibleReviews"
              :key="item.idx"
              class="pdx-review"
            >
              <span class="pdx-stars pdx-stars-sm" :style="{ '--fill': (Number(item.rv.rating) || 0) / 5 }" aria-hidden="true">
                <span class="pdx-stars-base">★★★★★</span>
                <span class="pdx-stars-fill">★★★★★</span>
              </span>
              <p class="pdx-review-text">{{ item.rv.text }}</p>
              <div class="pdx-review-author">
                <span class="pdx-review-avatar" aria-hidden="true">{{ (item.rv.author || '?').trim().charAt(0) }}</span>
                <div>
                  <p class="pdx-review-name">{{ item.rv.author }}</p>
                  <p class="pdx-review-role">{{ item.rv.role }}</p>
                </div>
              </div>
            </article>
          </div>
        </Transition>

        <!-- Navigation row — centered below the card track so users navigate
             after reading the visible reviews, not before. -->
        <div class="pdx-carousel-nav reveal">
          <button type="button" class="pdx-carousel-btn" @click="prevReview" aria-label="Previous review">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
              <path d="M15 18l-6-6 6-6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <!-- Dot indicators -->
          <div class="pdx-carousel-dots" aria-hidden="true">
            <button
              v-for="(_, k) in reviews"
              :key="k"
              type="button"
              class="pdx-carousel-dot"
              :class="{ 'is-active': reviewOffset === k }"
              @click="() => { reviewDir = k > reviewOffset ? 'next' : 'prev'; reviewOffset = k }"
            ></button>
          </div>
          <button type="button" class="pdx-carousel-btn" @click="nextReview" aria-label="Next review">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
              <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </section>
    </template>

    <!-- Unknown / out-of-range id -->
    <div v-else class="max-w-6xl mx-auto px-6 py-40 text-center">
      <p class="font-serif font-light text-2xl text-ink">{{ t('products.detail.notFound') }}</p>
      <router-link to="/products" class="mt-6 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1 hover:text-gold transition-colors">
        {{ t('products.detail.back') }}
      </router-link>
    </div>
  </div>

  <!-- ── Fullscreen overlay ─────────────────────────────────────────────────── -->
  <Teleport to="body">
    <Transition name="pdx-fs">
      <div
        v-if="isFullscreen && product"
        class="pdx-fs-overlay"
        role="dialog"
        aria-modal="true"
        @click.self="isFullscreen = false"
      >
        <button type="button" class="pdx-fs-close" @click="isFullscreen = false" aria-label="Close fullscreen">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
            <path d="M18 6 6 18M6 6l12 12" stroke-linecap="round"/>
          </svg>
        </button>
        <div class="pdx-fs-stage">
          <svg
            class="pdx-fs-art"
            :viewBox="GALLERY_SLIDES[activeSlide].viewBox"
            fill="none"
            stroke-width="0.6"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <g class="pdx-frame"><path v-for="(d, k) in deviceArt(product.category).frame" :key="'f'+k" :d="d"/></g>
            <g class="pdx-signal"><path v-for="(d, k) in deviceArt(product.category).signal" :key="'s'+k" :d="d"/></g>
          </svg>
          <div class="pdx-fs-thumbs">
            <button
              v-for="(slide, k) in GALLERY_SLIDES"
              :key="k"
              type="button"
              class="pdx-thumb pdx-fs-thumb-btn"
              :class="{ 'is-active': activeSlide === k }"
              @click="activeSlide = k"
            >
              <svg :viewBox="slide.viewBox" fill="none" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" class="pdx-thumb-art" aria-hidden="true">
                <g class="pdx-frame"><path v-for="(d, m) in deviceArt(product.category).frame" :key="'f'+m" :d="d"/></g>
                <g class="pdx-signal"><path v-for="(d, m) in deviceArt(product.category).signal" :key="'s'+m" :d="d"/></g>
              </svg>
            </button>
          </div>
          <p class="pdx-fs-label">{{ GALLERY_SLIDES[activeSlide].label }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.pdx-page {
  min-height: 100vh;
  --pdx-shadow: 0 6px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  --pdx-shadow-lift: 0 16px 38px rgba(0, 0, 0, 0.14), 0 4px 10px rgba(0, 0, 0, 0.08);
}
.pdx-h2 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: 2.1rem;
  line-height: 1.12;
  color: rgb(var(--c-ink));
}
html[lang='fa'] .pdx-h2 { font-family: inherit; font-weight: 700; }
.pdx-hairline {
  display: block;
  height: 1px;
  margin-block: 1.6rem 2.4rem;
  background: linear-gradient(90deg, rgb(var(--c-gold) / 0.6), rgb(var(--c-gold) / 0.12) 40%, transparent 80%);
}

/* ── Gallery ───────────────────────────────────────────────────────────────── */
.pdx-gallery {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.pdx-gallery-main {
  position: relative;
  aspect-ratio: 5 / 4;
  border-radius: 16px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background-color: rgb(var(--c-parchment));
  background-image:
    radial-gradient(80% 70% at 50% 38%, rgb(var(--c-gold) / 0.07), transparent 70%),
    repeating-linear-gradient(0deg, transparent 0 39px, rgb(var(--c-gold) / 0.05) 39px 40px),
    repeating-linear-gradient(90deg, transparent 0 39px, rgb(var(--c-gold) / 0.05) 39px 40px);
  overflow: hidden;
  box-shadow: var(--pdx-shadow);
  transition: box-shadow 460ms ease;
}
.pdx-gallery-main:hover { box-shadow: var(--pdx-shadow-lift); }

/* Slides container fills the figure */
.pdx-slides-wrap {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
}

/* Each slide stacks in the same cell; inactive ones fade + scale out */
.pdx-slide {
  grid-area: 1 / 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  opacity: 0;
  transform: scale(0.96);
  transition: opacity 480ms cubic-bezier(0.22, 1, 0.36, 1),
              transform 480ms cubic-bezier(0.22, 1, 0.36, 1);
  pointer-events: none;
}
.pdx-slide.is-active {
  opacity: 1;
  transform: scale(1);
  pointer-events: auto;
}

.pdx-render-art,
.pdx-fs-art {
  width: 72%;
  height: 72%;
  object-fit: contain;
}
.pdx-frame { stroke: rgb(var(--c-ink) / 0.55); }
.pdx-signal { stroke: rgb(var(--c-gold-dark)); }

/* Slide view label — bottom-centre chip */
.pdx-slide-label {
  position: absolute;
  inset-block-end: 1.2rem;
  inset-inline-start: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.28em;
  font-weight: 400;
  color: rgb(var(--c-gold-dark));
  white-space: nowrap;
}

/* Category / SKU labels */
.pdx-render-cat {
  position: absolute;
  inset-block-start: 1.25rem;
  inset-inline-start: 1.5rem;
  z-index: 2;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-weight: 400;
  color: rgb(var(--c-gold-dark));
}
.pdx-render-ref {
  position: absolute;
  inset-block-end: 1.25rem;
  inset-inline-end: 1.5rem;
  z-index: 2;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 300;
  color: rgb(var(--c-ink-hint));
  font-feature-settings: 'tnum' 1;
}

/* Fullscreen toggle — top-right corner */
.pdx-fs-btn {
  position: absolute;
  inset-block-start: 1rem;
  inset-inline-end: 1rem;
  z-index: 3;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 8px;
  background: rgb(var(--c-parchment) / 0.7);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  border: 1px solid rgb(var(--c-gold) / 0.35);
  color: rgb(var(--c-gold-dark));
  cursor: pointer;
  transition: background-color 220ms ease, border-color 220ms ease, transform 260ms cubic-bezier(0.22,1,0.36,1);
}
.pdx-fs-btn:hover {
  background: rgb(var(--c-gold) / 0.12);
  border-color: rgb(var(--c-gold) / 0.7);
  transform: scale(1.08);
}

/* Gold registration ticks */
.pdx-tick { position: absolute; width: 16px; height: 16px; z-index: 2; }
.pdx-tick-tl { inset-block-start: 1rem; inset-inline-start: 1rem; border-top: 1px solid rgb(var(--c-gold) / 0.55); border-inline-start: 1px solid rgb(var(--c-gold) / 0.55); }
.pdx-tick-br { inset-block-end: 1rem; inset-inline-end: 1rem; border-bottom: 1px solid rgb(var(--c-gold) / 0.55); border-inline-end: 1px solid rgb(var(--c-gold) / 0.55); }

/* ── Thumbnail strip ───────────────────────────────────────────────────────── */
.pdx-thumbs {
  display: flex;
  gap: 0.6rem;
}
.pdx-thumb {
  flex: 1;
  aspect-ratio: 5 / 4;
  display: grid;
  place-items: center;
  padding: 0.5rem;
  border-radius: 10px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  cursor: pointer;
  transition: border-color 220ms ease, background-color 220ms ease, transform 280ms cubic-bezier(0.22,1,0.36,1), box-shadow 280ms ease;
}
.pdx-thumb:hover {
  border-color: rgb(var(--c-gold) / 0.55);
  background: rgb(var(--c-gold) / 0.06);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}
.pdx-thumb.is-active {
  border-color: rgb(var(--c-gold));
  background: rgb(var(--c-gold) / 0.08);
  box-shadow: 0 0 0 2px rgb(var(--c-gold) / 0.25);
}
.pdx-thumb-art {
  width: 80%;
  height: 80%;
  object-fit: contain;
}

.pdx-essence-rule { display: block; width: 26px; height: 1px; background: rgb(var(--c-gold) / 0.7); }

.pdx-badge {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-weight: 300;
  color: rgb(var(--c-gold-dark));
  border: 1px solid rgb(var(--c-gold) / 0.4);
  background: rgb(var(--c-gold) / 0.06);
  border-radius: 9999px;
  padding-block: 0.32rem;
  padding-inline: 0.8rem;
}

/* ── Buttons — shared base then per-variant ────────────────────────────────── */
.pdx-btn-primary,
.pdx-btn-ghost,
.pdx-cta-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  padding-block: 0.85rem;
  padding-inline: 1.75rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-weight: 400;
}
/* Primary and CTA lift on hover; Ghost pill does NOT lift — it sweeps instead */
.pdx-btn-primary,
.pdx-cta-btn {
  border-radius: 8px;
  transition: background-color 300ms cubic-bezier(0.22, 1, 0.36, 1),
              color 300ms ease,
              border-color 300ms ease,
              transform 380ms cubic-bezier(0.34, 1.28, 0.64, 1),
              box-shadow 300ms ease;
}
.pdx-btn-primary:hover,
.pdx-cta-btn:hover { transform: translateY(-3px); }
.pdx-btn-primary:active,
.pdx-cta-btn:active { transform: translateY(0); transition-duration: 120ms; }

/* Primary — a rich ink slab with soft depth and a warm-to-gold hover */
.pdx-btn-primary {
  background: rgb(var(--c-ink));
  color: rgb(var(--c-parchment-light));
  /* Soft elevation with an inner shimmer on top */
  box-shadow:
    0 4px 16px rgba(0,0,0,0.16),
    0 1px 3px rgba(0,0,0,0.1),
    inset 0 1px 0 rgba(255,255,255,0.06);
}
.pdx-btn-primary:hover {
  background: rgb(var(--c-gold-dark));
  box-shadow:
    0 10px 28px rgba(0,0,0,0.22),
    0 3px 8px rgba(0,0,0,0.12);
}
.pdx-btn-primary:active {
  box-shadow: 0 3px 10px rgba(0,0,0,0.14);
}

/* Ghost secondary — sits beside the solid primary; a clean 1px gold outline
   with a soft background fill on hover. Rectangular to match the primary.
   The ::after arrow provides the directional nudge since this button has no
   inline dir-arrow span in its template. */
.pdx-btn-ghost {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 7px;
  border: 1px solid rgb(var(--c-gold) / 0.55);
  color: rgb(var(--c-gold-dark));
  background: transparent;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: color 280ms ease, border-color 280ms ease, box-shadow 280ms ease;
}
.pdx-btn-ghost::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: rgb(var(--c-gold));
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 400ms cubic-bezier(0.22, 1, 0.36, 1);
}
html[dir='rtl'] .pdx-btn-ghost::before { transform-origin: right center; }
.pdx-btn-ghost::after {
  content: '\2192';
  display: inline-block;
  font-style: normal;
  transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}
html[dir='rtl'] .pdx-btn-ghost::after { content: '\2190'; }
.pdx-btn-ghost:hover {
  color: #1a1714;
  border-color: rgb(var(--c-gold));
  box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
.pdx-btn-ghost:hover::before { transform: scaleX(1); }
.pdx-btn-ghost:hover::after { transform: translateX(4px); }
html[dir='rtl'] .pdx-btn-ghost:hover::after { transform: translateX(-4px); }

/* ── Technical Blueprint ───────────────────────────────────────────────────── */
.pdx-blueprint { padding-block: 5rem; margin-block-start: 4rem; }
.pdx-grid {
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment-deep));
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--pdx-shadow);
}
.pdx-cell {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 12rem;
  padding: 1.75rem;
  background: rgb(var(--c-parchment));
  transition: background-color 260ms ease;
}
.pdx-cell:hover { background: rgb(var(--c-gold) / 0.05); }
.pdx-cell-no {
  font-size: 11px;
  letter-spacing: 0.2em;
  font-weight: 400;
  color: rgb(var(--c-gold-dark));
  font-feature-settings: 'tnum' 1;
}
.pdx-cell-icon { width: 26px; height: 26px; color: rgb(var(--c-gold-dark)); }
.pdx-cell-text {
  margin-block-start: auto;
  font-size: 0.9rem;
  line-height: 1.6;
  font-weight: 300;
  color: rgb(var(--c-ink-soft));
}

/* ── Clinical Validation & Certifications ──────────────────────────────────── */
.pdx-cert {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.4rem 1.5rem;
  border-radius: 14px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  box-shadow: var(--pdx-shadow);
  transition: transform 320ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 320ms ease;
}
.pdx-cert:hover { transform: translateY(-3px); box-shadow: var(--pdx-shadow-lift); }
.pdx-cert-mark {
  flex: none;
  display: inline-grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: rgb(var(--c-gold-dark));
  background: rgb(var(--c-gold) / 0.1);
  border: 1px solid rgb(var(--c-gold) / 0.4);
  box-shadow: inset 0 1px 2px rgb(var(--c-gold) / 0.12);
}
.pdx-cert-name { font-size: 0.95rem; font-weight: 400; color: rgb(var(--c-ink)); }
.pdx-cert-note { margin-block-start: 0.3rem; font-size: 0.8rem; line-height: 1.55; font-weight: 300; color: rgb(var(--c-ink-muted)); }

.pdx-trial {
  padding: 1.6rem 1.5rem;
  border-radius: 14px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  box-shadow: var(--pdx-shadow);
}
.pdx-trial-stat {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: 2.3rem;
  line-height: 1;
  color: rgb(var(--c-gold-dark));
}
html[lang='fa'] .pdx-trial-stat { font-family: inherit; font-weight: 700; font-size: 1.9rem; }
.pdx-trial-label { margin-block-start: 0.7rem; font-size: 11px; text-transform: uppercase; letter-spacing: 0.18em; font-weight: 400; color: rgb(var(--c-ink)); }
.pdx-trial-note { margin-block-start: 0.55rem; font-size: 0.82rem; line-height: 1.6; font-weight: 300; color: rgb(var(--c-ink-muted)); }

/* ── Software Ecosystem ────────────────────────────────────────────────────── */
.pdx-eco {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  min-height: 11rem;
  padding: 1.6rem 1.5rem;
  border-radius: 14px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  box-shadow: var(--pdx-shadow);
  transition: transform 320ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 320ms ease;
}
.pdx-eco:hover { transform: translateY(-3px); box-shadow: var(--pdx-shadow-lift); }
.pdx-eco-icon { width: 30px; height: 30px; color: rgb(var(--c-gold-dark)); }
.pdx-eco-name { font-size: 1rem; font-weight: 400; color: rgb(var(--c-ink)); }
.pdx-eco-desc { margin-block-start: auto; font-size: 0.83rem; line-height: 1.6; font-weight: 300; color: rgb(var(--c-ink-muted)); }
.pdx-eco-dot { flex: none; width: 7px; height: 7px; border-radius: 9999px; background: rgb(var(--c-gold)); }

/* ── Stars ─────────────────────────────────────────────────────────────────── */
.pdx-stars {
  position: relative;
  display: inline-block;
  white-space: nowrap;
  font-size: 1.05rem;
  line-height: 1;
  letter-spacing: 0.12em;
}
.pdx-stars-base { color: rgb(var(--c-ink) / 0.18); }
.pdx-stars-fill {
  position: absolute;
  inset-block-start: 0;
  inset-inline-start: 0;
  width: calc(var(--fill, 0) * 100%);
  overflow: hidden;
  color: rgb(var(--c-gold-dark));
}
.pdx-stars-sm { font-size: 0.9rem; }

/* ── Rating summary ────────────────────────────────────────────────────────── */
.pdx-rating-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1.25rem 2rem;
  margin-block-end: 2rem;
  padding: 1.6rem 1.75rem;
  border-radius: 16px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  box-shadow: var(--pdx-shadow);
}
.pdx-rating-score { display: flex; align-items: baseline; gap: 0.4rem; }
.pdx-rating-avg {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: 3.2rem;
  line-height: 1;
  color: rgb(var(--c-ink));
}
html[lang='fa'] .pdx-rating-avg { font-family: inherit; font-weight: 700; font-size: 2.6rem; }
.pdx-rating-outof { font-size: 0.95rem; font-weight: 300; color: rgb(var(--c-ink-muted)); }
.pdx-rating-meta { display: flex; flex-direction: column; gap: 0.5rem; }
.pdx-rating-count { font-size: 11px; letter-spacing: 0.06em; font-weight: 300; color: rgb(var(--c-ink-muted)); }

/* ── Review Carousel (3-up, group paging) ──────────────────────────────────── */

/* Navigation row: prev button · dots · next button.
   Default sits below the card track with a 2rem top margin; no bottom margin
   needed since the section carries its own pb-24. */
.pdx-carousel-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  margin-block-start: 2rem;
}

/* Gold-frosted circular prev/next buttons */
.pdx-carousel-btn {
  flex: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  border: 1px solid rgb(var(--c-gold) / 0.5);
  background: rgb(var(--c-parchment));
  color: rgb(var(--c-gold-dark));
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  transition: background-color 220ms ease, border-color 220ms ease,
              box-shadow 220ms ease, transform 300ms cubic-bezier(0.34, 1.28, 0.64, 1);
}
.pdx-carousel-btn:hover {
  background: rgb(var(--c-gold) / 0.1);
  border-color: rgb(var(--c-gold));
  box-shadow: 0 6px 16px rgba(0,0,0,0.11);
  transform: scale(1.07);
}
.pdx-carousel-btn:active { transform: scale(0.95); transition-duration: 90ms; }

/* Dot indicators */
.pdx-carousel-dots { display: flex; gap: 0.45rem; }
.pdx-carousel-dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  border: 1px solid rgb(var(--c-gold) / 0.45);
  background: transparent;
  cursor: pointer;
  transition: background-color 220ms ease, border-color 220ms ease, transform 220ms ease;
}
.pdx-carousel-dot.is-active {
  background: rgb(var(--c-gold));
  border-color: rgb(var(--c-gold));
  transform: scale(1.35);
}

/* 3-column review grid — responsive: 1 col mobile, 2 tablet, 3 desktop */
.pdx-review-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}
@media (min-width: 640px) { .pdx-review-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .pdx-review-grid { grid-template-columns: repeat(3, 1fr); } }

/* Direction-aware slide transitions for the group (:key="reviewOffset" triggers) */
.rv-next-enter-active,
.rv-next-leave-active,
.rv-prev-enter-active,
.rv-prev-leave-active {
  transition: transform 360ms cubic-bezier(0.22, 1, 0.36, 1), opacity 260ms ease;
}
/* Forward (next): old group slides left out, new group enters from right */
.rv-next-enter-from { transform: translateX(48px); opacity: 0; }
.rv-next-leave-to  { transform: translateX(-48px); opacity: 0; }
/* Backward (prev): old group slides right out, new group enters from left */
.rv-prev-enter-from { transform: translateX(-48px); opacity: 0; }
.rv-prev-leave-to  { transform: translateX(48px);  opacity: 0; }

/* Individual review card */
.pdx-review {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.75rem 1.75rem 1.6rem;
  border-radius: 16px;
  border: 1px solid rgb(var(--c-parchment-deep));
  background: rgb(var(--c-parchment));
  box-shadow: var(--pdx-shadow);
  transition: box-shadow 300ms ease, transform 300ms cubic-bezier(0.22, 1, 0.36, 1);
}
.pdx-review:hover { transform: translateY(-3px); box-shadow: var(--pdx-shadow-lift); }
.pdx-review-text { font-size: 0.9rem; line-height: 1.75; font-weight: 300; color: rgb(var(--c-ink-soft)); flex: 1; }
.pdx-review-author {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-block-start: 0.75rem;
  border-block-start: 1px solid rgb(var(--c-parchment-deep) / 0.7);
}
.pdx-review-avatar {
  flex: none;
  display: inline-grid;
  place-items: center;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 9999px;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 1.1rem;
  color: rgb(var(--c-gold-dark));
  background: rgb(var(--c-gold) / 0.1);
  border: 1px solid rgb(var(--c-gold) / 0.32);
}
html[lang='fa'] .pdx-review-avatar { font-family: inherit; font-weight: 700; font-size: 0.95rem; }
.pdx-review-name { font-size: 0.88rem; font-weight: 500; color: rgb(var(--c-ink)); }
.pdx-review-role { margin-block-start: 0.12rem; font-size: 0.76rem; font-weight: 300; color: rgb(var(--c-ink-muted)); }

/* ── Specifications ────────────────────────────────────────────────────────── */
.pdx-specs {
  border: 1px solid rgb(var(--c-parchment-deep));
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--pdx-shadow);
}
.pdx-spec-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.25rem;
  padding: 1rem 1.5rem;
}
@media (min-width: 640px) {
  .pdx-spec-row { grid-template-columns: 1fr 2fr; gap: 1.5rem; align-items: center; }
}
.pdx-spec-row + .pdx-spec-row { border-block-start: 1px solid rgb(var(--c-parchment-deep) / 0.7); }
.pdx-spec-row:nth-child(odd) { background: rgb(var(--c-gold) / 0.04); }
.pdx-spec-row dt { font-size: 11px; text-transform: uppercase; letter-spacing: 0.16em; font-weight: 400; color: rgb(var(--c-gold-dark)); }
.pdx-spec-row dd { font-size: 0.95rem; font-weight: 300; color: rgb(var(--c-ink)); }

/* ── CTA band ──────────────────────────────────────────────────────────────── */
.pdx-cta {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  border-radius: 20px;
  padding: 3.5rem 2.5rem;
  background: rgb(var(--c-ink));
  border: 1px solid rgb(var(--c-gold) / 0.25);
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.2), 0 4px 12px rgba(0, 0, 0, 0.1);
}
@media (min-width: 768px) { .pdx-cta { padding: 5rem 4rem; } }
.pdx-cta-grid {
  position: absolute;
  inset: 0;
  z-index: -1;
  background-image:
    repeating-linear-gradient(90deg, transparent 0 79px, rgb(var(--c-gold) / 0.06) 79px 80px),
    radial-gradient(60% 120% at 100% 0%, rgb(var(--c-gold) / 0.12), transparent 60%);
  -webkit-mask-image: linear-gradient(180deg, #000, transparent 120%);
          mask-image: linear-gradient(180deg, #000, transparent 120%);
}
.pdx-cta-eyebrow { color: rgb(var(--c-gold-light)); }
.pdx-cta-title { color: rgb(var(--c-parchment-light)); }
.pdx-cta-note { color: rgb(var(--c-parchment-light) / 0.7); }
.pdx-cta-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  padding-block: 0.95rem;
  padding-inline: 1.75rem;
  border-radius: 8px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.24em;
  font-weight: 400;
  background: rgb(var(--c-gold));
  color: #1a1714;
  box-shadow: 0 4px 16px rgba(0,0,0,0.16), inset 0 1px 0 rgba(255,255,255,0.15);
  transition: background-color 300ms ease, transform 380ms cubic-bezier(0.34, 1.28, 0.64, 1), box-shadow 300ms ease;
}
.pdx-cta-btn:hover { background: rgb(var(--c-gold-light)); transform: translateY(-3px); box-shadow: 0 10px 26px rgba(0,0,0,0.22); }
.pdx-cta-btn:active { transform: translateY(0); transition-duration: 120ms; }
.pdx-cta-meta {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 11px;
  font-weight: 300;
  letter-spacing: 0.04em;
  color: rgb(var(--c-parchment-light) / 0.65);
}
.pdx-cta-dot { width: 7px; height: 7px; border-radius: 9999px; background: rgb(var(--c-gold)); }

/* ── Fullscreen overlay ────────────────────────────────────────────────────── */
.pdx-fs-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(12, 10, 8, 0.88);
  -webkit-backdrop-filter: blur(18px) saturate(1.2);
  backdrop-filter: blur(18px) saturate(1.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.pdx-fs-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  border: 1px solid rgba(237, 192, 113, 0.4);
  background: rgba(255, 255, 255, 0.06);
  color: #f2ede4;
  cursor: pointer;
  transition: background-color 200ms ease, transform 260ms cubic-bezier(0.22, 1, 0.36, 1);
}
.pdx-fs-close:hover { background: rgba(237, 192, 113, 0.15); transform: scale(1.1); }
.pdx-fs-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
  max-width: 640px;
}
.pdx-fs-art {
  width: 100%;
  max-width: 540px;
  height: auto;
  max-height: 60vh;
}
.pdx-fs-thumbs {
  display: flex;
  gap: 0.6rem;
  justify-content: center;
}
.pdx-fs-thumb-btn {
  width: 4rem;
  height: 3rem;
}
.pdx-fs-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  color: rgba(237, 192, 113, 0.75);
}

/* Fullscreen enter/leave */
.pdx-fs-enter-active { transition: opacity 300ms ease; }
.pdx-fs-leave-active { transition: opacity 200ms ease; }
.pdx-fs-enter-from,
.pdx-fs-leave-to { opacity: 0; }

/* ── Persian — drop Latin tracking / uppercase ─────────────────────────────── */
html[lang='fa'] .pdx-badge,
html[lang='fa'] .pdx-btn-primary,
html[lang='fa'] .pdx-btn-ghost,
html[lang='fa'] .pdx-cta-btn,
html[lang='fa'] .pdx-render-cat,
html[lang='fa'] .pdx-trial-label,
html[lang='fa'] .pdx-spec-row dt,
html[lang='fa'] .pdx-slide-label,
html[lang='fa'] .pdx-fs-label { letter-spacing: 0; text-transform: none; }

@media (prefers-reduced-motion: reduce) {
  .pdx-slide,
  .pdx-thumb,
  .pdx-carousel-btn,
  .pdx-carousel-dot,
  .pdx-review,
  .pdx-btn-primary,
  .pdx-cta-btn,
  .pdx-cert,
  .pdx-eco { transition: none; }
  .pdx-btn-ghost { transition: color 160ms ease, border-color 160ms ease; }
  .pdx-btn-ghost::before { transition: opacity 200ms ease; transform: scaleX(1); opacity: 0; }
  .pdx-btn-ghost:hover::before { opacity: 1; }
  .pdx-btn-ghost::after,
  .pdx-btn-ghost:hover::after { transition: none; transform: none; }
  .rv-next-enter-active, .rv-next-leave-active,
  .rv-prev-enter-active, .rv-prev-leave-active { transition: opacity 160ms ease; }
  .rv-next-enter-from, .rv-prev-enter-from { transform: none; }
  .rv-next-leave-to, .rv-prev-leave-to { transform: none; }
  .pdx-slide { opacity: 0; }
  .pdx-slide.is-active { opacity: 1; }
  .pdx-cert:hover,
  .pdx-eco:hover,
  .pdx-review:hover,
  .pdx-btn-primary:hover,
  .pdx-cta-btn:hover,
  .pdx-carousel-btn:hover { transform: none; }
  .pdx-fs-enter-active,
  .pdx-fs-leave-active { transition: none; }
}
</style>
