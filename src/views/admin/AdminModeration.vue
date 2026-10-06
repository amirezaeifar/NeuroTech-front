<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { academyApi } from '../../api/academy.js'
const { locale } = useI18n(), route = useRoute(), router = useRouter()
const tr = (en,fa) => locale.value==='fa' ? fa : en
const queue=ref([]), courses=ref([]), error=ref(''), busy=ref(false), course=ref(String(route.query.course||'')), status=ref(String(route.query.status||'pending')), dateFrom=ref(''), dateTo=ref(''), page=ref(1), total=ref(0), replies=ref({}), openReply=ref(null)
const statuses={attention:['Needs attention','نیازمند رسیدگی'],pending:['New','جدید'],approved:['Approved','تأییدشده'],rejected:['Rejected','ردشده'],needs_reply:['Needs reply','نیازمند پاسخ'],hidden:['Hidden','مخفی‌شده'],all:['All statuses','همه وضعیت‌ها']}
const statusLabel=value=>tr(...(statuses[value]||[value,value]))
const date=value=>new Intl.DateTimeFormat(locale.value,{dateStyle:'medium',timeStyle:'short'}).format(new Date(value))
async function load(reset=false){if(reset)page.value=1;busy.value=true;error.value='';try{const result=await academyApi.adminComments({course:course.value,status:status.value,date_from:dateFrom.value,date_to:dateTo.value,page:page.value,page_size:20});queue.value=result.data;total.value=result.meta.total;router.replace({query:{...(course.value&&{course:course.value}),...(status.value!=='pending'&&{status:status.value})}})}catch(problem){error.value=problem.message}finally{busy.value=false}}
async function act(item,decision){try{await academyApi.moderateComment(item.id,decision);await load()}catch(problem){error.value=problem.message}}
async function sendReply(item){const body=String(replies.value[item.id]||'').trim();if(!body)return;try{await academyApi.replyComment(item.id,body);replies.value[item.id]='';openReply.value=null;await load()}catch(problem){error.value=problem.message}}
async function remove(item){if(!window.confirm(tr('Delete this comment permanently?','این دیدگاه برای همیشه حذف شود؟')))return;try{await academyApi.deleteComment(item.id);await load()}catch(problem){error.value=problem.message}}
let timer
watch([course,status,dateFrom,dateTo],()=>{clearTimeout(timer);timer=setTimeout(()=>load(true),200)})
onMounted(async()=>{try{courses.value=(await academyApi.moderationCourses()).data}catch(_){}await load()})
</script>
<template>
  <div>
    <p class="admin-eyebrow">{{ tr('Comment inbox','صندوق دیدگاه‌ها') }}</p><h1 class="admin-h1 mt-2">{{ tr('Course comment management','مدیریت دیدگاه‌های دوره‌ها') }}</h1><p class="mt-2 text-sm text-ink-muted">{{ tr('Review every discussion with its course and session context.','هر دیدگاه را همراه با زمینه دوره و جلسه بررسی کنید.') }}</p>
    <div class="admin-card p-5 mt-7 grid md:grid-cols-2 xl:grid-cols-4 gap-4">
      <label><span class="admin-label">{{ tr('Course','دوره') }}</span><select v-model="course" class="admin-select"><option value="">{{ tr('All courses','همه دوره‌ها') }}</option><option v-for="item in courses" :key="item.id" :value="item.slug">{{ item.title }}</option></select></label>
      <label><span class="admin-label">{{ tr('Status','وضعیت') }}</span><select v-model="status" class="admin-select"><option v-for="(_,key) in statuses" :key="key" :value="key">{{ statusLabel(key) }}</option></select></label>
      <label><span class="admin-label">{{ tr('From date','از تاریخ') }}</span><input v-model="dateFrom" type="date" class="admin-input"></label><label><span class="admin-label">{{ tr('To date','تا تاریخ') }}</span><input v-model="dateTo" type="date" class="admin-input"></label>
    </div><p v-if="error" class="field-error mt-4" role="alert">{{ error }}</p>
    <div class="mt-6 space-y-4">
      <article v-for="item in queue" :key="item.id" class="admin-card p-5 md:p-6"><div class="grid lg:grid-cols-[1fr,auto] gap-5"><div><div class="flex flex-wrap items-center gap-3"><strong>{{ item.author }}</strong><span class="admin-badge">{{ statusLabel(item.status) }}</span><time class="text-xs text-ink-muted">{{ date(item.created_at) }}</time></div><p class="mt-3 text-sm text-ink-soft leading-7 whitespace-pre-wrap">{{ item.body }}</p><div class="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-ink-muted"><router-link :to="`/academy/course/${item.course_slug}`" class="text-gold-dark hover:underline">{{ item.course_title||item.course_slug }}</router-link><span>{{ item.lesson_title ? tr('Session: ','جلسه: ')+item.lesson_title : tr('General course discussion','دیدگاه عمومی دوره') }}</span></div></div><div class="flex flex-wrap lg:flex-col gap-2 lg:min-w-32"><button class="admin-btn admin-btn-primary admin-btn-sm" @click="openReply=openReply===item.id?null:item.id">{{ tr('Reply','پاسخ') }}</button><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="act(item,'approved')">{{ tr('Approve','تأیید') }}</button><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="act(item,'rejected')">{{ tr('Reject','رد') }}</button><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="act(item,'needs_reply')">{{ tr('Needs reply','نیازمند پاسخ') }}</button><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="act(item,'hidden')">{{ tr('Hide','مخفی‌کردن') }}</button><button class="admin-btn admin-btn-danger admin-btn-sm" @click="remove(item)">{{ tr('Delete','حذف') }}</button></div></div>
        <form v-if="openReply===item.id" class="mt-5 border-t border-parchment-deep/60 pt-5" @submit.prevent="sendReply(item)"><label class="admin-label">{{ tr('Reply text','متن پاسخ') }}</label><textarea v-model="replies[item.id]" required minlength="2" maxlength="4000" rows="3" class="admin-textarea"></textarea><button class="admin-btn admin-btn-primary admin-btn-sm mt-3">{{ tr('Send reply','ارسال پاسخ') }}</button></form>
      </article><p v-if="!queue.length" class="admin-card p-10 text-center text-sm text-ink-muted">{{ busy?tr('Loading…','در حال دریافت…'):tr('No comments match these filters.','دیدگاهی مطابق این فیلترها نیست.') }}</p>
    </div><div v-if="total>20" class="flex justify-between mt-5"><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="busy||page===1" @click="page--;load()">{{ tr('Previous','قبلی') }}</button><span>{{ page }}</span><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="busy||page*20>=total" @click="page++;load()">{{ tr('Next','بعدی') }}</button></div>
  </div>
</template>
