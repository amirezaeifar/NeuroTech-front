<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { useReveal } from '../composables/useReveal.js'
import { documentById } from '../data/tradeReports.js'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const doc = computed(() => documentById(route.params.id))

useReveal()
</script>

<template>
  <div v-if="doc">
    <section class="bg-ink py-16 md:py-24">
      <div class="max-w-3xl mx-auto px-8">
        <router-link to="/global-trade" class="text-[11px] uppercase tracking-[0.25em] text-gold/80 hover:text-gold transition-colors inline-flex items-center gap-2">
          <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('globalTrade.documentDetail.back') }}
        </router-link>
        <p class="mt-8 text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light">
          {{ t('globalTrade.documentDetail.eyebrow') }} · <span class="font-mono">{{ doc.id }}</span>
        </p>
        <h1 class="mt-3 font-serif font-light text-parchment-light text-4xl md:text-5xl tracking-wide leading-snug">{{ doc.title }}</h1>
        <p class="mt-4 text-sm text-parchment-light/70 uppercase tracking-[0.2em] font-light">{{ doc.partner }} · {{ doc.category }}</p>
      </div>
    </section>

    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-3xl mx-auto px-8 grid md:grid-cols-5 gap-12">
        <!-- Body — every original field group, rendered in order -->
        <div class="md:col-span-3 space-y-12">
          <div v-for="g in doc.groups" :key="g.label" class="reveal">
            <SectionEyebrow :text="g.label" align="start" />
            <ul v-if="g.kind === 'list'" class="mt-6 space-y-3">
              <li v-for="(item, k) in g.items" :key="k" class="flex items-start gap-3 text-sm text-ink-soft font-light leading-relaxed">
                <span class="text-gold-dark mt-1 text-[10px]">◆</span>
                <span>{{ item }}</span>
              </li>
            </ul>
            <dl v-else-if="g.kind === 'pairs'" class="mt-6 space-y-3">
              <div v-for="(p, k) in g.pairs" :key="k" class="flex items-baseline justify-between gap-4 border-b border-parchment-deep/60 pb-3">
                <dt class="text-[11px] uppercase tracking-[0.15em] text-ink-muted font-light">{{ p.k }}</dt>
                <dd class="text-sm text-ink font-light text-right">{{ p.v }}</dd>
              </div>
            </dl>
            <p v-else class="mt-6 text-sm text-ink-soft font-light leading-relaxed">{{ g.text }}</p>
          </div>
        </div>

        <!-- Aside — document profile -->
        <div class="md:col-span-2">
          <LuxeCard class="reveal" :title="t('globalTrade.documentDetail.summaryTitle')">
            <dl class="space-y-4 text-sm">
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('globalTrade.documentDetail.documentIdLabel') }}</dt>
                <dd class="text-ink font-light text-right font-mono text-[13px]">{{ doc.id }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('globalTrade.documentDetail.docTypeLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ doc.docType }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('globalTrade.documentDetail.partnerLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ doc.partner }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('globalTrade.documentDetail.categoryLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ doc.category }}</dd>
              </div>
              <div v-if="doc.location" class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('globalTrade.documentDetail.locationLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ doc.location }}</dd>
              </div>
              <div v-if="doc.region" class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('globalTrade.documentDetail.regionLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ doc.region }}</dd>
              </div>
            </dl>
          </LuxeCard>
        </div>
      </div>
    </section>
  </div>

  <div v-else class="py-32 text-center">
    <button class="text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1" @click="router.push('/global-trade')">
      {{ t('globalTrade.documentDetail.back') }}
    </button>
  </div>
</template>
