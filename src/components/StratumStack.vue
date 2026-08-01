<script setup>
/**
 * StratumStack — a course's modules rendered as layered cortical "strata".
 *
 * Each module is a stratum in a stack. At rest it is a perfectly legible list
 * (clarity first). On interaction the stack fans into a shallow 3D
 * cross-section (a nod to the laminae of the cerebral cortex): hovering the
 * stack tilts and separates the layers, and hovering a single stratum lifts it
 * toward the viewer with a gold edge-glow.
 *
 * Modules are reference sections of one standalone course, so each is marked
 * with a catalog section ref (A, B, C …) — not a sequential 1→N number. State
 * (done / current) is supplied by the parent; this component is presentational.
 *
 * Scope note: development is locked to LTR (English). Physical CSS properties
 * only — no BiDi / logical-property mirroring. Collapses to a flat, motionless
 * list under `prefers-reduced-motion`.
 *
 * Emits `select(index)` when a stratum is activated (click / Enter).
 */
defineProps({
  /** [{ index:Number, ref:String, name:String, done:Boolean, current:Boolean }] */
  items: { type: Array, required: true },
})

const emit = defineEmits(['select'])
</script>

<template>
  <div class="stratum-stack">
    <div class="strata">
      <button
        v-for="(it, i) in items"
        :key="it.index"
        type="button"
        class="stratum"
        :style="{ '--i': i }"
        :class="{ 'is-done': it.done, 'is-current': it.current }"
        :aria-current="it.current ? 'true' : undefined"
        @click="emit('select', it.index)"
      >
        <span class="stratum__edge" aria-hidden="true"></span>

        <span class="stratum__ref">{{ it.ref }}</span>
        <span class="stratum__name">{{ it.name }}</span>

        <span class="stratum__state" aria-hidden="true">
          <svg v-if="it.done" class="stratum__check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5L19 8" /></svg>
          <span v-else-if="it.current" class="stratum__dot"></span>
          <span v-else class="stratum__tick"></span>
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* var(--c-*) are the shared theme triplets (parchment / ink / gold), so the
   stack tracks light, dark, and the scoped #323A45 charcoal automatically.
   LTR-only: physical properties throughout. */

.stratum-stack { perspective: 1500px; }

.strata {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transform-style: preserve-3d;
  transition: transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
}
/* Stack-hover: a gentle cross-section tilt that reveals the layering. */
.stratum-stack:hover .strata { transform: rotateX(9deg); }

.stratum {
  --i: 0;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  padding-top: 0.7rem;
  padding-bottom: 0.7rem;
  padding-left: 1.5rem;          /* room for the edge band */
  padding-right: 0.9rem;
  text-align: left;
  background: rgb(var(--c-parchment));
  border: 1px solid rgb(var(--c-parchment-deep) / 0.7);
  border-radius: 8px;
  cursor: pointer;
  transform-style: preserve-3d;
  transition:
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.4s cubic-bezier(0.22, 1, 0.36, 1),
    background-color 0.4s,
    border-color 0.4s;
}

/* Stack-hover: fan the layers by depth. */
.stratum-stack:hover .stratum {
  transform: translateZ(calc(var(--i) * 7px));
}

/* Single-stratum hover/focus: lift toward the viewer with a gold edge-glow. */
.stratum:hover,
.stratum:focus-visible {
  transform: translateZ(52px) scale(1.014);
  border-color: rgb(var(--c-gold) / 0.6);
  box-shadow:
    0 0 0 1px rgb(var(--c-gold) / 0.45),
    0 26px 50px -22px rgb(2 6 12 / 0.55),
    0 0 34px -6px rgb(var(--c-gold-light) / 0.35);
  outline: none;
  z-index: 3;
}

/* ── The cortical "edge" band on the left face ─────────────────────────── */
.stratum__edge {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 4px;
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
  background: rgb(var(--c-parchment-deep));
  transition: background-color 0.4s, width 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.stratum:hover .stratum__edge { width: 6px; background: rgb(var(--c-gold)); }
.is-done .stratum__edge { background: rgb(var(--c-gold) / 0.85); }
.is-current .stratum__edge { background: rgb(var(--c-gold)); }

/* ── Section ref (data voice) ─────────────────────────────────────────── */
.stratum__ref {
  flex-shrink: 0;
  width: 1.5rem;
  font-size: 0.6875rem;
  letter-spacing: 0.12em;
  font-weight: 400;
  color: rgb(var(--c-gold-dark));
}

/* ── Module name (reading voice) ──────────────────────────────────────── */
.stratum__name {
  flex: 1 1 auto;
  min-width: 0;
  font-size: 0.875rem;
  font-weight: 300;
  line-height: 1.35;
  color: rgb(var(--c-ink-soft));
  transition: color 0.4s;
}
.stratum:hover .stratum__name,
.is-current .stratum__name { color: rgb(var(--c-ink)); }

/* ── State marker on the right ────────────────────────────────────────── */
.stratum__state {
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 1.1rem;
  height: 1.1rem;
  color: rgb(var(--c-gold-dark));
}
.stratum__check { width: 1rem; height: 1rem; }
.stratum__dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: rgb(var(--c-gold));
  box-shadow: 0 0 0 3px rgb(var(--c-gold) / 0.15);
}
.stratum__tick {
  width: 8px;
  height: 1px;
  background: rgb(var(--c-parchment-deep));
}

/* ── Reduced motion: flat, legible list, no 3D ────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .stratum-stack { perspective: none; }
  .strata,
  .stratum,
  .stratum-stack:hover .strata,
  .stratum-stack:hover .stratum,
  .stratum:hover,
  .stratum:focus-visible { transform: none; transition: none; }
}
</style>
