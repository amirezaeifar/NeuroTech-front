<script setup>
import { useI18n } from 'vue-i18n'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import LuxeCard from '../components/LuxeCard.vue'
import GoldRule from '../components/GoldRule.vue'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()
const regions = tm('agencies.regions')
const become = tm('agencies.become.items')

useReveal()
</script>

<template>
  <div>
    <!-- Page header (no dark hero — already one on home; here keep light) -->
    <section class="py-20 md:py-28 bg-parchment-light text-center">
      <div class="max-w-5xl mx-auto px-8">
        <SectionEyebrow :text="t('agencies.hero.eyebrow')" />
        <h1 class="font-serif font-light text-5xl md:text-6xl text-ink tracking-wide mt-8">
          {{ t('agencies.hero.title') }}
        </h1>
      </div>
    </section>

    <section class="bg-parchment-light pb-8">
      <div class="reveal max-w-2xl mx-auto px-8 text-center font-serif italic font-light text-2xl text-ink-soft leading-relaxed">
        {{ t('agencies.intro') }}
      </div>
      <div class="max-w-5xl mx-auto px-8">
        <GoldRule diamond />
      </div>
    </section>

    <!-- Regions -->
    <section class="py-12 md:py-20 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8">
        <div class="reveal text-center mb-14">
          <SectionEyebrow :text="t('agencies.regionsTitle')" />
        </div>

        <div class="grid md:grid-cols-2 gap-12">
          <LuxeCard
            v-for="(r, i) in regions" :key="r.name"
            :title="r.name"
            class="reveal"
            :style="{ transitionDelay: `${i * 80}ms` }"
          >
            <div class="flex flex-wrap gap-2 mb-5">
              <span v-for="(c, j) in r.countries" :key="j"
                    class="text-xs px-3 py-1 bg-parchment-dark text-ink-soft font-light tracking-wide">
                {{ c }}
              </span>
            </div>
            <p class="text-sm text-ink-soft font-light leading-relaxed">{{ r.note }}</p>
          </LuxeCard>
        </div>
      </div>
    </section>

    <!-- Become a representative -->
    <section class="py-16 md:py-24 bg-parchment">
      <div class="max-w-5xl mx-auto px-8 grid md:grid-cols-5 gap-12 items-start">
        <div class="md:col-span-3 reveal">
          <h2 class="font-serif font-light text-4xl text-ink tracking-wide">
            {{ t('agencies.become.title') }}
          </h2>
          <p class="mt-2 font-serif italic font-light text-xl text-ink-muted">
            {{ t('agencies.become.italic') }}
          </p>
          <div class="h-px w-10 bg-gold mt-8 mb-8"></div>
          <ul class="space-y-4">
            <li v-for="(b, i) in become" :key="i" class="flex items-start gap-4 text-ink-soft font-light leading-relaxed">
              <span class="text-gold mt-1 text-xs">◆</span>
              <span>{{ b }}</span>
            </li>
          </ul>
        </div>
        <div class="md:col-span-2 md:text-end reveal" style="transition-delay: 120ms">
          <router-link to="/contact" class="btn-ghost-gold">
            {{ t('agencies.become.cta') }} <span class="dir-arrow" aria-hidden="true"></span>
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>
