<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { eventsApi } from '../../api/events.js'
import { productsApi } from '../../api/products.js'
const props = defineProps({ event: { type: Object, required: true } })
const emit = defineEmits(['changed'])
const { locale } = useI18n(), tr = (en, fa) => locale.value === 'fa' ? fa : en
const attendees = ref([]), room = ref(null), error = ref(''), notice = ref(''), busy = ref(false)
let timer, stopped = false, refreshing = false
const refresh = async () => {
  if (stopped || refreshing) return
  refreshing = true
  try {
    const people = await eventsApi.attendees(props.event.id)
    const state = props.event.published && props.event.status !== 'cancelled' ? await eventsApi.live(props.event.slug, locale.value) : null
    if (!stopped) { attendees.value = people.data; room.value = state?.data; error.value = '' }
  } catch (problem) { if (!stopped) error.value = problem.message }
  finally { refreshing = false }
}
const run = async (fn) => {
  if (busy.value) return
  busy.value = true
  try { await fn(); await refresh(); emit('changed') }
  catch (problem) { error.value = problem.message }
  finally { busy.value = false }
}
const configure = (body) => run(() => eventsApi.liveControl(props.event.slug, body))
const cancel = (person) => { if (confirm(tr('Cancel this reservation and free the seat?', 'رزرو این کاربر لغو و ظرفیت آزاد شود؟'))) run(() => eventsApi.cancelAttendee(props.event.id,person.user_id)) }
const finish = () => { if (confirm(tr('End the live session and move this event to the archive?', 'پخش پایان یابد و رویداد به گذشته منتقل شود؟'))) configure({ status: 'completed' }) }
const uploadDocument = async (event) => {
  const file = event.target.files?.[0]
  if (!file || busy.value) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    const uploaded = (await productsApi.upload(file)).data
    const saved = (await eventsApi.adminList()).data.find(item => item.id === props.event.id)
    if (!saved) throw new Error(tr('Event not found.', 'رویداد پیدا نشد.'))
    const document = { name: file.name, url: uploaded.url, type: file.name.split('.').pop().toUpperCase(), size: `${Math.ceil(file.size / 1024)} KB` }
    const translations = saved.translations.map(item => ({ ...item, content: { ...item.content, documents: [...(item.content?.documents || []), document] } }))
    const result = await eventsApi.adminUpdate(saved.id, { translations })
    notice.value = result.data?.approval ? tr('Document sent for approval.', 'سند برای تأیید ارسال شد.') : tr('Document added to Clinical Documents.', 'سند به بخش اسناد بالینی اضافه شد.')
    emit('changed')
  } catch (problem) { error.value = problem.message }
  finally { busy.value = false; event.target.value = '' }
}
onMounted(() => { refresh(); timer = window.setInterval(() => { if (!document.hidden) refresh() }, 5000) })
onUnmounted(() => { stopped = true; clearInterval(timer) })
</script>
<template>
  <div class="space-y-6">
    <p v-if="error" role="alert" class="text-sm text-red-600">{{ error }}</p>
    <section class="admin-panel p-5 space-y-5">
      <div class="flex flex-wrap items-center justify-between gap-3"><h3 class="admin-h2">{{ tr('Live control room','اتاق کنترل زنده') }}</h3><router-link v-if="event.published" :to="`/events/live/${event.slug}`" target="_blank" class="admin-btn admin-btn-ghost admin-btn-sm">{{ tr('Open live hub','مشاهده لایو هاب') }}</router-link></div>
      <p v-if="!event.published" class="text-sm text-ink-muted">{{ tr('Save and publish this event before opening its live room.','برای فعال‌شدن اتاق زنده، ابتدا رویداد را ذخیره و منتشر کنید.') }}</p>
      <template v-if="room">
        <div class="flex flex-wrap gap-3 items-center"><span class="admin-eyebrow">{{ room.event.status }} · {{ room.viewer_count }} {{ tr('online','نفر حاضر') }}</span><button v-if="room.event.status==='upcoming'" :disabled="busy" class="admin-btn admin-btn-primary" @click="configure({status:'live'})">{{ tr('Start live session','شروع پخش زنده') }}</button><button v-if="room.event.status==='live'" :disabled="busy" class="admin-btn admin-btn-danger" @click="finish">{{ tr('End session','پایان برنامه') }}</button></div>
        <div class="flex flex-wrap gap-5"><label class="flex items-center gap-2 text-sm"><input type="checkbox" :checked="room.chat_enabled" :disabled="busy" @change="configure({chat_enabled:$event.target.checked})">{{ tr('Chat open','گفت‌وگو فعال') }}</label><label class="flex items-center gap-2 text-sm"><input type="checkbox" :checked="room.questions_enabled" :disabled="busy" @change="configure({questions_enabled:$event.target.checked})">{{ tr('Questions open','پرسش‌ها فعال') }}</label></div>
        <div class="flex flex-wrap gap-2"><button v-for="(step,index) in room.event.agenda_steps" :key="index" class="admin-btn admin-btn-sm" :class="room.event.current_step===index?'admin-btn-primary':'admin-btn-ghost'" :disabled="busy || room.event.status!=='live'" @click="run(() => eventsApi.liveStep(event.slug,index))">{{ index+1 }} · {{ step }}</button></div>
        <section v-if="room.event.status==='live'" class="border-t border-parchment-deep pt-4"><h4 class="admin-label">{{ tr('Clinical Documents','اسناد بالینی') }}</h4><label class="admin-btn admin-btn-ghost cursor-pointer mt-2">{{ busy ? tr('Uploading…','در حال بارگذاری…') : tr('Upload document','بارگذاری سند') }}<input type="file" accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.txt,.csv" class="sr-only" :disabled="busy" @change="uploadDocument"></label><p v-if="notice" role="status" class="mt-2 text-sm text-emerald-700">{{ notice }}</p></section>
        <div class="grid lg:grid-cols-2 gap-5"><section v-for="kind in ['questions','messages']" :key="kind"><h4 class="admin-label">{{ kind==='questions'?tr('Questions','پرسش‌ها'):tr('Chat','گفت‌وگو') }}</h4><div class="max-h-80 overflow-y-auto space-y-3"><p v-if="!room[kind].length" class="text-sm text-ink-muted">{{ tr('No activity yet.','هنوز پیامی ثبت نشده است.') }}</p><article v-for="item in room[kind]" :key="item.id" class="border border-parchment-deep rounded-lg p-3"><p class="text-xs text-ink-muted">{{ item.author }} <span v-if="item.answered">· {{ tr('Answered','پاسخ داده شد') }}</span></p><p class="text-sm my-2 whitespace-pre-wrap">{{ item.body }}</p><div class="flex gap-2"><button v-if="kind==='questions' && !item.answered" :disabled="busy || room.event.status!=='live'" class="admin-btn admin-btn-ghost admin-btn-sm" @click="run(() => eventsApi.liveAnswer(event.slug,item.id))">{{ tr('Mark answered','علامت پاسخ') }}</button><button :disabled="busy" class="admin-btn admin-btn-danger admin-btn-sm" @click="run(() => eventsApi.liveDelete(event.slug,kind,item.id))">{{ tr('Remove','حذف') }}</button></div></article></div></section></div>
      </template>
    </section>
    <section class="admin-panel p-5 overflow-x-auto"><h3 class="admin-h2 mb-4">{{ tr('Reservations','رزروها') }} · {{ attendees.filter(p=>p.status==='confirmed').length }} / {{ event.capacity ?? '∞' }}</h3><table class="admin-table"><thead><tr><th>{{ tr('Name','نام') }}</th><th>{{ tr('Reserved at','زمان رزرو') }}</th><th>{{ tr('Status','وضعیت') }}</th><th></th></tr></thead><tbody><tr v-for="person in attendees" :key="person.id"><td>{{ person.name }}</td><td>{{ new Date(person.reserved_at).toLocaleString(locale) }}</td><td>{{ person.status==='confirmed'?tr('Confirmed','تأییدشده'):tr('Cancelled','لغوشده') }}</td><td><button v-if="person.status==='confirmed'" :disabled="busy" class="admin-btn admin-btn-danger admin-btn-sm" @click="cancel(person)">{{ tr('Cancel reservation','لغو رزرو') }}</button></td></tr></tbody></table><p v-if="!attendees.length" class="text-sm text-ink-muted">{{ tr('No reservations yet.','هنوز رزروی ثبت نشده است.') }}</p></section>
  </div>
</template>
