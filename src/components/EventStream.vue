<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { eventMedia } from '../utils/eventMedia.js'
const props = defineProps({ url: { type: String, default: '' }, title: { type: String, default: '' } })
const { locale } = useI18n()
const media = computed(() => eventMedia(props.url)), video = ref(null), failed = ref(false)
let player, generation = 0
const dispose = () => { player?.destroy(); player = null }
watch(() => props.url, async () => {
  const request = ++generation; dispose(); failed.value = false
  await nextTick()
  const element = video.value, source = media.value
  if (!element || source?.type !== 'video') return
  if (/\.m3u8(?:[?#]|$)/i.test(source.src) && !element.canPlayType('application/vnd.apple.mpegurl')) {
    try {
      const { default: Hls } = await import('hls.js')
      if (request !== generation) return
      if (!Hls.isSupported()) { failed.value = true; return }
      player = new Hls()
      player.on(Hls.Events.ERROR, (_, data) => { if (data.fatal) failed.value = true })
      player.loadSource(source.src); player.attachMedia(element)
    } catch { if (request === generation) failed.value = true }
  } else element.src = source.src
}, { immediate: true, flush: 'post' })
onUnmounted(() => { generation++; dispose() })
</script>
<template>
  <div class="relative h-full w-full">
    <iframe v-if="media?.type==='iframe'" :src="media.src" :title="title || 'Event video'" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin" class="h-full w-full"></iframe>
    <video v-else-if="media?.type==='video'" ref="video" controls playsinline preload="metadata" :aria-label="title" class="h-full w-full" @error="failed=true"></video>
    <p v-if="failed || !media" role="status" class="absolute bottom-0 inset-x-0 bg-black/80 p-3 text-center text-sm text-white">{{ locale==='fa'?'پخش در دسترس نیست؛ اتصال یا آدرس ویدئو را بررسی کنید.':'Playback unavailable. Check the connection or video address.' }}</p>
  </div>
</template>
