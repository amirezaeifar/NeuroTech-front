<script setup>
import { useI18n } from 'vue-i18n'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import LivingBrain from '../components/LivingBrain.vue'
import HomeHeroStars from '../components/HomeHeroStars.vue'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()
const stats = tm('home.stats')
const expertise = tm('home.expertise.items')
const partners = ['Forbo', 'GE Healthcare', 'Oxford', 'Verin', 'Siemens', 'Brainlab']
// Repeat the four names so the marquee track fills wide screens; the template
// renders this row twice more for a seamless translateX(-50%) loop.
const partnerRow = [...partners, ...partners, ...partners, ...partners]

useReveal()
</script>

<template>
  <div>
    <!-- Hero — the ONE dark section -->
    <section class="home-living-hero hero-ink-texture relative flex items-center">
      <HomeHeroStars />
      <div class="home-hero-layout mx-auto px-8 w-full">
        <div class="home-hero-copy">
        <p class="reveal text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light mb-10">
          {{ t('home.hero.eyebrow') }}
        </p>
        <h1 class="reveal font-serif font-light text-parchment-light text-5xl md:text-6xl lg:text-7xl leading-[1.1] tracking-wide max-w-3xl"
            style="transition-delay: 80ms">
          {{ t('home.hero.titleA') }}
          <em class="not-italic md:italic text-gold-light font-light"> {{ t('home.hero.titleEm') }} </em>
          {{ t('home.hero.titleB') }}
        </h1>
        <p class="reveal mt-10 max-w-lg text-parchment-dark/70 font-light text-base leading-loose"
           style="transition-delay: 160ms">
          {{ t('home.hero.subline') }}
        </p>
        <div class="reveal mt-14" style="transition-delay: 240ms">
          <router-link to="/products" class="btn-ghost-gold">
            {{ t('home.hero.cta') }}
            <span class="dir-arrow" aria-hidden="true"></span>
          </router-link>
        </div>
        </div>
        <div class="home-brain-wrap reveal" style="transition-delay: 180ms"><LivingBrain /></div>
      </div>
      <!-- Bottom fading gold rule -->
      <div class="absolute left-0 right-0 bottom-0 gold-fade-rule"></div>
    </section>

    <!-- Stats Row -->
    <section class="bg-parchment py-16">
      <div class="max-w-5xl mx-auto px-8">
        <div class="grid grid-cols-2 md:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-parchment-deep rtl:md:divide-x-reverse">
          <div v-for="(s, i) in stats" :key="i"
               class="reveal px-6 py-8 text-center" :style="{ transitionDelay: `${i * 80}ms` }">
            <div class="font-serif font-light text-ink text-5xl md:text-6xl leading-none">{{ s.value }}</div>
            <div class="mt-4 text-[11px] uppercase tracking-[0.3em] text-ink-muted font-light">{{ s.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- What We Do -->
    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8">
        <div class="reveal text-center mb-16">
          <SectionEyebrow :text="t('home.expertise.eyebrow')" />
          <h2 class="font-serif font-light text-4xl md:text-5xl mt-6 text-ink tracking-wide">
            {{ t('home.expertise.title') }}
          </h2>
        </div>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-12 md:gap-10">
          <div v-for="(f, i) in expertise" :key="i"
               class="reveal" :style="{ transitionDelay: `${i * 80}ms` }">
            <div class="h-px w-10 bg-gold mb-6"></div>
            <h3 class="font-serif font-light text-xl md:text-2xl text-ink mb-4 leading-snug">{{ f.title }}</h3>
            <p class="text-sm text-ink-soft font-light leading-relaxed">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Partners marquee -->
    <section class="bg-parchment-dark py-12">
      <div class="max-w-5xl mx-auto px-8 mb-6">
        <p class="text-center text-[12px] uppercase tracking-[0.3em] text-ink-soft font-normal">{{ t('home.partners') }}</p>
      </div>
      <div class="marquee">
        <div class="marquee-track">
          <span v-for="(p, i) in [...partnerRow, ...partnerRow]" :key="i"
                class="partner-name-latin italic font-normal text-ink-soft text-2xl" dir="ltr">
            {{ p }}
          </span>
        </div>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="bg-parchment pt-16 md:pt-24 pb-32 md:pb-48">
      <div class="reveal max-w-3xl mx-auto px-8 text-center">
        <h2 class="font-serif font-light text-4xl md:text-5xl text-ink tracking-wide leading-tight">
          {{ t('home.finalCta.title') }}
        </h2>
        <p class="mt-3 font-serif italic font-light text-2xl text-ink-soft">{{ t('home.finalCta.italic') }}</p>
        <div class="mt-12">
          <router-link to="/contact" class="btn-ghost-gold">
            {{ t('home.finalCta.button') }}
            <span class="dir-arrow" aria-hidden="true"></span>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-living-hero { min-height: clamp(580px,74svh,760px); isolation: isolate; }
.home-hero-layout { position: relative; z-index: 1; max-width: 1280px; display: grid; grid-template-columns: 1fr 1fr; align-items: center; gap: 32px; padding-block: 48px; }
.home-hero-copy { min-width: 0; }.home-brain-wrap { min-width: 0; display: flex; justify-content: center; }
@media (max-width: 900px) { .home-living-hero { min-height: 0; }.home-hero-layout { grid-template-columns: 1fr; padding-block: 40px 24px; gap: 5px; }.home-brain-wrap { width: min(480px,100%); justify-self: center; }.home-hero-copy h1 { max-width: 650px; } }
@media (prefers-reduced-motion: reduce) { .home-living-hero .reveal { opacity: 1; transform: none; transition: none; } }
.partner-name-latin {
  direction: ltr;
  unicode-bidi: isolate;
  font-family: 'Cormorant Garamond', Georgia, serif;
}
</style>
