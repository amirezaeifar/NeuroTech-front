<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ticketsApi } from '../api/tickets.js'
const route = useRoute(), { locale } = useI18n()
const ticket = ref(null), error = ref(''), busy = ref(false)
const tr = (en,fa) => locale.value==='fa'?fa:en
const label = (status) => ({submitted:tr('Open','باز'),in_progress:tr('In progress','در حال بررسی'),resolved:tr('Completed','انجام‌شده'),rejected:tr('Rejected','ردشده')})[status]
async function load(){busy.value=true;error.value='';try{ticket.value=(await ticketsApi.track(route.params.token)).data}catch(e){ticket.value=null;error.value=e.message}finally{busy.value=false}}
watch(()=>route.params.token,load,{immediate:true})
</script>
<template><main class="max-w-3xl mx-auto px-6 pt-32 pb-24 w-full"><p class="text-gold-dark">{{ tr('Request tracking','پیگیری درخواست') }}</p><h1 class="text-3xl mt-3">{{ ticket?.subject || tr('Your support request','درخواست پشتیبانی شما') }}</h1><p v-if="error" role="alert" class="mt-6">{{ error }}</p><template v-if="ticket"><p class="mt-6 text-gold-dark">{{ label(ticket.status) }}</p><p class="whitespace-pre-wrap my-8">{{ ticket.message }}</p><article v-for="(event,i) in ticket.history" :key="i" class="border-s-2 border-gold/40 ps-6 pb-8"><p>{{ label(event.status) }} · <small>{{ new Date(event.at).toLocaleString(locale) }}</small></p><p class="whitespace-pre-wrap mt-3">{{ event.reply }}</p></article></template><button class="btn-ghost-gold mt-8" :disabled="busy" @click="load">{{ busy ? tr('Loading…','در حال دریافت…') : tr('Refresh status','به‌روزرسانی وضعیت') }}</button></main></template>
