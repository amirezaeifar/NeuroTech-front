<script setup>
import { computed, ref, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()
const route = useRoute()

const people = computed(() => tm('partners.people'))

const initials = (name) => name
  .replace(/^(Dr\.|د\.|دکتر|Dr|Prof\.?)\s*/i, '')
  .trim()
  .split(/\s+/)
  .map((w) => w[0])
  .slice(0, 2)
  .join('')
  .toUpperCase()

// ── Deep-link focus: /partners?focus=<index> (e.g. from an event speaker card)
//    scrolls to the matching profile and briefly highlights it. ──────────────
const highlightIndex = ref(null)
const focusProfile = async (raw) => {
  const idx = Number(raw)
  if (!Number.isInteger(idx) || idx < 0 || idx >= people.value.length) return
  await nextTick()
  const el = document.getElementById('partner-' + idx)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  highlightIndex.value = idx
  window.setTimeout(() => { if (highlightIndex.value === idx) highlightIndex.value = null }, 2800)
}
onMounted(() => { if (route.query.focus != null) focusProfile(route.query.focus) })
watch(() => route.query.focus, (v) => { if (v != null) focusProfile(v) })

useReveal()
</script>

<template>
  <div class="partners-page">
    <!-- ───────────────────────── Hero — flat deep-charcoal band ───────────────────────── -->
    <section class="partners-hero py-28 md:py-40">
      <div class="max-w-5xl mx-auto px-8 text-center">
        <p class="partners-hero-eyebrow text-[11px] uppercase tracking-[0.4em] text-gold-light/80 font-light mb-7">
          {{ t('partners.hero.eyebrow') }}
        </p>
        <h1 class="partners-hero-title font-serif font-light text-parchment-light text-5xl md:text-7xl tracking-wide leading-[1.05]">
          {{ t('partners.hero.title') }}
        </h1>
        <div class="partners-hero-rule mx-auto mt-10 h-px w-24 bg-gold"></div>
      </div>
    </section>

    <!-- ───────────────────────── Intro ───────────────────────── -->
    <section class="bg-parchment-light pt-20 md:pt-28">
      <p class="reveal max-w-2xl mx-auto px-8 text-center font-serif italic font-light text-2xl md:text-[2rem] text-ink-soft leading-relaxed">
        {{ t('partners.intro') }}
      </p>
    </section>

    <!-- ───────────────────────── Profiles ─────────────────────────
         Compact "preview" cards. The whole card is a single flat link that
         routes to the dedicated Doctor/Partner profile page (/partners/:id).
         Footprint is deliberately small — a gold-ringed avatar, name + lead
         role, a slim credential line and the Areas-of-Collaboration chips —
         with the long bio removed so the grid stays minimal. A slim gold accent
         rail and a gold hairline keep the rhythm without any 3D. Reverses
         naturally under dir="rtl". -->
    <section class="py-20 md:py-28 bg-parchment-light">
      <div class="max-w-6xl mx-auto px-8">
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6">
          <router-link
            v-for="(p, i) in people" :key="p.name + i"
            :id="`partner-${i}`"
            :to="`/partners/${i}`"
            :aria-label="t('partners.viewProfile') + ' — ' + p.name"
            class="reveal partner-card group relative flex flex-col scroll-mt-28 overflow-hidden rounded-xl border border-parchment-deep bg-parchment"
            :class="{ 'is-focused': highlightIndex === i }"
            :style="{ transitionDelay: `${(i % 6) * 60}ms` }"
          >
            <!-- Slim gold accent rail welded to the inline-start edge. -->
            <span class="partner-accent" aria-hidden="true"></span>

            <div class="relative flex flex-col flex-1 p-6 md:p-7 text-center sm:text-start">
              <!-- Header: flat avatar + name / lead role -->
              <header class="flex flex-col sm:flex-row items-center gap-4">
                <div class="partner-avatar grid place-items-center shrink-0">
                  <span class="partner-initials font-serif font-light leading-none">{{ initials(p.name) }}</span>
                </div>
                <div class="min-w-0">
                  <h3 class="partner-name font-serif font-light text-[1.4rem] leading-tight transition-colors">{{ p.name }}</h3>
                  <p v-if="p.title || (p.collaborations && p.collaborations.length)" class="partner-role mt-1 text-[11px] uppercase tracking-[0.22em] font-light">
                    {{ p.title || p.collaborations[0] }}
                  </p>
                </div>
              </header>

              <span class="partner-divider" aria-hidden="true"></span>

              <div class="flex flex-col gap-0.5 text-center sm:text-start">
                <span class="text-[10px] uppercase tracking-[0.25em] text-gold-dark font-light">{{ t('partners.labels.qualification') }}</span>
                <span class="text-[13px] text-ink-soft font-light leading-snug line-clamp-2">{{ p.qualification }}</span>
              </div>

              <div class="mt-4">
                <span class="text-[10px] uppercase tracking-[0.25em] text-ink-muted font-light">{{ t('partners.labels.collaborations') }}</span>
                <div class="mt-2 flex flex-wrap justify-center sm:justify-start gap-1.5">
                  <span
                    v-for="(c, j) in p.collaborations" :key="j"
                    class="partner-tag text-[11px] px-2.5 py-0.5 rounded-full font-light tracking-wide"
                  >{{ c }}</span>
                </div>
              </div>

              <!-- View-profile affordance pinned to the foot of the card. -->
              <span class="partner-view mt-5 pt-4 inline-flex items-center justify-center sm:justify-start gap-2 text-[11px] uppercase tracking-[0.25em] font-light">
                {{ t('partners.viewProfile') }}
                <span class="dir-arrow" aria-hidden="true"></span>
              </span>
            </div>
          </router-link>
        </div>

        <!-- ── Collaborate CTA — premium dark editorial panel ──────────────────
             A simpler kin of the Global-Trade "Become a representative" slab:
             the same deep-charcoal gradient, gold hairline border and soft gold
             aura + whisper-fine hairline grid — but WITHOUT the glassmorphic
             numbered grid. Just editorial copy on the start side and a gold
             ghost button on the end side. Strictly flat — no 3D lift, no glow.
             Reverses naturally under dir="rtl". -->
        <div class="partners-collab reveal relative overflow-hidden rounded-[1.75rem] mt-24">
          <!-- Ambient layers (decorative, flat) -->
          <div class="partners-collab-aura pointer-events-none absolute inset-0" aria-hidden="true"></div>
          <div class="partners-collab-grid pointer-events-none absolute inset-0" aria-hidden="true"></div>

          <div class="relative grid lg:grid-cols-12 gap-10 lg:gap-12 items-center p-10 md:p-14 lg:p-16">
            <div class="lg:col-span-8 text-center lg:text-start">
              <span class="inline-flex items-center gap-3 text-[11px] uppercase tracking-[0.35em] font-light">
                <span class="partners-collab-rule h-px w-8"></span>
                <span class="partners-collab-mark">&#9670;</span>
              </span>
              <h2 class="mt-6 font-serif font-light text-3xl md:text-4xl lg:text-5xl tracking-wide leading-[1.1] partners-collab-title">
                {{ t('partners.cta.title') }}
              </h2>
              <p class="mt-5 text-sm md:text-base font-light leading-relaxed max-w-xl mx-auto lg:mx-0 partners-collab-desc">
                {{ t('partners.cta.desc') }}
              </p>
            </div>
            <div class="lg:col-span-4 flex justify-center lg:justify-end">
              <router-link to="/contact" class="btn-ghost-gold">
                {{ t('partners.cta.button') }} <span class="dir-arrow" aria-hidden="true"></span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ── Hero / portrait panels — flat solid deep charcoal (#1A1714) ─────────────
   The dark-mode inversion to warm parchment #F2EDE4 (and the dark ink/amber
   text that keeps it legible) lives in src/style.css (`html.dark .partners-hero
   …`), mirroring the Academy and Global Trade heroes. */
.partners-hero { background: #1A1714; transition: background-color 300ms ease; }

/* Slim gold accent rail on the card's inline-start edge — grows a touch warmer
   on hover. Flat detail, no shadow. */
.partner-accent {
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  width: 3px;
  background: rgb(var(--c-gold) / 0.55);
  transition: background-color 300ms ease;
}
.partner-card:hover .partner-accent { background: rgb(var(--c-gold)); }

/* Large flat avatar — a clean geometric disc on a soft, highly-transparent gold
   tint with a gold hairline ring. No harsh dark panel, no shadow. */
.partner-avatar {
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 9999px;
  background: rgb(var(--c-gold) / 0.1);
  border: 1.5px solid rgb(var(--c-gold) / 0.55);
  transition: background-color 300ms ease, border-color 300ms ease;
}
.partner-card:hover .partner-avatar {
  background: rgb(var(--c-gold) / 0.16);
  border-color: rgb(var(--c-gold));
}
.partner-initials {
  color: rgb(var(--c-gold-dark));
  font-size: 1.6rem;
  letter-spacing: 0.04em;
}

/* View-profile affordance — a tracked gold caption pinned to the card foot, on a
   gold hairline. Pushed to the bottom so cards of differing height stay aligned. */
.partner-view {
  margin-block-start: auto;
  color: rgb(var(--c-gold-dark));
  border-block-start: 1px solid rgb(var(--c-gold) / 0.25);
  transition: color 240ms ease;
}
.partner-card:hover .partner-view { color: rgb(var(--c-gold)); }

/* Name + lead role — name warms to gold on hover; role is a tracked gold caption. */
.partner-name { color: rgb(var(--c-ink)); }
.partner-card:hover .partner-name { color: rgb(var(--c-gold-dark)); }
.partner-role { color: rgb(var(--c-gold-dark) / 0.85); }

/* Gold hairline separating the header from the credentials. */
.partner-divider {
  display: block;
  height: 1px;
  width: 100%;
  margin-block: 1.2rem;
  background: linear-gradient(
    to right,
    rgb(var(--c-gold) / 0.45),
    rgb(var(--c-parchment-deep) / 0.6) 60%,
    transparent
  );
}
/* Mirror the fade so it always starts from the inline-start edge under RTL. */
html[dir='rtl'] .partner-divider {
  background: linear-gradient(
    to left,
    rgb(var(--c-gold) / 0.45),
    rgb(var(--c-parchment-deep) / 0.6) 60%,
    transparent
  );
}

/* Collaboration pills — gold-tinted, lively, flat. */
.partner-tag {
  color: rgb(var(--c-gold-dark));
  border: 1px solid rgb(var(--c-gold) / 0.45);
  background: rgb(var(--c-gold) / 0.06);
  transition: background-color 240ms ease, border-color 240ms ease;
}
.partner-card:hover .partner-tag { background: rgb(var(--c-gold) / 0.1); }

/* Flat hover + focus: the card warms its border to gold (no shadow, no lift). */
.partner-card { transition: border-color 300ms ease; }
.partner-card:hover { border-color: rgb(var(--c-gold) / 0.6); }
.partner-card.is-focused {
  border-color: rgb(var(--c-gold));
  outline: 2px solid rgb(var(--c-gold));
  outline-offset: -1px;
}

/* ── Collaborate band — premium dark editorial panel ────────────────────────
   A simpler kin of the Global-Trade "Become a representative" slab: the same
   deep-charcoal gradient (anchored on #1A1714), gold hairline border and soft
   gold aura + whisper-fine hairline grid — but no glassmorphic numbered tiles
   and no 3D lift. Strictly flat 2D. */
.partners-collab {
  background: linear-gradient(155deg, #2b2620 0%, #1a1714 55%, #100e0b 100%);
  border: 1px solid rgba(237, 192, 113, 0.18);
}
/* Soft gold aura blooming from the upper-start corner. */
.partners-collab-aura {
  background: radial-gradient(70% 90% at 18% 0%, rgba(237, 192, 113, 0.16), transparent 60%);
}
/* Whisper-fine vertical hairlines for editorial texture, fading downward. */
.partners-collab-grid {
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent 79px, rgba(244, 215, 145, 0.035) 79px, rgba(244, 215, 145, 0.035) 80px);
  -webkit-mask-image: linear-gradient(180deg, #000, transparent 85%);
          mask-image: linear-gradient(180deg, #000, transparent 85%);
}
.partners-collab-rule { background: rgba(237, 192, 113, 0.6); }
.partners-collab-mark { color: #EDC071; }
.partners-collab-title { color: #F7F2E9; }
.partners-collab-desc { color: rgba(217, 210, 197, 0.72); }
</style>
