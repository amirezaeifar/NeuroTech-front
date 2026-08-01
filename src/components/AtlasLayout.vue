<script setup>
/**
 * AtlasLayout — the "Substrate" of the Atlas Console.
 *
 * A two-zone asymmetric spread: a narrow, sticky "Spine" (index / wayfinding)
 * and a wide "Field" (editorial content). On desktop it resolves to a 5 / 7
 * column split; below `lg` it stacks to a single column.
 *
 * Scope note: development is locked to LTR (English). Physical CSS properties
 * only — no BiDi / logical-property mirroring.
 *
 * Slots:
 *   #spine   → the IndexSpine (or any rail content)
 *   default  → the Field; mark each scroll target with `data-atlas-section`
 *              and a matching `id` so the Spine can observe / jump to it.
 */
defineProps({
  /** Max width of the whole spread. */
  maxWidth: { type: String, default: '80rem' },
})
</script>

<template>
  <div class="atlas" :style="{ '--atlas-max': maxWidth }">
    <aside class="atlas__spine">
      <slot name="spine" />
    </aside>

    <div class="atlas__field">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.atlas {
  display: grid;
  grid-template-columns: 1fr;                 /* mobile: single column */
  column-gap: clamp(2rem, 6vw, 6rem);
  row-gap: clamp(2rem, 5vw, 3rem);
  width: 100%;
  max-width: var(--atlas-max, 80rem);
  margin-left: auto;
  margin-right: auto;
  padding-left: clamp(1.5rem, 5vw, 4rem);
  padding-right: clamp(1.5rem, 5vw, 4rem);
}

.atlas__field {
  min-width: 0;                               /* allow content to shrink in grid */
  padding-top: clamp(3rem, 8vh, 7rem);
  padding-bottom: clamp(3rem, 8vh, 7rem);
}

/* Give every Field section a scroll offset so smooth-jumps from the Spine land
   cleanly under any sticky chrome. */
.atlas__field :deep([data-atlas-section]) {
  scroll-margin-top: clamp(2rem, 8vh, 6rem);
}

@media (min-width: 1024px) {
  .atlas {
    /* The signature asymmetry: 5 (Spine) / 7 (Field). */
    grid-template-columns: minmax(180px, 5fr) minmax(0, 7fr);
  }

  .atlas__spine {
    position: sticky;
    top: 0;
    height: 100vh;
    align-self: start;
    padding-top: clamp(4rem, 12vh, 8rem);
    padding-bottom: clamp(4rem, 12vh, 8rem);
    overflow: hidden;
    /* Soft top/bottom fade so a long index dissolves into the substrate. */
    -webkit-mask-image: linear-gradient(to bottom, transparent 0, #000 7%, #000 93%, transparent 100%);
            mask-image: linear-gradient(to bottom, transparent 0, #000 7%, #000 93%, transparent 100%);
  }
}
</style>
