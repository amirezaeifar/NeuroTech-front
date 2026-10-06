<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AccountShell from '../../components/account/AccountShell.vue'
import { userApi } from '../../api/user.js'

const { locale } = useI18n()
const rows = ref([]), loading = ref(true), error = ref(''), downloading = ref('')
const date = (value) => new Date(value).toLocaleDateString(locale.value, { year: 'numeric', month: 'long', day: 'numeric' })
const money = (item) => new Intl.NumberFormat(locale.value).format(item.currency === 'USD' ? item.amount_minor / 100 : item.amount_minor) + ' ' + item.currency
onMounted(async () => {
  try { rows.value = (await userApi.payments()).data }
  catch (problem) { error.value = problem.message }
  finally { loading.value = false }
})
const download = async (item) => {
  downloading.value = item.id; error.value = ''
  try { await userApi.downloadInvoice(item) }
  catch (problem) { error.value = locale.value === 'fa' ? 'دریافت فاکتور ممکن نشد. دوباره تلاش کنید.' : problem.message }
  finally { downloading.value = '' }
}
</script>

<template>
  <AccountShell section="payments">
    <p class="payment-intro">{{ locale === 'fa' ? 'پرداخت‌های موفق و ناموفق را اینجا می‌بینید. فاکتور هر پرداخت موفق را می‌توانید دریافت کنید.' : 'Review your payments and download an invoice for each successful one.' }}</p>
    <p class="payment-format">{{ locale === 'fa' ? 'فاکتور به‌صورت فایل HTML دریافت می‌شود؛ پس از باز کردن آن می‌توانید نسخه PDF ذخیره کنید.' : 'Invoices download as HTML files. Open one to save a PDF copy.' }}</p>
    <p v-if="error" class="payment-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="payment-intro">{{ locale === 'fa' ? 'در حال دریافت…' : 'Loading…' }}</p>
    <div v-else class="payment-list">
      <div v-if="!rows.length" class="payment-empty">{{ locale === 'fa' ? 'هنوز پرداختی ثبت نشده است.' : 'No payments recorded yet.' }}</div>
      <article v-for="item in rows" :key="item.id" class="payment-card">
        <div class="payment-icon" aria-hidden="true">↗</div>
        <div class="payment-main">
          <span class="payment-type">{{ item.type === 'course' ? (locale === 'fa' ? 'دوره' : 'Course') : (locale === 'fa' ? 'محصول' : 'Product') }}</span>
          <strong>{{ money(item) }}</strong>
          <span class="payment-meta">{{ date(item.created_at) }} · {{ locale === 'fa' ? 'سفارش' : 'Order' }} {{ item.order_id.slice(0, 8) }}</span>
        </div>
        <div class="payment-actions">
          <span class="payment-status" :class="item.status === 'succeeded' ? 'is-paid' : ''">{{ item.status === 'succeeded' ? (locale === 'fa' ? 'پرداخت موفق' : 'Paid') : item.status }}</span>
          <button v-if="item.status === 'succeeded'" type="button" :disabled="downloading === item.id" @click="download(item)">
            {{ downloading === item.id ? (locale === 'fa' ? 'در حال دریافت…' : 'Downloading…') : (locale === 'fa' ? 'دریافت فاکتور' : 'Download invoice') }} <span aria-hidden="true">↓</span>
          </button>
        </div>
      </article>
    </div>
  </AccountShell>
</template>

<style scoped>
.payment-intro { margin-top: 1.2rem; color: rgb(var(--c-ink-muted)); font-size: .82rem; line-height: 1.7; }.payment-error { margin-top: 1rem; color: #ad4148; }
.payment-format { margin-top: .45rem; color: rgb(var(--c-ink-muted)); font-size: .72rem; line-height: 1.7; }
.payment-list { display: grid; gap: .65rem; margin-top: 1.25rem; }.payment-card { display: flex; align-items: center; gap: .9rem; padding: 1rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .7rem; background: rgb(var(--c-parchment-light)); box-shadow: 0 12px 24px #00000009; }
.payment-icon { display: grid; flex: none; place-items: center; width: 2.6rem; height: 2.6rem; border-radius: .5rem; background: rgb(var(--c-gold) / .13); color: rgb(var(--c-gold-dark)); font-size: 1.2rem; }.payment-main { display: grid; gap: .2rem; min-width: 0; flex: 1; }.payment-main strong { font-size: 1rem; }.payment-type { color: rgb(var(--c-gold-dark)); font-size: .64rem; text-transform: uppercase; letter-spacing: .12em; }.payment-meta { color: rgb(var(--c-ink-muted)); font-size: .72rem; overflow-wrap: anywhere; }
.payment-actions { display: flex; flex-direction: row; align-items: center; justify-content: flex-end; gap: .7rem; white-space: nowrap; }.payment-status { padding: .25rem .6rem; border-radius: 99px; background: rgb(var(--c-ink) / .08); color: rgb(var(--c-ink-muted)); font-size: .7rem; }.payment-status.is-paid { background: #2c9a721b; color: #237653; }.payment-actions button { display: inline-flex; align-items: center; gap: .45rem; padding: .5rem .65rem; border: 1px solid rgb(var(--c-gold)); border-radius: .45rem; color: rgb(var(--c-gold-dark)); font-size: .72rem; }.payment-actions button:hover { background: rgb(var(--c-gold) / .12); }.payment-actions button:disabled { opacity: .5; cursor: wait; }
.payment-empty { padding: 2.5rem; border: 1px dashed rgb(var(--c-parchment-deep)); border-radius: .7rem; color: rgb(var(--c-ink-muted)); text-align: center; }
@media (max-width: 640px) { .payment-card { align-items: flex-start; flex-wrap: wrap; }.payment-actions { width: 100%; justify-content: flex-end; } }
</style>
