<script setup>
defineProps({
  title: { type: String, default: '' },
  hover: { type: Boolean, default: false },
})
</script>

<template>
  <article
    :class="[
      'bg-parchment border border-parchment-deep/70 rounded-lg p-8 md:p-10 shadow-card transition-all duration-300',
      hover ? 'hover:-translate-y-0.5 hover:shadow-card-hover hover:border-gold/50' : ''
    ]"
  >
    <h3 v-if="title" class="font-serif font-light text-xl text-ink mb-4">{{ title }}</h3>
    <slot />
  </article>
</template>
