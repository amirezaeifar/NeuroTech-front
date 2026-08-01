<script setup>
import { useI18n } from 'vue-i18n'
import BrandLogo from './BrandLogo.vue'

const { t, locale } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
<footer class="bg-ink text-parchment-dark">
  <div class="max-w-5xl mx-auto px-8">
    <div class="h-px bg-gold/40 mt-0"></div>
  </div>

  <div class="max-w-5xl mx-auto px-8 pt-16 pb-10">
    <div class="grid md:grid-cols-3 gap-12">
      <div>
        <BrandLogo :width="200" :height="54" tone="parchment" />
        <p class="mt-5 text-sm text-parchment-deep/80 font-light leading-relaxed max-w-xs">
          {{ t('footer.tagline') }}
        </p>
      </div>

      <div>
        <h4 class="text-[11px] tracking-[0.3em] uppercase text-parchment-deep mb-5">{{ t('footer.links') }}</h4>
        <ul class="space-y-3 text-xs uppercase tracking-[0.2em] font-light text-parchment-dark/80">
          <li><router-link to="/" class="hover:text-gold-light transition-colors">{{ t('nav.home') }}</router-link></li>
          <li><router-link to="/academy" class="hover:text-gold-light transition-colors">{{ t('nav.academy') }}</router-link></li>
          <li><router-link to="/events" class="hover:text-gold-light transition-colors">{{ t('nav.events') }}</router-link></li>
          <li><router-link to="/products" class="hover:text-gold-light transition-colors">{{ t('nav.products') }}</router-link></li>
          <li><router-link to="/global-trade" class="hover:text-gold-light transition-colors">{{ t('nav.globalTrade') }}</router-link></li>
          <li><router-link to="/partners" class="hover:text-gold-light transition-colors">{{ t('nav.partners') }}</router-link></li>
        </ul>
      </div>

      <div>
        <h4 class="text-[11px] tracking-[0.3em] uppercase text-parchment-deep mb-5">{{ t('footer.more') }}</h4>
        <ul class="space-y-3 text-xs uppercase tracking-[0.2em] font-light text-parchment-dark/80 mb-8">
          <li><router-link to="/about" class="hover:text-gold-light transition-colors">{{ t('nav.about') }}</router-link></li>
          <li><router-link to="/contact" class="hover:text-gold-light transition-colors">{{ t('nav.contact') }}</router-link></li>
        </ul>

        <h4 class="text-[11px] tracking-[0.3em] uppercase text-parchment-deep mb-5">{{ t('footer.contact') }}</h4>
        <ul class="space-y-3 text-sm font-light text-parchment-dark/80 leading-relaxed">
          <li>{{ t('contact.info.address.value') }}</li>
          <li>{{ t('contact.info.phone.value') }}</li>
          <li>{{ t('contact.info.email.value') }}</li>
        </ul>
      </div>
    </div>

    <div class="mt-16 flex flex-col md:flex-row items-center justify-center gap-3 text-xs text-ink-muted/90 font-light">
      <span>&copy; {{ year }} {{ t('brand') }}. {{ t('footer.rights') }}</span>
      <span class="text-gold">&#9670;</span>
      <span class="uppercase tracking-[0.25em]">{{ locale.toUpperCase() }}</span>
    </div>
  </div>
</footer>
</template>
