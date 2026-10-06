<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import VideoPlayer from '../components/VideoPlayer.vue'
import { useReveal } from '../composables/useReveal.js'
import { eventsApi } from '../api/events.js'
import { resolveApiUrl } from '../api/client.js'

const { t, locale } = useI18n(), route = useRoute(), router = useRouter()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const room = ref(null), error = ref(''), loading = ref(true), busy = ref(false)
const showRegistered = ref(true), panel = ref('chat'), draft = ref(''), clock = ref(Date.now())
const slug = computed(() => route.params.slug || route.params.id)
const item = computed(() => room.value?.event)
const isLive = computed(() => item.value?.status === 'live')
const isOnsite = computed(() => item.value?.kind === 'onsite' && !isLive.value)
const presenter = computed(() => item.value?.host_label || item.value?.venue || '')
const content = computed(() => item.value?.content || {})
const viewers = computed(() => room.value?.viewer_count || 0)
const questionsAsked = computed(() => room.value?.question_count || 0)
const initialLoading = ref(true)
let pollTimer, clockTimer, sequence = 0, stopped = false
const refresh = async () => {
  const request = ++sequence
  try {
    const response = await eventsApi.live(slug.value, locale.value)
    if (stopped || request !== sequence) return
    room.value = response.data; error.value = ''
  } catch (problem) {
    if (!stopped && request === sequence) {
      error.value = problem.message
      if ([401,403,404,409].includes(problem.status)) room.value = null
    }
  } finally { if (!stopped && request === sequence) { loading.value = false; initialLoading.value = false } }
}
const poll = async () => { if (!document.hidden || initialLoading.value) await refresh(); if (!stopped) pollTimer = setTimeout(poll, 5000) }
onMounted(() => { poll(); clockTimer = setInterval(() => { clock.value = Date.now() }, 1000) })
onUnmounted(() => { stopped = true; sequence++; clearTimeout(pollTimer); clearInterval(clockTimer) })
watch([slug, locale], () => { room.value = null; loading.value = true; showRegistered.value = true; draft.value = ''; refresh() })
const durationLabel = (seconds) => { const n = Math.max(0, Math.floor(seconds || 0)); return [Math.floor(n/3600),Math.floor(n/60)%60,n%60].map(v=>String(v).padStart(2,'0')).join(':') }
const elapsed = computed(() => isLive.value ? durationLabel((clock.value - new Date(item.value?.live_started_at || item.value?.starts_at).getTime())/1000) : '00:00:00')
const countries = computed(() => room.value?.countries || {})
const stats = computed(() => [
  { label: t('events.active.stats.viewers'), value: viewers.value },
  { label: t('events.active.stats.questions'), value: questionsAsked.value },
  { label: t('events.active.stats.elapsed'), value: elapsed.value },
  { label: t('events.active.stats.countries'), value: Object.keys(countries.value).filter(c=>c!=='--').length },
])
const asset = url => url?.startsWith('/api/') ? resolveApiUrl(url) : url
const download = url => url?.startsWith('/api/') ? `${resolveApiUrl(url)}?download=1` : url
const documents = computed(() => content.value.documents || [])
const venueSchedule = computed(() => (content.value.agenda || []).map(a => ({ time: a.time, label: a.title })))
const onsiteStats = computed(() => [
  { label: tr('Confirmed reservations','رزروهای تأییدشده'), value: item.value?.reserved || 0 },
  { label: t('events.active.onsiteStats.sessions'), value: agenda.value.length },
  { label: tr('Scheduled duration','مدت برنامه'), value: durationLabel((new Date(item.value?.ends_at)-new Date(item.value?.starts_at))/1000) },
  { label: t('events.active.onsiteStats.materials'), value: documents.value.length },
])
const mediaUrl = computed(() => isLive.value ? item.value?.online_url || '' : item.value?.status === 'completed' ? content.value.videos?.[0]?.url || '' : '')
const mediaNotice = computed(() => mediaUrl.value ? '' : isLive.value ? tr('The host has not added a stream yet.','لینک پخش هنوز ثبت نشده است.') : item.value?.status === 'completed' ? tr('The recording will appear here when available.','ویدئوی ضبط‌شده پس از انتشار اینجا نمایش داده می‌شود.') : tr('The live session has not started yet.','پخش زنده هنوز آغاز نشده است.'))
const initials = name => String(name || '').split(/[\s.]+/).filter(Boolean).slice(0,2).map(p=>p[0]).join('').toUpperCase()
const timeLabel = value => value ? new Intl.DateTimeFormat(locale.value,{hour:'2-digit',minute:'2-digit',timeZone:item.value?.timezone || 'Asia/Tehran'}).format(new Date(value)) : ''
const chat = computed(() => (room.value?.messages || []).map(m => ({...m,user:m.author,text:m.body,time:timeLabel(m.created_at)})))
const qa = computed(() => (room.value?.questions || []).map(q => ({...q,user:q.author,text:q.body,time:timeLabel(q.created_at)})).sort((a,b)=>Number(a.answered)-Number(b.answered)||b.votes-a.votes))
const conversationClosed = computed(() => !isLive.value || !(panel.value==='chat' ? room.value?.chat_enabled : room.value?.questions_enabled))
const action = async fn => { if (busy.value) return; busy.value = true; try { await fn(); await refresh() } catch (problem) { error.value = problem.message } finally { busy.value = false } }
const send = async () => {
  const text = draft.value.trim(); if (!text || conversationClosed.value || busy.value) return
  await action(async () => { await (panel.value==='chat' ? eventsApi.liveMessage(slug.value,text) : eventsApi.liveQuestion(slug.value,text)); draft.value = '' })
}
const agenda = computed(() => (item.value?.agenda_steps || []).map((title,index) => ({
  title, time: content.value.agenda?.[index]?.time || String(index+1).padStart(2,'0'),
  duration: durationLabel((item.value.step_durations?.[index] || 0) + (isLive.value && index === item.value.current_step && item.value.step_started_at ? Math.max(0, (clock.value - new Date(item.value.step_started_at).getTime()) / 1000) : 0)),
  status: item.value.status==='completed' || (isLive.value && index < item.value.current_step) ? 'done' : isLive.value && index === item.value.current_step ? 'live' : 'upcoming',
})))
const statusLabel = s => ({done:t('events.active.done'),live:t('events.active.now'),soon:t('events.active.soon'),upcoming:''}[s] || '')
const speakers = computed(() => (item.value?.speakers || []).map(sp => ({ ...sp, title:sp.role_label, org:presenter.value, tag:sp.role_label })))
const docIcon = type => type==='XLSX' ? 'M7 3h7l4 4v14H7z M9 12l4 4 M13 12l-4 4' : 'M7 3h7l4 4v14H7z M14 3v4h4 M9 13h6 M9 16h4'
useReveal()
</script>

<template>
  <div v-if="item" class="event-hub-page bg-parchment-light min-h-screen pb-20">
    <!-- Live header bar — just the back link (the Live badge and viewer count
         that used to sit here have been removed for a cleaner header). -->
    <div class="bg-ink">
      <div class="max-w-6xl mx-auto px-6 py-5 flex flex-wrap items-center gap-4">
        <router-link to="/events" class="text-[11px] uppercase tracking-[0.25em] text-gold/80 hover:text-gold transition-colors inline-flex items-center gap-2">
          <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('events.active.back') }}
        </router-link>
      </div>
    </div>

    <!-- Registered confirmation — dismissible. The X collapses it out with a
         smooth fade + slide-up <Transition> (alert-collapse). -->
    <Transition name="alert-collapse">
      <div v-if="showRegistered && !isOnsite && !room.instructor" class="bg-gold/10 border-b border-gold/30">
        <div class="max-w-6xl mx-auto px-6 py-2.5 flex items-center justify-between gap-3 text-xs text-ink-soft font-light">
          <span class="flex items-center gap-2.5">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" class="text-gold-dark shrink-0"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>{{ t('events.active.registered') }}</span>
          </span>
          <button
            type="button"
            @click="showRegistered = false"
            :aria-label="t('events.active.dismiss')"
            class="shrink-0 p-1 text-ink-muted hover:text-gold-dark transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
          </button>
        </div>
      </div>
    </Transition>

    <p v-if="error" role="alert" class="max-w-6xl mx-auto px-6 pt-5 text-sm text-red-600">{{ error }}</p><div class="max-w-6xl mx-auto px-6 pt-6 grid lg:grid-cols-12 gap-6">
      <!-- ================= MAIN COLUMN ================= -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Title -->
        <div>
          <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ item.kind }}</span>
          <h1 class="font-serif font-light text-2xl md:text-3xl text-ink mt-1.5 leading-snug">{{ item.title }}</h1>
          <p class="mt-1 text-sm text-ink-muted font-light">{{ presenter }}</p>
        </div>

        <!-- ── Focal media ──────────────────────────────────────────────
             Online sessions stream live. On-site sessions are physical events
             that are *recorded* — so they present the VOD recording with chapter
             markers ("Key Moments") rather than a live feed. -->
        <template v-if="!isOnsite">
          <VideoPlayer
            :live="isLive"
            :media-url="mediaUrl" managed :poster="asset(item.cover_url)" :notice="mediaNotice" :elapsed="elapsed" duration="—"
            :viewers="viewers.toLocaleString()"
            :title="item.title"
            :subtitle="presenter"
          />
        </template>

        <template v-else>
          <div class="space-y-5">
            <!-- Recorded-on-site label strip (flat, no live ping) -->
            <div class="flex items-center gap-2.5 rounded-lg border border-gold/30 bg-gold/10 px-4 py-3">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="shrink-0 text-gold-dark"><path d="m23 7-7 5 7 5V7zM1 5h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H1z" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <span class="text-[11px] uppercase tracking-[0.22em] text-gold-dark font-light">{{ t('events.active.recordingSubtitle') }}</span>
            </div>

            <!-- VOD recording of the physical event -->
            <VideoPlayer
              :title="item.title"
              :subtitle="t('events.active.recordingTitle')"
              :media-url="mediaUrl" managed :poster="asset(item.cover_url)" :notice="mediaNotice" duration="—"
              elapsed="00:00"
            />
          </div>
        </template>

        <!-- Stats strip -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="s in (isOnsite ? onsiteStats : stats)" :key="s.label" class="rounded-lg border border-parchment-deep/70 bg-parchment shadow-card px-4 py-3.5 text-center">
            <p class="font-serif text-2xl text-ink leading-none">{{ s.value }}</p>
            <p class="mt-1.5 text-[10px] uppercase tracking-[0.2em] text-ink-muted font-light">{{ s.label }}</p>
          </div>
        </div>
        <p v-if="!isOnsite" class="text-[10px] text-ink-muted">
          {{ tr('Country data:', 'دادهٔ کشورها:') }}
          <a href="https://db-ip.com" target="_blank" rel="noopener noreferrer" class="underline hover:text-gold-dark">IP Geolocation by DB-IP</a>
        </p>

        <!-- Agenda / schedule timeline -->
        <div class="rounded-lg border border-parchment-deep/70 bg-parchment shadow-card p-7">
          <h2 class="font-serif font-light text-lg text-ink mb-5">{{ isOnsite ? t('events.active.scheduleTitle') : t('events.active.agendaTitle') }}</h2>
          <ol class="relative">
            <li v-for="(a, i) in agenda" :key="i" class="relative flex gap-4 pb-5 last:pb-0">
              <!-- rail -->
              <span v-if="i < agenda.length - 1" class="absolute left-[7px] top-4 bottom-0 w-px bg-parchment-deep"></span>
              <!-- dot -->
              <span class="relative z-10 mt-1 shrink-0 w-3.5 h-3.5 rounded-full border-2"
                :class="a.status === 'live' ? 'border-red-500 bg-red-500 animate-pulse-dot'
                  : a.status === 'done' ? 'border-gold bg-gold'
                  : 'border-parchment-deep bg-parchment-light'"></span>
              <div class="flex-1 -mt-0.5">
                <div class="flex items-baseline justify-between gap-3">
                  <span class="text-[11px] tabular-nums tracking-[0.1em] font-light"
                        :class="a.status === 'live' ? 'text-red-600 dark:text-red-400' : 'text-ink-muted'">{{ a.time }}</span>
                  <span v-if="statusLabel(a.status)" class="text-[9px] uppercase tracking-[0.2em] font-light px-2 py-0.5 rounded-full"
                        :class="a.status === 'live' ? 'bg-red-500/10 text-red-600 dark:text-red-400'
                          : a.status === 'done' ? 'text-ink-hint' : 'text-gold-dark border border-gold/40'">{{ statusLabel(a.status) }}</span>
                  <span v-if="a.status !== 'upcoming'" class="text-[11px] tabular-nums text-ink-muted">{{ a.duration }}</span>
                </div>
                <button type="button" :disabled="!room.instructor || !isLive || busy" @click="action(() => eventsApi.liveStep(slug,i))" class="text-sm font-light leading-snug mt-0.5 text-start disabled:cursor-default"
                   :class="a.status === 'upcoming' ? 'text-ink-muted' : 'text-ink'">{{ a.title }}</button>
              </div>
            </li>
          </ol>
        </div>

        <!-- Speakers -->
        <div class="rounded-lg border border-parchment-deep/70 bg-parchment shadow-card p-7">
          <h2 class="font-serif font-light text-lg text-ink mb-5">{{ t('events.active.speakersTitle') }}</h2>
          <div class="grid sm:grid-cols-3 gap-5">
            <component
              :is="sp.profile_slug ? RouterLink : 'div'"
              v-for="sp in speakers"
              :key="sp.name"
              :to="sp.profile_slug ? `/partners/${sp.profile_slug}` : undefined"
              class="speaker-card text-center sm:text-left"
              :class="sp.profile_slug ? 'cursor-pointer hover:border-gold/50 focus-visible:outline-gold' : ''"
            >
              <div class="flex items-center gap-3 sm:block">
                <div class="relative shrink-0 w-12 h-12 rounded-full bg-ink text-parchment-light flex items-center justify-center font-serif text-sm sm:mb-3">
                  {{ initials(sp.name) }}
                  <span v-if="sp.live && !isOnsite" class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-red-500 border-2 border-parchment"></span>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-light leading-snug text-ink">{{ sp.name }}</p>
                  <p class="text-[11px] text-ink-muted font-light">{{ sp.title }}</p>
                </div>
              </div>
              <p class="mt-2 text-[11px] text-ink-hint font-light">{{ sp.org }}</p>
              <div class="mt-2.5 flex items-center gap-2 justify-center sm:justify-start">
                <span class="text-[9px] uppercase tracking-[0.2em] font-light px-2 py-0.5 rounded-full"
                      :class="(sp.live && !isOnsite) ? 'bg-red-500/10 text-red-600 dark:text-red-400' : 'text-gold-dark border border-gold/40'">{{ sp.tag }}</span>
                
              </div>
              <span
                v-if="sp.profile_slug"
                class="speaker-profile-link mt-2.5 inline-flex items-center gap-1.5 text-[10px] uppercase tracking-[0.2em] text-gold-dark font-light border-b border-gold/40 pb-0.5 hover:text-gold hover:border-gold transition-colors"
              >
                {{ t('events.active.viewProfile') }} <span class="dir-arrow" aria-hidden="true"></span>
              </span>
            </component>
          </div>
        </div>

      </div>

      <!-- ================= SIDE COLUMN ================= -->
      <aside class="lg:col-span-4 space-y-6">
        <!-- Live chat / Q&A — online sessions only. On-site (recorded physical)
             events have no live audience interaction, so this is omitted there. -->
        <div v-if="!isOnsite" class="rounded-lg border border-parchment-deep/70 bg-parchment shadow-card flex flex-col h-[560px] overflow-hidden">
          <div class="px-4 pt-4">
            <h2 class="font-serif font-light text-lg text-ink mb-3 px-1">{{ t('events.active.chatTitle') }}</h2>
            <div class="flex p-1 rounded-md bg-parchment-light border border-parchment-deep/60 text-[11px] uppercase tracking-[0.15em]">
              <button @click="panel = 'chat'" :class="['flex-1 py-2 rounded transition-colors', panel === 'chat' ? 'bg-ink text-parchment-light' : 'text-ink-muted hover:text-ink']">{{ t('events.active.chatTab') }}</button>
              <button @click="panel = 'qa'" :class="['flex-1 py-2 rounded transition-colors', panel === 'qa' ? 'bg-ink text-parchment-light' : 'text-ink-muted hover:text-ink']">{{ t('events.active.qaTab') }}</button>
            </div>
          </div>

          <!-- Chat list -->
          <div v-if="panel === 'chat'" class="flex-1 overflow-y-auto px-4 py-4 space-y-3.5">
            <div v-for="(m, i) in chat" :key="i" class="flex gap-2.5" :class="m.mine ? 'flex-row-reverse text-right' : ''">
              <span class="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-light"
                    :class="m.faculty ? 'bg-gold/20 text-gold-dark border border-gold/40' : 'bg-parchment-deep/40 text-ink-soft'">{{ initials(m.user) }}</span>
              <div class="min-w-0">
                <p class="text-[11px] leading-none">
                  <span class="font-light" :class="m.faculty ? 'text-gold-dark' : 'text-ink'">{{ m.user }}</span>
                  <span v-if="m.faculty" class="ms-1.5 text-[8px] uppercase tracking-[0.15em] text-gold-dark border border-gold/40 rounded px-1 py-px">{{ m.role }}</span>
                  <span class="ms-1.5 text-ink-hint">{{ m.time }}</span>
                </p>
                <p class="mt-1 text-sm text-ink-soft font-light leading-snug">{{ m.text }}</p>
              </div>
            </div>
          </div>

          <!-- Q&A list -->
          <div v-else class="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            <div v-for="(q, i) in qa" :key="i" class="rounded-md border border-parchment-deep/60 bg-parchment-light p-3.5 flex gap-3">
              <button type="button" :disabled="busy || !isLive || !room.questions_enabled" :aria-pressed="q.voted" :aria-label="tr('Vote for this question','رأی به این پرسش')" @click="action(() => eventsApi.liveVote(slug,q.id))" class="shrink-0 flex flex-col items-center gap-0.5" :class="q.voted?'text-gold-dark':'text-ink-muted'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 19V5M5 12l7-7 7 7" stroke-linecap="round" stroke-linejoin="round"/></svg>
                <span class="text-[11px] font-light tabular-nums">{{ q.votes }}</span>
              </button>
              <div class="min-w-0">
                <p class="text-sm text-ink-soft font-light leading-snug">{{ q.text }}</p>
                <p class="mt-1.5 text-[10px] uppercase tracking-[0.15em] font-light">
                  <span class="text-ink-hint">{{ q.user }} · {{ q.time }}</span>
                  <button v-if="room.instructor && !q.answered && isLive" type="button" :disabled="busy" class="ms-2 text-gold-dark underline" @click="action(() => eventsApi.liveAnswer(slug,q.id))">{{ tr('Mark answered','علامت پاسخ') }}</button><span v-if="q.answered" class="ms-2 text-gold-dark">{{ tr('✓ answered','✓ پاسخ‌داده‌شده') }}</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Input -->
          <form class="border-t border-parchment-deep/60 p-3 flex items-center gap-2" @submit.prevent="send">
            <input
              v-model="draft" maxlength="1000" :disabled="conversationClosed || busy"
              type="text"
              :placeholder="conversationClosed ? tr('Conversation is paused.','گفت‌وگو فعلاً بسته است.') : panel === 'chat' ? t('events.active.chatPlaceholder') : tr('Ask a question…','سؤال خود را بپرسید…')" :aria-label="panel === 'chat' ? tr('Message','پیام') : tr('Question','پرسش')"
              class="min-w-0 flex-1 bg-parchment-light border border-parchment-deep/70 rounded-md px-3.5 py-2.5 text-sm font-light text-ink placeholder:text-ink-hint focus:outline-none focus:border-gold/60 transition-colors"
            />
            <button type="submit" :disabled="conversationClosed || busy || !draft.trim()" class="shrink-0 w-10 h-10 rounded-md bg-ink text-parchment-light hover:bg-gold-dark transition-colors flex items-center justify-center" :aria-label="t('events.active.send')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M22 2 11 13 M22 2 15 22l-4-9-9-4z" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </form>
        </div>

        <!-- Venue Guide & Event Agenda — on-site (physical) events only.
             Location details, a flat top-down hall map and the day's timings. -->
        <div v-if="item.kind === 'onsite' || item.venue" class="rounded-lg border border-parchment-deep/70 bg-parchment shadow-card p-6">
          <h2 class="font-serif font-light text-lg text-ink mb-4">{{ t('events.active.venueTitle') }}</h2>

          <!-- Location details -->
          <div class="flex items-start gap-3">
            <span class="shrink-0 w-9 h-9 rounded border border-gold/40 flex items-center justify-center text-gold-dark">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M12 21s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="9" r="2.5"/></svg>
            </span>
            <div class="min-w-0">
              <p class="text-sm text-ink font-light leading-snug">{{ item.venue || presenter }}</p>
              <p class="text-[12px] text-ink-muted font-light mt-0.5">{{ new Date(item.starts_at).toLocaleString(locale, { timeZone: item.timezone }) }}</p>
            </div>
          </div>

          <!-- Flat top-down hall map (decorative schematic) -->
          <div v-if="item.kind === 'onsite'" class="mt-5">
            <p class="text-[10px] uppercase tracking-[0.25em] text-gold-dark font-light mb-2">{{ tr('Illustrative seating layout','چیدمان نمایشی سالن') }}</p>
            <div class="rounded-md border border-parchment-deep/60 bg-parchment-light p-3">
              <svg viewBox="0 0 200 120" class="w-full h-auto" role="img" :aria-label="t('events.active.venueMapLabel')">
                <g fill="none" stroke="rgb(var(--c-gold) / 0.55)" stroke-width="1">
                  <rect x="6" y="6" width="188" height="108" rx="3" stroke="rgb(var(--c-parchment-deep))"/>
                  <rect x="16" y="14" width="168" height="22" rx="2" fill="rgb(var(--c-gold) / 0.12)"/>
                  <rect x="16" y="44" width="100" height="62" rx="2"/>
                  <rect x="124" y="44" width="60" height="28" rx="2"/>
                  <rect x="124" y="78" width="60" height="28" rx="2"/>
                </g>
                <g fill="rgb(var(--c-ink-soft))" font-size="7" font-family="inherit" letter-spacing="0.5">
                  <text x="100" y="28" text-anchor="middle" fill="rgb(var(--c-gold-dark))">{{ t('events.active.mapStage') }}</text>
                  <text x="66" y="78" text-anchor="middle">{{ t('events.active.mapSeating') }}</text>
                  <text x="154" y="60" text-anchor="middle">{{ t('events.active.mapHall') }}</text>
                  <text x="154" y="94" text-anchor="middle">{{ t('events.active.mapStations') }}</text>
                </g>
                <g fill="rgb(var(--c-gold-dark))">
                  <circle cx="100" cy="110" r="2.5"/>
                  <text x="100" y="118" text-anchor="middle" font-size="6" fill="rgb(var(--c-ink-muted))">{{ t('events.active.mapEntrance') }}</text>
                </g>
              </svg>
            </div>
          </div>

          <!-- Event agenda / timings -->
          <div class="mt-5">
            <p class="text-[10px] uppercase tracking-[0.25em] text-gold-dark font-light mb-2.5">{{ t('events.active.venueAgendaLabel') }}</p>
            <ul class="space-y-2">
              <li v-for="(s, i) in venueSchedule" :key="i" class="flex items-baseline gap-3">
                <span class="shrink-0 text-[11px] text-gold-dark font-light tabular-nums tracking-[0.1em]">{{ s.time }}</span>
                <span class="text-sm text-ink-soft font-light leading-snug">{{ s.label }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Clinical Documents — shown for both online and on-site events. For
             on-site it sits directly below the Venue Guide; for online it closes
             the sidebar after the live chat/Q&A. Flat editorial download list. -->
        <div class="rounded-lg border border-parchment-deep/70 bg-parchment shadow-card p-6">
          <h2 class="font-serif font-light text-lg text-ink mb-4">{{ t('events.active.docsTitle') }}</h2>
          <ul class="space-y-2.5">
            <li v-for="doc in documents" :key="doc.name">
              <a :href="download(doc.url)" target="_blank" rel="noopener noreferrer" class="group flex min-w-0 max-w-full items-center gap-3 overflow-hidden rounded-md border border-parchment-deep/60 bg-parchment-light px-3.5 py-3 hover:border-gold/50 transition-colors">
                <span class="shrink-0 w-9 h-9 rounded border border-gold/40 flex items-center justify-center text-gold-dark">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path :d="docIcon(doc.type)" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <span class="min-w-0 flex-1">
                  <span class="block max-w-full truncate text-sm text-ink font-light leading-snug group-hover:text-gold-dark transition-colors" :title="doc.name">{{ doc.name }}</span>
                  <span class="block text-[10px] uppercase tracking-[0.15em] text-ink-hint font-light mt-0.5">{{ doc.type }} · {{ doc.size }}</span>
                </span>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" class="shrink-0 text-ink-muted group-hover:text-gold-dark transition-colors"><path d="M12 3v12m0 0 4-4m-4 4-4-4M5 21h14" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </a>
            </li>
          </ul>
          <p class="mt-4 text-[11px] text-ink-hint font-light italic leading-relaxed">{{ t('events.active.docsNote') }}</p>
        </div>
      </aside>
    </div>
  </div>

  <div v-else class="py-32 px-6 text-center"><p role="status" class="mb-6 text-sm text-ink-muted">{{ loading ? tr('Loading event…','در حال دریافت رویداد…') : error }}</p><router-link v-if="!loading" :to="`/events/reserve/online/${slug}`" class="inline-block mx-4 text-sm text-gold-dark underline">{{ tr('Reserve a place','رزرو رویداد') }}</router-link>
    <button class="text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1" @click="router.push('/events')">
      {{ t('events.active.back') }}
    </button>
  </div>
</template>

<style scoped>
/* Dismiss animation for the "you're registered" banner — fades out while
   sliding up and collapsing its height, so the content below glides into place
   rather than snapping. */
.alert-collapse-leave-active {
  transition: opacity 300ms ease, transform 360ms cubic-bezier(0.4, 0, 0.2, 1), max-height 360ms ease;
  overflow: hidden;
  max-height: 120px;
}
.alert-collapse-leave-to {
  opacity: 0;
  transform: translateY(-12px);
  max-height: 0;
}
@media (prefers-reduced-motion: reduce) {
  .alert-collapse-leave-active { transition: opacity 200ms ease; }
  .alert-collapse-leave-to { transform: none; }
}
</style>


