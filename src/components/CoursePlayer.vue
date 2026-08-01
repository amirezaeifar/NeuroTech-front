<script setup>
/**
 * CoursePlayer — an in-house LMS video player.
 *
 * Plays a course playlist of locally-hosted .mp4 lessons through a fully custom
 * dark/gold/glass control layer built directly on the native HTML <video>
 * element. There is NO external player, embed or third-party engine: the file is
 * served from the app's own origin (see src/data/courseVideos.js). Native
 * controls are disabled in favour of our own, and a transparent shield captures
 * click-to-pause.
 *
 * Features: a playlist sidebar, seekable progress bar, prev/next, mute,
 * playback-speed control, fullscreen, continuous auto-next, a graceful fallback
 * when a file is missing, and resume-from-where-you-left-off via localStorage.
 * Playback never autoplays on open — the viewer presses play — so the page never
 * fights browser autoplay policies.
 *
 * Two-way bound to the parent's current-lesson number (1-based) so the syllabus
 * and progress stay in sync.
 */
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  /** [{ title, src }] in playlist order. `src` is a local, same-origin URL. */
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
const videoEl = ref(null)

const currentIndex = ref(Math.max(0, (props.modelValue || 1) - 1))
const isPlaying = ref(false)
const muted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const rate = ref(1)
const isFullscreen = ref(false)
const speedOpen = ref(false)
const ready = ref(false)
const loading = ref(true)
const errored = ref(false)
const started = ref(false)        // playback has begun at least once (hides splash)

// Seek/autoplay intent applied once the next source's metadata is ready.
let pendingSeek = 0
let pendingAutoplay = false

const currentLesson = computed(() => props.lessons[currentIndex.value] || {})
const currentTitle = computed(() =>
  currentLesson.value.title || `Lesson ${currentIndex.value + 1}`)
const currentSrc = computed(() => currentLesson.value.src || '')
const hasSource = computed(() => !!currentSrc.value)
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
// Switch lesson. The <video> :src is bound reactively, so we record the desired
// seek/autoplay, force a reload, and finish wiring up in onLoadedMetadata.
async function loadLesson(i, { autoplay = true, seek = 0 } = {}) {
  const clamped = Math.min(Math.max(0, i), props.lessons.length - 1)
  const changed = clamped !== currentIndex.value
  currentIndex.value = clamped
  emit('update:modelValue', clamped + 1)
  currentTime.value = seek
  duration.value = 0
  loading.value = true            // show the loading state while the clip swaps
  errored.value = false
  pendingSeek = seek
  pendingAutoplay = autoplay
  speedOpen.value = false
  const v = videoEl.value
  if (!v) return
  // Let the bound :src update first, then reload the media element.
  await nextTick()
  v.load()
}

const play = () => {
  const v = videoEl.value
  if (!v || !hasSource.value) return
  started.value = true
  v.play().catch(() => { /* user-gesture / decode race — non-fatal */ })
}
const togglePlay = () => {
  const v = videoEl.value
  if (!v || !hasSource.value) return
  if (isPlaying.value) v.pause()
  else play()
}
const next = () => { if (canNext.value) loadLesson(currentIndex.value + 1, { autoplay: started.value }) }
const prev = () => { if (canPrev.value) loadLesson(currentIndex.value - 1, { autoplay: started.value }) }
const selectLesson = (i) => { loadLesson(i, { autoplay: true }); started.value = true }
const retry = () => { loadLesson(currentIndex.value, { autoplay: true }) }

const toggleMute = () => {
  const v = videoEl.value
  if (!v) return
  v.muted = !v.muted
  muted.value = v.muted
}

const setRate = (r) => {
  rate.value = r
  speedOpen.value = false
  if (videoEl.value) videoEl.value.playbackRate = r
}

const seek = (e) => {
  const v = videoEl.value
  if (!v || !duration.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  // Progress always runs visually left→right for the media, regardless of dir.
  const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
  const target = ratio * duration.value
  currentTime.value = target
  v.currentTime = target
}

const toggleFullscreen = () => {
  const el = root.value
  if (!el) return
  if (!document.fullscreenElement) el.requestFullscreen?.()
  else document.exitFullscreen?.()
}
const onFsChange = () => { isFullscreen.value = !!document.fullscreenElement }

// ── Native <video> events ─────────────────────────────────────────────────────
const onLoadedMetadata = () => {
  const v = videoEl.value
  if (!v) return
  ready.value = true
  duration.value = v.duration || 0
  v.playbackRate = rate.value
  if (pendingSeek && isFinite(pendingSeek)) {
    try { v.currentTime = pendingSeek } catch { /* out of range — ignore */ }
  }
  pendingSeek = 0
  loading.value = false
  if (pendingAutoplay) { pendingAutoplay = false; play() }
}
const onTimeUpdate = () => {
  const v = videoEl.value
  if (!v) return
  currentTime.value = v.currentTime || 0
  saveResume()
}
const onPlay = () => { isPlaying.value = true; started.value = true; errored.value = false }
const onPause = () => { isPlaying.value = false }
const onWaiting = () => { loading.value = true }
const onPlaying = () => { loading.value = false; isPlaying.value = true }
const onEnded = () => { isPlaying.value = false; next() }
const onError = () => {
  // The file failed to load (missing / unsupported). Surface a fallback so the
  // learner is never left staring at a broken player; they can retry or skip.
  errored.value = true
  loading.value = false
  isPlaying.value = false
}

// ── Lifecycle ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  const resume = readResume()
  if (resume && Number.isInteger(resume.lesson) && resume.lesson < props.lessons.length) {
    currentIndex.value = resume.lesson
    emit('update:modelValue', resume.lesson + 1)
  }
  pendingSeek = resume?.t || 0
  pendingAutoplay = false        // never autoplay on first open

  document.addEventListener('fullscreenchange', onFsChange)

  // Kick the element to load the initial source (and apply any resume seek).
  await nextTick()
  if (videoEl.value && hasSource.value) videoEl.value.load()
})

onBeforeUnmount(() => {
  saveResume()
  document.removeEventListener('fullscreenchange', onFsChange)
})

// Parent drives the lesson (e.g. clicking the syllabus) → load it here.
watch(() => props.modelValue, (v) => {
  if (!v) return
  if (v - 1 !== currentIndex.value) loadLesson(v - 1, { autoplay: started.value })
})
</script>

<template>
  <div ref="root" class="cplayer" :class="{ 'cplayer--fs': isFullscreen }">
    <!-- Stage -->
    <div class="cplayer__main">
      <div class="cplayer__stage">
        <!-- Native, same-origin <video>. Native controls are off; our own UI
             below drives it. `playsinline` keeps it inline on mobile. -->
        <video
          ref="videoEl"
          class="cplayer__video"
          :src="currentSrc"
          preload="metadata"
          playsinline
          @loadedmetadata="onLoadedMetadata"
          @timeupdate="onTimeUpdate"
          @play="onPlay"
          @pause="onPause"
          @waiting="onWaiting"
          @playing="onPlaying"
          @ended="onEnded"
          @error="onError"
        ></video>

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
        <div v-if="loading && !errored && hasSource" class="cplayer__loading" aria-live="polite">
          <span class="cplayer__spinner" aria-hidden="true"></span>
        </div>

        <!-- Fallback — the file is missing/unavailable, or the course has no
             local footage yet. Never a broken player; offer retry / skip. -->
        <div v-if="errored || !hasSource" class="cplayer__fallback" role="status">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M12 9v4m0 4h.01M10.3 4.3 1.8 19a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0z" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <p class="cplayer__fallback-text">{{ hasSource ? 'This lesson could not be loaded.' : 'Video for this lesson is coming soon.' }}</p>
          <div class="cplayer__fallback-actions">
            <button v-if="hasSource" type="button" class="cplayer__fallback-btn" @click="retry">Retry</button>
            <button v-if="canNext" type="button" class="cplayer__fallback-btn" @click="next">Next lesson</button>
          </div>
        </div>

        <!-- Center play (when paused, with a playable source) -->
        <button v-if="!isPlaying && !loading && !errored && hasSource" type="button" class="cplayer__bigplay" aria-label="Play" @click="togglePlay">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
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
.cplayer__video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
  background: #000;
  object-fit: contain;   /* never crop the lecture frame */
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
/* Missing / failed-source fallback — centred over the dark stage. */
.cplayer__fallback {
  position: absolute;
  inset: 0;
  z-index: 25;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.9rem;
  padding: 1.5rem;
  text-align: center;
  color: rgba(246, 243, 236, 0.92);
}
.cplayer__fallback svg { color: rgba(234, 192, 121, 0.85); }
.cplayer__fallback-text { font-size: 0.86rem; font-weight: 300; max-width: 22rem; line-height: 1.5; }
.cplayer__fallback-actions { display: flex; gap: 0.6rem; }
.cplayer__fallback-btn {
  padding: 0.45rem 1.05rem;
  border-radius: 9999px;
  border: 1px solid rgba(237, 192, 113, 0.5);
  background: rgba(16, 14, 11, 0.7);
  color: #eac079;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}
.cplayer__fallback-btn:hover { background: rgba(234, 192, 121, 0.16); color: #f6f3ec; }

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
