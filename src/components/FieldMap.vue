<script setup>
/**
 * FieldMap — a vertical "Medical Treasure Map" wayfinder.
 *
 * A portrait, fully-transparent chart that lives in the Atlas left column and
 * stays sticky beside the SpecimenPlates. Medical domains are drawn as ragged,
 * weather-beaten pirate-map coastlines (fractal displacement, never smooth
 * splines). Each course is a waypoint plotted on its territory and reached by a
 * winding treasure trail: the completed stretch glows solid champagne gold, the
 * road ahead stays a faint dotted outline. A fully completed course drops its
 * trail entirely and is marked with the classic X.
 *
 * The empty sea is filled with fantasy-medical cartography: EEG mountain ranges,
 * vascular rivers that branch like cerebral vessels, and synaptic fortresses.
 *
 * It doubles as the index: as a plate scrolls into view its waypoint lights up
 * ("you are here"); clicking a waypoint redirects to that course's detail page
 * via <router-link>.
 *
 * Transparent by design — it renders straight onto the page substrate. Colours
 * use the gold/ink tokens, so it reads correctly on charcoal (#323A45, dark)
 * and parchment (light) alike. LTR-only; physical attributes throughout.
 *
 * Props: sections = [{ id, code, field, title, progress, to }]  (progress 0..1)
 */
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'

const props = defineProps({
  sections: { type: Array, required: true },
  label: { type: String, default: 'Course map' },
  rootMargin: { type: String, default: '-12% 0px -55% 0px' },
})

/* Enlarged canvas — taller landmasses, wider scatter, more room to breathe. */
const W = 360
const H = 1180
const TAU = Math.PI * 2

/* Domain → vintage label + organic seed; vertical order top→bottom. */
const REGION_META = {
  neurology: { name: 'Neurology', seed: 7 },
  general: { name: 'General Medicine', seed: 23 },
  psychEmergency: { name: 'Psychiatric Emergency', seed: 41 },
}
const ORDER = ['neurology', 'general', 'psychEmergency']

/* ── Seeded RNG (mulberry32) for deterministic, organic shapes ─────────── */
function rng(seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/* Periodic 1-D value noise: random values at `controls` points around the
   circle, smoothstep-interpolated. Periodic over t∈[0,1) so coastlines close
   seamlessly. */
function makeNoise1D(seed, controls) {
  const r = rng(seed)
  const vals = Array.from({ length: controls }, () => r() * 2 - 1)
  return (t) => {
    const x = t * controls
    const i = ((Math.floor(x) % controls) + controls) % controls
    const j = (i + 1) % controls
    const f = x - Math.floor(x)
    const u = f * f * (3 - 2 * f)
    return vals[i] * (1 - u) + vals[j] * u
  }
}

/* Jagged, weather-beaten coastline: an ellipse displaced by fractal (multi-
   octave) noise plus micro-spikes, connected with straight segments — ragged
   like a vintage pirate-map shore, not a smooth modern spline. */
function jaggedCoast(cx, cy, rx, ry, seed, points = 84, amps = [0.24, 0.13, 0.07, 0.04]) {
  const octaves = [
    makeNoise1D(seed, 5),
    makeNoise1D(seed + 1, 11),
    makeNoise1D(seed + 2, 23),
    makeNoise1D(seed + 3, 47),
  ]
  const r = rng(seed + 7)
  let d = ''
  for (let i = 0; i < points; i++) {
    const t = i / points
    const a = t * TAU
    let disp = 0
    for (let o = 0; o < octaves.length; o++) disp += octaves[o](t) * (amps[o] || 0)
    const spike = (r() - 0.5) * 0.06 // weather-beaten micro-jitter
    const f = 1 + disp + spike
    const x = cx + Math.cos(a) * rx * f
    const y = cy + Math.sin(a) * ry * f
    d += (i === 0 ? 'M ' : 'L ') + x.toFixed(1) + ' ' + y.toFixed(1) + ' '
  }
  return d + 'Z'
}

/* Vascular river: a winding trunk that flows down the landmass with a branch
   peeling off — reads as a cerebral vessel / neural tributary. */
function river(cx, cy, rx, ry, seed) {
  const r = rng(seed)
  let x = cx + (r() - 0.5) * rx * 0.5
  let y = cy - ry * 0.72
  let main = `M ${x.toFixed(1)} ${y.toFixed(1)} `
  const steps = 4
  const span = ry * 1.45
  const branches = []
  for (let i = 1; i <= steps; i++) {
    const nx = cx + (r() - 0.5) * rx * 1.05
    const ny = y + span / steps
    const c1x = x + (r() - 0.5) * rx * 0.45
    const c1y = y + (ny - y) * 0.4
    const c2x = nx + (r() - 0.5) * rx * 0.45
    const c2y = ny - (ny - y) * 0.4
    main += `C ${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${nx.toFixed(1)} ${ny.toFixed(1)} `
    if (i === 2) branches.push([nx, ny])
    x = nx
    y = ny
  }
  let branch = ''
  for (const [bx, by] of branches) {
    const ex = bx + (r() - 0.5) * rx * 0.9
    const ey = by + ry * 0.42
    branch += `M ${bx.toFixed(1)} ${by.toFixed(1)} Q ${(bx + (r() - 0.5) * rx * 0.5).toFixed(1)} ${((by + ey) / 2).toFixed(1)} ${ex.toFixed(1)} ${ey.toFixed(1)} `
  }
  return { main, branch }
}

/* EEG mountain range: a jagged ridge whose peaks and valleys mimic an EEG
   readout — occasional tall spikes over low background rhythm. */
function eegRidge(cx, cy, rx, ry, seed) {
  const r = rng(seed)
  const baseY = cy + ry * 0.52
  const w = rx * 1.35
  const x0 = cx - w / 2
  const n = 24
  let d = `M ${x0.toFixed(1)} ${baseY.toFixed(1)} `
  for (let i = 1; i <= n; i++) {
    const x = x0 + (w * i) / n
    const spike = r() < 0.24 ? 0.7 + r() * 0.55 : 0.12 + r() * 0.3 // rare tall peaks
    const peakY = baseY - spike * ry * 0.5
    d += `L ${x.toFixed(1)} ${peakY.toFixed(1)} `
    const xd = x0 + (w * (i + 0.5)) / n
    const valY = baseY - (0.04 + r() * 0.12) * ry * 0.5
    d += `L ${xd.toFixed(1)} ${valY.toFixed(1)} `
  }
  return d
}

/* Synaptic fortress: a battlemented tower (historic landmark) crowned with a
   neuron soma and radiating dendrites. Returns a placement; geometry is drawn
   inline so it stays a stable host node. */
function fortress(cx, cy, rx, ry, seed) {
  const r = rng(seed)
  return {
    x: Math.round(cx + (r() - 0.5) * rx * 0.7),
    y: Math.round(cy - ry * 0.46),
  }
}

/* Winding treasure trail leading up to a waypoint. Drawn start→node so the
   glowing "completed" stretch grows from the journey's start toward the goal. */
function nodeTrail(n, seed) {
  const r = rng(seed)
  const len = 50 + r() * 30
  const ang = 2.2 + r() * 1.8 // bias the approach from below/side
  const sx = n.x + Math.cos(ang) * len
  const sy = n.y + Math.sin(ang) * len * 0.7 + 26
  const m1x = sx + (n.x - sx) * 0.34 + (r() - 0.5) * 34
  const m1y = sy + (n.y - sy) * 0.34 + (r() - 0.5) * 34
  const midx = sx + (n.x - sx) * 0.6
  const midy = sy + (n.y - sy) * 0.6
  const m2x = midx + (r() - 0.5) * 30
  const m2y = midy + (r() - 0.5) * 30
  return `M ${sx.toFixed(1)} ${sy.toFixed(1)} C ${m1x.toFixed(1)} ${m1y.toFixed(1)} ${m2x.toFixed(1)} ${m2y.toFixed(1)} ${midx.toFixed(1)} ${midy.toFixed(1)} S ${m2x.toFixed(1)} ${m2y.toFixed(1)} ${n.x} ${n.y}`
}

/* Faint meandering nerve-tract — full-height background texture. */
function tract(seed) {
  const r = rng(seed)
  const steps = 5
  let d = `M ${(50 + r() * 260).toFixed(0)} -10 `
  for (let i = 1; i <= steps; i++) {
    const y = (H * i) / steps
    const cx1 = 50 + r() * 260, cy1 = y - H / steps + r() * 70
    const cx2 = 50 + r() * 260, cy2 = y - r() * 70
    d += `C ${cx1.toFixed(0)} ${cy1.toFixed(0)} ${cx2.toFixed(0)} ${cy2.toFixed(0)} ${(50 + r() * 260).toFixed(0)} ${y.toFixed(0)} `
  }
  return d
}
const tracts = [tract(101), tract(202)]

/* ── Model: regions (landmasses + iconography) + plotted waypoints ─────── */
const model = computed(() => {
  const groups = {}
  for (const s of props.sections) (groups[s.field] ||= []).push(s)

  const present = [
    ...ORDER.filter((f) => groups[f]),
    ...Object.keys(groups).filter((f) => !ORDER.includes(f)),
  ]
  const n = present.length || 1

  const regions = []
  const nodes = []

  present.forEach((field, ri) => {
    const meta = REGION_META[field] || { name: field, seed: 60 + ri * 7 }
    const cy = (H * (ri + 0.5)) / n
    const cx = 180 + (ri % 2 === 0 ? -18 : 18)
    const rx = 132
    const ry = Math.min((H / n) * 0.46, 200)

    const riv = river(cx, cy, rx, ry, meta.seed + 31)

    regions.push({
      field,
      name: meta.name,
      coast: jaggedCoast(cx, cy, rx, ry, meta.seed),
      echo: jaggedCoast(cx, cy, rx * 0.78, ry * 0.78, meta.seed + 5, 60, [0.2, 0.1, 0.05]),
      river: riv.main,
      branch: riv.branch,
      ridge: eegRidge(cx, cy, rx, ry, meta.seed + 17),
      fort: fortress(cx, cy, rx, ry, meta.seed + 53),
      label: { x: cx, y: cy - ry * 0.58 },
    })

    const items = groups[field]
    const r = rng(meta.seed + 99)
    items.forEach((s, k) => {
      const ty = items.length > 1 ? k / (items.length - 1) - 0.5 : 0
      const x = cx + (r() - 0.5) * rx * 0.95
      const y = cy + ty * ry * 1.05 + (r() - 0.5) * ry * 0.18
      const node = {
        ...s,
        to: s.to || '#',
        x: Math.round(x),
        y: Math.round(y),
        complete: s.progress >= 1,
        started: s.progress > 0 && s.progress < 1,
      }
      node.trail = nodeTrail(node, meta.seed + 200 + k)
      nodes.push(node)
    })
  })

  return { regions, nodes }
})

/* ── Wayfinder: active waypoint tracks the in-view plate ───────────────── */
const activeId = ref(props.sections[0]?.id ?? null)
const hoveredId = ref(null)
const visible = new Set()
let observer = null

const recomputeActive = () => {
  for (const s of props.sections) {
    if (visible.has(s.id)) { activeId.value = s.id; return }
  }
}
const onIntersect = (entries) => {
  for (const e of entries) {
    if (e.isIntersecting) visible.add(e.target.id)
    else visible.delete(e.target.id)
  }
  recomputeActive()
}
const observeSections = () => {
  observer?.disconnect()
  observer = new IntersectionObserver(onIntersect, { rootMargin: props.rootMargin, threshold: 0 })
  for (const s of props.sections) {
    const el = document.getElementById(s.id)
    if (el) observer.observe(el)
  }
}

watch(
  () => props.sections.map((s) => s.id).join('|'),
  async () => {
    visible.clear()
    if (!props.sections.some((s) => s.id === activeId.value)) {
      activeId.value = props.sections[0]?.id ?? null
    }
    await nextTick()
    observeSections()
  }
)

onMounted(observeSections)
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div class="treasuremap">
    <svg class="treasuremap__svg" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="xMidYMid meet" role="navigation" :aria-label="label">
      <defs>
        <filter id="tm-glow" x="-70%" y="-70%" width="240%" height="240%">
          <feGaussianBlur stdDeviation="2" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <!-- Faint nerve-tract routes (background texture) -->
      <g aria-hidden="true">
        <path v-for="(t, i) in tracts" :key="i" class="tm-tract" :d="t" />
      </g>

      <!-- Organic landmasses + fantasy-medical cartography -->
      <g aria-hidden="true">
        <g v-for="r in model.regions" :key="r.field">
          <path class="tm-coast" :d="r.coast" />
          <path class="tm-coast-echo" :d="r.echo" />

          <!-- Vascular rivers (branch like cerebral vessels) -->
          <path class="tm-river" :d="r.river" />
          <path class="tm-river tm-river--branch" :d="r.branch" />

          <!-- EEG mountain range -->
          <path class="tm-ridge" :d="r.ridge" />

          <!-- Synaptic fortress: battlemented tower + neuron soma & dendrites -->
          <g class="tm-fort" :transform="`translate(${r.fort.x} ${r.fort.y})`">
            <path class="tm-fort-tower" d="M -6 0 L -6 -15 L -4 -15 L -4 -18 L -1.5 -18 L -1.5 -15 L 1.5 -15 L 1.5 -18 L 4 -18 L 4 -15 L 6 -15 L 6 0 Z" />
            <line class="tm-fort-dend" x1="0" y1="-22" x2="-6" y2="-30" />
            <line class="tm-fort-dend" x1="0" y1="-22" x2="6" y2="-30" />
            <line class="tm-fort-dend" x1="0" y1="-22" x2="0" y2="-32" />
            <circle class="tm-fort-end" cx="-6" cy="-30" r="1.2" />
            <circle class="tm-fort-end" cx="6" cy="-30" r="1.2" />
            <circle class="tm-fort-end" cx="0" cy="-32" r="1.2" />
            <circle class="tm-fort-soma" cx="0" cy="-22" r="3.2" />
          </g>

          <text class="tm-region" :x="r.label.x" :y="r.label.y">{{ r.name }}</text>
        </g>
      </g>

      <!-- Treasure trails (under the waypoints). None drawn for completed
           courses — those carry only the X. -->
      <g class="tm-trails" aria-hidden="true">
        <g v-for="n in model.nodes" :key="n.id" v-show="!n.complete">
          <!-- road ahead: faint, darker, dotted -->
          <path class="tm-trail-base" :d="n.trail" />
          <!-- completed stretch: solid champagne gold, glowing, revealed by progress -->
          <path
            class="tm-trail-done"
            v-show="n.started"
            :d="n.trail"
            pathLength="1"
            :style="{ strokeDashoffset: String(1 - n.progress) }"
          />
        </g>
      </g>

      <!-- Waypoints — each a real router-link to the course detail page -->
      <g class="tm-nodes">
        <router-link
          v-for="n in model.nodes"
          :key="n.id"
          :to="n.to"
          custom
          v-slot="{ href, navigate }"
        >
          <a
            class="tm-node"
            :class="{ 'is-active': n.id === activeId, 'is-complete': n.complete, 'is-started': n.started }"
            :href="href"
            tabindex="0"
            :aria-label="`${n.code} — ${n.title}${n.complete ? ', completed' : n.started ? `, ${Math.round(n.progress * 100)}% complete` : ''}`"
            @click="navigate"
            @keydown.enter.prevent="navigate"
            @keydown.space.prevent="navigate"
            @mouseenter="hoveredId = n.id"
            @mouseleave="hoveredId = null"
            @focus="hoveredId = n.id"
            @blur="hoveredId = null"
          >
            <!-- generous transparent hit target -->
            <circle class="tm-hit" :cx="n.x" :cy="n.y" r="18" />

            <!-- glowing halo for active / in-progress -->
            <circle
              class="tm-halo"
              v-show="n.id === activeId || n.started"
              :cx="n.x"
              :cy="n.y"
              :r="n.id === activeId ? 13 : 9"
            />

            <!-- marker: X marks a completed course, otherwise a synaptic dot -->
            <line class="tm-x" v-show="n.complete" :x1="n.x - 5.5" :y1="n.y - 5.5" :x2="n.x + 5.5" :y2="n.y + 5.5" />
            <line class="tm-x" v-show="n.complete" :x1="n.x - 5.5" :y1="n.y + 5.5" :x2="n.x + 5.5" :y2="n.y - 5.5" />
            <circle class="tm-dot" v-show="!n.complete" :cx="n.x" :cy="n.y" :r="n.id === activeId ? 5 : n.started ? 4 : 3" />

            <!-- 'you are here' crosshair on the active waypoint -->
            <g class="tm-cross" v-show="n.id === activeId">
              <line :x1="n.x" :y1="n.y - 17" :x2="n.x" :y2="n.y - 11" />
              <line :x1="n.x" :y1="n.y + 11" :x2="n.x" :y2="n.y + 17" />
              <line :x1="n.x - 17" :y1="n.y" :x2="n.x - 11" :y2="n.y" />
              <line :x1="n.x + 11" :y1="n.y" :x2="n.x + 17" :y2="n.y" />
            </g>

            <text class="tm-code" :x="n.x + 15" :y="n.y + 3.5">{{ n.code }}</text>
            <text class="tm-title" v-show="n.id === activeId || n.id === hoveredId" :x="n.x + 15" :y="n.y + 18">{{ n.title }}</text>
          </a>
        </router-link>
      </g>
    </svg>
  </div>
</template>

<style scoped>
/* Transparent — no background, border or shadow. Colours use the gold/ink
   tokens so the chart blends onto charcoal (dark) or parchment (light).
   In the academy charcoal scope, --c-gold-light resolves to champagne #F4D791. */
.treasuremap {
  width: 100%;
  height: 100%;
  min-height: 74vh;
}
.treasuremap__svg {
  width: 100%;
  height: 100%;
  display: block;
  overflow: visible;
}

/* ── Nerve tracts ──────────────────────────────────────────────────────── */
.tm-tract {
  fill: none;
  stroke: rgb(var(--c-gold) / 0.08);
  stroke-width: 1;
  stroke-dasharray: 1 7;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

/* ── Landmasses (ragged coastlines) ────────────────────────────────────── */
.tm-coast {
  fill: rgb(var(--c-gold) / 0.035);
  stroke: rgb(var(--c-gold) / 0.46);
  stroke-width: 1.1;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.tm-coast-echo {
  fill: none;
  stroke: rgb(var(--c-gold) / 0.16);
  stroke-width: 1;
  stroke-dasharray: 2 4;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.tm-region {
  fill: rgb(var(--c-ink-muted));
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-style: italic;
  font-size: 17px;
  letter-spacing: 0.12em;
  text-anchor: middle;
}

/* ── Fantasy-medical cartography ───────────────────────────────────────── */
.tm-river {
  fill: none;
  stroke: rgb(var(--c-gold) / 0.22);
  stroke-width: 1.2;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
.tm-river--branch { stroke: rgb(var(--c-gold) / 0.14); stroke-width: 1; }

.tm-ridge {
  fill: none;
  stroke: rgb(var(--c-gold) / 0.24);
  stroke-width: 1;
  stroke-linejoin: round;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}

.tm-fort-tower {
  fill: rgb(var(--c-gold) / 0.06);
  stroke: rgb(var(--c-gold) / 0.4);
  stroke-width: 1;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}
.tm-fort-dend { stroke: rgb(var(--c-gold) / 0.3); stroke-width: 1; stroke-linecap: round; vector-effect: non-scaling-stroke; }
.tm-fort-end { fill: rgb(var(--c-gold) / 0.45); }
.tm-fort-soma { fill: none; stroke: rgb(var(--c-gold) / 0.5); stroke-width: 1; vector-effect: non-scaling-stroke; }

/* ── Treasure trails ───────────────────────────────────────────────────── */
.tm-trail-base {
  fill: none;
  stroke: rgb(var(--c-gold) / 0.16);
  stroke-width: 1.4;
  stroke-dasharray: 1.5 5;
  stroke-linecap: round;
  vector-effect: non-scaling-stroke;
}
.tm-trail-done {
  fill: none;
  stroke: rgb(var(--c-gold-light));
  stroke-width: 2.6;
  stroke-linecap: round;
  /* pathLength="1": one full-length dash + one gap; dashoffset (1 − progress)
     reveals the completed stretch solid from the journey's start. */
  stroke-dasharray: 1 1;
  filter: url(#tm-glow);
  transition: stroke-dashoffset 0.5s ease;
}

/* ── Waypoints ─────────────────────────────────────────────────────────── */
.tm-node { cursor: pointer; outline: none; }
.tm-hit { fill: transparent; }

.tm-halo {
  fill: none;
  stroke: rgb(var(--c-gold) / 0.3);
  stroke-width: 1;
  stroke-dasharray: 2 3;
  transition: stroke 0.35s ease;
}
.tm-dot { fill: rgb(var(--c-gold) / 0.42); transition: fill 0.35s ease, r 0.35s ease; }
.is-started .tm-dot { fill: rgb(var(--c-gold)); }
.tm-x { stroke: rgb(var(--c-gold)); stroke-width: 1.8; stroke-linecap: round; transition: stroke 0.35s ease; }
.tm-cross line { stroke: rgb(var(--c-gold-light)); stroke-width: 1; opacity: 0.8; }

.tm-code {
  fill: rgb(var(--c-ink-muted));
  font-size: 11px;
  letter-spacing: 0.12em;
  font-feature-settings: "tnum" 1;
  dominant-baseline: middle;
  transition: fill 0.35s ease;
}
.tm-title {
  fill: rgb(var(--c-ink-soft));
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-style: italic;
  font-size: 14px;
}

/* Active ("you are here") */
.is-active .tm-halo { stroke: rgb(var(--c-gold-light) / 0.65); filter: url(#tm-glow); animation: tm-breathe 2.6s ease-in-out infinite; }
.is-active .tm-dot { fill: rgb(var(--c-gold-light)); filter: url(#tm-glow); }
.is-active .tm-x { stroke: rgb(var(--c-gold-light)); filter: url(#tm-glow); }
.is-active .tm-code { fill: rgb(var(--c-gold)); }

/* Hover / focus echo of the active treatment */
.tm-node:hover .tm-code,
.tm-node:focus-visible .tm-code { fill: rgb(var(--c-ink)); }
.tm-node:focus-visible .tm-dot { stroke: rgb(var(--c-gold-light)); stroke-width: 1; }

@keyframes tm-breathe {
  0%, 100% { opacity: 0.75; }
  50% { opacity: 0.3; }
}

@media (prefers-reduced-motion: reduce) {
  .is-active .tm-halo { animation: none; }
  .tm-halo, .tm-dot, .tm-x, .tm-code, .tm-trail-done { transition: none; }
}
</style>
