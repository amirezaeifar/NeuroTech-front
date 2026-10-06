<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ticketsApi } from '../../api/tickets.js'
const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const labels = { submitted: ['Open', 'باز'], in_progress: ['In progress', 'در حال بررسی'], resolved: ['Completed', 'انجام‌شده'], rejected: ['Rejected', 'ردشده'] }
const label = (key) => tr(...labels[key])
const categoryLabels = { technical:['Technical','فنی'], courses:['Courses','دوره‌ها'], orders_payments:['Orders & payments','سفارش و پرداخت'], products:['Products','محصولات'], partnerships:['Partnerships','همکاری'], general:['General','عمومی'] }
const categoryLabel = (key) => tr(...(categoryLabels[key] || categoryLabels.general))
const rows = ref([]), selected = ref(null), error = ref(''), busy = ref(false)
const history = ref([]), historyPage = ref(1), historyTotal = ref(0)
const query = ref(''), status = ref(''), category = ref(''), page = ref(1), total = ref(0), nextStatus = ref('submitted')
const date = (value) => new Date(value).toLocaleString(locale.value)
let requestId = 0
async function load(reset = false) {
  if (reset) { page.value = 1; historyPage.value = 1 }
  const id = ++requestId
  busy.value = true; error.value = ''
  try {
    const [result, completed] = await Promise.allSettled([
      ticketsApi.list({ q: query.value, status: status.value, category: category.value, page: page.value, page_size: 20 }),
      ticketsApi.list({ q: query.value, status: 'closed', category: category.value, page: historyPage.value, page_size: 4 }),
    ])
    if (id !== requestId) return
    if (result.status === 'fulfilled') { rows.value = result.value.data; total.value = result.value.meta.total }
    if (completed.status === 'fulfilled') { history.value = completed.value.data; historyTotal.value = completed.value.meta.total }
    const problem = [result, completed].find((response) => response.status === 'rejected')
    if (problem) error.value = problem.reason.message
  } catch (e) { error.value = e.message } finally { if (id === requestId) busy.value = false }
}
let selectionRequest = 0
async function open(item) {
  const request = ++selectionRequest
  error.value = ''; busy.value = true
  try { const result = await ticketsApi.detail(item.id); if (request !== selectionRequest) return; selected.value = result.data; nextStatus.value = selected.value.status }
  catch (e) { error.value = e.message } finally { busy.value = false }
}
async function save() {
  busy.value = true; error.value = ''
  try {
    selected.value = (await ticketsApi.update(selected.value.id, { status: nextStatus.value, version: selected.value.version })).data
    await load()
  } catch (e) { error.value = e.message } finally { busy.value = false }
}
let searchTimer
watch([query, status, category], () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(true), 250)
})
onMounted(() => load())
</script>
<template>
  <div>
    <p class="admin-eyebrow">{{ tr('Support desk', 'مرکز پشتیبانی') }}</p>
    <h1 class="admin-h1 mt-2">{{ tr('Ticket management', 'مدیریت تیکت‌ها') }}</h1>
    <p class="text-ink-muted mt-3">{{ tr('Requests from the contact form. Replies are available through the guest tracking link.', 'درخواست‌های فرم تماس؛ پاسخ‌ها از لینک اختصاصی پیگیری در دسترس کاربرند.') }}</p>
    <p v-if="error" role="alert" class="admin-panel p-4 mt-5">{{ error }}</p>
    <div class="flex flex-wrap gap-3 mt-7">
      <input v-model="query" class="admin-input flex-1" :placeholder="tr('Name, phone or subject', 'نام، شماره تماس یا موضوع')">
      <select v-model="status" class="admin-select !w-auto">
        <option value="">{{ tr('All requests', 'همه درخواست‌ها') }}</option>
        <option v-for="key in ['submitted','in_progress','resolved','rejected']" :key="key" :value="key">{{ label(key) }}</option>
      </select>
      <select v-model="category" class="admin-select !w-auto"><option value="">{{ tr('All categories','همه دسته‌بندی‌ها') }}</option><option v-for="(_,key) in categoryLabels" :key="key" :value="key">{{ categoryLabel(key) }}</option></select>
    </div>
    <div class="ticket-workspace mt-6">
      <section class="admin-card p-4">
        <p class="admin-label mb-3">{{ total }} {{ tr('matching requests', 'درخواست مطابق فیلتر') }}</p>
        <div class="ticket-grid ticket-grid-head"><span>{{ tr('Subject','موضوع') }}</span><span>{{ tr('Category','دسته') }}</span><span>{{ tr('Requester','درخواست‌کننده') }}</span><span>{{ tr('Status','وضعیت') }}</span><span>{{ tr('Date','تاریخ') }}</span></div>
        <button v-for="item in rows" :key="item.id" type="button" class="ticket-row" :class="[{selected:selected?.id===item.id}, 'ticket-status-'+item.status]" @click="open(item)">
          <strong class="ticket-subject">{{ item.subject }}</strong><span>{{ categoryLabel(item.category) }}</span><span>{{ item.name }} · <bdi>{{ item.phone }}</bdi></span><span class="ticket-status-text">{{ label(item.status) }}</span><small>{{ date(item.created_at) }}</small>
        </button>
        <p v-if="!rows.length" class="p-8 text-ink-muted">{{ busy ? tr('Loading…','در حال دریافت…') : tr('No matching requests.', 'درخواستی پیدا نشد.') }}</p>
        <div class="flex items-center justify-between mt-5"><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="busy||page===1" @click="page--;load()">{{ tr('Previous','قبلی') }}</button><span>{{ page }}</span><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="busy||page*20>=total" @click="page++;load()">{{ tr('Next','بعدی') }}</button></div>
      </section>
      <section v-if="selected" class="admin-card p-6 md:p-8">
        <div class="flex justify-between gap-4"><h2 class="admin-h2 ticket-subject" :class="'ticket-status-'+selected.status">{{ selected.subject }}</h2><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="selected=null;selectionRequest++">{{ tr('Back to history','بازگشت به تاریخچه') }}</button></div><p class="mt-3"><span class="admin-badge me-2">{{ categoryLabel(selected.category) }}</span>{{ selected.name }} · <bdi>{{ selected.phone }}</bdi></p><p v-if="selected.email" class="text-sm text-ink-muted">{{ selected.email }}</p>
        <p class="whitespace-pre-wrap admin-panel p-5 my-6">{{ selected.message }}</p>
        <ol class="ticket-history"><li v-for="(event,i) in selected.history" :key="i"><div class="flex justify-between gap-3"><strong>{{ label(event.status) }}</strong><small>{{ date(event.at) }}</small></div><p v-if="event.reply" class="mt-3 whitespace-pre-wrap">{{ event.reply }}</p><details class="mt-3 text-xs text-ink-muted"><summary>{{ tr('SMS notification', 'اطلاع‌رسانی پیامکی') }} · {{ event.notification === 'mock' ? tr('Simulation','آزمایشی') : event.notification }}</summary><p class="whitespace-pre-wrap break-all mt-2">{{ event.sms_text }}</p></details></li></ol>
        <form class="mt-7 space-y-4" @submit.prevent="save">
          <label class="block"><span class="admin-label">{{ tr('Status','وضعیت') }}</span><select v-model="nextStatus" class="admin-select"><option v-for="(_,key) in labels" :key="key" :value="key">{{ label(key) }}</option></select></label>
          <button :disabled="busy" class="admin-btn admin-btn-primary">{{ tr('Save status','ثبت وضعیت') }}</button>
        </form>
      </section>
      <section v-else class="admin-card p-6 md:p-8 ticket-archive">
        <div class="flex justify-between items-center gap-3"><h2 class="admin-h2">{{ tr('Ticket history','تاریخچه تیکت‌ها') }}</h2><span class="admin-badge">{{ historyTotal }} {{ tr('closed','بسته‌شده') }}</span></div>
        <div class="ticket-grid ticket-grid-head"><span>{{ tr('Subject','موضوع') }}</span><span>{{ tr('Category','دسته') }}</span><span>{{ tr('Requester','درخواست‌کننده') }}</span><span>{{ tr('Status','وضعیت') }}</span><span>{{ tr('Date','تاریخ') }}</span></div>
        <button v-for="item in history" :key="item.id" type="button" :class="['ticket-row', 'ticket-status-'+item.status]" @click="open(item)"><strong class="ticket-subject">{{ item.subject }}</strong><span>{{ categoryLabel(item.category) }}</span><span>{{ item.name }}</span><span class="ticket-status-text">{{ label(item.status) }}</span><small>{{ date(item.updated_at || item.created_at) }}</small></button>
        <p v-if="!history.length" class="py-10 text-ink-muted">{{ busy ? tr('Loading…','در حال دریافت…') : tr('No closed requests.','هنوز درخواست بسته‌شده‌ای وجود ندارد.') }}</p>
        <div v-if="historyTotal>4" class="flex justify-between mt-5"><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="busy||historyPage===1" @click="historyPage--;load()">{{ tr('Previous','قبلی') }}</button><span>{{ historyPage }}</span><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="busy||historyPage*4>=historyTotal" @click="historyPage++;load()">{{ tr('Next','بعدی') }}</button></div>
      </section>
    </div>
  </div>
</template>
<style scoped>
.ticket-workspace{display:grid;grid-template-columns:minmax(0,1fr);gap:1.5rem;align-items:start}.ticket-grid,.ticket-row{display:grid;grid-template-columns:minmax(180px,1.6fr) minmax(110px,.8fr) minmax(160px,1.2fr) minmax(100px,.7fr) minmax(145px,1fr);gap:1rem;align-items:center}.ticket-grid-head{padding:.65rem .8rem;border-bottom:1px solid rgb(var(--c-ink)/.16);font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;color:rgb(var(--c-ink-muted))}.ticket-row{width:100%;text-align:start;padding:1rem .8rem;border-bottom:1px solid rgb(var(--c-ink)/.1);border-inline-start:3px solid transparent}.ticket-row.selected{background:rgb(var(--c-gold)/.1);border-inline-start-color:rgb(var(--c-gold))}.ticket-status-text{font-size:.78rem;font-weight:500;color:var(--ticket-color,rgb(var(--c-ink-soft)))}.ticket-history li{border-inline-start:2px solid rgb(var(--c-gold)/.4);padding:0 1rem 1.5rem}.ticket-history small{color:rgb(var(--c-ink-muted))}@media(max-width:850px){.ticket-grid-head{display:none}.ticket-row{grid-template-columns:1fr 1fr}.ticket-row>*:first-child{grid-column:1/-1}}
</style>
