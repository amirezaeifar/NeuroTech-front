<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { academyApi } from '../../api/academy.js'
import { productsApi } from '../../api/products.js'
import { partnersApi } from '../../api/content.js'
import { ticketsApi } from '../../api/tickets.js'
import { eventsApi } from '../../api/events.js'
import { governanceApi } from '../../api/governance.js'
import { ordersApi } from '../../api/orders.js'
import { authApi } from '../../api/auth.js'
import { sectionsForRole } from '../../data/adminSections.js'
import { useAuth } from '../../composables/useAuth.js'
const { locale } = useI18n()
const { user, role, isAdmin } = useAuth()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const busy = ref(true), error = ref(''), courses = ref([]), products = ref([]), partners = ref([]), events = ref([]), articles = ref([]), orders = ref([]), approvals = ref([]), members = ref([]), comments = ref([]), tickets = ref([]), pending = ref(null), active = ref(null), completed = ref(null), updatedAt = ref(null)
const allowed = computed(() => new Set(sectionsForRole(role.value).map(section => section.key)))
const can = key => allowed.value.has(key)
const name = computed(() => user.value?.display_name || user.value?.email?.split('@')[0] || '')
async function load() {
  busy.value = true; error.value = ''
  const jobs = []
  if (can('courses')) jobs.push([() => academyApi.adminList(), result => { courses.value = result.data }])
  if (can('products')) jobs.push([() => productsApi.adminList(), result => { products.value = result.data }])
  if (can('partners')) jobs.push([() => partnersApi.adminList(), result => { partners.value = result.data }])
  if (can('events')) jobs.push([() => eventsApi.adminList(), result => { events.value = result.data }])
  if (can('blog')) jobs.push([() => governanceApi.blogs(), result => { articles.value = result.data }])
  if (can('orders')) jobs.push([() => ordersApi.adminList(), result => { orders.value = result.data }])
  if (can('approvals')) jobs.push([() => governanceApi.approvals(), result => { approvals.value = result.data }])
  if (can('users')) jobs.push([() => authApi.adminUsers(), result => { members.value = result.data }])
  if (can('moderation')) jobs.push([() => academyApi.adminComments({ status: 'pending', page_size: 5 }), result => { comments.value = result.data }])
  if (isAdmin.value) jobs.push(
    [() => ticketsApi.list({page_size:5}), result => { tickets.value = result.data }],
    [() => ticketsApi.list({status:'submitted',page_size:1}), result => { pending.value = result.meta.total }],
    [() => ticketsApi.list({status:'in_progress',page_size:1}), result => { active.value = result.meta.total }],
    [() => ticketsApi.list({status:'resolved',page_size:1}), result => { completed.value = result.meta.total }],
  )
  const results = await Promise.allSettled(jobs.map(async ([fetch, apply]) => apply(await fetch())))
  if (results.some(result => result.status === 'rejected')) error.value = tr('Some information could not be loaded. Please refresh.', 'بخشی از اطلاعات دریافت نشد؛ دوباره تلاش کنید.')
  if (!error.value) updatedAt.value = new Date()
  busy.value = false
}
const collections = computed(() => [
  {title:tr('Courses','دوره‌ها'),items:courses.value,path:'/admin/courses',icon:'book',hint:tr('Curriculum, lessons & learning','سرفصل‌ها، درس‌ها و یادگیری')},
  {title:tr('Products','محصولات'),items:products.value,path:'/admin/products',icon:'box',hint:tr('Catalogue, images & specifications','کاتالوگ، تصاویر و مشخصات')},
  {title:tr('Partners','همکاران'),items:partners.value,path:'/admin/partners',icon:'users',hint:tr('People, experience & expertise','افراد، سوابق و تخصص‌ها')},
  {title:tr('Events','رویدادها'),items:events.value,path:'/admin/events',icon:'calendar',hint:tr('Upcoming, live and past events','رویدادهای آینده، زنده و گذشته')},
  {title:tr('Articles','مقالات'),items:articles.value,path:'/admin/articles',icon:'doc',hint:tr('Scientific articles and stories','مقالات علمی و یادداشت‌ها')},
].filter(collection => can(collection.path.split('/').at(-1) === 'articles' ? 'blog' : collection.path.split('/').at(-1))))
const previews = computed(() => [
  can('courses') && { title:tr('Recent courses','دوره‌های اخیر'), path:'/admin/courses', items:courses.value, label:item=>item.title || item.name },
  can('products') && { title:tr('Recent products','محصولات اخیر'), path:'/admin/products', items:products.value, label:item=>item.title || item.name },
  can('events') && { title:tr('Upcoming and live events','رویدادهای پیش‌رو و زنده'), path:'/admin/events', items:events.value.filter(item=>['upcoming','live'].includes(item.status)), label:item=>`${item.title} · ${item.status}` },
  can('blog') && { title:tr('Recent articles','مقالات اخیر'), path:'/admin/articles', items:articles.value, label:item=>item.title },
  can('partners') && { title:tr('Recent partners','همکاران اخیر'), path:'/admin/partners', items:partners.value, label:item=>item.name || item.title },
  can('orders') && { title:tr('Recent orders','سفارش‌های اخیر'), path:'/admin/orders', items:orders.value, label:item=>item.order_number || item.id },
  can('approvals') && { title:tr('Pending approvals','تأییدهای در انتظار'), path:'/admin/approvals', items:approvals.value, label:item=>item.action || item.entity_type || item.id },
  can('users') && { title:tr('Recent members','اعضای اخیر'), path:'/admin/users', items:members.value, label:item=>item.display_name || item.email },
  can('moderation') && { title:tr('Comments awaiting review','دیدگاه‌های در انتظار'), path:'/admin/moderation', items:comments.value, label:item=>item.body },
].filter(Boolean))
const published = items => items.filter(item => item.published).length
const status = value => ({submitted:tr('Open','باز'),in_progress:tr('In progress','در حال بررسی'),resolved:tr('Completed','انجام‌شده'),rejected:tr('Rejected','ردشده')})[value]
onMounted(load)
</script>
<template>
  <div class="overview">
    <header class="overview-intro"><div><p class="admin-eyebrow">{{ tr('Management overview','نمای کلی مدیریت') }}</p><h1>{{ tr('Dashboard','داشبورد') }}</h1><p class="overview-subtitle">{{ tr('Content status and support requests.', 'وضعیت محتوا و درخواست‌های پشتیبانی.') }}</p></div><button class="admin-btn admin-btn-ghost" :disabled="busy" @click="load">{{ busy ? tr('Loading…','در حال دریافت…') : tr('Refresh','به‌روزرسانی') }}</button></header>
    <div class="overview-details"><span>{{ tr('Signed in as','کاربر') }}: <strong>{{ name }}</strong></span><span>{{ tr('Published content','محتوای منتشرشده') }}: <strong>{{ busy ? '—' : collections.reduce((sum,c)=>sum+published(c.items),0) }}</strong></span><span>{{ tr('Last updated','آخرین دریافت') }}: <time>{{ updatedAt ? updatedAt.toLocaleTimeString(locale,{hour:'2-digit',minute:'2-digit'}) : '—' }}</time></span></div>
    <p v-if="error" role="alert" class="admin-panel p-4">{{ error }}</p>
    <section v-if="isAdmin" class="support-focus">
      <div class="focus-copy"><span class="focus-kicker">{{ tr('Support','پشتیبانی') }}</span><h2>{{ tr('Request status', 'وضعیت درخواست‌ها') }}</h2><p>{{ tr('Review requests and record responses.', 'درخواست‌ها را بررسی و پاسخ را ثبت کنید.') }}</p><router-link to="/admin/tickets" class="focus-link">{{ tr('Open support desk','ورود به مرکز تیکت‌ها') }} <span aria-hidden="true">↗</span></router-link></div>
      <div class="focus-counts"><router-link to="/admin/tickets"><strong>{{ pending ?? '—' }}</strong><span>{{ tr('Awaiting review','در انتظار بررسی') }}</span></router-link><router-link to="/admin/tickets"><strong>{{ active ?? '—' }}</strong><span>{{ tr('In progress','در حال رسیدگی') }}</span></router-link><router-link to="/admin/tickets"><strong>{{ completed ?? '—' }}</strong><span>{{ tr('Completed','انجام‌شده') }}</span></router-link></div>
    </section>
    <div class="overview-section-title"><h2>{{ tr('Your collections','محتوای شما') }}</h2><span>{{ tr('Publication status','وضعیت انتشار') }}</span></div>
    <section class="collection-grid"><router-link v-for="collection in collections" :key="collection.path" :to="collection.path" class="collection-card"><div class="flex justify-between"><h3>{{ collection.title }}</h3><span class="collection-arrow">↗</span></div><p>{{ collection.hint }}</p><strong class="collection-number">{{ busy ? '—' : collection.items.length }}</strong><div class="collection-meter"><span :style="{width: `${collection.items.length ? published(collection.items)/collection.items.length*100 : 0}%`}"></span></div><div class="collection-meta"><span>{{ published(collection.items) }} {{ tr('published','منتشرشده') }}</span><span>{{ collection.items.length-published(collection.items) }} {{ tr('drafts','پیش‌نویس') }}</span></div></router-link></section>
    <div class="overview-bottom"><section v-if="isAdmin" class="admin-card p-6"><div class="overview-section-title !mt-0"><h2>{{ tr('Latest requests','آخرین درخواست‌ها') }}</h2><router-link to="/admin/tickets">{{ tr('View all','مشاهده همه') }}</router-link></div><router-link v-for="ticket in tickets" :key="ticket.id" to="/admin/tickets" class="recent-ticket"><span><strong class="ticket-subject" :class="'ticket-status-'+ticket.status">{{ ticket.subject }}</strong><small>{{ ticket.name }}</small></span><span class="admin-badge">{{ status(ticket.status) }}</span></router-link><p v-if="!tickets.length" class="py-8 text-ink-muted">{{ tr('New requests will appear here.','درخواست‌های جدید اینجا نمایش داده می‌شوند.') }}</p></section><section class="admin-card p-6"><h2 class="admin-h2">{{ tr('Quick access','دسترسی سریع') }}</h2><router-link v-for="collection in collections" :key="collection.path" :to="collection.path" class="quick-action"><span>+ {{ tr('Create / edit','ایجاد / ویرایش') }} {{ collection.title }}</span><span>↗</span></router-link></section></div>
    <div class="overview-section-title"><h2>{{ tr('Section previews','پیش‌نمایش بخش‌ها') }}</h2></div>
    <section class="preview-grid"><article v-for="preview in previews" :key="preview.path" class="admin-card p-5"><div class="flex items-center justify-between gap-3"><h3 class="admin-h2">{{ preview.title }}</h3><router-link :to="preview.path" class="text-xs text-gold-dark">{{ tr('View all','مشاهده همه') }} ↗</router-link></div><router-link v-for="(item,index) in preview.items.slice(0,3)" :key="item.id || index" :to="preview.path" class="quick-action"><span class="truncate">{{ preview.label(item) || '—' }}</span><span>↗</span></router-link><p v-if="!preview.items.length" class="mt-5 text-sm text-ink-muted">{{ tr('Nothing to show yet.','هنوز موردی برای نمایش نیست.') }}</p></article></section>
  </div>
</template>
<style scoped>
.overview-details{display:flex;flex-wrap:wrap;gap:1rem 2rem;padding:.9rem 0 1.2rem;margin-bottom:1rem;border-bottom:1px solid rgb(var(--c-ink)/.1);font-size:.75rem;color:rgb(var(--c-ink-muted))}.overview-details strong,.overview-details time{color:rgb(var(--c-ink));font-variant-numeric:tabular-nums}.collection-meter span{transition:width .35s ease}.focus-counts a{min-width:0}
.preview-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:1.2rem}.preview-grid .quick-action{min-width:0}

.overview{max-width:1440px;margin:auto}.overview-intro{display:flex;align-items:center;justify-content:space-between;gap:2rem;margin-bottom:2rem}.overview-intro h1{font-family:'Mikhak','Inter',sans-serif;font-size:clamp(1.7rem,3vw,2.7rem);font-weight:500;line-height:1.5;margin:.65rem 0}.overview-subtitle{color:rgb(var(--c-ink-muted));font-size:.9rem;line-height:1.9}.support-focus{display:grid;grid-template-columns:1.3fr 1fr;background:#252c2a;border:1px solid #404940;color:#f5f1e6;border-radius:22px;overflow:hidden}.focus-copy{padding:2.4rem}.focus-kicker{font-size:.72rem;color:#d8bd80}.focus-copy h2{font-size:clamp(1.4rem,2.4vw,2rem);line-height:1.65;margin:1rem 0}.focus-copy p{max-width:440px;font-size:.85rem;color:#c5cec6;line-height:1.9}.focus-link{display:inline-flex;align-items:center;gap:2rem;background:#dfc897;color:#242b27;padding:.8rem 1.2rem;border-radius:9px;margin-top:1.8rem;font-size:.85rem}.focus-counts{display:grid;grid-template-columns:repeat(3,1fr);align-items:center;border-inline-start:1px solid #455047;background:radial-gradient(ellipse at bottom,#48524670,transparent)}.focus-counts a{display:flex;flex-direction:column;text-align:center;padding:2rem .5rem}.focus-counts a+a{border-inline-start:1px solid #455047}.focus-counts strong{font-size:3rem;font-weight:400;font-variant-numeric:tabular-nums;color:#dfc897;line-height:1.3}.focus-counts span{font-size:.8rem;color:#c5cec6;margin-top:1rem}.overview-section-title{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:2.1rem 0 1.1rem}.overview-section-title h2{font-size:1.1rem;font-weight:500}.overview-section-title>span,.overview-section-title>a{font-size:.75rem;color:rgb(var(--c-ink-muted))}.collection-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem}.collection-card{border:1px solid rgb(var(--c-ink)/.12);background:rgb(var(--c-parchment));border-radius:16px;padding:1.6rem;transition:border-color .2s,background .2s}.collection-card:hover{border-color:rgb(var(--c-gold))}.collection-card h3{font-size:1.1rem}.collection-card p{font-size:.78rem;color:rgb(var(--c-ink-muted));margin-top:.7rem}.collection-arrow{color:rgb(var(--c-gold-dark))}.collection-number{display:block;font-size:2.6rem;font-weight:400;margin:1.5rem 0 .9rem}.collection-meter{height:4px;background:rgb(var(--c-ink)/.07);border-radius:4px;overflow:hidden}.collection-meter span{display:block;height:100%;background:rgb(var(--c-gold))}.collection-meta{display:flex;justify-content:space-between;margin-top:.8rem;font-size:.7rem;color:rgb(var(--c-ink-muted))}.overview-bottom{display:grid;grid-template-columns:1.4fr 1fr;gap:1.2rem;margin-top:1.5rem}.recent-ticket,.quick-action{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:1.15rem 0;border-bottom:1px solid rgb(var(--c-ink)/.09);font-size:.85rem}.recent-ticket small{display:block;margin-top:.4rem;color:rgb(var(--c-ink-muted))}.quick-action:last-child,.recent-ticket:last-child{border-bottom:0}@media(max-width:1100px){.support-focus{grid-template-columns:1fr}.focus-counts{border-inline-start:0;border-top:1px solid #455047}.focus-counts a{padding:1rem}.focus-counts strong{font-size:2.5rem}}@media(max-width:700px){.overview-intro{align-items:start;gap:.7rem}.overview-intro button{font-size:.7rem}.collection-grid,.overview-bottom{grid-template-columns:1fr}.focus-copy{padding:1.5rem}.collection-number{margin:1rem 0}.overview-section-title>span{display:none}}
</style>
