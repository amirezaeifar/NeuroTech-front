<script setup>
defineProps({
  size: { type: [Number, String], default: 48 },
  tone: { type: String, default: 'gold' }, // 'gold' | 'parchment' | 'mono'
})
</script>

<template>
  <!-- Brand mark -->
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 200 200"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Neuro Tech"
    :class="['brand-mark', `is-${tone}`]"
  >
    <image href="/favicon-new.png" width="200" height="200" preserveAspectRatio="xMidYMid meet" />
  </svg>
</template>

<style scoped>
.brand-mark.is-gold { color: #B8922A; }
/* Theme-aware so it always contrasts the inverting `bg-ink` surface. */
.brand-mark.is-parchment { color: var(--parchment-light); }
.brand-mark.is-mono { color: currentColor; }
</style>
