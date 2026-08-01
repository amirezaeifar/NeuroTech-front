<script setup>
/**
 * CoursePlayer — an in-house LMS video player.
 *
 * Plays a course playlist through a fully custom, dark/gold/glass control layer.
 * The underlying playback engine is loaded lazily and kept entirely behind our
 * own UI: native controls are disabled, a transparent shield captures clicks,
 * and no source URLs or external branding are ever surfaced — lessons are
 * presented purely as internal learning resources.
 *
 * Features: autoplay (muted) on open, continuous auto-next, a playlist sidebar,
 * seekable progress bar, prev/next, playback-speed control, fullscreen, and
 * resume-from-where-you-left-off via localStorage.
 *
 * Two-way bound to the parent's current-lesson number (1-based) so the syllabus
 * and progress stay in sync.
 */
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  /** [{ title, id }] in playlist order. `id` is an internal resource id. */
  lessons: { type: Array, required: true },
  /** Stable key for resume memory, e.g. "course-3". */
  courseKey: { type: String, required: true },
  /** Secondary line (course · instructor). */
  subtitle: { type: String, default: '' },
  /** 1-based current lesson number (v-model). */
  modelValue: { type: Number, default: 1 },
})
const emit = defineEmits(['update:modelValue'])

const RATES = [1, 1.25, 1.5]
const STORE_KEY = computed(() => `coursePlayer:${props.courseKey}`)

const root = ref(null)
const ytHost = ref(null)
let player = null
let poll = null

const currentIndex = ref(Math.max(0, (props.modelValue || 1) - 1))
const isPlaying = ref(false)
const muted = ref(true)
const currentTime = ref(0)
const duration = ref(0)
const rate = ref(1)
const isFullscreen = ref(false)
const speedOpen = ref(false)
const ready = ref(false)
const loading = ref(true)
const errored = ref(false)

const currentLesson = computed(() => props.lessons[currentIndex.value] || {})
const currentTitle = computed(() =>
  currentLesson.value.title || `Lesson ${currentIndex.value + 1}`)
const pct = computed(() =>
  duration.value ? `${Math.min(100, (currentTime.value / duration.value) * 100)}%` : '0%')
const canPrev = computed(() => currentIndex.value > 0)
const canNext = computed(() => currentIndex.value < props.lessons.length - 1)

const fmt = (s) => {
  if (!s || !isFinite(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${String(sec).padStart(2, '0')}`
}

// ── Lazy engine loader (singleton) ───────────────────────────────────────────
let enginePromise = null
function loadEngine() {
  if (typeof window === 'undefined') return Promise.reject()
  if (window.YT && window.YT.Player) return Promise.resolve(window.YT)
  if (enginePromise) return enginePromise
  enginePromise = new Promise((resolve) => {
    const prev = window.onYouTubeIframeAPIReady
    window.onYouTubeIframeAPIReady = () => { if (prev) prev(); resolve(window.YT) }
    const tag = document.createElement('script')
    tag.src = 'https://www.youtube.com/iframe_api'
    tag.async = true
    document.head.appendChild(tag)
  })
  return enginePromise
}

// ── Resume memory ─────────────────────────────────────────────────────────────
function readResume() {
  try {
    const raw = localStorage.getItem(STORE_KEY.value)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}
function saveResume() {
  try {
    localStorage.setItem(STORE_KEY.value, JSON.stringify({
      lesson: currentIndex.value,
      t: Math.floor(currentTime.value),
    }))
  } catch { /* storage unavailable — non-fatal */ }
}

// ── Playback control ──────────────────────────────────────────────────────────
function startPoll() {
  stopPoll()
  poll = window.setInterval(() => {
    if (!player || !player.getCurrentTime) return
    currentTime.value = player.getCurrentTime() || 0
    duration.value = player.getDuration() || 0
    saveResume()
  }, 500)
}
function stopPoll() { if (poll) { clearInterval(poll); poll = null } }

function loadLesson(i, { autoplay = true, seek = 0 } = {}) {
  const clamped = Math.min(Math.max(0, i), props.lessons.length - 1)
  currentIndex.value = clamped
  emit('update:modelValue', clamped + 1)
  currentTime.value = seek
  duration.value = 0
  loading.value = true            // show the loading state while the clip swaps
  errored.value = false
  if (!player || !player.loadVideoById) return
  const id = props.lessons[clamped]?.id
  if (!id) return
  const opts = { videoId: id, startSeconds: seek }
  if (autoplay) player.loadVideoById(opts)
  else player.cueVideoById(opts)
}

const togglePlay = () => {
  if (!player) return
  if (isPlaying.value) player.pauseVideo()
  else player.playVideo()
}
const next = () => { if (canNext.value) loadLesson(currentIndex.value + 1) }
const prev = () => { if (canPrev.value) loadLesson(currentIndex.value - 1) }
const selectLesson = (i) => { loadLesson(i); speedOpen.value = false }

const toggleMute = () => {
  if (!player) return
  if (muted.value) { player.unMute(); player.setVolume(100); muted.value = false }
  else { player.mute(); muted.value = true }
}

const setRate = (r) => {
  rate.value = r
  speedOpen.value = false
  if (player && player.setPlaybackRate) player.setPlaybackRate(r)
}

const seek = (e) => {
  if (!player || !duration.value) return
  const barEl = e.currentTarget
  const rect = barEl.getBoundingClientRect()
  // Account for RTL: progress always runs visually left→right for the media.
  const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
  const target = ratio * duration.value
  currentTime.value = target
  player.seekTo(target, true)
}

const toggleFullscreen = () => {
  const el = root.value
  if (!el) return
  if (!document.fullscreenElement) el.requestFullscreen?.()
  else document.exitFullscreen?.()
}
const onFsChange = () => { isFullscreen.value = !!document.fullscreenElement }

// ── Engine lifecycle ──────────────────────────────────────────────────────────
onMounted(async () => {
  const resume = readResume()
  if (resume && Number.isInteger(resume.lesson) && resume.lesson < props.lessons.length) {
    currentIndex.value = resume.lesson
    emit('update:modelValue', resume.lesson + 1)
  }
  const startSeconds = resume?.t || 0

  document.addEventListener('fullscreenchange', onFsChange)

  const YT = await loadEngine().catch(() => null)
  if (!YT || !ytHost.value) return

  player = new YT.Player(ytHost.value, {
    videoId: props.lessons[currentIndex.value]?.id,
    playerVars: {
      autoplay: 1, mute: 1, controls: 0, modestbranding: 1, rel: 0,
      iv_load_policy: 3, disablekb: 1, fs: 0, playsinline: 1,
      enablejsapi: 1, origin: window.location.origin,
    },
    events: {
      onReady: (e) => {
        ready.value = true
        e.target.setPlaybackRate(rate.value)
        e.target.mute()
        muted.value = true
        if (startSeconds) e.target.seekTo(startSeconds, true)
        e.target.playVideo()
        startPoll()
      },
      onStateChange: (e) => {
        // YT.PlayerState: 1 playing · 2 paused · 0 ended · 3 buffering
        if (e.data === 1) { isPlaying.value = true; loading.value = false; errored.value = false }
        else if (e.data === 2) isPlaying.value = false
        else if (e.data === 3) loading.value = true
        else if (e.data === 0) { isPlaying.value = false; next() }
      },
      onError: () => {
        // A clip failed to load (removed / not embeddable). Surface it briefly
        // and advance to the next lesson so the playlist keeps flowing.
        errored.value = true
        loading.value = false
        if (canNext.value) window.setTimeout(() => { if (errored.value) next() }, 1800)
      },
    },
  })
})

onBeforeUnmount(() => {
  stopPoll()
  saveResume()
  document.removeEventListener('fullscreenchange', onFsChange)
  if (player && player.destroy) player.destroy()
  player = null
})

// Parent drives the lesson (e.g. clicking the syllabus) → load it here.
watch(() => props.modelValue, (v) => {
  if (!v) return
  if (v - 1 !== currentIndex.value && ready.value) loadLesson(v - 1)
  else currentIndex.value = v - 1
})
</script>

<template>
  <div ref="root" class="cplayer" :class="{ 'cplayer--fs': isFullscreen }">
    <!-- Stage -->
    <div class="cplayer__main">
      <div class="cplayer__stage">
        <!-- The API replaces the inner node with its iframe; the wrapper keeps
             our absolute positioning regardless. -->
        <div class="cplayer__engine"><div ref="ytHost"></div></div>

        <!-- Transparent shield: owns click-to-pause, hides any external chrome. -->
        <button
          type="button"
          class="cplayer__shield"
          :aria-label="isPlaying ? 'Pause' : 'Play'"
          @click="togglePlay"
        ></button>

        <!-- Top: lesson identity -->
        <div class="cplayer__top">
          <p class="cplayer__title">{{ currentTitle }}</p>
          <p v-if="subtitle" class="cplayer__subtitle">{{ subtitle }}</p>
        </div>

        <!-- Loading state (initial load + clip changes + buffering) -->
        <div v-if="loading && !errored" class="cplayer__loading" aria-live="polite">
          <span class="cplayer__spinner" aria-hidden="true"></span>
        </div>

        <!-- Error notice — a clip is unavailable; auto-advancing. -->
        <div v-if="errored" class="cplayer__notice" role="status">
          This lesson is temporarily unavailable — continuing to the next.
        </div>

        <!-- Center play (when paused) -->
        <button v-if="!isPlaying && !loading && !errored" type="button" class="cplayer__bigplay" aria-label="Play" @click="togglePlay">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
        </button>

        <!-- Unmute nudge (autoplay starts muted) -->
        <button v-if="muted && ready" type="button" class="cplayer__unmute" @click="toggleMute">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M11 5 6 9H2v6h4l5 4zM22 9l-6 6M16 9l6 6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Tap to unmute
        </button>

        <!-- Controls -->
        <div class="cplayer__controls">
          <div class="cplayer__bar" @click="seek">
            <div class="cplayer__fill" :style="{ width: pct }"><span class="cplayer__knob"></span></div>
          </div>
          <div class="cplayer__row">
            <div class="cplayer__group">
              <button type="button" class="cplayer__btn" :disabled="!canPrev" aria-label="Previous lesson" @click="prev">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h2v14H6zM20 5v14L9 12z"/></svg>
              </button>
              <button type="button" class="cplayer__btn" :aria-label="isPlaying ? 'Pause' : 'Play'" @click="togglePlay">
                <svg v-if="!isPlaying" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
              </button>
              <button type="button" class="cplayer__btn" :disabled="!canNext" aria-label="Next lesson" @click="next">
                <svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 5h2v14h-2zM4 5l11 7L4 19z"/></svg>
              </button>
              <button type="button" class="cplayer__btn" :aria-label="muted ? 'Unmute' : 'Mute'" @click="toggleMute">
                <svg v-if="!muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M11 5 6 9H2v6h4l5 4zM15.5 8.5a5 5 0 0 1 0 7M19 5a9 9 0 0 1 0 14" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M11 5 6 9H2v6h4l5 4zM22 9l-6 6M16 9l6 6" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>
              <span class="cplayer__time tabular-nums">{{ fmt(currentTime) }} / {{ fmt(duration) }}</span>
            </div>

            <div class="cplayer__group">
              <div class="cplayer__speed">
                <button type="button" class="cplayer__btn cplayer__btn--text" aria-label="Playback speed" @click="speedOpen = !speedOpen">
                  {{ rate }}×
                </button>
                <div v-if="speedOpen" class="cplayer__menu">
                  <button v-for="r in RATES" :key="r" type="button" class="cplayer__menu-item" :class="{ 'is-active': r === rate }" @click="setRate(r)">{{ r }}×</button>
                </div>
              </div>
              <button type="button" class="cplayer__btn" :aria-label="isFullscreen ? 'Exit fullscreen' : 'Fullscreen'" @click="toggleFullscreen">
                <svg v-if="!isFullscreen" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M21 16v3a2 2 0 0 1-2 2h-3M3 16v3a2 2 0 0 0 2 2h3" stroke-linecap="round"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3v3a2 2 0 0 1-2 2H3M21 8h-3a2 2 0 0 1-2-2V3M16 21v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" stroke-linecap="round"/></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Playlist sidebar -->
    <aside class="cplayer__playlist">
      <div class="cplayer__playlist-inner">
      <header class="cplayer__playlist-head">
        <span class="cplayer__playlist-title">Course Content</span>
        <span class="cplayer__playlist-count">{{ lessons.length }} lessons</span>
      </header>
      <ol class="cplayer__list">
        <li v-for="(l, i) in lessons" :key="i">
          <button
            type="button"
            class="cplayer__lesson"
            :class="{ 'is-active': i === currentIndex }"
            :aria-current="i === currentIndex ? 'true' : undefined"
            @click="selectLesson(i)"
          >
            <span class="cplayer__lesson-icon">
              <svg v-if="i === currentIndex && isPlaying" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            </span>
            <span class="cplayer__lesson-text">
              <span class="cplayer__lesson-num">Lesson {{ String(i + 1).padStart(2, '0') }}</span>
              <span class="cplayer__lesson-name">{{ l.title }}</span>
            </span>
          </button>
        </li>
      </ol>
      </div>
    </aside>
  </div>
</template>

<style scoped>
/* In-house LMS player — dark charcoal glass with gold accents, matching the
   platform's premium aesthetic. No external player chrome is ever shown. */
.cplayer {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(237, 192, 113, 0.22);
  background: #100e0b;
  box-shadow: 0 30px 70px -40px rgba(0, 0, 0, 0.8);
}
@media (min-width: 1024px) {
  /* Desktop: video 70% / playlist 30%, side by side. minmax(0,…) keeps the
     video from overflowing its track; align-items: stretch lets the playlist
     column match the video's height (it then scrolls internally). */
  .cplayer {
    grid-template-columns: minmax(0, 7fr) minmax(0, 3fr);
    align-items: stretch;
  }
}

.cplayer__main { min-width: 0; background: #000; }

.cplayer__stage {
  position: relative;
  aspect-ratio: 16 / 9;
  width: 100%;
  overflow: hidden;
  background: radial-gradient(120% 120% at 50% 20%, #1c1915 0%, #0b0907 70%);
}
.cplayer__engine { position: absolute; inset: 0; }
.cplayer__engine :deep(iframe),
.cplayer__engine :deep(div) {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}

/* Transparent click layer — owns play/pause, masks any external interaction. */
.cplayer__shield {
  position: absolute;
  inset: 0;
  z-index: 10;
  width: 100%;
  height: 100%;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.cplayer__top {
  position: absolute;
  top: 0; left: 0; right: 0;
  z-index: 20;
  padding: 0.9rem 1.1rem;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.6), transparent);
  pointer-events: none;
}
.cplayer__title { color: #f6f3ec; font-size: 0.9rem; font-weight: 300; line-height: 1.3; }
.cplayer__subtitle { color: rgba(246, 243, 236, 0.6); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.2em; margin-top: 0.15rem; }

.cplayer__bigplay {
  position: absolute;
  inset: 0;
  margin: auto;
  z-index: 20;
  width: 4.5rem; height: 4.5rem;
  display: grid; place-items: center;
  border-radius: 9999px;
  border: 0;
  color: #14110d;
  background: rgba(234, 192, 121, 0.92);
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}
.cplayer__bigplay:hover { background: #eac079; transform: scale(1.06); }
.cplayer__bigplay svg { width: 1.8rem; height: 1.8rem; margin-inline-start: 3px; }

/* Loading + error states — sit above the shield, never block our controls. */
.cplayer__loading {
  position: absolute;
  inset: 0;
  z-index: 20;
  display: grid;
  place-items: center;
  pointer-events: none;
}
.cplayer__spinner {
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 9999px;
  border: 2px solid rgba(234, 192, 121, 0.25);
  border-top-color: #eac079;
  animation: cplayer-spin 0.8s linear infinite;
}
@keyframes cplayer-spin { to { transform: rotate(360deg); } }
.cplayer__notice {
  position: absolute;
  inset-inline: 1.2rem;
  bottom: 4.6rem;
  z-index: 25;
  margin: 0 auto;
  max-width: 24rem;
  padding: 0.55rem 0.9rem;
  border-radius: 8px;
  border: 1px solid rgba(237, 192, 113, 0.4);
  background: rgba(16, 14, 11, 0.82);
  -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
  color: rgba(246, 243, 236, 0.9);
  font-size: 0.72rem;
  text-align: center;
  line-height: 1.4;
}

.cplayer__unmute {
  position: absolute;
  z-index: 20;
  bottom: 4.6rem;
  inset-inline-end: 1.1rem;
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  border-radius: 9999px;
  border: 1px solid rgba(237, 192, 113, 0.5);
  background: rgba(16, 14, 11, 0.7);
  -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
  color: #eac079;
  font-size: 0.68rem; letter-spacing: 0.08em;
  cursor: pointer;
}

/* Control bar — glass strip over a gradient scrim. */
.cplayer__controls {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  z-index: 30;
  padding: 0.5rem 0.9rem 0.7rem;
  background: linear-gradient(0deg, rgba(0, 0, 0, 0.82), transparent);
}
.cplayer__bar {
  position: relative;
  height: 5px;
  width: 100%;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
}
.cplayer__fill {
  position: relative;
  height: 100%;
  border-radius: 9999px;
  background: #eac079;
}
.cplayer__knob {
  position: absolute;
  inset-inline-end: -5px; top: 50%;
  transform: translateY(-50%);
  width: 11px; height: 11px;
  border-radius: 9999px;
  background: #eac079;
  box-shadow: 0 0 0 3px rgba(234, 192, 121, 0.25);
}
.cplayer__row {
  margin-top: 0.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.cplayer__group { display: flex; align-items: center; gap: 0.35rem; }
.cplayer__btn {
  display: grid; place-items: center;
  width: 2rem; height: 2rem;
  border: 0; background: transparent;
  color: rgba(246, 243, 236, 0.85);
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease;
}
.cplayer__btn:hover { color: #eac079; background: rgba(255, 255, 255, 0.06); }
.cplayer__btn:disabled { opacity: 0.3; cursor: not-allowed; }
.cplayer__btn svg { width: 1.05rem; height: 1.05rem; }
.cplayer__btn--text { width: auto; padding: 0 0.55rem; font-size: 0.74rem; letter-spacing: 0.04em; }
.cplayer__time { color: rgba(246, 243, 236, 0.7); font-size: 0.7rem; margin-inline-start: 0.4rem; }

.cplayer__speed { position: relative; }
.cplayer__menu {
  position: absolute;
  bottom: calc(100% + 0.4rem);
  inset-inline-end: 0;
  display: flex; flex-direction: column;
  min-width: 4rem;
  padding: 0.3rem;
  border-radius: 8px;
  border: 1px solid rgba(237, 192, 113, 0.25);
  background: rgba(16, 14, 11, 0.95);
  -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
}
.cplayer__menu-item {
  border: 0; background: transparent;
  color: rgba(246, 243, 236, 0.8);
  font-size: 0.74rem;
  padding: 0.35rem 0.5rem;
  border-radius: 5px;
  cursor: pointer;
  text-align: start;
}
.cplayer__menu-item:hover { background: rgba(255, 255, 255, 0.07); color: #eac079; }
.cplayer__menu-item.is-active { color: #eac079; }

/* ── Playlist sidebar ──────────────────────────────────────────────────────── */
.cplayer__playlist {
  position: relative;       /* containing block for the absolute inner (desktop) */
  min-width: 0;
  background: rgba(20, 17, 13, 0.92);
  -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
}
/* Tablet / mobile: the playlist sits below the video with a bounded scroll. */
.cplayer__playlist-inner {
  display: flex;
  flex-direction: column;
  max-height: 22rem;
}
/* Desktop: fill the stretched column (= video height) and scroll internally, so
   the lesson list never dictates the row height or overlaps the player. */
@media (min-width: 1024px) {
  .cplayer__playlist-inner {
    position: absolute;
    inset: 0;
    max-height: none;
  }
}
.cplayer__playlist-head {
  display: flex; align-items: baseline; justify-content: space-between;
  gap: 0.5rem;
  padding: 0.95rem 1rem;
  border-bottom: 1px solid rgba(237, 192, 113, 0.16);
}
.cplayer__playlist-title { color: #f6f3ec; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.25em; font-weight: 300; }
.cplayer__playlist-count { color: rgba(234, 192, 121, 0.75); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.18em; }

.cplayer__list { flex: 1 1 auto; min-height: 0; overflow-y: auto; padding: 0.4rem; }
.cplayer__lesson {
  display: flex; align-items: flex-start; gap: 0.65rem;
  width: 100%;
  padding: 0.6rem 0.65rem;
  border: 0; background: transparent;
  border-radius: 8px;
  text-align: start;
  cursor: pointer;
  transition: background 0.2s ease;
}
.cplayer__lesson:hover { background: rgba(255, 255, 255, 0.05); }
.cplayer__lesson.is-active { background: rgba(234, 192, 121, 0.12); }
.cplayer__lesson-icon {
  flex-shrink: 0;
  display: grid; place-items: center;
  width: 1.6rem; height: 1.6rem;
  margin-top: 0.1rem;
  border-radius: 6px;
  border: 1px solid rgba(237, 192, 113, 0.35);
  color: #eac079;
}
.cplayer__lesson.is-active .cplayer__lesson-icon { background: rgba(234, 192, 121, 0.18); }
.cplayer__lesson-icon svg { width: 0.7rem; height: 0.7rem; }
.cplayer__lesson-text { min-width: 0; display: flex; flex-direction: column; gap: 0.1rem; }
.cplayer__lesson-num { color: rgba(234, 192, 121, 0.75); font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.2em; }
.cplayer__lesson-name { color: rgba(246, 243, 236, 0.88); font-size: 0.82rem; font-weight: 300; line-height: 1.3; }
.cplayer__lesson.is-active .cplayer__lesson-name { color: #f6f3ec; }

/* Fullscreen: stage fills, playlist becomes a docked rail. */
.cplayer--fs {
  width: 100vw; height: 100vh;
  border-radius: 0; border: 0;
}
.cplayer--fs .cplayer__stage { aspect-ratio: auto; height: 100vh; }
@media (min-width: 1024px) {
  .cplayer--fs { grid-template-columns: minmax(0, 1fr) 22rem; }
  .cplayer--fs .cplayer__playlist { max-height: 100vh; }
}

@media (prefers-reduced-motion: reduce) {
  .cplayer__btn, .cplayer__bigplay, .cplayer__lesson { transition: none; }
  .cplayer__spinner { animation-duration: 1.6s; }
}
</style>
