<script setup>
/**
 * ScrollToTop — a premium soft-3D floating control pinned to the bottom-end
 * corner of the viewport. It springs + glides in only after the page has been
 * scrolled past a threshold, and smooth-scrolls back to the top on click.
 *
 * Aesthetic (updated brand system — depth, not flat): a sleek micro-square
 * (rounded squircle) with a 12px frosted-glass backdrop, a razor-thin gold
 * hairline border, a low-profile drop shadow, and a refined minimalist arrow.
 * Hover gives a gentle, dampened spring lift; the arrow nudges up on hover and
 * dips on press. The entrance uses the same dampened spring so it feels alive.
 * The corner uses the logical `inset-inline-end`, so it sits bottom-right in LTR
 * and bottom-left in RTL (Persian) with no direction-specific code.
 */
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const visible = ref(false)
const THRESHOLD = 400 // px scrolled before the button appears

const onScroll = () => {
  visible.value = window.scrollY > THRESHOLD
}

const toTop = () => {
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' })
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <Transition name="fab-pop">
    <button
      v-if="visible"
      type="button"
      class="scroll-fab"
      :aria-label="t('common.scrollTop')"
      :title="t('common.scrollTop')"
      @click="toTop"
    >
      <svg class="scroll-fab-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
        <!-- Refined minimalist arrow — a clean stem with a crisp chevron head. -->
        <path d="M12 18.5V6" stroke-linecap="round" />
        <path d="M6.5 11.5 12 5.8l5.5 5.7" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
  </Transition>
</template>

<style scoped>
.scroll-fab {
  position: fixed;
  bottom: 1.75rem;
  inset-inline-end: 1.75rem;
  z-index: 50;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px; /* circular frosted-glass disc */
  /* Premium frosted glass: a light translucent wash + a 12px backdrop blur so
     the page (and drifting particles) show softly through. Theme-adaptive via
     --c-ink (charcoal in light, parchment in dark); --c-gold for the arrow. */
  background: rgb(var(--c-ink) / 0.55);
  -webkit-backdrop-filter: blur(12px) saturate(1.4);
  backdrop-filter: blur(12px) saturate(1.4);
  color: rgb(var(--c-gold));
  border: 1px solid rgb(var(--c-gold) / 0.28); /* razor-thin hairline */
  cursor: pointer;
  /* Soft, low-profile elevation. */
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18), 0 1px 2px rgba(0, 0, 0, 0.12);
  /* Dampened spring — a gentle settle with only a hint of overshoot. */
  transition: transform 460ms cubic-bezier(0.34, 1.32, 0.64, 1),
              background-color 320ms ease, color 320ms ease,
              border-color 320ms ease, box-shadow 320ms ease;
}
.scroll-fab-icon {
  /* The arrow carries the secondary motion: it lifts on hover, dips on press. */
  transition: transform 320ms cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform;
}
.scroll-fab:hover {
  background: rgb(var(--c-gold)); /* warms to solid gold */
  color: #1a1714;                 /* dark arrow — gold is light-ish in both themes */
  border-color: rgb(var(--c-gold));
  /* Gentle dampened lift — a refined 3px rise, no exaggerated pop. */
  transform: translateY(-3px) scale(1.03);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22), 0 2px 5px rgba(0, 0, 0, 0.14);
}
.scroll-fab:hover .scroll-fab-icon {
  transform: translateY(-2px); /* elegant upward nudge */
}
.scroll-fab:active {
  transform: translateY(-1px) scale(1.0);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition-duration: 150ms;
}
.scroll-fab:active .scroll-fab-icon {
  transform: translateY(1px);
  transition-duration: 120ms;
}
.scroll-fab:focus-visible {
  outline: 2px solid rgb(var(--c-gold) / 0.6);
  outline-offset: 3px;
}

/* Dampened spring glide in, soft fall-away out. */
.fab-pop-enter-active {
  transition: opacity 380ms ease, transform 540ms cubic-bezier(0.34, 1.32, 0.64, 1);
}
.fab-pop-leave-active {
  transition: opacity 240ms ease, transform 300ms cubic-bezier(0.4, 0, 1, 1);
}
.fab-pop-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.85);
}
.fab-pop-leave-to {
  opacity: 0;
  transform: translateY(14px) scale(0.9);
}

@media (prefers-reduced-motion: reduce) {
  .scroll-fab {
    transition: background-color 200ms ease, color 200ms ease, box-shadow 200ms ease;
  }
  .scroll-fab:hover,
  .scroll-fab:active { transform: none; }
  .scroll-fab-icon,
  .scroll-fab:hover .scroll-fab-icon,
  .scroll-fab:active .scroll-fab-icon { transition: none; transform: none; }
  .fab-pop-enter-active,
  .fab-pop-leave-active { transition: opacity 200ms ease; }
  .fab-pop-enter-from,
  .fab-pop-leave-to { transform: none; }
}
</style>
