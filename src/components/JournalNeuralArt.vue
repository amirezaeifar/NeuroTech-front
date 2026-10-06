<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

defineProps({ spacious: Boolean })

const artwork = ref(null)
const visible = ref(true)
let observer
onMounted(() => {
  if (!('IntersectionObserver' in window)) return
  observer = new IntersectionObserver(([entry]) => { visible.value = entry.isIntersecting })
  observer.observe(artwork.value)
})
onUnmounted(() => observer?.disconnect())

// Deterministic vector fibres; animation needs no JavaScript render loop.
const fibres = Array.from({ length: 42 }, (_, i) => {
  const angle = i / 42 * Math.PI * 2
  const radius = 164 + Math.sin(i * 2.3) * 32
  const x = 300 + Math.cos(angle) * radius
  const y = 260 + Math.sin(angle) * radius * .94
  const bend = angle + .48
  return { d: `M300 267 C${300 + Math.cos(bend) * 72} ${260 + Math.sin(bend) * 72}, ${x - Math.sin(angle) * 74} ${y + Math.cos(angle) * 74}, ${x} ${y}`, x, y, delay: `${-i * .43}s` }
})
</script>

<template>
  <div ref="artwork" class="journal-neural-art" :class="{ 'is-paused': !visible }" aria-hidden="true">
    <svg :viewBox="spacious ? '0 0 600 590' : '0 0 600 520'" fill="none" focusable="false">
      <g class="neural-fibres">
        <g v-for="(fibre, i) in fibres" :key="i">
          <path :d="fibre.d" class="neural-fibre" />
          <path v-if="i % 3 === 0" :d="fibre.d" class="neural-impulse" pathLength="100" :style="{ animationDelay: fibre.delay }" />
          <circle :cx="fibre.x" :cy="fibre.y" :r="i % 4 === 0 ? 2.5 : 1.2" class="neural-terminal" />
        </g>
        <circle cx="300" cy="267" r="17" class="neural-core-halo" />
        <circle cx="300" cy="267" r="4" fill="currentColor" />
      </g>
      <g class="neural-signal-group" :transform="spacious ? 'translate(0 65)' : undefined">
        <path d="M40 456H195l10-9 10 18 10-32 11 46 12-23h312" class="neural-signal" />
        <path d="M40 456H195l10-9 10 18 10-32 11 46 12-23h312" pathLength="100" class="neural-signal-trail" />
        <path d="M40 456H195l10-9 10 18 10-32 11 46 12-23h312" pathLength="100" class="neural-signal-current" />
      </g>
      <path d="M40 42h24M40 42v24M560 42h-24M560 42v24M40 420v-24M560 420v-24" stroke="currentColor" opacity=".3" />
    </svg>
  </div>
</template>

<style scoped>
.journal-neural-art { color: #d4ae5a; position: relative; width: 100%; background: radial-gradient(ellipse at 50% 50%, #b8922a19, transparent 60%); }
svg { width: 100%; height: 100%; display: block; }
.neural-fibres { transform-origin: 300px 267px; animation: neural-breathe 12s ease-in-out infinite; }
.neural-fibre { stroke: currentColor; stroke-width: .7; opacity: .48; }
.neural-impulse { stroke: #f4dfac; stroke-width: 1.5; stroke-dasharray: 3 97; animation: neural-flow 9s linear infinite; }
.neural-terminal { fill: currentColor; opacity: .8; }
.neural-core-halo { stroke: currentColor; opacity: .25; }
.neural-signal { stroke: currentColor; stroke-width: .8; opacity: .45; }
.neural-signal-group { animation: neural-signal-intensity 6s ease-in-out infinite; }
.neural-signal-trail { stroke: #d4ae5a; stroke-width: 4; stroke-linecap: round; stroke-dasharray: 15 85; filter: blur(3px); opacity: .5; animation: neural-signal-flow 3.6s linear infinite; }
.neural-signal-current { stroke: #ffedc3; stroke-width: 1.6; stroke-linecap: round; stroke-dasharray: 3 97; animation: neural-signal-flow 3.6s linear infinite; }
.is-paused :is(.neural-fibres,.neural-impulse,.neural-signal-group,.neural-signal-trail,.neural-signal-current) { animation-play-state: paused; }
@keyframes neural-signal-flow { from { stroke-dashoffset: 100; } to { stroke-dashoffset: 0; } }
@keyframes neural-signal-intensity { 0%,100% { opacity: .45; } 35% { opacity: 1; } 65% { opacity: .65; } }
@keyframes neural-breathe { 50% { transform: scale(1.045) rotate(3deg); } }
@keyframes neural-flow { from { stroke-dashoffset: 100; } to { stroke-dashoffset: -100; } }
@media (prefers-reduced-motion: reduce) { .neural-fibres, .neural-impulse, .neural-signal-group, .neural-signal-trail, .neural-signal-current { animation: none; } }
</style>
