<script setup>
import { computed } from 'vue'
import { productIcon } from '../data/productIcons.js'

const props = defineProps({ name: { type: String, default: 'certificate' } })
const icon = computed(() => productIcon(props.name))
</script>

<template>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path v-for="(path, index) in icon.paths" :key="index" :d="path" />
  </svg>
</template>
