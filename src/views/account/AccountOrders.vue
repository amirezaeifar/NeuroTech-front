<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AccountShell from '../../components/account/AccountShell.vue'
import { userApi } from '../../api/user.js'

const { locale } = useI18n()
const rows = ref([]), loading = ref(true), error = ref('')
const money = (item) => new Intl.NumberFormat(locale.value, { style: 'currency', currency: item.currency, maximumFractionDigits: item.currency === 'USD' ? 2 : 0 }).format(item.currency === 'USD' ? item.total_minor / 100 : item.total_minor)
onMounted(async () => {
  try { rows.value = (await userApi.orders()).data }
  catch (problem) { error.value = problem.message }
  finally { loading.value = false }
})
</script>

<template>
  <AccountShell section="orders">
    <p class="section-intro">{{ locale === 'fa' ? 'سوابق خرید دوره و محصول شما در یک فهرست.' : 'Your course and product orders in one place.' }}</p>
    <p v-if="error" class="section-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="section-intro">{{ locale === 'fa' ? 'در حال دریافت…' : 'Loading…' }}</p>
    <div v-else class="order-list">
      <p v-if="!rows.length" class="section-empty">{{ locale === 'fa' ? 'هنوز سفارشی ندارید.' : 'You have no orders yet.' }}</p>
      <article v-for="item in rows" :key="item.id" class="order-entry">
        <div class="order-glyph" aria-hidden="true">{{ item.type === 'course' ? '◈' : '◇' }}</div>
        <div class="order-copy"><span class="order-type">{{ item.type === 'course' ? (locale === 'fa' ? 'دوره' : 'Course') : (locale === 'fa' ? 'محصول' : 'Product') }}</span><strong>{{ item.items?.join('، ') || item.id }}</strong><small>{{ new Date(item.created_at).toLocaleDateString(locale) }} · {{ item.status }}</small></div>
        <strong class="order-amount">{{ money(item) }}</strong>
      </article>
    </div>
  </AccountShell>
</template>
<style scoped>
.section-intro { margin: 1.2rem 0; color: rgb(var(--c-ink-muted)); font-size: .82rem; }.section-error { color: #ad4148; }.order-list { display: grid; gap: .55rem; margin-top: 1.2rem; }.order-entry { display: flex; align-items: center; flex-wrap: wrap; gap: .75rem; padding: .8rem .9rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .6rem; background: rgb(var(--c-parchment-light)); box-shadow: 0 10px 25px #00000009; }.order-glyph { display: grid; flex: none; place-items: center; width: 2.2rem; height: 2.2rem; border-radius: .45rem; background: rgb(var(--c-gold) / .14); color: rgb(var(--c-gold-dark)); font-size: 1.1rem; }.order-copy { display: grid; gap: .12rem; min-width: 0; flex: 1; }.order-copy strong { font-size: .8rem; font-weight: 500; line-height: 1.4; }.order-copy small { color: rgb(var(--c-ink-muted)); font-size: .64rem; line-height: 1.35; }.order-type { color: rgb(var(--c-gold-dark)); font-size: .6rem; line-height: 1.4; }.order-amount { margin-inline-start: auto; white-space: nowrap; font-size: .8rem; }.section-empty { padding: 2.2rem; border: 1px dashed rgb(var(--c-parchment-deep)); border-radius: .7rem; color: rgb(var(--c-ink-muted)); text-align: center; }
</style>
