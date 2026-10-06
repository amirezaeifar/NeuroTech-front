<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import { ticketsApi } from '../api/tickets.js'
import { useReveal } from '../composables/useReveal.js'

const { t, locale } = useI18n()
const route = useRoute()
const sending = ref(false), sendError = ref(''), trackingToken = ref('')

const form = reactive({ name: '', email: '', phone: '', category: 'general', subject: '', message: '' })
const categories = [
  ['technical', 'Technical support', 'پشتیبانی فنی'],
  ['courses', 'Courses and learning', 'دوره‌ها و آموزش'],
  ['orders_payments', 'Orders and payments', 'سفارش‌ها و پرداخت'],
  ['products', 'Products and equipment', 'محصولات و تجهیزات'],
  ['partnerships', 'Partnerships', 'همکاری و مشارکت'],
  ['general', 'General enquiry', 'سایر درخواست‌ها'],
]
onMounted(() => {
  if (categories.some((item) => item[0] === route.query.category)) form.category = route.query.category
  if (route.query.product) {
    form.subject = locale.value === 'fa' ? `استعلام محصول: ${route.query.product}` : `Product inquiry: ${route.query.product}`
    form.message = locale.value === 'fa'
      ? `برای محصول «${route.query.product}»${route.query.ref ? ` با کد ${route.query.ref}` : ''} درخواست استعلام دارم.`
      : `I would like a quote for “${route.query.product}”${route.query.ref ? ` (${route.query.ref})` : ''}.`
  }
})
const submitted = ref(false)

const isFilled = (k) => !!form[k] && String(form[k]).length > 0
const active = computed(() => ({
  name: isFilled('name'),
  email: isFilled('email'),
  phone: isFilled('phone'),
  subject: isFilled('subject'),
  message: isFilled('message'),
}))

const handleSubmit = async () => {
  if (sending.value) return
  sending.value = true; sendError.value = ''
  try {
    const result = await ticketsApi.create({ ...form, email: form.email || null, locale: locale.value })
    trackingToken.value = result.data.tracking_token
    submitted.value = true
    Object.assign(form, { name: '', email: '', phone: '', category: 'general', subject: '', message: '' })
  } catch (error) { sendError.value = error.message } finally { sending.value = false }
}

// Icons for the contact info channels.
const infoIcons = {
  address: 'M12 21s-7-5.2-7-11a7 7 0 0 1 14 0c0 5.8-7 11-7 11z M12 10a2 2 0 1 0 0-0.01',
  phone: 'M4 4h4l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 2 6a2 2 0 0 1 2-2z',
  email: 'M3 6h18v12H3z M3 7l9 6 9-6',
  hours: 'M12 7v5l3 2 M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z',
}

useReveal()
</script>

<template>
  <div class="contact-page bg-parchment-light">
    <!-- ───────────────────────── Hero — flat, generous whitespace ───────────────────────── -->
    <section class="pt-28 md:pt-36 pb-6 text-center">
      <div class="max-w-5xl mx-auto px-8">
        <SectionEyebrow :text="t('contact.hero.eyebrow')" />
        <h1 class="font-serif font-light text-5xl md:text-7xl lg:text-8xl text-ink tracking-wide mt-8 leading-[1.02]">
          {{ t('contact.hero.title') }}
        </h1>
        <p class="reveal mt-10 max-w-xl mx-auto font-serif italic font-light text-xl md:text-2xl text-ink-soft leading-relaxed">
          {{ t('contact.intro') }}
        </p>
      </div>
    </section>

    <!-- ───────────────────────── Unboxed editorial body ─────────────────────────
         No card, no panel — the information rail and the form sit directly on the
         page. A single hairline column rule divides them on large screens. The
         grid reverses naturally under dir="rtl". -->
    <section class="pt-16 md:pt-24 pb-28 md:pb-36">
      <div class="max-w-6xl mx-auto px-8">
        <div class="grid lg:grid-cols-12 gap-16 lg:gap-0">

          <!-- ── Information rail — bare on the background ── -->
          <aside class="lg:col-span-5 lg:pe-16">
            <span class="inline-flex items-center gap-2.5 text-[11px] uppercase tracking-[0.35em] text-gold-dark font-light">
              <span class="h-px w-8 bg-gold/60"></span>
              {{ t('contact.rail.eyebrow') }}
            </span>
            <h2 class="mt-6 font-serif font-light text-3xl md:text-4xl text-ink leading-[1.12] tracking-wide">
              {{ t('contact.rail.title') }}
            </h2>
            <p class="mt-5 text-sm md:text-base text-ink-soft font-light leading-relaxed max-w-sm">
              {{ t('contact.rail.desc') }}
            </p>

            <div class="mt-12 space-y-8">
              <div v-for="key in ['address', 'phone', 'email', 'hours']" :key="key" class="flex items-start gap-4">
                <span class="contact-ico shrink-0 text-gold-dark">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><path :d="infoIcons[key]" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <div>
                  <p class="text-[10px] uppercase tracking-[0.3em] text-ink-muted font-light mb-1.5">{{ t(`contact.info.${key}.title`) }}</p>
                  <p class="font-serif font-light text-lg md:text-xl text-ink leading-snug">{{ t(`contact.info.${key}.value`) }}</p>
                </div>
              </div>
            </div>
          </aside>

          <!-- ── Form — bare fields on the background ── -->
          <div class="lg:col-span-7 contact-form-col lg:ps-16">
            <Transition name="fade" mode="out-in">
              <div v-if="submitted" key="success" class="min-h-[420px] flex flex-col items-center lg:items-start justify-center text-center lg:text-start">
                <div class="w-16 h-16 rounded-full border border-gold/50 flex items-center justify-center text-gold-dark">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
                <p class="mt-7 font-serif italic font-light text-3xl md:text-4xl text-gold-dark">
                  {{ t('contact.form.success') }}
                </p>
                <router-link :to="`/tickets/${trackingToken}`" class="btn-ghost-gold mt-6">{{ locale === 'fa' ? 'مشاهده و پیگیری درخواست' : 'Track your request' }}</router-link>
                <p class="mt-4 text-sm">{{ locale === 'fa' ? 'لینک پیگیری را نگه دارید؛ ارسال پیامک فعلاً آزمایشی است.' : 'Keep your tracking link; SMS delivery is currently simulated.' }}</p>
                <button @click="submitted = false" class="btn-ghost-gold mt-10">
                  <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('nav.contact') }}
                </button>
              </div>

              <form v-else key="form" @submit.prevent="handleSubmit">
                <p class="text-[11px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t('contact.form.eyebrow') }}</p>
                <h3 class="mt-3 font-serif font-light text-3xl md:text-4xl text-ink leading-snug">{{ t('contact.form.title') }}</h3>
                <div class="h-px w-12 bg-gold/70 mt-6 mb-12"></div>

                <div class="space-y-10">
                  <div>
                    <label for="ticket-category" class="block text-[10px] uppercase tracking-[0.3em] text-ink-muted font-light mb-3">{{ locale === 'fa' ? 'دسته‌بندی درخواست' : 'Request category' }}</label>
                    <select id="ticket-category" v-model="form.category" class="contact-select">
                      <option v-for="item in categories" :key="item[0]" :value="item[0]">{{ locale === 'fa' ? item[2] : item[1] }}</option>
                    </select>
                  </div>
                  <div class="grid md:grid-cols-2 gap-x-10 gap-y-10">
                    <div class="float-field" :class="{ 'is-active': active.name }">
                      <input maxlength="160" id="name" v-model="form.name" type="text" required placeholder=" " />
                      <label for="name">{{ t('contact.form.name') }}</label>
                    </div>
                    <div class="float-field" :class="{ 'is-active': active.email }">
                      <input maxlength="254" id="email" v-model="form.email" type="email" placeholder=" " />
                      <label for="email">{{ t('contact.form.email') }}</label>
                    </div>
                  </div>

                  <div class="grid md:grid-cols-2 gap-x-10 gap-y-10">
                    <div class="float-field" :class="{ 'is-active': active.phone }">
                      <input maxlength="24" id="phone" v-model="form.phone" type="tel" required placeholder=" " />
                      <label for="phone">{{ t('contact.form.phone') }}</label>
                    </div>
                    <div class="float-field" :class="{ 'is-active': active.subject }">
                      <input maxlength="240" id="subject" v-model="form.subject" type="text" required placeholder=" " />
                      <label for="subject">{{ t('contact.form.subject') }}</label>
                    </div>
                  </div>

                  <div class="float-field" :class="{ 'is-active': active.message }">
                    <textarea maxlength="10000" id="message" v-model="form.message" rows="4" required placeholder=" "></textarea>
                    <label for="message">{{ t('contact.form.message') }}</label>
                  </div>
                </div>

                <p v-if="sendError" role="alert" class="mt-6 text-red-700">{{ sendError }}</p>
                <button type="submit" :disabled="sending" class="btn-ghost-gold mt-14">
                  {{ t('contact.form.submit') }} <span class="dir-arrow" aria-hidden="true"></span>
                </button>
              </form>
            </Transition>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* The form column carries the only divider on the page — a single hairline
   on its inline-start edge (logical, so it sits correctly in RTL). */
@media (min-width: 1024px) {
  .contact-form-col { border-inline-start: 1px solid rgb(var(--c-parchment-deep)); }
}

/* Bare channel icon — no chip, no box; just the gold glyph on the background. */
.contact-ico { display: inline-grid; place-items: center; padding-top: 0.15rem; }

/* Larger, airier floating-label fields for the editorial layout. The base
   .float-field styles (underline, floating label, RTL handling) live globally
   in style.css; here we only enlarge the type and let textareas breathe. */
.float-field :deep(input),
.float-field :deep(textarea) {
  font-size: 1.05rem;
  padding-bottom: 0.65rem;
}
.float-field :deep(textarea) {
  resize: vertical;
  min-height: 4.5rem;
  line-height: 1.6;
}
.contact-select{width:100%;background:transparent;border:0;border-bottom:1px solid rgb(var(--c-parchment-deep));padding:.55rem 0 .75rem;color:rgb(var(--c-ink));outline:none}.contact-select:focus{border-color:rgb(var(--c-gold))}
</style>
