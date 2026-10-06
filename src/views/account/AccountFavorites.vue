<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AccountShell from '../../components/account/AccountShell.vue'
import { userApi } from '../../api/user.js'

const { locale } = useI18n()
const rows = ref([]), loading = ref(true), error = ref('')
const load = async () => {
  try { rows.value = (await userApi.favorites()).data }
  catch (problem) { error.value = problem.message }
  finally { loading.value = false }
}
const remove = async (item) => {
  error.value = ''
  try { await userApi.removeFavorite(item.id); rows.value = rows.value.filter((row) => row.id !== item.id) }
  catch (problem) { error.value = problem.message }
}
onMounted(load)
</script>

<template>
  <AccountShell section="favorites">
    <p class="section-intro">{{ locale === 'fa' ? 'دوره‌ها و محصولاتی که برای بازدید دوباره نگه داشته‌اید.' : 'Courses and products you saved for later.' }}</p>
    <p v-if="error" class="section-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="section-intro">{{ locale === 'fa' ? 'در حال دریافت…' : 'Loading…' }}</p>
    <div v-else class="favorite-list">
      <div v-if="!rows.length" class="section-empty"><p>{{ locale === 'fa' ? 'هنوز موردی به علاقه‌مندی‌ها اضافه نکرده‌اید.' : 'No favorites yet.' }}</p><router-link to="/academy">{{ locale === 'fa' ? 'مشاهده دوره‌ها ←' : 'Explore courses →' }}</router-link></div>
      <article v-for="item in rows" :key="item.id" class="favorite-entry">
        <div class="favorite-mark" aria-hidden="true">♥</div>
        <div class="favorite-copy"><span>{{ item.item_type === 'course' ? (locale === 'fa' ? 'دوره' : 'Course') : (locale === 'fa' ? 'محصول' : 'Product') }}</span><router-link :to="item.item_type === 'course' ? `/academy/course/${item.slug}` : `/products/${item.slug}`">{{ item.titles?.[locale] || item.titles?.en || item.slug }}</router-link></div>
        <button type="button" class="favorite-remove" @click="remove(item)">{{ locale === 'fa' ? 'حذف' : 'Remove' }}</button>
      </article>
    </div>
  </AccountShell>
</template>
<style scoped>
.section-intro { margin: 1.2rem 0; color: rgb(var(--c-ink-muted)); font-size: .82rem; }.section-error { color: #ad4148; }.favorite-list { display: grid; gap: .6rem; margin-top: 1.2rem; }.favorite-entry { display: flex; align-items: center; gap: .9rem; padding: 1rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .65rem; background: rgb(var(--c-parchment-light)); box-shadow: 0 10px 25px #00000009; }.favorite-mark { display: grid; flex: none; place-items: center; width: 2.6rem; height: 2.6rem; border-radius: .5rem; color: #a63f4c; background: #a63f4c13; }.favorite-copy { display: grid; gap: .25rem; flex: 1; min-width: 0; }.favorite-copy span { color: rgb(var(--c-gold-dark)); font-size: .66rem; }.favorite-copy a { font-size: .9rem; font-weight: 500; }.favorite-copy a:hover { color: rgb(var(--c-gold-dark)); }.favorite-remove { padding: .5rem .7rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .4rem; color: #9f4651; font-size: .74rem; }.favorite-remove:hover { background: #a63f4c13; }.section-empty { padding: 2.2rem; border: 1px dashed rgb(var(--c-parchment-deep)); border-radius: .7rem; color: rgb(var(--c-ink-muted)); text-align: center; }.section-empty a { display: inline-block; margin-top: .75rem; color: rgb(var(--c-gold-dark)); }
</style>
