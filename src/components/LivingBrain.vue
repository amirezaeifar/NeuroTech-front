<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useTheme } from '../composables/useTheme.js'
import brainArtwork from '../assets/brain/vascular-brain.png'

const root = ref(null)
const canvas = ref(null)
const vesselBed = ref(null)
const artwork = ref(null)
const running = ref(false)
const loaded = ref(false)
const { isDark } = useTheme()
let observer, resizeObserver, motionQuery, context, vesselMask
let visible = true
let raf = 0
let lastTime = 0
let elapsed = 0
let flowField, flowContext, flowPixels, flowCells = []

function prepareVesselMask() {
  // Confine the moving highlights to the artwork's gold vessels. The source
  // image stays untouched; this mask only clips the transient light layer.
  vesselMask = document.createElement('canvas')
  vesselMask.width = vesselMask.height = 1254
  const maskContext = vesselMask.getContext('2d', { willReadFrequently: true })
  maskContext.drawImage(artwork.value, 0, 0, 1254, 1254)
  const pixels = maskContext.getImageData(0, 0, 1254, 1254)
  for (let i = 0; i < pixels.data.length; i += 4) {
    const r = pixels.data[i], g = pixels.data[i + 1], b = pixels.data[i + 2], a = pixels.data[i + 3]
    const gold = r > g * 1.025 && g > b * 1.12 ? Math.min(1, Math.max(0, ((r - b) / Math.max(r, 1) - .21) / .16)) : 0
    pixels.data[i + 3] = Math.round(a * gold)
  }
  maskContext.putImageData(pixels, 0, 0)
  prepareFlowField(pixels)
  paintVesselBed()
}

function prepareFlowField(mask) {
  // Build a distance field through ALL visible vessels, including the fine
  // branches and cerebellum. A small topology grid bridges antialiased gaps;
  // the original full-resolution vessel mask still clips every rendered frame.
  const step = 3, side = 418, count = side * side
  const vessels = new Uint8Array(count)
  for (let y = 0; y < 1254; y++) {
    for (let x = 0; x < 1254; x++) {
      if (mask.data[(y * 1254 + x) * 4 + 3] > 24) vessels[Math.floor(y / step) * side + Math.floor(x / step)] = 1
    }
  }
  const connected = vessels.slice()
  for (let i = 0; i < count; i++) {
    if (!vessels[i]) continue
    const x = i % side, y = Math.floor(i / side)
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      if (x + dx >= 0 && x + dx < side && y + dy >= 0 && y + dy < side) connected[i + dy * side + dx] = 1
    }
  }
  const distances = new Float32Array(count).fill(-1)
  const queue = new Int32Array(count)
  const rootX = 719 / step, rootY = 1110 / step
  let seed = -1, nearest = Infinity
  for (let i = 0; i < count; i++) {
    if (!vessels[i]) continue
    const distance = Math.hypot(i % side - rootX, Math.floor(i / side) - rootY)
    if (distance < nearest) { nearest = distance; seed = i }
  }
  function propagate(origin, start) {
    let head = 0, tail = 1
    queue[0] = origin
    distances[origin] = start
    while (head < tail) {
      const current = queue[head++]
      const x = current % side, y = Math.floor(current / side)
      for (const next of [x > 0 ? current - 1 : -1, x < side - 1 ? current + 1 : -1, y > 0 ? current - side : -1, y < side - 1 ? current + side : -1]) {
        if (next < 0 || !connected[next] || distances[next] >= 0) continue
        distances[next] = distances[current] + step
        queue[tail++] = next
      }
    }
  }
  if (seed >= 0) propagate(seed, 0)
  // Separate visible branches also receive flow, even where the illustration
  // hides their connection behind a fold of the cortex.
  for (let i = 0; i < count; i++) {
    if (connected[i] && distances[i] < 0) propagate(i, Math.hypot(i % side - rootX, Math.floor(i / side) - rootY) * step)
  }
  flowField = document.createElement('canvas')
  flowField.width = flowField.height = side
  flowContext = flowField.getContext('2d')
  flowPixels = flowContext.createImageData(side, side)
  flowCells = []
  for (let i = 0; i < count; i++) {
    if (!connected[i]) continue
    const pixel = i * 4
    const x = i % side * step, y = Math.floor(i / side) * step
    const phaseA = x * .014 + y * .01 + distances[i] * .002
    const phaseB = x * .006 - y * .015
    flowCells.push({ alpha: pixel + 3, distance: distances[i], sinA: Math.sin(phaseA), cosA: Math.cos(phaseA), sinB: Math.sin(phaseB), cosB: Math.cos(phaseB) })
  }
  paintFlowPalette()
}

function paintFlowPalette() {
  if (!flowPixels) return
  // Half the RGB intensity of the vessel bed in each theme.
  const [r, g, b] = isDark.value ? [56, 22, 28] : [67, 27, 33]
  for (const cell of flowCells) {
    flowPixels.data[cell.alpha - 3] = r
    flowPixels.data[cell.alpha - 2] = g
    flowPixels.data[cell.alpha - 1] = b
  }
}
watch(isDark, () => {
  paintFlowPalette()
  paintVesselBed()
  if (!motionQuery?.matches) drawFlow()
})

function paintVesselBed() {
  if (!vesselMask || !vesselBed.value) return
  const bed = vesselBed.value.getContext('2d')
  if (!bed) return
  bed.clearRect(0, 0, vesselBed.value.width, vesselBed.value.height)
  bed.drawImage(vesselMask, 0, 0, vesselBed.value.width, vesselBed.value.height)
  bed.globalCompositeOperation = 'source-in'
  bed.fillStyle = isDark.value ? 'rgb(112, 43, 55)' : 'rgb(133, 53, 66)'
  bed.fillRect(0, 0, vesselBed.value.width, vesselBed.value.height)
  bed.globalCompositeOperation = 'source-over'
}

function resizeCanvas() {
  if (!canvas.value || !context) return
  // Render sharply on phones while bounding the cost on high-density screens.
  const size = Math.min(1280, Math.round(root.value.clientWidth * .88 * Math.min(window.devicePixelRatio || 1, 2)))
  if (!size) return
  canvas.value.width = size
  canvas.value.height = size
  vesselBed.value.width = size
  vesselBed.value.height = size
  paintVesselBed()
  context.setTransform(size / 1254, 0, 0, size / 1254, 0, 0)
  if (!motionQuery?.matches) drawFlow()
}

function drawFlow() {
  if (!context || !flowPixels) return
  context.clearRect(0, 0, 1280, 1280)
  const travel = elapsed * 62 + Math.sin(elapsed * .24) * 7
  const sinA = Math.sin(elapsed * .33), cosA = Math.cos(elapsed * .33)
  const sinB = Math.sin(elapsed * .23), cosB = Math.cos(elapsed * .23)
  for (const cell of flowCells) {
    const behind = ((travel - cell.distance) % 430 + 430) % 430
    const envelope = behind > 220 ? 0 : Math.sin(Math.PI * Math.min(behind / 46, 1) / 2) * Math.pow(1 - behind / 220, 1.25)
    // Spatially smooth, independent changes in local strength. Neighbouring
    // branches brighten at different times instead of flashing in unison.
    const intensity = .72 + .12 * (cell.sinA * cosA + cell.cosA * sinA) + .08 * (cell.sinB * cosB + cell.cosB * sinB)
    flowPixels.data[cell.alpha] = Math.round(envelope * intensity * 255)
  }
  flowContext.putImageData(flowPixels, 0, 0)
  context.drawImage(flowField, 0, 0, 1254, 1254)
  if (vesselMask) {
    context.globalCompositeOperation = 'destination-in'
    context.drawImage(vesselMask, 0, 0)
    context.globalCompositeOperation = 'source-over'
  }
}

function frame(time) {
  const dt = lastTime ? Math.min((time - lastTime) / 1000, .05) : 0
  lastTime = time
  elapsed += dt
  drawFlow()
  raf = requestAnimationFrame(frame)
}
function syncMotion() {
  const shouldRun = loaded.value && visible && !document.hidden && !motionQuery?.matches && !!context
  running.value = shouldRun
  if (shouldRun && !raf) {
    lastTime = 0
    raf = requestAnimationFrame(frame)
  } else if (!shouldRun) {
    cancelAnimationFrame(raf)
    raf = 0
    if (motionQuery?.matches) context?.clearRect(0, 0, 1280, 1280)
  }
}
function artworkReady() {
  if (!vesselMask) prepareVesselMask()
  loaded.value = true
  syncMotion()
}
onMounted(() => {
  context = canvas.value.getContext('2d')
  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')

  resizeCanvas()
  motionQuery.addEventListener('change', syncMotion)
  document.addEventListener('visibilitychange', syncMotion)
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(resizeCanvas)
    resizeObserver.observe(root.value)
  } else window.addEventListener('resize', resizeCanvas)
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; syncMotion() })
    observer.observe(root.value)
  }
  if (artwork.value.complete && artwork.value.naturalWidth) artworkReady()
  syncMotion()
})
onUnmounted(() => {
  cancelAnimationFrame(raf)
  observer?.disconnect()
  resizeObserver?.disconnect()
  motionQuery?.removeEventListener('change', syncMotion)
  document.removeEventListener('visibilitychange', syncMotion)
  window.removeEventListener('resize', resizeCanvas)
})
</script>

<template>
  <div ref="root" class="living-brain" :class="{ 'is-paused': !running, 'is-loaded': loaded }" aria-hidden="true">
    <div class="living-brain-aura"></div>
    <div class="living-brain-halo"></div>
    <div class="brain-atmosphere">
      <div class="brain-wisp brain-wisp-one"></div>
      <div class="brain-wisp brain-wisp-two"></div>
    </div>
    <div class="brain-breathe">
      <img ref="artwork" class="brain-artwork" :src="brainArtwork" alt="" width="1254" height="1254" fetchpriority="high" decoding="async" draggable="false" @load="artworkReady" />
      <canvas ref="vesselBed" class="brain-vessel-bed"></canvas>
      <canvas ref="canvas" class="brain-vessel-flow"></canvas>
    </div>
  </div>
</template>

<style scoped>
.living-brain { position: relative; width: 100%; max-width: 600px; aspect-ratio: 1; isolation: isolate; pointer-events: none; }
.brain-breathe { position: absolute; inset: 6%; width: 88%; height: 88%; transform-origin: 50% 54%; animation: brain-breathe 14s ease-in-out infinite; opacity: 0; transition: opacity 1.2s ease; }
.is-loaded .brain-breathe { opacity: 1; }
/* Keep the anatomy translucent, with independently lit vessels above it. */
.brain-artwork { display: block; width: 100%; height: 100%; object-fit: contain; opacity: .4; filter: saturate(.65) contrast(.9); user-select: none; mask-image: radial-gradient(ellipse at 49% 43%, #000 28%, #000d 60%, #0008 84%); }
.brain-vessel-bed, .brain-vessel-flow { position: absolute; inset: 0; width: 100%; height: 100%; }
.brain-vessel-bed { opacity: .8; filter: none; }
.brain-vessel-flow { filter: drop-shadow(0 0 2px #431b2180) drop-shadow(0 0 5px #431b2140); }
.living-brain-aura { position: absolute; inset: 3% 2% 10%; z-index: -1; border-radius: 50%; background: radial-gradient(ellipse at 43% 42%, #d5b67c0e, #b9873607 43%, transparent 70%); filter: blur(28px); animation: brain-aura 18s ease-in-out infinite; }
.living-brain-halo { position: absolute; inset: 4% 0 9%; z-index: -1; border-radius: 50%; background: radial-gradient(ellipse at 29% 36%, #d6b77d13, transparent 42%), radial-gradient(ellipse at 72% 65%, #bda0710d, transparent 45%); filter: blur(30px); animation: brain-halo 22s ease-in-out infinite; }
.brain-atmosphere { position: absolute; inset: 0; z-index: -1; opacity: 0; transition: opacity 1.8s ease; }
.is-loaded .brain-atmosphere { opacity: 1; }
.brain-wisp { position: absolute; width: 43%; height: 22%; border-radius: 50%; background: radial-gradient(ellipse, #dfc89d14, #b58d4908 45%, transparent 72%); filter: blur(20px); animation: brain-wisp 24s ease-in-out infinite; }
.brain-wisp-one { left: 1%; top: 26%; transform: rotate(-38deg); }
.brain-wisp-two { right: 0; bottom: 17%; transform: rotate(-38deg); animation-delay: -12s; }
.is-paused * { animation-play-state: paused; }
:global(html.dark .living-brain .brain-artwork) { opacity: .68; filter: grayscale(1) contrast(1.08) brightness(.96); }
:global(html.dark .living-brain .brain-vessel-bed) { opacity: .78; filter: none; }
:global(html.dark .living-brain .brain-vessel-flow) { filter: drop-shadow(0 0 2px #38161c80) drop-shadow(0 0 6px #38161c50); }
:global(html.dark .living-brain .living-brain-aura) { background: radial-gradient(ellipse at 43% 42%, #c49b4b0d, #ba8e3806 40%, transparent 70%); }
:global(html.dark .living-brain .living-brain-halo) { background: radial-gradient(ellipse at 29% 36%, #b8955410, transparent 42%), radial-gradient(ellipse at 72% 65%, #bda0710a, transparent 45%); }
@keyframes brain-breathe { 0%,100% { transform: translateY(0) rotate(-1deg); } 50% { transform: translateY(-7px) rotate(.5deg); } }
@keyframes brain-aura { 50% { opacity: .5; transform: scale(.96) translateY(4px); } }
@keyframes brain-halo { 50% { transform: translate(7px, -5px) scale(1.04); opacity: .55; } }
@keyframes brain-wisp { 50% { transform: translate(10px, -12px) rotate(-30deg) scale(1.12); opacity: .45; } }
@media (prefers-reduced-motion: reduce) { .living-brain * { animation: none !important; transition: none !important; } }
</style>



