<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { eventsApi } from '../api/events.js'

const route = useRoute()
const { locale } = useI18n()
const busy = ref(true)
const error = ref('')
const reservation = ref(null)
onMounted(async () => {
  try {
    if (typeof route.query.token !== 'string') throw new Error(locale.value === 'fa' ? 'لینک تأیید معتبر نیست.' : 'The confirmation link is invalid.')
    reservation.value = (await eventsApi.confirmReservation(route.query.token)).data
  } catch (problem) { error.value = problem.message }
  finally { busy.value = false }
})
</script>

<template>
  <main class="mx-auto max-w-2xl px-6 py-24 text-center">
    <h1 class="font-serif text-3xl text-ink">{{ locale === 'fa' ? 'تأیید رزرو رویداد' : 'Confirm event reservation' }}</h1>
    <p v-if="busy" class="mt-6 text-ink-muted">{{ locale === 'fa' ? 'در حال تأیید…' : 'Confirming…' }}</p>
    <p v-else-if="error" role="alert" class="mt-6 text-red-700">{{ error }}</p>
    <template v-else-if="reservation">
      <p role="status" class="mt-6 text-ink-soft">{{ locale === 'fa' ? 'رزرو شما تأیید و ثبت شد.' : 'Your reservation is confirmed.' }}</p>
      <router-link :to="`/events/live/${reservation.event_slug}`" class="mt-7 inline-block border-b border-gold text-gold-dark">{{ locale === 'fa' ? 'ورود به صفحه رویداد' : 'Open event hub' }}</router-link>
    </template>
  </main>
</template>
