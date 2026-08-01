<script setup>
defineProps({
  size: { type: [Number, String], default: 48 },
  tone: { type: String, default: 'gold' }, // 'gold' | 'parchment' | 'mono'
})
</script>

<template>
  <!--
    "N-brain" emblem — a neural/circuit brain silhouette fused with a
    calligraphic "N" letterform, capped by a thin sweeping arc. This is a
    redrawn interpretation of the supplied artwork in clean vector form so it
    scales cleanly for the navbar, footer and favicon alike.
  -->
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 200 200"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Neuro Tech"
    :class="['brand-mark', `is-${tone}`]"
  >
    <!-- Sweeping arc -->
    <path d="M 38 42 C 58 4 142 4 168 50" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" opacity="0.9" />

    <!-- Brain lobe (left) with circuit / neural pathway pattern -->
    <g stroke="currentColor" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M70 46
               c-16 0-22 12-24 18
               c-12 2-20 12-20 24
               c0 9 4 16 10 20
               c-4 6-6 13-6 19
               c0 16 12 28 30 30
               c4 8 13 13 24 13
               c8 0 15-3 20-9
               l0-104
               c-5-7-13-11-22-11
               c-5 0-9 1-12 4 z" />
      <!-- circuit traces -->
      <path d="M58 64 h14 v12 h12 M64 76 v14 M84 70 l10 10 v12 M50 92 h16 l8 8 h14 M46 112 h12 l6 -6 M58 128 h18 v-10 M70 146 h12 v10 h10 M86 158 l8 -8 h10" />
      <circle cx="58" cy="64" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="84" cy="70" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="94" cy="92" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="50" cy="92" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="88" cy="100" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="46" cy="112" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="58" cy="128" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="76" cy="138" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="92" cy="146" r="2.6" fill="currentColor" stroke="none" />
      <circle cx="104" cy="158" r="2.6" fill="currentColor" stroke="none" />
    </g>

    <!-- Calligraphic "N" letterform, fused to the right of the brain -->
    <g fill="currentColor">
      <path d="M104 54
               L120 54
               L162 134
               L162 54
               L176 54
               L176 168
               L160 168
               L118 88
               L118 168
               L104 168 Z" opacity="0.96" />
    </g>
  </svg>
</template>

<style scoped>
.brand-mark.is-gold { color: #B8922A; }
/* Theme-aware so it always contrasts the inverting `bg-ink` surface. */
.brand-mark.is-parchment { color: var(--parchment-light); }
.brand-mark.is-mono { color: currentColor; }
</style>
