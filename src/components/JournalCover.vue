<script setup>
import { ref, watch } from 'vue'
import { resolveApiUrl } from '../api/client.js'
import JournalNeuralArt from './JournalNeuralArt.vue'
const props = defineProps({ post: { type: Object, required: true }, eager: Boolean })
const failed = ref(false)
watch(() => props.post.cover_url, () => { failed.value = false })
const cover = (url) => url?.startsWith('/api/') ? resolveApiUrl(url) : url
</script>

<template>
  <div class="journal-cover">
    <img v-if="post.cover_url && !failed" :src="cover(post.cover_url)" :alt="post.cover_alt || post.title" :loading="eager ? 'eager' : 'lazy'" :fetchpriority="eager ? 'high' : 'auto'" decoding="async" @error="failed = true">
    <template v-else>
      <JournalNeuralArt />
      <span class="journal-cover-mark" aria-hidden="true">NEUROTECH <span> / </span> JOURNAL</span>
    </template>
  </div>
</template>

<style scoped>
.journal-cover { position: relative; isolation: isolate; overflow: hidden; background: #1c1915; min-height: 220px; }
.journal-cover > img { width: 100%; height: 100%; position: absolute; inset: 0; object-fit: cover; transform: scale(var(--journal-image-scale, 1)); transition: transform 1.4s cubic-bezier(.16,1,.3,1); }
.journal-cover > .journal-neural-art { height: 100%; position: absolute; inset: 0; }
.journal-cover-mark { position: absolute; bottom: 24px; left: 28px; font: 9px Inter, sans-serif; letter-spacing: .22em; color: #e1d5bb; }
.journal-cover-mark span { color: #d4ae5a; padding: 0 8px; }
@media (prefers-reduced-motion: reduce) { .journal-cover > img { transition: none; } }
</style>
