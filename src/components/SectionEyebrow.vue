<script setup>
defineProps({
  text: { type: String, required: true },
  align: { type: String, default: 'center' },
})
</script>

<template>
  <div
    :class="[
      'flex items-center gap-4',
      align === 'center' ? 'justify-center' : 'justify-start',
    ]"
  >
    <span class="h-px w-8 bg-gold/60"></span>
    <span class="text-[11px] uppercase tracking-[0.3em] text-ink-muted font-light">{{ text }}</span>
    <span class="h-px w-8 bg-gold/60"></span>
  </div>
</template>
