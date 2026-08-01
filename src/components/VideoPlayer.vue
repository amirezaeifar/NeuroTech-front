<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  live: { type: Boolean, default: false },
  viewers: { type: [String, Number], default: '' },
  poster: { type: String, default: '' },
  duration: { type: String, default: '12:48' },
  elapsed: { type: String, default: '04:12' },
  /** Embeddable iframe URL (e.g. a YouTube embed). When set, the play button
   *  swaps the luxe poster for the real responsive video. Empty = mock only. */
  embedUrl: { type: String, default: '' },
  /** Notice shown over the poster while the embed is a replaceable placeholder. */
  notice: { type: String, default: '' },
})

const hasEmbed = computed(() => !!props.embedUrl)

// Poster-first: the real iframe is only mounted once the viewer hits play, so
// the page stays light and the design leads. Switching lesson (embedUrl change)
// returns to the poster.
const activated = ref(false)
const iframeSrc = computed(() =>
  props.embedUrl + (props.embedUrl.includes('?') ? '&' : '?') + 'autoplay=1')
watch(() => props.embedUrl, () => { activated.value = false; playing.value = false })

const playing = ref(false)
const onPlay = () => {
  if (hasEmbed.value) { activated.value = true; playing.value = true }
  else playing.value = !playing.value
}
const togglePlay = () => { if (!activated.value) onPlay() }
</script>

<template>
  <div class="video-player rounded-lg overflow-hidden border border-parchment-deep/70 shadow-card bg-ink">
    <!-- Stage -->
    <div class="relative aspect-video w-full select-none">
      <!-- Real responsive embed — mounted only after the viewer hits play. -->
      <iframe
        v-if="activated && hasEmbed"
        class="absolute inset-0 w-full h-full"
        :src="iframeSrc"
        :title="title || subtitle || 'Course video'"
        frameborder="0"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
      ></iframe>

      <!-- Luxe poster + mock controls. Hidden once the real embed is playing. -->
      <template v-else>
      <!-- Backdrop -->
      <div
        class="absolute inset-0"
        :style="poster
          ? { backgroundImage: `url(${poster})`, backgroundSize: 'cover', backgroundPosition: 'center' }
          : { background: 'radial-gradient(120% 120% at 50% 20%, #2a2620 0%, #14110d 60%, #0b0907 100%)' }"
      ></div>
      <!-- Faint grid texture -->
      <div class="absolute inset-0 opacity-[0.06]"
           style="background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px); background-size: 44px 44px;"></div>
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-black/30"></div>

      <!-- Top bar -->
      <div class="absolute top-0 inset-x-0 flex items-start justify-between gap-4 p-4 md:p-5">
        <div class="min-w-0">
          <p v-if="title" class="text-parchment-light text-sm md:text-base font-light leading-snug truncate">{{ title }}</p>
          <p v-if="subtitle" class="mt-0.5 text-parchment-light/60 text-[11px] uppercase tracking-[0.2em] font-light truncate">{{ subtitle }}</p>
        </div>
        <div v-if="live" class="shrink-0 flex items-center gap-3">
          <span class="inline-flex items-center gap-1.5 bg-red-600/90 text-white text-[10px] uppercase tracking-[0.25em] font-medium px-2.5 py-1 rounded">
            <span class="w-1.5 h-1.5 rounded-full bg-white animate-pulse-dot"></span> Live
          </span>
          <span v-if="viewers" class="inline-flex items-center gap-1.5 bg-black/40 backdrop-blur-sm text-parchment-light/90 text-[10px] tracking-[0.15em] px-2.5 py-1 rounded">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/></svg>
            {{ viewers }}
          </span>
        </div>
      </div>

      <!-- Center play -->
      <button
        type="button"
        @click="onPlay"
        class="absolute inset-0 m-auto w-16 h-16 md:w-20 md:h-20 rounded-full bg-gold/90 hover:bg-gold text-ink flex items-center justify-center shadow-soft transition-all hover:scale-105"
        :aria-label="hasEmbed ? 'Play video' : (playing ? 'Pause' : 'Play')"
      >
        <svg v-if="hasEmbed || !playing" width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        <svg v-else width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
      </button>

      <!-- Replaceable-placeholder notice (sits just under the play button). -->
      <p
        v-if="notice"
        class="absolute inset-x-0 bottom-[22%] mx-auto max-w-[80%] text-center text-[11px] text-parchment-light/70 font-light leading-relaxed"
      >{{ notice }}</p>

      <!-- Quality / time badges -->
      <span class="absolute top-1/2 right-4 -translate-y-1/2 hidden md:inline-flex items-center gap-1.5 bg-black/40 text-parchment-light/80 text-[10px] tracking-[0.2em] uppercase px-2 py-1 rounded">
        1080p · HD
      </span>

      <!-- Control bar -->
      <div class="absolute bottom-0 inset-x-0 px-4 md:px-5 pb-4 pt-8 bg-gradient-to-t from-black/80 to-transparent">
        <!-- Scrubber -->
        <div class="group h-1 w-full bg-white/20 rounded-full cursor-pointer">
          <div class="relative h-full rounded-full bg-gold" :style="{ width: live ? '100%' : '34%' }">
            <span v-if="!live" class="absolute -right-1.5 -top-1 w-3 h-3 rounded-full bg-gold shadow"></span>
          </div>
        </div>
        <div class="mt-2.5 flex items-center justify-between text-parchment-light/85">
          <div class="flex items-center gap-4">
            <button type="button" @click="onPlay" :aria-label="hasEmbed ? 'Play video' : (playing ? 'Pause' : 'Play')" class="hover:text-gold-light transition-colors">
              <svg v-if="hasEmbed || !playing" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
            </button>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="hover:text-gold-light transition-colors cursor-pointer"><path d="M11 5 6 9H2v6h4l5 4zM15.5 8.5a5 5 0 0 1 0 7M19 5a9 9 0 0 1 0 14" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span class="text-[11px] tracking-[0.1em] font-light tabular-nums">
              <template v-if="live"><span class="text-red-400">●</span> Live</template>
              <template v-else>{{ elapsed }} / {{ duration }}</template>
            </span>
          </div>
          <div class="flex items-center gap-4">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="hover:text-gold-light transition-colors cursor-pointer"><path d="M21 15v4a2 2 0 0 1-2 2h-4M3 9V5a2 2 0 0 1 2-2h4" stroke-linecap="round"/><circle cx="12" cy="12" r="3"/></svg>
            <span class="text-[11px] tracking-[0.1em] font-light cursor-pointer hover:text-gold-light transition-colors">CC</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="hover:text-gold-light transition-colors cursor-pointer"><path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M21 16v3a2 2 0 0 1-2 2h-3M3 16v3a2 2 0 0 0 2 2h3" stroke-linecap="round"/></svg>
          </div>
        </div>
      </div>
      </template>
    </div>
  </div>
</template>
