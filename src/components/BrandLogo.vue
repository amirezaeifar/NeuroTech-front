<script setup>
import logo from '../assets/logo.png'

defineProps({
  width: { type: [Number, String], default: 220 },
  height: { type: [Number, String], default: 60 },
  tone: { type: String, default: 'gold' }, // 'gold' | 'parchment'
})
</script>

<template>
  <!--
    The logo is ALWAYS rendered left-to-right, regardless of the document's
    dir attribute or locale. We force LTR at three levels:
      1. an outer wrapper div with direction: ltr / unicode-bidi: isolate
      2. the <svg> root with direction="ltr" unicode-bidi="embed"
      3. each <text> node with writing-mode="lr"
    The wordmark is always English (Cormorant Garamond + Inter) — no YekanBakh.
  -->
  <div
    class="brand-logo-wrap"
    style="direction: ltr; unicode-bidi: isolate; display: inline-flex; align-items: center; gap: 12px; line-height: 0;"
  >
    <img :src="logo" alt="" aria-hidden="true" :style="{ height: height + 'px', width: 'auto' }" />

    <svg
      :width="width"
      :height="height"
      viewBox="0 0 190 60"
      xmlns="http://www.w3.org/2000/svg"
      direction="ltr"
      unicode-bidi="embed"
      role="img"
      aria-label="Neuro Tech"
      :class="['brand-logo', tone === 'parchment' ? 'is-parchment' : 'is-gold']"
    >
      <!-- Wordmark -->
      <text
        x="4" y="33"
        writing-mode="lr"
        direction="ltr"
        font-family="'Cormorant Garamond', Georgia, serif"
        font-size="24"
        font-weight="300"
        fill="currentColor"
        letter-spacing="2"
      >Neuro Tech</text>
      <text
        x="5" y="48"
        writing-mode="lr"
        direction="ltr"
        font-family="'Inter', sans-serif"
        font-size="8"
        font-weight="300"
        :class="tone === 'parchment' ? 'brand-sub-parchment' : 'brand-sub-gold'"
        letter-spacing="4"
      >NEUROLOGY · CRAFTED</text>
      <line x1="5" y1="54" x2="178" y2="54" stroke="currentColor" stroke-width="0.4" opacity="0.35" />
    </svg>
  </div>
</template>

<style scoped>
/* Gold reads on any backdrop, so it stays a fixed metallic tone.
   The "parchment" tone is used on the footer, whose `bg-ink` surface inverts
   with the theme (dark in light mode, light in dark mode). Binding the wordmark
   to the theme-aware `--parchment-light` token makes it ALWAYS contrast that
   surface — no more white-on-white when the footer flips in dark mode. */
.brand-logo.is-gold { color: #B8922A; }
.brand-logo.is-parchment { color: var(--parchment-light); }

.brand-sub-parchment { fill: var(--parchment-deep); }
.brand-sub-gold { fill: var(--ink-muted); }

/* Hard guarantee: never inherit RTL or YekanBakh inside the logo */
.brand-logo-wrap,
.brand-logo,
.brand-logo text {
  direction: ltr !important;
  unicode-bidi: isolate !important;
  font-family: 'Cormorant Garamond', 'Inter', Georgia, serif !important;
}
</style>
