<script setup>
import { brandLogoUrl } from '../data/brandAssets.js'

defineProps({
  size: { type: [Number, String], default: 48 },
  tone: { type: String, default: 'gold' }, // Retained for API compatibility.
})
</script>

<template>
  <img
    :src="brandLogoUrl"
    alt="Neuro Tech"
    :width="size"
    :height="size"
    class="brand-mark"
  />
</template>

<style scoped>
.brand-mark {
  display: block;
  object-fit: contain;
}
</style>
