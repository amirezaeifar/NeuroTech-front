<script setup>
/**
 * IndexSpine — non-linear vertical wayfinder for the Atlas Console.
 *
 * Renders the library as a precision reference index: each entry shows a stable
 * catalog code (e.g. NRO-101) over the course title, with hairline tick-marks
 * and a gold "playhead" that rides the boundary rail and glides to whichever
 * Field section is in view. Click any entry to jump — courses are independent,
 * so there is no implied order.
 *
 * Scope note: development is locked to LTR (English). This component uses
 * physical CSS properties only — no BiDi / logical-property mirroring.
 *
 * Self-contained: pass `sections` ({ id, label, ref }) and it observes the
 * matching `id`'d elements anywhere in the document.
 */
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'

const props = defineProps({
  /** [{ id: string, label: string, ref: string }] — `ref` is the catalog code. */
  sections: { type: Array, required: true },
  /** Accessible name for the landmark. Pass a translated string. */
  label: { type: String, default: 'Course index' },
  /**
   * Activation band, measured from the viewport edges (top / bottom). A section
   * is "active" while its box intersects this thin band near the top.
   */
  rootMargin: { type: String, default: '-8% 0px -55% 0px' },
})

const emit = defineEmits(['change'])

/* ── State ─────────────────────────────────────────────────────────────── */
const spineEl = ref(null)             // the <nav> (offset parent + playhead host)
const itemEls = ref([])               // <li> elements, index-aligned to sections
const activeId = ref(props.sections[0]?.id ?? null)
const isDesktop = ref(false)

const visible = new Set()             // ids currently inside the activation band
let observer = null
let mql = null
let onMqlChange = null

const activeIndex = computed(() =>
  props.sections.findIndex((s) => s.id === activeId.value)
)

const setItemRef = (el, i) => { if (el) itemEls.value[i] = el }

/* ── Active-section detection (IntersectionObserver) ───────────────────── */
const recomputeActive = () => {
  // First section in document order that sits within the band wins; if none is
  // in the band (scrolling through a gap) we keep the last active id.
  for (const s of props.sections) {
    if (visible.has(s.id)) {
      if (activeId.value !== s.id) {
        activeId.value = s.id
        emit('change', s.id)
      }
      return
    }
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
  observer = new IntersectionObserver(onIntersect, {
    root: null,
    rootMargin: props.rootMargin,
    threshold: 0,
  })
  for (const s of props.sections) {
    const el = document.getElementById(s.id)
    if (el) observer.observe(el)
  }
}

/* ── Playhead positioning ──────────────────────────────────────────────── */
const movePlayhead = async () => {
  if (!isDesktop.value) return
  await nextTick()
  const item = itemEls.value[activeIndex.value]
  const host = spineEl.value
  if (!item || !host) return
  const y = item.offsetTop + item.offsetHeight / 2
  host.style.setProperty('--ph', `${y}px`)
}

watch(activeId, movePlayhead)

/* Re-wire when the section set changes (e.g. the library is filtered): reset
   state, keep the active entry if it survived, re-observe the new targets. */
watch(
  () => props.sections.map((s) => s.id).join('|'),
  async () => {
    visible.clear()
    itemEls.value = []
    if (!props.sections.some((s) => s.id === activeId.value)) {
      activeId.value = props.sections[0]?.id ?? null
    }
    await nextTick()
    observeSections()
    requestAnimationFrame(movePlayhead)
  }
)

/* ── Click-to-jump ─────────────────────────────────────────────────────── */
const goTo = (s) => {
  activeId.value = s.id          // immediate feedback
  emit('change', s.id)
  movePlayhead()
  const el = document.getElementById(s.id)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

/* ── Lifecycle ─────────────────────────────────────────────────────────── */
const onResize = () => movePlayhead()

onMounted(() => {
  mql = window.matchMedia('(min-width: 1024px)')
  isDesktop.value = mql.matches
  onMqlChange = (e) => { isDesktop.value = e.matches; movePlayhead() }
  mql.addEventListener('change', onMqlChange)

  observeSections()
  requestAnimationFrame(movePlayhead)
  window.addEventListener('resize', onResize, { passive: true })
})

onBeforeUnmount(() => {
  observer?.disconnect()
  mql?.removeEventListener('change', onMqlChange)
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <nav ref="spineEl" class="spine" :aria-label="label">
    <!-- Boundary rail (the persistent gold hairline) -->
    <span class="spine__rail" aria-hidden="true"></span>
    <!-- Gold playhead — desktop only; rides the rail to the active entry -->
    <span v-show="isDesktop" class="spine__playhead" aria-hidden="true"></span>

    <ol class="spine__list">
      <li
        v-for="(s, i) in sections"
        :key="s.id"
        :ref="(el) => setItemRef(el, i)"
        class="spine__item"
        :class="{ 'is-active': s.id === activeId }"
      >
        <button
          type="button"
          class="spine__link"
          :aria-current="s.id === activeId ? 'true' : undefined"
          @click="goTo(s)"
        >
          <span class="spine__ref tabular-nums">{{ s.ref }}</span>
          <span class="spine__label">{{ s.label }}</span>
          <span class="spine__tick" aria-hidden="true"></span>
        </button>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
/* var(--c-*) are the shared theme triplets (parchment / ink / gold), so the
   spine tracks light, dark, and the scoped #323A45 charcoal automatically.
   LTR-only: physical properties throughout. */

.spine {
  position: relative;            /* offset parent for items + playhead */
  width: 100%;
}

/* ── Boundary rail ─────────────────────────────────────────────────────── */
.spine__rail {
  position: absolute;
  top: 0;
  bottom: 0;
  right: 0;                      /* the Spine/Field boundary */
  width: 1px;
  background: rgb(var(--c-parchment-deep));
  opacity: 0.8;
}

/* ── Playhead ──────────────────────────────────────────────────────────── */
.spine__playhead {
  position: absolute;
  top: 0;
  right: 0;
  width: 7px;
  height: 7px;
  margin-right: -3px;            /* straddle the 1px rail */
  border-radius: 9999px;
  background: rgb(var(--c-gold));
  box-shadow:
    0 0 0 4px rgb(var(--c-gold) / 0.12),
    0 0 12px rgb(var(--c-gold-light) / 0.65);
  transform: translateY(calc(var(--ph, 0px) - 50%));
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}

/* ── Index list ────────────────────────────────────────────────────────── */
.spine__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(0.65rem, 1.6vh, 1.25rem);
}

.spine__link {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;        /* catalog code over title */
  align-items: flex-start;
  gap: 0.2rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  padding-right: 2rem;           /* room for ticks + rail */
  background: none;
  border: 0;
  cursor: pointer;
  text-align: left;
  color: inherit;
}
.spine__link:focus-visible {
  outline: 1px solid rgb(var(--c-gold) / 0.6);
  outline-offset: 4px;
  border-radius: 2px;
}

/* Catalog code (data voice) */
.spine__ref {
  font-feature-settings: "tnum" 1;
  font-size: 0.625rem;
  letter-spacing: 0.12em;
  color: rgb(var(--c-gold-dark));
  transition: color 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Course title (reading voice) */
.spine__label {
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  line-height: 1.3;
  color: rgb(var(--c-ink-muted));
  transition: color 0.4s cubic-bezier(0.22, 1, 0.36, 1),
              letter-spacing 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

/* ── Per-entry tick on the rail ────────────────────────────────────────── */
.spine__tick {
  position: absolute;
  top: 50%;
  right: 0;                      /* reaches the boundary rail */
  width: 8px;
  height: 1px;
  background: rgb(var(--c-parchment-deep));
  transform: translateY(-50%);
  transition: width 0.4s cubic-bezier(0.22, 1, 0.36, 1),
              background-color 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

/* ── States ────────────────────────────────────────────────────────────── */
.spine__link:hover .spine__label,
.spine__link:hover .spine__ref {
  color: rgb(var(--c-ink));
}
.spine__link:hover .spine__tick {
  width: 13px;
  background: rgb(var(--c-gold) / 0.7);
}

.is-active .spine__ref { color: rgb(var(--c-gold)); }
.is-active .spine__label {
  color: rgb(var(--c-ink));
  letter-spacing: 0.16em;        /* tracking tightens on activation */
}
.is-active .spine__tick {
  width: 18px;
  background: rgb(var(--c-gold));
}

/* ── Reduced motion ────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .spine__playhead,
  .spine__tick,
  .spine__label,
  .spine__ref { transition: none; }
}
</style>
