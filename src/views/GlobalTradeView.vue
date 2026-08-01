<script setup>
import { useI18n } from 'vue-i18n'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useReveal } from '../composables/useReveal.js'
import {
  documents,
  marketReport,
  documentationOverview,
  documentationDisclaimer,
} from '../data/tradeReports.js'

const { t, tm } = useI18n()
const regions = tm('globalTrade.regions')
const become = tm('globalTrade.become.items')
const importItems = tm('globalTrade.importExport.import.items')
const exportItems = tm('globalTrade.importExport.export.items')

// The outcome statement of each reference document doubles as its card preview.
const docOutcome = (d) => (d.groups.find((g) => g.label === 'Outcome') || {}).text || ''

useReveal()
</script>

<template>
  <div class="trade-page">
    <!-- ───────────────────────── Hero ───────────────────────── -->
    <section class="trade-hero relative overflow-hidden py-28 md:py-40 text-center">
      <div class="trade-hero-grid pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div class="relative max-w-5xl mx-auto px-8">
        <div class="flex items-center justify-center gap-4">
          <span class="trade-hero-rule h-px w-10 bg-gold/60"></span>
          <span class="trade-hero-eyebrow text-[11px] uppercase tracking-[0.4em] text-gold/80 font-light">{{ t('globalTrade.hero.eyebrow') }}</span>
          <span class="trade-hero-rule h-px w-10 bg-gold/60"></span>
        </div>
        <h1 class="trade-hero-title font-serif font-light text-5xl md:text-7xl text-[#F2EDE4] tracking-wide mt-8 leading-[1.05]">
          {{ t('globalTrade.hero.title') }}
        </h1>
      </div>
    </section>

    <!-- ──────────────── Intro statement (generous top breathing room) ──────────────── -->
    <section class="bg-parchment-light">
      <div class="reveal max-w-3xl mx-auto px-8 mt-20 md:mt-28 text-center">
        <p class="font-serif italic font-light text-2xl md:text-[2rem] text-ink-soft leading-relaxed">
          {{ t('globalTrade.intro') }}
        </p>
        <div class="mx-auto mt-10 flex items-center justify-center gap-3 text-gold">
          <span class="h-px w-12 bg-gold/40"></span>
          <span class="text-xs">&#9670;</span>
          <span class="h-px w-12 bg-gold/40"></span>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Regions ───────────────────────── -->
    <section class="py-20 md:py-32 bg-parchment-light">
      <div class="max-w-6xl mx-auto px-8">
        <div class="reveal text-center mb-16">
          <SectionEyebrow :text="t('globalTrade.regionsTitle')" />
        </div>

        <div class="grid md:grid-cols-2 gap-6 lg:gap-8">
          <article
            v-for="(r, i) in regions" :key="r.name"
            class="reveal group relative overflow-hidden rounded-xl border border-parchment-deep/70 bg-parchment p-9 md:p-11 lux-card"
            :style="{ transitionDelay: `${i * 80}ms` }"
          >
            <h3 class="relative font-serif font-light text-2xl text-ink leading-snug group-hover:text-gold-dark transition-colors">{{ r.name }}</h3>
            <div class="relative h-px w-10 bg-gold/50 my-5"></div>
            <div class="relative flex flex-wrap gap-2 mb-6">
              <span v-for="(c, j) in r.countries" :key="j"
                    class="text-[11px] px-3 py-1 rounded-full border border-parchment-deep text-ink-soft font-light tracking-wide">
                {{ c }}
              </span>
            </div>
            <p class="relative text-sm text-ink-soft font-light leading-relaxed">{{ r.note }}</p>
          </article>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Import & Export ───────────────────────── -->
    <section class="relative overflow-hidden py-24 md:py-32 bg-ink">
      <div class="trade-ie-glow pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div class="relative max-w-6xl mx-auto px-8">
        <div class="reveal text-center max-w-2xl mx-auto">
          <p class="text-[11px] uppercase tracking-[0.4em] text-gold/80 font-light mb-6">
            {{ t('globalTrade.importExport.eyebrow') }}
          </p>
          <h2 class="font-serif font-light text-4xl md:text-5xl text-parchment-light tracking-wide">
            {{ t('globalTrade.importExport.title') }}
          </h2>
          <p class="mt-6 text-sm text-parchment-deep/80 font-light leading-relaxed">
            {{ t('globalTrade.importExport.intro') }}
          </p>
        </div>

        <div class="mt-16 grid md:grid-cols-2 gap-6 lg:gap-8">
          <div class="reveal rounded-xl border border-gold/25 bg-white/[0.02] p-10 md:p-12 transition-colors hover:border-gold/45">
            <div class="flex items-center gap-3 mb-5">
              <span class="grid place-items-center w-10 h-10 rounded-full border border-gold/40 text-gold">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M12 3v13m0 0 5-5m-5 5-5-5M5 21h14" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
              <h3 class="font-serif font-light text-2xl text-parchment-light">{{ t('globalTrade.importExport.import.title') }}</h3>
            </div>
            <p class="text-sm text-parchment-deep/80 font-light leading-relaxed mb-6">{{ t('globalTrade.importExport.import.desc') }}</p>
            <ul class="space-y-3.5">
              <li v-for="(item, i) in importItems" :key="i" class="flex items-start gap-3 text-sm text-parchment-dark/90 font-light leading-relaxed">
                <span class="text-gold mt-1 text-[10px]">◆</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>
          <div class="reveal rounded-xl border border-gold/25 bg-white/[0.02] p-10 md:p-12 transition-colors hover:border-gold/45" style="transition-delay: 100ms">
            <div class="flex items-center gap-3 mb-5">
              <span class="grid place-items-center w-10 h-10 rounded-full border border-gold/40 text-gold">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M12 21V8m0 0 5 5m-5-5-5 5M5 3h14" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
              <h3 class="font-serif font-light text-2xl text-parchment-light">{{ t('globalTrade.importExport.export.title') }}</h3>
            </div>
            <p class="text-sm text-parchment-deep/80 font-light leading-relaxed mb-6">{{ t('globalTrade.importExport.export.desc') }}</p>
            <ul class="space-y-3.5">
              <li v-for="(item, i) in exportItems" :key="i" class="flex items-start gap-3 text-sm text-parchment-dark/90 font-light leading-relaxed">
                <span class="text-gold mt-1 text-[10px]">◆</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ──────────── Corporate Documentation & Technical References ──────────── -->
    <section class="py-20 md:py-32 bg-parchment-light border-t border-parchment-deep">
      <div class="max-w-6xl mx-auto px-8">
        <div class="reveal text-center max-w-3xl mx-auto">
          <p class="text-[11px] uppercase tracking-[0.4em] text-gold/80 font-light mb-6">{{ t('globalTrade.documentation.eyebrow') }}</p>
          <h2 class="font-serif font-light text-4xl md:text-5xl text-ink tracking-wide">{{ t('globalTrade.documentation.title') }}</h2>
          <p class="mt-6 text-sm text-ink-soft font-light leading-relaxed">{{ t('globalTrade.documentation.subtitle') }}</p>
          <p class="mt-5 text-sm text-ink-soft font-light leading-relaxed">{{ documentationOverview }}</p>
        </div>

        <div class="mt-16 grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          <router-link
            v-for="(d, i) in documents"
            :key="d.id"
            :to="`/global-trade/document/${d.id}`"
            class="reveal group block"
            :style="{ transitionDelay: `${(i % 3) * 70}ms` }"
          >
            <article class="bg-parchment-light border border-parchment-deep/70 rounded-xl p-8 md:p-9 h-full lux-card group-hover:border-gold/50 group-hover:-translate-y-1 flex flex-col">
              <!-- 1 · Technology partner — strongest non-title emphasis -->
              <span class="self-start text-[10px] uppercase tracking-[0.25em] font-medium px-2.5 py-1 rounded-full border text-gold-dark border-gold/50">{{ d.partner }}</span>
              <!-- 2 · Document ID — monospace reference -->
              <p class="mt-4 text-[11px] tracking-[0.12em] text-ink-hint font-mono">{{ d.id }}</p>
              <!-- 3 · Documentation type -->
              <p class="mt-3 text-[11px] uppercase tracking-[0.25em] text-ink-muted font-light">{{ d.docType }}</p>
              <!-- 4 · Project title -->
              <h3 class="font-serif font-light text-xl text-ink mt-2 mb-1.5 leading-snug group-hover:text-gold-dark transition-colors">{{ d.title }}</h3>
              <!-- 5 · Category -->
              <p class="text-xs text-ink-muted font-light uppercase tracking-[0.15em]">{{ d.category }}</p>
              <!-- 6 · Summary -->
              <p class="mt-4 text-sm text-ink-soft font-light leading-relaxed flex-1">{{ docOutcome(d) }}</p>
              <!-- 7 · View document -->
              <span class="mt-6 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink group-hover:text-gold-dark transition-colors border-b border-gold/40 pb-1 self-start">
                {{ t('globalTrade.documentation.viewDocument') }} <span class="dir-arrow" aria-hidden="true"></span>
              </span>
            </article>
          </router-link>
        </div>

        <p class="reveal mt-14 max-w-3xl mx-auto text-center text-[12px] text-ink-hint font-light leading-relaxed italic">
          {{ documentationDisclaimer }}
        </p>
      </div>
    </section>

    <!-- ───────────────────── Market Intelligence Documentation ───────────────── -->
    <section class="relative overflow-hidden py-24 md:py-32 bg-ink">
      <div class="trade-ie-glow pointer-events-none absolute inset-0" aria-hidden="true"></div>
      <div class="relative max-w-5xl mx-auto px-8">
        <div class="reveal text-center max-w-2xl mx-auto">
          <p class="text-[11px] uppercase tracking-[0.4em] text-gold/80 font-light mb-6">{{ t('globalTrade.marketReport.eyebrow') }}</p>
          <h2 class="font-serif font-light text-4xl md:text-5xl text-parchment-light tracking-wide">{{ marketReport.title }}</h2>
          <p class="mt-5 text-[12px] uppercase tracking-[0.25em] text-gold-light/70 font-light">
            {{ t('globalTrade.marketReport.reportingPeriodLabel') }} · {{ marketReport.reportingPeriod }}
          </p>
        </div>

        <div class="mt-16 grid md:grid-cols-3 gap-6 lg:gap-8">
          <div
            v-for="(g, i) in marketReport.groups"
            :key="g.label"
            class="reveal rounded-xl border border-gold/25 bg-white/[0.02] p-8 md:p-9 transition-colors hover:border-gold/45"
            :style="{ transitionDelay: `${i * 90}ms` }"
          >
            <h3 class="font-serif font-light text-xl text-parchment-light">{{ g.label }}</h3>
            <div class="h-px w-8 bg-gold/40 my-5"></div>
            <ul class="space-y-3">
              <li v-for="(item, k) in g.items" :key="k" class="flex items-start gap-3 text-sm text-parchment-dark/90 font-light leading-relaxed">
                <span class="text-gold mt-1 text-[10px]">◆</span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="reveal mt-12 max-w-3xl mx-auto rounded-xl border border-gold/25 bg-white/[0.03] p-9 md:p-11 text-center">
          <p class="text-[11px] uppercase tracking-[0.3em] text-gold/80 font-light mb-4">{{ t('globalTrade.marketReport.outlookLabel') }}</p>
          <p class="font-serif italic font-light text-xl md:text-2xl text-parchment-light/90 leading-relaxed">{{ marketReport.marketOutlook }}</p>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Become a representative ─────────────────────────
         Premium dark editorial panel: a deep-charcoal slab with a soft gold
         aura, a glassmorphic checklist grid, and a high-contrast CTA. -->
    <section class="py-20 md:py-32 bg-parchment">
      <div class="max-w-6xl mx-auto px-8">
        <div class="become-panel reveal relative overflow-hidden rounded-[1.75rem]">
          <!-- Ambient layers -->
          <div class="become-aura pointer-events-none absolute inset-0" aria-hidden="true"></div>
          <div class="become-grid pointer-events-none absolute inset-0" aria-hidden="true"></div>
          <div class="become-ring pointer-events-none absolute -right-24 -top-24 w-80 h-80 rounded-full" aria-hidden="true"></div>

          <div class="relative grid lg:grid-cols-12 gap-x-12 gap-y-12 p-10 md:p-16">
            <!-- Left: heading + invitation -->
            <div class="lg:col-span-5 flex flex-col">
              <span class="inline-flex items-center gap-2.5 text-[11px] uppercase tracking-[0.35em] text-gold-light/90 font-light mb-7">
                <span class="h-px w-8 bg-gold-light/60"></span>
                {{ t('globalTrade.become.eyebrow') }}
              </span>
              <h2 class="font-serif font-light text-4xl md:text-5xl text-[#F7F2E9] tracking-wide leading-[1.08]">
                {{ t('globalTrade.become.title') }}
              </h2>
              <p class="mt-5 font-serif italic font-light text-xl text-gold-light/80">
                {{ t('globalTrade.become.italic') }}
              </p>
              <p class="mt-6 text-sm text-[#D9D2C5]/70 font-light leading-relaxed max-w-sm">
                {{ t('globalTrade.become.lead') }}
              </p>

              <div class="mt-auto pt-10">
                <router-link to="/contact" class="become-cta group">
                  <span>{{ t('globalTrade.become.cta') }}</span>
                  <span class="become-cta-arrow dir-arrow" aria-hidden="true"></span>
                </router-link>
              </div>
            </div>

            <!-- Right: glassmorphic criteria grid -->
            <div class="lg:col-span-7 lg:ps-12 lg:border-s border-white/10">
              <p class="text-[11px] uppercase tracking-[0.3em] text-[#D9D2C5]/55 font-light mb-6">
                {{ t('globalTrade.become.criteriaTitle') }}
              </p>
              <div class="grid sm:grid-cols-2 gap-4">
                <div
                  v-for="(b, i) in become" :key="i"
                  class="become-tile group flex items-start gap-4 rounded-xl p-5"
                >
                  <span class="become-tile-num shrink-0 grid place-items-center w-9 h-9 rounded-lg font-serif text-sm">{{ String(i + 1).padStart(2, '0') }}</span>
                  <span class="text-sm text-[#E8E2D6]/90 font-light leading-relaxed pt-0.5">{{ b }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Hero band — deep charcoal in light mode. The dark-mode inversion to #F2EDE4
   (and the dark text that keeps it legible) lives in src/style.css
   (`html.dark .trade-hero …`). */
.trade-hero { background: #1A1714; transition: background-color 300ms ease; }
.trade-hero-grid {
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent 119px, rgba(244, 215, 145, 0.04) 119px, rgba(244, 215, 145, 0.04) 120px);
}
/* Soft amber light-pool behind the dark Import/Export band. */
.trade-ie-glow { background: radial-gradient(60% 80% at 50% 0%, rgba(237, 192, 113, 0.10), transparent 70%); }

/* ── Become-a-representative — premium dark editorial panel ─────────────────── */
.become-panel {
  background:
    linear-gradient(155deg, #2b2620 0%, #1a1714 55%, #100e0b 100%);
  border: 1px solid rgba(237, 192, 113, 0.18);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 40px 90px -40px rgba(0, 0, 0, 0.7);
}
/* Soft gold aura blooming from the upper-left. */
.become-aura {
  background: radial-gradient(70% 90% at 18% 0%, rgba(237, 192, 113, 0.16), transparent 60%);
}
/* Whisper-fine vertical hairlines for editorial texture. */
.become-grid {
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent 79px, rgba(244, 215, 145, 0.035) 79px, rgba(244, 215, 145, 0.035) 80px);
  -webkit-mask-image: linear-gradient(180deg, #000, transparent 85%);
          mask-image: linear-gradient(180deg, #000, transparent 85%);
}
/* Faint gold ring accent in the corner. */
.become-ring {
  border: 1px solid rgba(237, 192, 113, 0.12);
  background: radial-gradient(circle at center, transparent 58%, rgba(237, 192, 113, 0.06) 60%, transparent 72%);
}

/* Glassmorphic criteria tiles. */
.become-tile {
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
  -webkit-backdrop-filter: blur(6px);
          backdrop-filter: blur(6px);
  transition: background 280ms ease, border-color 280ms ease, transform 280ms ease;
}
.become-tile:hover {
  background: rgba(237, 192, 113, 0.06);
  border-color: rgba(237, 192, 113, 0.32);
  transform: translateY(-2px);
}
.become-tile-num {
  color: #EAC079;
  background: rgba(237, 192, 113, 0.10);
  border: 1px solid rgba(237, 192, 113, 0.28);
  transition: background 280ms ease, color 280ms ease;
}
.become-tile:hover .become-tile-num {
  background: rgba(237, 192, 113, 0.9);
  color: #14110d;
}

/* High-contrast gold CTA pill. */
.become-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.95rem 2.1rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #EAC079 0%, #C79A3E 100%);
  color: #14110d;
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  box-shadow: 0 16px 36px -16px rgba(237, 192, 113, 0.6);
  transition: box-shadow 280ms ease, transform 280ms ease, filter 280ms ease;
}
.become-cta:hover {
  filter: brightness(1.06);
  transform: translateY(-2px);
  box-shadow: 0 22px 48px -16px rgba(237, 192, 113, 0.72);
}
.become-cta-arrow { transition: transform 280ms ease; }
.become-cta:hover .become-cta-arrow { transform: translateX(4px); }
html[lang='fa'] .become-cta { letter-spacing: 0; font-family: 'YekanBakh', sans-serif; }
/* Native RTL: the arrow glyph itself swaps direction (.dir-arrow) — no scaleX
   mirroring. The hover nudge stays on the inline axis. */
html[dir='rtl'] .become-cta:hover .become-cta-arrow { transform: translateX(-4px); }
</style>
