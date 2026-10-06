<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFavorites } from '../composables/useFavorites.js'

const props = defineProps({ type: { type: String, required: true }, itemId: { type: String, required: true }, light: { type: Boolean, default: false } })
const { locale } = useI18n()
const { favorites, refresh, toggle } = useFavorites()
const active = computed(() => favorites.value.some((item) => item.item_type === props.type && item.item_id === props.itemId))
const busy = ref(false)
const error = ref('')
const label = computed(() => active.value
  ? (locale.value === 'fa' ? 'حذف از علاقه‌مندی‌ها' : 'Remove from favorites')
  : (locale.value === 'fa' ? 'افزودن به علاقه‌مندی‌ها' : 'Add to favorites'))

onMounted(() => { refresh().catch(() => {}) })
const click = async () => {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try { await toggle(props.type, props.itemId) }
  catch (problem) { error.value = problem.message }
  finally { busy.value = false }
}
</script>

<template>
  <span class="favorite-control">
    <button type="button" class="favorite-button" :class="{ 'is-active': active, 'is-light': light }" :disabled="busy" :aria-label="label" :aria-pressed="active" :title="label" @click.stop.prevent="click">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.6 4.9a5.5 5.5 0 0 0-7.8 0L12 5.7l-.8-.8a5.5 5.5 0 0 0-7.8 7.8L12 21.3l8.6-8.6a5.5 5.5 0 0 0 0-7.8Z" /></svg>
    </button>
    <span v-if="error" class="favorite-error" role="alert">{{ error }}</span>
  </span>
</template>

<style scoped>
.favorite-control { display: inline-flex; align-items: center; gap: .4rem; }
.favorite-button { display: grid; place-items: center; width: 2rem; height: 2rem; padding: .2rem; border: 0; border-radius: 0; color: rgb(var(--c-gold-dark)); background: transparent; box-shadow: none; transition: transform .22s ease, color .22s ease; }
.favorite-button:hover { transform: translateY(-1px); }
.favorite-button:focus-visible { outline: 2px solid rgb(var(--c-gold-dark)); outline-offset: 3px; }
.favorite-button:disabled { opacity: .6; cursor: wait; }
.favorite-button svg { width: 1.25rem; height: 1.25rem; fill: none; stroke: currentColor; stroke-width: 1.15; stroke-linecap: round; stroke-linejoin: round; transition: transform .22s ease, fill .22s ease; }
.favorite-button.is-active { color: #a63f4c; }
.favorite-button.is-light { color: #efd099; }
.favorite-button.is-light.is-active { color: #f3abb6; }
.favorite-button.is-active svg { fill: currentColor; fill-opacity: .16; stroke-width: 1.3; }
.favorite-error { max-width: 12rem; color: #a63f4c; font-size: .7rem; }
@media (prefers-reduced-motion: reduce) { .favorite-button, .favorite-button svg { transition: none; } }
</style>
