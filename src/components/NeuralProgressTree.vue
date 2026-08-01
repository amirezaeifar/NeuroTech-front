<script setup>
/**
 * NeuralProgressTree — an organic, luminous neuron for "Browse the Library".
 *
 * A procedurally-grown biological neuron (soma, apical trunk, asymmetric
 * dendritic arbor, basal roots) rendered as pure-white light on a STRICTLY
 * transparent background — no panel, no glass, no border. It overlays directly
 * on whatever sits behind it.
 *
 *   • Shape      — every stroke is an organic Bézier branch grown from a seeded
 *                  RNG, so the arbor is asymmetric and fractal (never rigid).
 *                  Main branches carry Course nodes; dendrites sprouting off
 *                  them carry the learner's module / "video watched" nodes.
 *   • Light      — layered feGaussianBlur + feMerge bloom gives an intense,
 *                  shiny white neon glow with zero CSS background tricks.
 *   • Currents   — a continuous, fluid light flow (NOT dashed segments): a
 *                  repeating silver→white "comet" gradient (#npt-flow) streams
 *                  along the arbor. A rAF loop translates the gradient and reads
 *                  scroll velocity to drive the neuron's "energy" — fast scroll
 *                  brightens the flow, grows the bloom and speeds the travel;
 *                  at rest it eases down to a slow breathing pulse (see frame()).
 *   • The Pulse  — the node for the last-watched video (currentNodeId) emits a
 *                  continuous expanding glow, driven by useMotion().
 *
 * Sticky: the component pins itself (position: sticky; top) so the neuron stays
 * fixed in the viewport while the long library page scrolls past — the scroll is
 * what energises the currents.
 *
 * Accessibility / perf: respects prefers-reduced-motion (the flow freezes to a
 * low static glow, the pulse stops); the heavy bloom is rasterised over the
 * STATIC arbor (cached), while only the single gradient transform + the flow
 * group's opacity/bloom update per frame, targeting 60fps.
 *
 * Scope note: LTR-only, like the other Atlas wayfinders — physical coordinates.
 */
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useMotion, useReducedMotion } from '@vueuse/motion'
import { userProgress } from '../data/userProgress.js'

const props = defineProps({
  /** userProgress payload (see src/data/userProgress.js). */
  data: { type: Object, default: () => userProgress },
  /** Optional CSS selector for the scroll track; defaults to [data-progress-track]. */
  track: { type: String, default: '' },
  /** Sticky offset from the top of the viewport, in px. */
  stickyTop: { type: Number, default: 24 },
  /**
   * Whether the component positions itself `sticky`. Set false when an outer
   * wrapper owns the stickiness (e.g. so a faded underlay travels with it).
   */
  sticky: { type: Boolean, default: true },
  /** How many traversals a full page-scroll drives through the arbor. */
  currentSpeed: { type: Number, default: 3.2 },
  /**
   * Maps a clicked node → a router target. Receives the node
   * ({ id, type:'course'|'module', courseIndex, title, status, code }).
   * Defaults to the existing course-detail route, keyed by course index.
   */
  resolveRoute: { type: Function, default: null },
})

/* ── Canvas ────────────────────────────────────────────────────────────────── */
const VB_W = 380
const VB_H = 860
const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v)
const TAU = Math.PI * 2

/* Deterministic RNG so the arbor is identical every render (no jitter on
   re-computation). mulberry32. */
function makeRng(seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/* Grow one organic branch as a chain of quadratic Béziers that wanders away
   from `angle`, tapering as it goes. Returns the path `d`, the sampled points
   (for placing nodes & child branches) and the final heading. */
function growBranch(sx, sy, angle, length, segs, curl, rng) {
  let x = sx
  let y = sy
  let a = angle
  const pts = [{ x, y }]
  const segLen = length / segs
  let d = `M ${x.toFixed(1)} ${y.toFixed(1)}`
  for (let i = 0; i < segs; i++) {
    a += (rng() - 0.5) * curl
    const cx = x + Math.cos(a) * segLen * 0.5 + (rng() - 0.5) * segLen * 0.35
    const cy = y + Math.sin(a) * segLen * 0.5 + (rng() - 0.5) * segLen * 0.35
    x += Math.cos(a) * segLen
    y += Math.sin(a) * segLen
    d += ` Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)}`
    pts.push({ x, y })
  }
  return { d, pts, endAngle: a, end: { x, y }, length }
}

/* Linear sample of a point a fraction `f` (0→1) along a branch's points. */
function pointAt(pts, f) {
  const i = clamp01(f) * (pts.length - 1)
  const lo = Math.floor(i)
  const hi = Math.min(lo + 1, pts.length - 1)
  const t = i - lo
  return { x: pts[lo].x + (pts[hi].x - pts[lo].x) * t, y: pts[lo].y + (pts[hi].y - pts[lo].y) * t }
}

/* ── Grow the whole arbor from the learner's curriculum ────────────────────── */
const arbor = computed(() => {
  const rng = makeRng(20240611)
  const courses = props.data?.courses ?? []

  const filaments = [] // decorative fractal twigs / roots (dim)
  const branches = [] // main course branches (mid)
  const currents = [] // paths the action potentials travel along
  const courseNodes = []
  const moduleNodes = []

  const soma = { x: VB_W * 0.5, y: VB_H * 0.7 }

  // Recursively spawn small child filaments off a parent branch for density.
  // Three children per level + deeper recursion = a denser, more fractal arbor
  // of fine sub-dendrites (the smaller twigs that read as biological detail).
  function fractal(parent, depth, lengthScale) {
    if (depth <= 0) return
    const spawnCount = 3
    for (let s = 0; s < spawnCount; s++) {
      const f = 0.3 + rng() * 0.65
      const p = pointAt(parent.pts, f)
      const side = rng() < 0.5 ? -1 : 1
      const a = parent.endAngle + side * (0.45 + rng() * 0.8)
      const child = growBranch(p.x, p.y, a, parent.length * lengthScale, 5 + ((rng() * 3) | 0), 0.55, rng)
      filaments.push({ d: child.d, w: Math.max(0.45, 1.4 * lengthScale), o: 0.15 + depth * 0.05 })
      fractal(child, depth - 1, lengthScale * 0.6)
    }
  }

  // ── Apical trunk: rises from the soma; courses branch off it. ──
  const trunk = growBranch(soma.x, soma.y, -Math.PI / 2, VB_H * 0.6, 16, 0.16, rng)
  currents.push({ d: trunk.d, phase: 0 })

  // ── Course main-branches, alternating sides up the trunk. ──
  courses.forEach((course, ci) => {
    const f = 0.14 + (ci / Math.max(courses.length, 1)) * 0.74 + rng() * 0.05
    const base = pointAt(trunk.pts, f)
    const side = ci % 2 === 0 ? -1 : 1
    const a = -Math.PI / 2 + side * (0.55 + rng() * 0.35)
    const len = 150 + rng() * 70
    const branch = growBranch(base.x, base.y, a, len, 10, 0.34, rng)
    branches.push({ d: branch.d })
    currents.push({ d: branch.d, phase: 0.12 + ci * 0.21 })

    // Course node sits a little way out along its branch.
    const cn = pointAt(branch.pts, 0.18)
    courseNodes.push({
      id: course.id, x: cn.x, y: cn.y, status: course.status,
      title: course.title, code: course.code, type: 'course', courseIndex: ci,
    })

    // Module nodes distributed along the branch; each sprouts a dendrite tuft.
    const mods = course.modules ?? []
    mods.forEach((m, mi) => {
      const mf = 0.42 + (mi / Math.max(mods.length, 1)) * 0.5
      const mp = pointAt(branch.pts, mf)
      moduleNodes.push({
        id: m.id, x: mp.x, y: mp.y, status: m.status,
        title: m.title, type: 'module', courseIndex: ci,
      })
      // dendrite tufts off the module — two splayed tufts, each branching
      // deeply into fine sub-dendrites for a dense, natural cluster.
      for (let k = 0; k < 2; k++) {
        const tuft = growBranch(mp.x, mp.y, a + (rng() - 0.5) * 1.7, 30 + rng() * 30, 5, 0.65, rng)
        filaments.push({ d: tuft.d, w: 0.9, o: 0.28 })
        fractal(tuft, 2, 0.55)
      }
    })

    fractal(branch, 2, 0.5)
  })

  // ── Apical tuft: dense canopy where the trunk ends. ──
  const tip = trunk.end
  for (let i = 0; i < 13; i++) {
    const a = -Math.PI / 2 + (rng() - 0.5) * 1.9
    const t = growBranch(tip.x, tip.y, a, 70 + rng() * 85, 7, 0.48, rng)
    filaments.push({ d: t.d, w: 1.1, o: 0.3 })
    fractal(t, 2, 0.55)
  }

  // ── Basal roots & axon: fan downward/out from the soma. ──
  for (let i = 0; i < 13; i++) {
    const a = Math.PI / 2 + (rng() - 0.5) * 2.5
    const t = growBranch(soma.x, soma.y, a, 90 + rng() * 115, 9, 0.42, rng)
    filaments.push({ d: t.d, w: 1.0, o: 0.24 })
    fractal(t, 2, 0.58)
  }

  // ── Extra fine sub-branches on the LEFT flank — adds organic, biological
  //    density and a deliberate left/right asymmetry. Twigs sprout leftward
  //    (≈180°) from points along the trunk and each branch into sub-dendrites. ──
  for (let i = 0; i < 12; i++) {
    const f = 0.18 + rng() * 0.72
    const base = pointAt(trunk.pts, f)
    const a = Math.PI + (rng() - 0.5) * 1.7   // ~180° → left, with vertical spread
    const t = growBranch(base.x, base.y, a, 36 + rng() * 66, 6, 0.55, rng)
    filaments.push({ d: t.d, w: 0.8, o: 0.2 })
    fractal(t, 2, 0.55)
  }

  return { soma, trunkD: trunk.d, filaments, branches, currents, courseNodes, moduleNodes }
})

/* The last-watched node — pulses. */
const currentNode = computed(() => {
  const id = props.data?.currentNodeId
  return (
    arbor.value.moduleNodes.find((n) => n.id === id) ||
    arbor.value.courseNodes.find((n) => n.id === id) ||
    null
  )
})

const nodeGlow = (status) =>
  status === 'completed' ? 0.95 : status === 'in-progress' ? 0.9 : 0.32
const nodeR = (status, base) => (status === 'completed' || status === 'in-progress' ? base : base * 0.7)

/* Every interactive node (courses + modules), in one list for the hit layer. */
const allNodes = computed(() => [...arbor.value.courseNodes, ...arbor.value.moduleNodes])

/* ── Hover tooltip + click navigation ──────────────────────────────────────── */
const router = useRouter()

const STATUS_LABEL = { completed: 'Completed', 'in-progress': 'In progress', locked: 'Locked' }
const statusLabel = (s) => STATUS_LABEL[s] || s
const typeLabel = (n) => (n.type === 'course' ? 'Course' : 'Module')

const hovered = ref(null)
// Pointer position + container width, in the overlay's local coordinates.
const ptr = reactive({ x: 0, y: 0, w: 0 })

function updatePtr(e) {
  const r = rootEl.value?.getBoundingClientRect()
  if (!r) return
  ptr.x = e.clientX - r.left
  ptr.y = e.clientY - r.top
  ptr.w = r.width
}
function onNodeEnter(node, e) {
  hovered.value = node
  updatePtr(e)
}
function onNodeMove(e) {
  if (hovered.value) updatePtr(e)
}
function onNodeLeave() {
  hovered.value = null
}

// Flip the tooltip to the cursor's left when near the right edge.
const tipStyle = computed(() => {
  const flip = ptr.x > ptr.w - 200
  return {
    left: `${ptr.x}px`,
    top: `${ptr.y}px`,
    transform: `translate(${flip ? 'calc(-100% - 16px)' : '16px'}, -50%)`,
  }
})

const defaultRoute = (node) => `/academy/course/${node.courseIndex}`
function onNodeClick(node) {
  const to = (props.resolveRoute || defaultRoute)(node)
  if (to) router.push(to)
}

/* ── Reduced motion ────────────────────────────────────────────────────────── */
const reduced = useReducedMotion()

const rootEl = ref(null)

/* ── Scroll-velocity-driven light flow ────────────────────────────────────────
   The travelling current is a repeating silver→white gradient (see <defs>): a
   train of "comets", each a hot white head trailing a soft silver tail. A rAF
   loop continuously advances the gradient (fluid — never dashed/segmented) and
   reads scroll velocity to drive the neuron's "energy":
     • fast scroll → brighter flow, larger bloom, faster travel ("excited"),
     • idle        → energy eases down to a calm, slowly-pulsing resting glow.
   prefers-reduced-motion freezes the travel and holds a low static glow. */
const FLOW_PERIOD = 230          // gradient repeat length (viewBox units)
const flowY = ref(0)             // animated gradient translate — the travel
const flowOpacity = ref(0.4)     // flow brightness (energy-mapped)
const flowGlow = ref(3)          // bloom radius in px (energy-mapped)

let rafId = 0
let lastScrollY = 0
let lastTs = 0
let vel = 0                      // smoothed scroll velocity (px / frame)
let energy = 0.15                // smoothed excitement, 0..1

function frame(ts) {
  const dt = lastTs ? Math.min((ts - lastTs) / 16.67, 3) : 1   // frames elapsed
  lastTs = ts

  const sy = window.scrollY || document.documentElement.scrollTop || 0
  vel += (Math.abs(sy - lastScrollY) - vel) * 0.3
  lastScrollY = sy

  // Excite quickly with velocity; dim slowly when it drops (elegant settle).
  const target = clamp01(vel / 45)
  energy += (target - energy) * (target > energy ? 0.25 : 0.035)

  // Resting floor: a slow breathing pulse so the neuron is never fully dark.
  const e = Math.max(energy, 0.14 + 0.06 * Math.sin(ts / 720))

  // Travel: idle drift + velocity surge. Negative → currents rise up the trunk.
  const speed = (0.5 + e * 4.2) * props.currentSpeed * 0.6
  // Round to keep DOM writes stable (no sub-pixel thrash) while staying smooth.
  flowY.value = Math.round(((flowY.value - speed * dt) % FLOW_PERIOD) * 10) / 10
  flowOpacity.value = Math.round((0.32 + e * 0.68) * 100) / 100
  flowGlow.value = Math.round((2 + e * 11) * 10) / 10

  rafId = requestAnimationFrame(frame)
}

/* ── The Pulse — useMotion() on the active node's expanding ring ───────────── */
const pulseEl = ref(null)
const pulseVariants = computed(() =>
  reduced.value
    ? { initial: { opacity: 0 }, enter: { opacity: 0 } }
    : {
        initial: { scale: 0.4, opacity: 0.85 },
        enter: {
          scale: 3.4,
          opacity: 0,
          transition: { duration: 1600, repeat: Infinity, repeatType: 'loop', ease: 'easeOut' },
        },
      },
)
useMotion(pulseEl, pulseVariants)

onMounted(() => {
  if (reduced.value) {
    flowOpacity.value = 0.5   // static, low-energy glow; no travel
    flowGlow.value = 3
    return
  }
  lastScrollY = window.scrollY || 0
  rafId = requestAnimationFrame(frame)
})
onBeforeUnmount(() => {
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<template>
  <div ref="rootEl" :class="['npt', { 'npt--sticky': sticky }]" :style="{ '--npt-top': stickyTop + 'px' }" aria-label="Learning pathway — neural progress">
    <svg
      class="npt__svg"
      :viewBox="`0 0 ${VB_W} ${VB_H}`"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="Organic neuron visualising course and module progress"
    >
      <defs>
        <!-- Intense white bloom: stacked blurs merged back over the source. -->
        <filter id="npt-bloom" x="-60%" y="-60%" width="220%" height="220%" color-interpolation-filters="sRGB">
          <feGaussianBlur in="SourceGraphic" stdDeviation="1.4" result="b1" />
          <feGaussianBlur in="SourceGraphic" stdDeviation="5" result="b2" />
          <feGaussianBlur in="SourceGraphic" stdDeviation="13" result="b3" />
          <feMerge>
            <feMergeNode in="b3" />
            <feMergeNode in="b2" />
            <feMergeNode in="b3" />
            <feMergeNode in="b1" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <!-- Tighter, hotter bloom for the travelling currents & nodes. -->
        <filter id="npt-core" x="-200%" y="-200%" width="500%" height="500%" color-interpolation-filters="sRGB">
          <feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="c1" />
          <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="c2" />
          <feMerge>
            <feMergeNode in="c2" />
            <feMergeNode in="c1" />
            <feMergeNode in="c1" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>

        <!-- Travelling light current: a repeating silver→white "comet" gradient.
             spreadMethod="repeat" tiles it into a continuous train of pulses; the
             rAF loop translates it along the arbor for a fluid, non-segmented
             flow. Non-linear stops give a bright white head and a soft silver
             tail, so each pulse reads as an organic comet rather than a band. -->
        <linearGradient
          id="npt-flow"
          gradientUnits="userSpaceOnUse"
          x1="0" y1="0" x2="0" :y2="FLOW_PERIOD"
          spreadMethod="repeat"
          :gradientTransform="`translate(0 ${flowY})`"
        >
          <stop offset="0" stop-color="#D1D5DB" stop-opacity="0" />
          <stop offset="0.40" stop-color="#D1D5DB" stop-opacity="0.22" />
          <stop offset="0.62" stop-color="#E9EDF2" stop-opacity="0.6" />
          <stop offset="0.74" stop-color="#FFFFFF" stop-opacity="1" />
          <stop offset="0.80" stop-color="#FFFFFF" stop-opacity="0.95" />
          <stop offset="0.88" stop-color="#D1D5DB" stop-opacity="0" />
          <stop offset="1" stop-color="#D1D5DB" stop-opacity="0" />
        </linearGradient>

        <!-- Soma mask: hides the travelling current within a disc around the
             central base node, so the flow stops at the node's edge and the
             node core stays clean and static. White = visible, black = hidden. -->
        <mask id="npt-soma-mask" maskUnits="userSpaceOnUse" x="0" y="0" :width="VB_W" :height="VB_H">
          <rect x="0" y="0" :width="VB_W" :height="VB_H" fill="#FFFFFF" />
          <circle :cx="arbor.soma.x" :cy="arbor.soma.y" r="15" fill="#000000" />
        </mask>
      </defs>

      <!-- ░░ STATIC ARBOR (bloomed once, cached) ░░
           Stroke/fill colours come from CSS vars (see <style>) so the arbor is
           luminous white in dark mode and dark-charcoal ink in light mode. -->
      <g class="npt__arbor" filter="url(#npt-bloom)" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <!-- decorative fractal filaments / roots -->
        <path
          v-for="(f, i) in arbor.filaments"
          :key="`f-${i}`"
          :d="f.d"
          :stroke-width="f.w"
          :stroke-opacity="f.o"
        />
        <!-- main course branches -->
        <path
          v-for="(b, i) in arbor.branches"
          :key="`b-${i}`"
          :d="b.d"
          stroke-width="2"
          stroke-opacity="0.55"
        />
        <!-- apical trunk -->
        <path :d="arbor.trunkD" stroke-width="3" stroke-opacity="0.72" />
        <!-- soma (cell body) -->
        <circle class="npt__soma" :cx="arbor.soma.x" :cy="arbor.soma.y" r="10" stroke="none" opacity="0.9" />
      </g>

      <!-- ░░ NEURAL CURRENTS — a fluid silver→white light flow ░░
           Stroke is the travelling gradient (#npt-flow), not a dash pattern, so
           the flow is continuous. Group opacity and a layered drop-shadow bloom
           are driven by scroll velocity (see frame()): the flow surges and
           brightens as you scroll, then settles to a calm pulse at rest. -->
      <g
        class="npt__currents"
        fill="none"
        stroke-linecap="round"
        mask="url(#npt-soma-mask)"
        :style="{
          opacity: flowOpacity,
          filter: `drop-shadow(0 0 ${flowGlow * 0.45}px rgba(255,255,255,${0.55 + 0.4 * flowOpacity})) drop-shadow(0 0 ${flowGlow}px rgba(209,213,219,${0.35 + 0.4 * flowOpacity}))`,
        }"
      >
        <path
          v-for="(c, i) in arbor.currents"
          :key="`c-${i}`"
          :d="c.d"
          stroke="url(#npt-flow)"
          :stroke-width="i === 0 ? 3.4 : 2.4"
        />
      </g>

      <!-- ░░ NODES ░░ — gold in light mode, white in dark mode (via CSS var). -->
      <g class="npt__nodes" filter="url(#npt-core)" stroke="none">
        <circle
          v-for="n in arbor.courseNodes"
          :key="n.id"
          :cx="n.x" :cy="n.y" :r="nodeR(n.status, 3.4)"
          :opacity="nodeGlow(n.status)"
        />
        <circle
          v-for="n in arbor.moduleNodes"
          :key="n.id"
          :cx="n.x" :cy="n.y" :r="nodeR(n.status, 2.2)"
          :opacity="nodeGlow(n.status)"
        />
      </g>

      <!-- ░░ THE PULSE — last watched video ░░ -->
      <g v-if="currentNode" filter="url(#npt-core)" :transform="`translate(${currentNode.x} ${currentNode.y})`">
        <circle ref="pulseEl" class="npt-pulse" r="4" fill="none" stroke-width="1.2" />
        <circle class="npt__pulse-core" r="2.8" />
      </g>

      <!-- ░░ HIT AREAS — invisible, pointer-enabled (hover + click) ░░
           Drawn last so they sit on top for hit-testing; transparent fill with
           pointer-events:all so the whole disc is grabbable. The decorative
           layers stay pointer-events:none, leaving the page beneath clickable. -->
      <g class="npt-hits">
        <circle
          v-for="n in allNodes"
          :key="`hit-${n.id}`"
          class="npt-hit"
          :cx="n.x" :cy="n.y"
          :r="n.type === 'course' ? 14 : 10"
          fill="transparent"
          @mouseenter="onNodeEnter(n, $event)"
          @mousemove="onNodeMove($event)"
          @mouseleave="onNodeLeave"
          @click="onNodeClick(n)"
        />
      </g>
    </svg>

    <!-- ░░ HOVER TOOLTIP — dark-glass, low-opacity, follows the cursor ░░ -->
    <Transition name="npt-tip">
      <div v-if="hovered" class="npt-tip" :style="tipStyle" aria-hidden="true">
        <span class="npt-tip__type">
          {{ typeLabel(hovered) }}<template v-if="hovered.code"> · {{ hovered.code }}</template>
        </span>
        <span class="npt-tip__title">{{ hovered.title }}</span>
        <span class="npt-tip__status" :data-s="hovered.status">
          <i class="npt-tip__dot"></i>{{ statusLabel(hovered.status) }}
        </span>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Strictly transparent — no background, panel, border or glass. LTR-only. */
.npt {
  position: relative;
  width: 100%;
  background: transparent;
  pointer-events: none; /* purely decorative overlay */

  /* ── Theme palette ────────────────────────────────────────────────────────
     LIGHT MODE (default): a sleek dark-metallic / ink neural structure —
     branches & soma in brand charcoal (#323A45), muted-charcoal nodes, and a
     cool-silver active-node pulse. The travelling current itself is a fixed
     silver→white metallic flow (the #npt-flow gradient), the same in both modes.
     DARK MODE (html.dark, in src/style.css) makes branches & nodes luminous
     white. Heavy contrast against the page in either theme. */
  --npt-branch: #323A45;   /* dendrites, branches, trunk, soma (charcoal ink) */
  --npt-current: #C9CED6;  /* active-node pulse — cool silver (matches the flow) */
  --npt-node: #20262E;     /* course/module nodes — a darker, muted charcoal so
                              they read as part of the body, not separate dots  */
}
/* DARK MODE keeps the original pure-white luminous network — the override lives
   in the global stylesheet (src/style.css, `html.dark .npt`), matching how the
   rest of the app's dark theming is done; scoped `:global()` is unreliable here. */

/* Wire the palette into the SVG. CSS stroke/fill override the (removed) white
   presentation attributes and let the bloom filter glow in the theme colour. */
.npt__arbor { stroke: var(--npt-branch); }
.npt__soma { fill: var(--npt-branch); }
.npt__currents { stroke: var(--npt-current); }
.npt__nodes { fill: var(--npt-node); }
.npt-pulse { stroke: var(--npt-current); }
.npt__pulse-core { fill: var(--npt-current); }
.npt--sticky {
  position: sticky;
  top: var(--npt-top, 24px);
}
.npt__svg {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 380 / 860; /* matches the viewBox; tall portrait, fits viewport */
  margin: 0 auto;
  overflow: visible;
}

/* The active-node ripple scales about its own centre. */
.npt-pulse {
  transform-box: fill-box;
  transform-origin: center;
}

/* Invisible node hit-discs: opt back into pointer events (the overlay is none)
   and make the whole transparent disc grabbable. */
.npt-hit {
  pointer-events: all;
  cursor: pointer;
}

/* ── Hover tooltip — dark glass, low opacity, minimal blur ─────────────────── */
.npt-tip {
  position: absolute;
  z-index: 5;
  top: 0;
  left: 0;
  pointer-events: none; /* never blocks the network or the cursor */
  min-width: 116px;
  max-width: 210px;
  padding: 9px 12px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  background: rgba(16, 20, 27, 0.42); /* semi-transparent so the glow shows through */
  backdrop-filter: blur(3px) saturate(140%);
  -webkit-backdrop-filter: blur(3px) saturate(140%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 10px 28px -12px rgba(0, 0, 0, 0.7);
  font-family: 'Inter', sans-serif;
  white-space: normal;
  will-change: left, top, transform;
}
.npt-tip__type {
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(209, 213, 219, 0.95); /* cool silver — matches the light flow */
}
.npt-tip__title {
  font-size: 12.5px;
  line-height: 1.3;
  color: #F6F8FB;
}
.npt-tip__status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  letter-spacing: 0.06em;
  color: rgba(234, 240, 246, 0.72);
}
.npt-tip__dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.5);
}
.npt-tip__status[data-s='completed'] .npt-tip__dot { background: #FFFFFF; box-shadow: 0 0 6px rgba(255, 255, 255, 0.85); }
.npt-tip__status[data-s='in-progress'] .npt-tip__dot { background: #9FD0FF; box-shadow: 0 0 6px #9FD0FF; }

.npt-tip-enter-active,
.npt-tip-leave-active { transition: opacity 0.16s ease; }
.npt-tip-enter-from,
.npt-tip-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .npt-pulse { display: none; }
  .npt-tip-enter-active,
  .npt-tip-leave-active { transition: none; }
}
</style>
