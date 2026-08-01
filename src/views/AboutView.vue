<script setup>
import { useI18n } from 'vue-i18n'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()
const team = tm('about.team')
const timeline = tm('about.timeline')
const values = tm('about.values.items')
const collab = tm('about.collaborate.items')

// Distinct line-icons for the three collaboration tracks.
const collabIcons = [
  'M3 21V8l9-5 9 5v13 M9 21v-6h6v6 M3 21h18',                        // manufacturers — factory/building
  'M12 3l9 5-9 5-9-5 9-5z M5 11v5a7 4 0 0 0 14 0v-5',                // institutions — campus
  'M5 5h14v10H5z M9 19h6 M12 15v4',                                  // educators — board/screen
]

const pad2 = (n) => String(n + 1).padStart(2, '0')

useReveal()
</script>

<template>
  <div class="about-page bg-parchment-light">
    <!-- ───────────────────────── Hero — oversized editorial type ───────────────────────── -->
    <section class="pt-28 md:pt-40 pb-16 md:pb-24 text-center">
      <div class="max-w-5xl mx-auto px-8">
        <SectionEyebrow :text="t('about.hero.eyebrow')" />
        <h1 class="font-serif font-light text-5xl md:text-7xl lg:text-8xl text-ink tracking-wide mt-8 leading-[1.0]">
          {{ t('about.hero.title') }}
        </h1>
        <p class="reveal mt-12 max-w-2xl mx-auto font-serif italic font-light text-2xl md:text-3xl text-ink-soft leading-snug tracking-wide">
          {{ t('about.pullquote') }}
        </p>
      </div>
    </section>

    <!-- ───────────────────────── Story — asymmetric, large type ───────────────────────── -->
    <section class="py-20 md:py-28 border-t border-parchment-deep">
      <div class="max-w-6xl mx-auto px-8 grid md:grid-cols-12 gap-12 lg:gap-16">
        <div class="md:col-span-5 reveal">
          <p class="text-[11px] uppercase tracking-[0.35em] text-gold-dark font-light mb-5">{{ t('about.story.eyebrow') }}</p>
          <h2 class="font-serif font-light text-4xl md:text-5xl lg:text-6xl text-ink tracking-wide leading-[1.05]">{{ t('about.story.title') }}</h2>
        </div>
        <div class="md:col-span-7 reveal md:pt-10" style="transition-delay: 120ms">
          <div class="h-px w-12 bg-gold mb-8"></div>
          <p class="text-ink-soft font-light leading-loose text-base md:text-lg">{{ t('about.story.body') }}</p>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Principles — big numerals, flat ─────────────────────────
         Dynamic editorial grid anchored by oversized index numerals. Each block
         is bare (a single top hairline) — no card, no shadow. -->
    <section class="py-20 md:py-28 border-t border-parchment-deep">
      <div class="max-w-6xl mx-auto px-8">
        <div class="reveal mb-14 md:mb-20">
          <SectionEyebrow :text="t('about.values.title')" align="start" />
        </div>
        <div class="grid md:grid-cols-3 gap-px bg-parchment-deep border border-parchment-deep">
          <div
            v-for="(v, i) in values" :key="v.title"
            class="principle-cell reveal bg-parchment-light p-9 md:p-10"
            :style="{ transitionDelay: `${i * 90}ms` }"
          >
            <span class="principle-no font-serif font-light leading-none">{{ pad2(i) }}</span>
            <h3 class="mt-6 font-serif font-light text-2xl md:text-3xl text-ink leading-snug">{{ v.title }}</h3>
            <div class="h-px w-9 bg-gold/50 my-5"></div>
            <p class="text-sm text-ink-soft font-light leading-relaxed">{{ v.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Mission & Vision — full-width #1A1714 band ─────────────────────────
         A striking dark editorial band with oversized type. Flat: solid colour,
         a single hairline divider, no gradient/shadow. -->
    <section class="mv-band py-20 md:py-32">
      <div class="max-w-6xl mx-auto px-8 grid md:grid-cols-2">
        <div class="mv-cell md:pe-14">
          <p class="mv-eyebrow text-[11px] uppercase tracking-[0.4em] font-light mb-6">{{ t('about.mission.title') }}</p>
          <h3 class="font-serif font-light text-2xl md:text-4xl mv-heading leading-[1.15]">{{ t('about.mission.desc') }}</h3>
        </div>
        <div class="mv-cell mv-cell--divided md:ps-14 mt-12 md:mt-0">
          <p class="mv-eyebrow text-[11px] uppercase tracking-[0.4em] font-light mb-6">{{ t('about.vision.title') }}</p>
          <h3 class="font-serif font-light text-2xl md:text-4xl mv-heading leading-[1.15]">{{ t('about.vision.desc') }}</h3>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Team — flat circular avatars ───────────────────────── -->
    <section class="py-20 md:py-28 border-t border-parchment-deep">
      <div class="max-w-5xl mx-auto px-8">
        <div class="reveal text-center mb-16">
          <SectionEyebrow :text="t('about.teamTitle')" />
        </div>
        <div class="grid sm:grid-cols-3 gap-10">
          <div v-for="(m, i) in team" :key="m.name"
               class="reveal text-center"
               :style="{ transitionDelay: `${i * 80}ms` }">
            <div class="team-avatar relative mx-auto w-32 h-32 md:w-36 md:h-36 rounded-full flex items-center justify-center">
              <span class="team-initials relative font-serif font-light text-4xl md:text-5xl">{{ m.initials }}</span>
            </div>
            <h4 class="mt-8 font-serif font-light text-2xl text-ink leading-snug">{{ m.name }}</h4>
            <div class="mx-auto h-px w-8 bg-gold/50 my-4"></div>
            <p class="text-[11px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ m.role }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Collaborate — flat #1A1714 band ─────────────────────────
         Editorial dark band with hairline-bordered, static collaboration tracks.
         No gradient, no blur, no hover motion. -->
    <section class="collab-band py-20 md:py-32">
      <div class="max-w-6xl mx-auto px-8">
        <div class="text-center max-w-2xl mx-auto reveal">
          <span class="inline-flex items-center gap-2.5 text-[11px] uppercase tracking-[0.35em] collab-eyebrow font-light">
            <span class="h-px w-8 collab-rule"></span>
            {{ t('about.collaborate.eyebrow') }}
            <span class="h-px w-8 collab-rule"></span>
          </span>
          <h2 class="mt-7 font-serif font-light text-4xl md:text-5xl lg:text-6xl collab-title tracking-wide leading-[1.05]">
            {{ t('about.collaborate.title') }}
          </h2>
          <p class="mt-6 text-sm md:text-base collab-desc font-light leading-relaxed">
            {{ t('about.collaborate.desc') }}
          </p>
        </div>

        <div class="mt-16 grid md:grid-cols-3 gap-6 lg:gap-8">
          <div
            v-for="(c, i) in collab" :key="c.title"
            class="collab-tile reveal p-8 md:p-9 flex flex-col"
            :style="{ transitionDelay: `${i * 80}ms` }"
          >
            <span class="collab-tile-icon grid place-items-center w-12 h-12">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path :d="collabIcons[i]" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            <h3 class="mt-6 font-serif font-light text-xl md:text-2xl collab-tile-title leading-snug">{{ c.title }}</h3>
            <p class="mt-3 text-sm collab-tile-desc font-light leading-relaxed">{{ c.desc }}</p>
          </div>
        </div>

        <div class="mt-16 text-center reveal">
          <router-link to="/contact" class="btn-ghost-gold">
            {{ t('about.collaborate.cta') }} <span class="dir-arrow" aria-hidden="true"></span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ───────────────────────── Timeline — Milestones ───────────────────────── -->
    <section class="py-20 md:py-28 border-t border-parchment-deep">
      <div class="max-w-3xl mx-auto px-8">
        <div class="reveal text-center mb-16">
          <SectionEyebrow :text="t('about.timelineTitle')" />
        </div>
        <ol class="about-timeline">
          <li v-for="(item, i) in timeline" :key="i" class="about-timeline-item reveal" :style="{ transitionDelay: `${i * 60}ms` }">
            <span class="about-timeline-dot" aria-hidden="true"></span>
            <div class="about-timeline-body">
              <div class="font-serif font-light text-gold-dark text-3xl md:text-4xl mb-2 tabular-nums leading-none">{{ item.year }}</div>
              <p class="text-ink-soft font-light leading-relaxed">{{ item.event }}</p>
            </div>
          </li>
        </ol>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ── Principles — oversized faint gold index numerals, flat bare cells ───────── */
.principle-cell { box-shadow: none; }
.principle-no {
  font-size: 3.25rem;
  color: rgb(var(--c-gold) / 0.45);
}
html[lang='fa'] .principle-no { font-family: 'YekanBakh', sans-serif; }

/* ── Mission & Vision — full-width flat #1A1714 band ────────────────────────── */
.mv-band { background: #1A1714; }
.mv-eyebrow { color: #EDC071; }
.mv-heading { color: #F2EDE4; }
/* Hairline divider between the two cells (logical border for RTL). */
@media (min-width: 768px) {
  .mv-cell--divided { border-inline-start: 1px solid rgba(237, 192, 113, 0.2); }
}

/* ── Team avatar — flat solid #1A1714 disc with luminous gold initials ───────── */
.team-avatar {
  background: #1A1714;
  border: 1px solid rgba(237, 192, 113, 0.4);
}
.team-initials { color: #EDC071; }

/* ── Collaborate — flat #1A1714 band + hairline tiles ───────────────────────── */
.collab-band { background: #1A1714; }
.collab-eyebrow { color: rgba(237, 192, 113, 0.9); }
.collab-rule { background: rgba(237, 192, 113, 0.6); }
.collab-title { color: #F2EDE4; }
.collab-desc { color: rgba(242, 237, 228, 0.72); }
.collab-tile { border: 1px solid rgba(237, 192, 113, 0.25); }
.collab-tile-icon {
  color: #EDC071;
  border: 1px solid rgba(237, 192, 113, 0.28);
}
.collab-tile-title { color: #F2EDE4; }
.collab-tile-desc { color: rgba(242, 237, 228, 0.7); }

/* ── Milestones timeline — clean rail, generous non-overlapping spacing ─────── */
.about-timeline { position: relative; margin: 0; padding: 0; list-style: none; }
.about-timeline-item {
  position: relative;
  padding-inline-start: 2.75rem;
  padding-bottom: 3rem;
}
.about-timeline-item:last-child { padding-bottom: 0; }
.about-timeline-item::before {
  content: '';
  position: absolute;
  inset-inline-start: 5px;
  top: 0.7rem;
  bottom: -0.7rem;
  width: 1px;
  background: rgb(var(--c-parchment-deep));
}
.about-timeline-item:last-child::before { display: none; }
.about-timeline-dot {
  position: absolute;
  inset-inline-start: 0;
  top: 0.45rem;
  width: 12px;
  height: 12px;
  border-radius: 9999px;
  background: rgb(var(--c-parchment-light));
  border: 2px solid rgb(var(--c-gold));
}
.about-timeline-body { min-width: 0; }
</style>
