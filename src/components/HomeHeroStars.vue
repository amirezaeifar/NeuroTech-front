<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useTheme } from '../composables/useTheme.js'

const field = ref(null)
const active = ref(false)
const maskReady = ref(false)
const { isDark } = useTheme()
let observer, resizeObserver, localeObserver
let brainRoot, brainImage, brainMask
let layoutFrame = 0
let visible = false
let hero, motionQuery, hoveredStar, pointerPosition
let pointerFrame = 0
let starElements = []
const blinks = new Map()
const clearHover = () => {
  hoveredStar?.classList.remove('is-hovered')
  hoveredStar = null
  pointerPosition = null
  cancelAnimationFrame(pointerFrame)
  pointerFrame = 0
}
const cancelBlinks = () => {
  for (const animations of blinks.values()) { animations.star.cancel(); animations.wave.cancel() }
  blinks.clear()
}
const sync = () => {
  active.value = visible && !document.hidden
  if (!active.value) { clearHover(); cancelBlinks() }
}
const onMotionChange = () => { if (motionQuery.matches) cancelBlinks() }
watch(isDark, cancelBlinks)

function blink(star) {
  if (motionQuery.matches) return
  const previous = blinks.get(star)
  previous?.star.cancel()
  previous?.wave.cancel()
  const opacity = getComputedStyle(star).opacity
  const peak = isDark.value ? .28 : 1.8
  const shoulder = isDark.value ? .55 : 1.3
  const animation = star.animate([
    { opacity, filter: 'brightness(1)', scale: '1' },
    { offset: .18, opacity: 1, filter: `brightness(${peak})`, scale: '1.22' },
    { offset: .48, opacity: .85, filter: `brightness(${shoulder})`, scale: '1.12' },
    { offset: .68, opacity: .95, filter: `brightness(${peak})`, scale: '1.16' },
    { opacity, filter: 'brightness(1)', scale: '1' },
  ], { duration: 1800, easing: 'ease-in-out' })
  const wave = star.querySelector('.hero-star-wave').animate([
    { offset: 0, opacity: 0, transform: 'translate(-50%,-50%) scale(.25)' },
    { offset: .08, opacity: .6, transform: 'translate(-50%,-50%) scale(.65)' },
    { offset: .25, opacity: .28, transform: 'translate(-50%,-50%) scale(1.35)' },
    { offset: .45, opacity: .1, transform: 'translate(-50%,-50%) scale(2.1)' },
    { offset: .65, opacity: .025, transform: 'translate(-50%,-50%) scale(2.7)' },
    { offset: .85, opacity: .003, transform: 'translate(-50%,-50%) scale(3.15)' },
    { offset: .95, opacity: 0, transform: 'translate(-50%,-50%) scale(3.35)' },
    { opacity: 0, transform: 'translate(-50%,-50%) scale(3.5)' },
  ], { duration: 1800, easing: 'linear' })
  blinks.set(star, { star: animation, wave })
  animation.onfinish = () => { if (blinks.get(star)?.star === animation) blinks.delete(star) }
}

function refreshExclusion() {
  layoutFrame = 0
  if (!field.value || !brainRoot) return
  const bounds = field.value.getBoundingClientRect()
  const rootBounds = brainRoot.getBoundingClientRect()
  const image = { left: rootBounds.left + rootBounds.width * .06, top: rootBounds.top + rootBounds.height * .06, width: rootBounds.width * .88, height: rootBounds.height * .88 }
  if (!image.width || !image.height) return
  starElements.forEach((star, index) => {
    const style = getComputedStyle(star)
    const x = bounds.left + positions[index][0] / 100 * bounds.width + parseFloat(style.width) / 2
    const y = bounds.top + positions[index][1] / 100 * bounds.height + parseFloat(style.height) / 2
    let overlaps = false
    // Keep the star, its drift and expanding wave outside the actual opaque
    // silhouette, rather than removing every star in the image's square box.
    for (let dy = -40; dy <= 40 && !overlaps; dy += 8) {
      for (let dx = -40; dx <= 40; dx += 8) {
        const mx = Math.floor((x + dx - image.left) / image.width * 128)
        const my = Math.floor((y + dy - image.top) / image.height * 128)
        if (mx >= 0 && mx < 128 && my >= 0 && my < 128 && (!brainMask || brainMask[(my * 128 + mx) * 4 + 3] > 24)) { overlaps = true; break }
      }
    }
    star.classList.toggle('is-over-brain', overlaps)
    if (overlaps) {
      const animations = blinks.get(star)
      animations?.star.cancel(); animations?.wave.cancel()
      blinks.delete(star)
      if (hoveredStar === star) clearHover()
    }
  })
  maskReady.value = true
}
function scheduleExclusion() {
  if (field.value && !layoutFrame) layoutFrame = requestAnimationFrame(refreshExclusion)
}
function readBrainSilhouette() {
  if (!brainImage?.naturalWidth) { scheduleExclusion(); return }
  const mask = document.createElement('canvas')
  mask.width = mask.height = 128
  const context = mask.getContext('2d', { willReadFrequently: true })
  context.drawImage(brainImage, 0, 0, 128, 128)
  brainMask = context.getImageData(0, 0, 128, 128).data
  scheduleExclusion()
}

function checkPointer() {
  pointerFrame = 0
  if (!pointerPosition || !active.value) return
  const { x, y } = pointerPosition
  let nearest = null, nearestDistance = Infinity
  for (const star of starElements) {
    const rect = star.getBoundingClientRect()
    if (!rect.width || x < rect.left - 6 || x > rect.right + 6 || y < rect.top - 6 || y > rect.bottom + 6) continue
    const distance = Math.hypot(x - rect.left - rect.width / 2, y - rect.top - rect.height / 2)
    if (distance < nearestDistance) { nearest = star; nearestDistance = distance }
  }
  if (nearest === hoveredStar) return
  hoveredStar?.classList.remove('is-hovered')
  hoveredStar = nearest
  if (nearest) { nearest.classList.add('is-hovered'); blink(nearest) }
}
function onPointerMove(event) {
  if (!active.value || event.pointerType === 'touch') return
  pointerPosition = { x: event.clientX, y: event.clientY }
  if (!pointerFrame) pointerFrame = requestAnimationFrame(checkPointer)
}

// Coordinates span the physical right half of the header in both locales.
const positions = [
  [8, 9], [35, 5], [68, 12], [92, 7], [20, 21], [51, 18],
  [82, 25], [5, 36], [37, 32], [63, 38], [95, 41], [23, 47],
  [48, 55], [77, 50], [10, 62], [92, 64], [33, 69], [65, 73],
  [19, 82], [49, 86], [81, 83], [6, 94], [68, 95], [94, 92],
  [19, 5], [47, 10], [78, 5], [7, 24], [35, 17], [66, 23],
  [94, 20], [21, 34], [51, 29], [81, 37], [8, 49], [38, 45],
  [64, 49], [94, 53], [24, 59], [61, 62], [79, 66], [5, 77],
  [44, 75], [95, 79], [33, 92], [62, 84], [80, 94], [18, 94],
]
const stars = positions.map(([x, y], index) => ({
  left: `${x}%`, top: `${y}%`, '--size': `${index % 13 === 0 ? 4.2 : [1.1, 1.6, 2.2, 1.4, 3.6, 1.8, 2.7, 1.3][index % 8]}px`,
  '--drift': `${19 + index % 7}s`, '--pulse': `${5.2 + index % 6 * .9}s`,
  '--delay': `${-index * 1.7}s`, '--dx': `${index % 2 ? -5 : 5}px`,
}))
onMounted(() => {
  hero = field.value.parentElement
  starElements = [...field.value.querySelectorAll('.hero-star')]
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  motionQuery.addEventListener('change', onMotionChange)
  // Listen on the header, keeping the decorative layer transparent to clicks
  // on the headline, navigation and CTA beneath it.
  hero.addEventListener('pointermove', onPointerMove, { passive: true })
  hero.addEventListener('pointerleave', clearHover)
  hero.addEventListener('transitionend', scheduleExclusion)
  window.addEventListener('resize', scheduleExclusion, { passive: true })
  nextTick(() => {
    if (!field.value) return
    brainRoot = hero.querySelector('.living-brain')
    brainImage = hero.querySelector('.brain-artwork')
    brainImage?.addEventListener('load', readBrainSilhouette)
    brainImage?.addEventListener('error', scheduleExclusion)
    if (brainImage?.complete) readBrainSilhouette()
    if ('ResizeObserver' in window) {
      resizeObserver = new ResizeObserver(scheduleExclusion)
      resizeObserver.observe(field.value)
      if (brainRoot) resizeObserver.observe(brainRoot)
    }
    localeObserver = new MutationObserver(scheduleExclusion)
    localeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['dir', 'lang'] })
    document.fonts?.ready.then(scheduleExclusion)
  })
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync() })
    observer.observe(field.value)
  } else { visible = true; sync() }
  document.addEventListener('visibilitychange', sync)
})
onUnmounted(() => {
  clearHover()
  cancelBlinks()
  hero?.removeEventListener('pointermove', onPointerMove)
  hero?.removeEventListener('pointerleave', clearHover)
  hero?.removeEventListener('transitionend', scheduleExclusion)
  window.removeEventListener('resize', scheduleExclusion)
  brainImage?.removeEventListener('load', readBrainSilhouette)
  brainImage?.removeEventListener('error', scheduleExclusion)
  cancelAnimationFrame(layoutFrame)
  resizeObserver?.disconnect()
  localeObserver?.disconnect()
  motionQuery?.removeEventListener('change', onMotionChange)
  observer?.disconnect()
  document.removeEventListener('visibilitychange', sync)
})
</script>

<template>
  <div ref="field" class="home-hero-stars" :class="{ 'is-paused': !active, 'is-filtering': !maskReady }" aria-hidden="true">
    <span v-for="(star, index) in stars" :key="index" class="hero-star" :style="star"><i class="hero-star-wave"></i></span>
  </div>
</template>

<style scoped>
.home-hero-stars { position: absolute; top: 0; right: 0; bottom: 0; width: 50%; z-index: 0; overflow: hidden; pointer-events: none; --star-color: #d5c4a5; --star-low: .15; --star-high: .52; }
.hero-star { --star-shape: polygon(50% 0,58% 41%,100% 50%,58% 59%,50% 100%,42% 59%,0 50%,42% 41%); position: absolute; width: calc(var(--size) * 3.2); height: calc(var(--size) * 4); opacity: .24; animation: star-drift var(--drift) ease-in-out var(--delay) infinite; }
.hero-star::before { content: ''; position: absolute; inset: 0; background: var(--star-color); clip-path: var(--star-shape); animation: star-twinkle var(--pulse) ease-in-out var(--delay) infinite; }
.hero-star::after { content: ''; position: absolute; inset: 16%; background: var(--star-color); clip-path: var(--star-shape); animation: star-pulse var(--pulse) ease-out var(--delay) infinite; }
.is-filtering .hero-star { visibility: hidden; }
.hero-star.is-over-brain { display: none; }
.hero-star-wave { position: absolute; left: 50%; top: 50%; width: calc(var(--size) * 4); height: calc(var(--size) * 4); box-sizing: border-box; border: clamp(.5px, calc(var(--size) * .2), .8px) solid #e3d0a8; border-radius: 50%; opacity: 0; transform: translate(-50%,-50%) scale(.25); }
.is-paused .hero-star, .is-paused .hero-star::before, .is-paused .hero-star::after { animation-play-state: paused; }
:global(html.dark .home-hero-stars) { --star-color: #939698; --star-low: .32; --star-high: .8; }
:global(html.dark .home-hero-stars .hero-star::before) { background: linear-gradient(135deg,#73777b 5%,#979a9c 45%,#b6b8b9 65%,#858889); }
:global(html.dark .home-hero-stars .hero-star-wave) { border-color: #55585b; }
@keyframes star-drift { 0%,100% { opacity: var(--star-low); transform: translate(0,0); } 50% { opacity: var(--star-high); transform: translate(var(--dx),-6px); } }
@keyframes star-twinkle { 0%,100% { opacity: .38; transform: scale(.82); } 45% { opacity: 1; transform: scale(1.06); } 72% { opacity: .55; transform: scale(.92); } }
@keyframes star-pulse { 0%,25%,100% { opacity: .06; transform: rotate(45deg) scale(.65); } 42% { opacity: .35; transform: rotate(45deg) scale(1); } 85% { opacity: .08; transform: rotate(45deg) scale(1.15); } }
@media (max-width: 600px) { .hero-star:nth-child(3n) { display: none; } }
@media (prefers-reduced-motion: reduce) { .hero-star, .hero-star::before, .hero-star::after { animation: none; }.hero-star { opacity: .2; }.hero-star::before { opacity: .3; }.hero-star::after { opacity: 0; }.hero-star.is-hovered { opacity: .8; filter: brightness(1.3); } }
@media (prefers-reduced-motion: reduce) { :global(html.dark .home-hero-stars .hero-star.is-hovered) { filter: brightness(.3); } }
</style>
