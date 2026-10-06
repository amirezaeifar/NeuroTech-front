<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AccountShell from '../../components/account/AccountShell.vue'
import { userApi } from '../../api/user.js'

const { locale } = useI18n()
const rows = ref([]), loading = ref(true), error = ref('')
onMounted(async () => {
  try { rows.value = (await userApi.courses()).data }
  catch (problem) { error.value = problem.message }
  finally { loading.value = false }
})
</script>

<template>
  <AccountShell section="courses">
    <p class="section-intro">{{ locale === 'fa' ? 'دوره‌هایی که به آن‌ها دسترسی دارید و مسیر یادگیری شما.' : 'Courses you can access and continue learning.' }}</p>
    <p v-if="error" class="section-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="section-intro">{{ locale === 'fa' ? 'در حال دریافت…' : 'Loading…' }}</p>
    <div v-else class="course-list">
      <div v-if="!rows.length" class="section-empty"><p>{{ locale === 'fa' ? 'هنوز در دوره‌ای ثبت‌نام نکرده‌اید.' : 'You have not enrolled in a course yet.' }}</p><router-link to="/academy">{{ locale === 'fa' ? 'مشاهده دوره‌ها ←' : 'Explore courses →' }}</router-link></div>
      <router-link v-for="(item, index) in rows" :key="item.id" :to="`/academy/course/${item.slug}`" class="course-entry">
        <span class="course-number">{{ String(index + 1).padStart(2, '0') }}</span>
        <span class="course-copy"><strong>{{ item.titles?.[locale] || item.titles?.en || item.slug }}</strong><small>{{ new Date(item.enrolled_at).toLocaleDateString(locale) }} · {{ item.status }}</small></span>
        <span class="course-arrow" aria-hidden="true">↗</span>
      </router-link>
    </div>
  </AccountShell>
</template>
<style scoped>
.section-intro { margin: 1.2rem 0; color: rgb(var(--c-ink-muted)); font-size: .82rem; }.section-error { color: #ad4148; }.course-list { display: grid; gap: .6rem; margin-top: 1.2rem; }.course-entry { display: flex; align-items: center; gap: 1rem; padding: 1rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .65rem; background: rgb(var(--c-parchment-light)); box-shadow: 0 10px 25px #00000009; transition: transform .2s, border-color .2s; }.course-entry:hover { transform: translateY(-2px); border-color: rgb(var(--c-gold)); }.course-number { color: rgb(var(--c-gold-dark)); font: 400 1.25rem Georgia,serif; }.course-copy { display: grid; gap: .3rem; min-width: 0; flex: 1; }.course-copy strong { font-size: .9rem; font-weight: 500; }.course-copy small { color: rgb(var(--c-ink-muted)); font-size: .72rem; }.course-arrow { color: rgb(var(--c-gold-dark)); font-size: 1.15rem; }.section-empty { padding: 2.2rem; border: 1px dashed rgb(var(--c-parchment-deep)); border-radius: .7rem; text-align: center; color: rgb(var(--c-ink-muted)); }.section-empty a { display: inline-block; margin-top: .75rem; color: rgb(var(--c-gold-dark)); }
@media(prefers-reduced-motion:reduce) { .course-entry { transition: none; } }
</style>
