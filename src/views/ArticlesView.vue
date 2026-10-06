<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { articlesApi } from '../api/articles.js'
import { useReveal } from '../composables/useReveal.js'
import JournalNeuralArt from '../components/JournalNeuralArt.vue'
import JournalCover from '../components/JournalCover.vue'
import '../assets/journal.css'

const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const category = ref('scientific')
const posts = ref([])
const loading = ref(true)
const error = ref('')
let request = 0
const load = async () => {
  const current = ++request
  loading.value = true
  error.value = ''
  try {
    const response = await articlesApi.list(locale.value, category.value)
    if (current === request) posts.value = response.data
  } catch (problem) {
    if (current === request) { error.value = problem.message; posts.value = [] }
  } finally { if (current === request) loading.value = false }
}
watch([locale, category], load)
onMounted(load)
onUnmounted(() => { request++ })
useReveal()
const hero = computed(() => posts.value[0])
const rest = computed(() => posts.value.slice(1))
const date = (value) => value && !Number.isNaN(Date.parse(value)) ? new Intl.DateTimeFormat(locale.value, { dateStyle: 'long' }).format(new Date(value)) : ''
const explore = () => document.getElementById('journal-library')?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' })
</script>

<template>
  <div class="journal-page">
    <header class="journal-hero journal-shell">
      <div class="journal-hero-copy journal-arrive">
        <p class="journal-eyebrow"><span class="journal-live-dot" aria-hidden="true"></span>{{ tr('NEUROTECH / THE JOURNAL', 'نوروتک / مجلهٔ دانش و تجربه') }}</p>
        <h1 class="font-serif">{{ tr('A closer look.', 'نگاهی عمیق‌تر،') }}<br><em>{{ tr('A wider perspective.', 'دریچه‌ای تازه.') }}</em></h1>
        <p class="journal-intro">{{ tr('Where neuroscience meets a new perspective. Research, discoveries and stories worth slowing down for.', 'آنجا که علوم اعصاب به نگاهی تازه می‌رسد. پژوهش‌ها، کشف‌ها و روایت‌هایی که ارزش مکث کردن دارند.') }}</p>
        <button class="journal-text-link" type="button" @click="explore">{{ tr('Explore the journal', 'ورق زدن مجله') }}<span class="journal-round-arrow" aria-hidden="true">↓</span></button>
      </div>
      <div class="journal-art-panel journal-arrive" style="--arrival-delay: 140ms">
        <p class="journal-art-top" dir="ltr">SCIENCE IN MOTION</p>
        <JournalNeuralArt spacious />
        <div class="journal-art-caption"><span>{{ tr('Every connection begins with curiosity.', 'هر ارتباط، از کنجکاوی آغاز می‌شود.') }}</span></div>
      </div>
      <div class="journal-hero-foot journal-arrive" style="--arrival-delay: 240ms"><span>{{ tr('RESEARCH · PERSPECTIVES · DISCOVERIES', 'پژوهش · بینش · کشف') }}</span><span>{{ tr('An ongoing exploration of the mind', 'کاوشی پیوسته در دنیای ذهن') }}</span></div>
    </header>

    <section id="journal-library" class="journal-library journal-shell" :aria-label="tr('Journal articles', 'مقاله‌های مجله')">
      <div class="journal-library-heading">
        <div><p class="journal-eyebrow">{{ tr('THE READING ROOM', 'برای خواندن، برای اندیشیدن') }}</p><h2 class="font-serif">{{ tr('From the journal', 'تازه‌های مجله') }}<span class="journal-heading-star" aria-hidden="true">✦</span></h2></div>
        <div class="journal-filters" role="group" :aria-label="tr('Article category', 'دسته‌بندی مطالب')">
          <span class="journal-filter-slider" :class="{ 'is-blog': category === 'blog' }" aria-hidden="true"></span>
          <button v-for="tab in ['scientific', 'blog']" :key="tab" type="button" :aria-pressed="category === tab" @click="category = tab">{{ tab === 'scientific' ? tr('Scientific articles', 'مقاله‌های علمی') : tr('Stories & insights', 'بلاگ و روایت‌ها') }}</button>
        </div>
      </div>
      <div :aria-busy="loading">
        <div v-if="loading" class="journal-loading" role="status"><span class="sr-only">{{ tr('Loading articles…', 'در حال بارگذاری مطالب…') }}</span><div class="journal-skeleton journal-skeleton-cover"></div><div><div class="journal-skeleton journal-skeleton-line"></div><div class="journal-skeleton journal-skeleton-title"></div><div class="journal-skeleton journal-skeleton-line"></div></div></div>
        <div v-else-if="error" class="journal-state" role="alert"><p>{{ error }}</p><button class="journal-text-link" type="button" @click="load">{{ tr('Try again', 'تلاش دوباره') }}<span aria-hidden="true">↻</span></button></div>
        <div v-else-if="!posts.length" class="journal-state"><span class="journal-state-star" aria-hidden="true">✦</span><h3 class="font-serif">{{ tr('The next story is on its way.', 'روایت بعدی در راه است.') }}</h3><p>{{ tr('No articles have been published in this section yet. Explore the other collection.', 'هنوز مطلبی در این بخش منتشر نشده است. سری به بخش دیگر مجله بزنید.') }}</p><button class="journal-text-link" type="button" @click="category = category === 'scientific' ? 'blog' : 'scientific'">{{ tr('Explore the other collection', 'دیدن بخش دیگر') }}<span class="dir-arrow" aria-hidden="true"></span></button></div>
        <div v-else :key="`${locale}-${category}`" class="journal-arrive">
          <router-link :to="`/articles/${hero.slug}`" class="journal-feature">
            <JournalCover :post="hero" eager />
            <div class="journal-feature-copy">
              <div class="journal-feature-label"><span class="journal-eyebrow">{{ tr('IN FOCUS', 'زیر ذره‌بین') }}</span><span aria-hidden="true">✦</span></div>
              <h3 class="font-serif">{{ hero.title }}</h3>
              <p class="journal-feature-excerpt">{{ hero.excerpt }}</p>
              <div class="journal-feature-bottom"><time :datetime="hero.created_at">{{ date(hero.created_at) }}</time><span class="journal-read-link">{{ tr('Read the story', 'مطالعهٔ مطلب') }}<span class="journal-round-arrow dir-arrow" aria-hidden="true"></span></span></div>
            </div>
          </router-link>
          <div v-if="rest.length" class="journal-grid">
            <router-link v-for="(post, index) in rest" :key="post.id" :to="`/articles/${post.slug}`" class="journal-card reveal" :style="{ '--reveal-delay': `${(index % 3) * 75}ms` }">
              <div class="journal-card-image"><JournalCover :post="post" /><span class="journal-card-image-arrow dir-arrow" aria-hidden="true"></span></div>
              <div class="journal-card-meta"><span>{{ category === 'scientific' ? tr('RESEARCH & SCIENCE', 'علم و پژوهش') : tr('PERSPECTIVES', 'نگاه و تجربه') }}</span><time :datetime="post.created_at">{{ date(post.created_at) }}</time></div>
              <h3 class="font-serif">{{ post.title }}</h3><p class="journal-card-excerpt">{{ post.excerpt }}</p>
              <span class="journal-card-read">{{ tr('Continue reading', 'ادامهٔ مطالعه') }}<span class="dir-arrow" aria-hidden="true"></span></span>
            </router-link>
          </div>
        </div>
      </div>
      <div class="journal-colophon"><span></span><p>{{ tr('Stay curious. Keep exploring.', 'کنجکاو بمانید. کشف کنید.') }}</p><span></span></div>
    </section>
  </div>
</template>
