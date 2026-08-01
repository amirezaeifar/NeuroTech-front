<script setup>
defineProps({
  diamond: { type: Boolean, default: false },
})
</script>

<template>
  <div class="flex items-center justify-center gap-5 my-12">
    <span class="h-px flex-1 bg-gold/40"></span>
    <span v-if="diamond" class="text-gold text-[10px] tracking-widest">◆</span>
    <span class="h-px flex-1 bg-gold/40"></span>
  </div>
</template>
