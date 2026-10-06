<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { articlesApi } from '../api/articles.js'
import { resolveApiUrl } from '../api/client.js'
import { renderArticle } from '../utils/articleMarkdown.js'
import { useReveal } from '../composables/useReveal.js'
import JournalCover from '../components/JournalCover.vue'
import JournalNeuralArt from '../components/JournalNeuralArt.vue'
import '../assets/journal.css'

const route = useRoute()
const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const post = ref(null)
const related = ref([])
const loading = ref(true)
const error = ref('')
const articleElement = ref(null)
const headings = ref([])
const activeHeading = ref('')
const progress = ref(0)
const shareState = ref('')
const shareUrl = ref('')
let request = 0
let frame = 0
let resizeObserver
let headingElements = []
const body = computed(() => renderArticle(post.value?.body))
const minutes = computed(() => Math.max(1, Math.ceil(String(post.value?.body || '').replace(/!\[[^\]]*\]\([^)]*\)/g, '').trim().split(/\s+/u).filter(Boolean).length / 200)))
const number = (value) => new Intl.NumberFormat(locale.value).format(value)
const date = (value) => value && !Number.isNaN(Date.parse(value)) ? new Intl.DateTimeFormat(locale.value, { dateStyle: 'long' }).format(new Date(value)) : ''
const cover = (url) => url?.startsWith('/api/') ? resolveApiUrl(url) : url
const categoryLabel = computed(() => post.value?.category === 'scientific' ? tr('Scientific article', 'مقالهٔ علمی') : tr('Stories & insights', 'بلاگ و روایت‌ها'))
const setMeta = (key, value, attribute = 'name') => {
  let element = document.head.querySelector(`meta[${attribute}="${key}"]`)
  if (!element) { element = document.createElement('meta'); element.setAttribute(attribute, key); document.head.appendChild(element) }
  element.content = value || ''
}
const updateMeta = () => {
  const item = post.value
  const title = item.seo_title || item.title
  const description = item.seo_description || item.excerpt
  const url = window.location.href
  setMeta('description', description)
  setMeta('keywords', item.seo_keywords)
  setMeta('og:type', 'article', 'property')
  setMeta('og:title', title, 'property')
  setMeta('og:description', description, 'property')
  setMeta('og:url', url, 'property')
  setMeta('og:image', item.cover_url ? cover(item.cover_url) : '', 'property')
  let canonical = document.head.querySelector('link[rel="canonical"]')
  if (!canonical) { canonical = document.createElement('link'); canonical.rel = 'canonical'; document.head.appendChild(canonical) }
  canonical.href = url
  let jsonLd = document.head.querySelector('script[data-article-structured-data]')
  if (!jsonLd) { jsonLd = document.createElement('script'); jsonLd.type = 'application/ld+json'; jsonLd.dataset.articleStructuredData = ''; document.head.appendChild(jsonLd) }
  jsonLd.textContent = JSON.stringify({ '@context': 'https://schema.org', '@type': 'Article', headline: item.title, description, image: item.cover_url ? cover(item.cover_url) : undefined, datePublished: item.created_at, inLanguage: locale.value, mainEntityOfPage: url })
}
const measureReading = () => {
  frame = 0
  if (!articleElement.value) return
  const rect = articleElement.value.getBoundingClientRect()
  const distance = Math.max(1, rect.height - Math.max(0, window.innerHeight - 160))
  progress.value = Math.round(Math.min(1, Math.max(0, (160 - rect.top) / distance)) * 100)
  let active = ''
  for (const heading of headingElements) if (heading.getBoundingClientRect().top <= 200) active = heading.id
  activeHeading.value = active
}
const scheduleMeasure = () => { if (!frame) frame = requestAnimationFrame(measureReading) }
const setupReading = async (current) => {
  await nextTick()
  if (current !== request || !articleElement.value) return
  headingElements = Array.from(articleElement.value.querySelectorAll('h1,h2,h3'))
  headings.value = headingElements.map((element, index) => {
    element.id = `article-section-${index}`
    element.tabIndex = -1
    return { id: element.id, text: element.textContent, nested: element.tagName === 'H3' }
  })
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(scheduleMeasure)
    resizeObserver.observe(articleElement.value)
  }
  scheduleMeasure()
}
const load = async () => {
  const current = ++request
  error.value = ''; loading.value = true; post.value = null; related.value = []
  headings.value = []; headingElements = []; progress.value = 0; activeHeading.value = ''; shareState.value = ''; shareUrl.value = ''
  resizeObserver?.disconnect()
  try {
    const result = await articlesApi.detail(route.params.slug, locale.value)
    if (current !== request) return
    post.value = result.data
    document.title = `${post.value.seo_title || post.value.title} | NeuroTech`
    updateMeta()
    loading.value = false
    await setupReading(current)
    if (current !== request) return
    articlesApi.list(locale.value, post.value.category).then(result => {
      if (current === request) related.value = result.data.filter(item => item.slug !== post.value.slug).slice(0, 2)
    }).catch(() => {})
  } catch (problem) {
    if (current === request) { post.value = null; error.value = problem.message }
  } finally { if (current === request) loading.value = false }
}
const goToHeading = (id) => {
  const element = headingElements.find(heading => heading.id === id)
  if (!element) return
  element.focus({ preventScroll: true })
  element.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' })
}
const copyLink = async () => {
  const current = request
  const url = window.location.href
  try { await navigator.clipboard.writeText(url); if (current === request) shareState.value = 'copied' }
  catch { if (current === request) { shareUrl.value = url; shareState.value = 'manual' } }
}
watch([() => route.params.slug, locale], load)
useReveal()
onMounted(() => {
  load()
  window.addEventListener('scroll', scheduleMeasure, { passive: true })
  window.addEventListener('resize', scheduleMeasure, { passive: true })
})
onUnmounted(() => {
  request++
  cancelAnimationFrame(frame)
  resizeObserver?.disconnect()
  window.removeEventListener('scroll', scheduleMeasure)
  window.removeEventListener('resize', scheduleMeasure)
  document.title = 'Neuro Tech — Neurology, Crafted'
  document.head.querySelector('meta[name="description"]')?.setAttribute('content', 'Neuro Tech — Neurology Devices, Academy, Events, Import & Export, Global Partnerships')
  document.head.querySelector('meta[name="keywords"]')?.remove()
  for (const name of ['og:type', 'og:title', 'og:description', 'og:url', 'og:image']) document.head.querySelector(`meta[property="${name}"]`)?.remove()
  document.head.querySelector('link[rel="canonical"]')?.remove()
  document.head.querySelector('script[data-article-structured-data]')?.remove()
})
</script>

<template>
  <div class="journal-page journal-detail">
    <div v-if="post" class="journal-reading-line" role="progressbar" :aria-valuenow="progress" aria-valuemin="0" aria-valuemax="100" :aria-label="tr('Reading progress', 'پیشرفت مطالعه')"><span :style="{ transform: `scaleX(${progress / 100})` }"></span></div>
    <div class="journal-shell">
      <nav class="journal-breadcrumb" :aria-label="tr('Breadcrumb', 'مسیر صفحه')"><router-link to="/articles"><span class="dir-arrow-back" aria-hidden="true"></span>{{ tr('The journal', 'مجلهٔ نوروتک') }}</router-link><span aria-hidden="true">/</span><span>{{ post ? categoryLabel : tr('Article', 'مقاله') }}</span></nav>
      <template v-if="post">
        <header class="journal-article-header journal-arrive">
          <div class="journal-header-art"><JournalNeuralArt /></div>
          <p class="journal-eyebrow"><span class="journal-live-dot" aria-hidden="true"></span>{{ categoryLabel }}</p>
          <h1 class="font-serif">{{ post.title }}</h1>
          <p class="journal-article-deck">{{ post.excerpt }}</p>
          <div class="journal-article-meta"><time :datetime="post.created_at">{{ date(post.created_at) }}</time><span aria-hidden="true">✦</span><span>{{ tr(`About ${number(minutes)} min read`, `حدود ${number(minutes)} دقیقه مطالعه`) }}</span></div>
        </header>
        <figure class="journal-article-figure journal-arrive" style="--arrival-delay: 120ms"><JournalCover :post="post" eager /><figcaption><span>NEUROTECH JOURNAL</span><span>{{ categoryLabel }}</span></figcaption></figure>
        <div class="journal-reading-layout">
          <aside class="journal-reading-aside">
            <div class="journal-reading-tools">
              <div class="journal-reading-caption"><span class="journal-eyebrow">{{ tr('YOUR READING', 'همراه مطالعه') }}</span><span>{{ number(progress) }}{{ tr('%', '٪') }}</span></div>
              <div class="journal-aside-progress" aria-hidden="true"><span :style="{ width: `${progress}%` }"></span></div>
              <nav v-if="headings.length" class="journal-toc" :aria-label="tr('In this article', 'در این مقاله')"><h2>{{ tr('In this article', 'در این مقاله') }}</h2><button v-for="heading in headings" :key="heading.id" type="button" :class="{ 'is-active': activeHeading === heading.id, 'is-nested': heading.nested }" :aria-current="activeHeading === heading.id ? 'location' : undefined" @click="goToHeading(heading.id)">{{ heading.text }}</button></nav>
              <p v-else class="journal-reading-note">{{ tr('A moment to read. A new way to see.', 'فرصتی برای خواندن؛ دریچه‌ای برای نگاهی تازه.') }}</p>
              <div class="journal-share"><button type="button" @click="copyLink"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="m10 13 4-4m-6 7-1 1a4 4 0 0 1-6-6l5-5a4 4 0 0 1 6 0m0 12a4 4 0 0 0 6 0l5-5a4 4 0 0 0-6-6l-1 1" transform="translate(1 0)"/></svg>{{ tr('Copy article link', 'کپی لینک مقاله') }}</button><p class="journal-share-status" role="status">{{ shareState === 'copied' ? tr('Link copied', 'لینک کپی شد') : shareState === 'manual' ? tr('Select and copy the link below', 'لینک زیر را انتخاب و کپی کنید') : '' }}</p><input v-if="shareState === 'manual'" :value="shareUrl" readonly :aria-label="tr('Article link', 'لینک مقاله')" dir="ltr" @focus="$event.target.select()"></div>
            </div>
          </aside>
          <div class="journal-reading-body">
            <article ref="articleElement" class="journal-prose" :dir="locale === 'fa' ? 'rtl' : 'ltr'" v-html="body"></article>
            <div class="journal-article-end"><span aria-hidden="true">✦</span><p>{{ tr('A little more knowledge. A wider horizon.', 'اندکی آگاهی بیشتر، افقی بازتر.') }}</p><router-link to="/articles" class="journal-text-link">{{ tr('Back to the journal', 'بازگشت به مجله') }}<span class="dir-arrow-back" aria-hidden="true"></span></router-link></div>
          </div>
        </div>
        <section v-if="related.length" class="journal-related" :aria-label="tr('More to explore', 'برای ادامهٔ کشف')"><div class="journal-library-heading"><div><p class="journal-eyebrow">{{ tr('KEEP EXPLORING', 'کشف ادامه دارد') }}</p><h2 class="font-serif">{{ tr('Another perspective', 'دریچه‌های دیگر') }}</h2></div><router-link to="/articles" class="journal-text-link">{{ tr('All articles', 'همهٔ مطالب') }}<span class="dir-arrow" aria-hidden="true"></span></router-link></div><div class="journal-related-grid"><router-link v-for="item in related" :key="item.id" :to="`/articles/${item.slug}`" class="journal-related-card reveal"><JournalCover :post="item" /><div><time :datetime="item.created_at">{{ date(item.created_at) }}</time><h3 class="font-serif">{{ item.title }}</h3><span class="journal-text-link">{{ tr('Read the story', 'مطالعهٔ مطلب') }}<span class="dir-arrow" aria-hidden="true"></span></span></div></router-link></div></section>
      </template>
      <div v-else-if="loading" class="journal-detail-loading" role="status"><span class="sr-only">{{ tr('Loading article…', 'در حال بارگذاری مقاله…') }}</span><div class="journal-skeleton journal-skeleton-line"></div><div class="journal-skeleton journal-skeleton-title"></div><div class="journal-skeleton journal-skeleton-line"></div><div class="journal-skeleton journal-skeleton-cover"></div></div>
      <div v-else class="journal-state" role="alert"><span class="journal-state-star" aria-hidden="true">✦</span><h1 class="font-serif">{{ tr('This story could not be opened.', 'این مطلب باز نشد.') }}</h1><p>{{ error }}</p><button class="journal-text-link" type="button" @click="load">{{ tr('Try again', 'تلاش دوباره') }}<span aria-hidden="true">↻</span></button></div>
    </div>
  </div>
</template>
