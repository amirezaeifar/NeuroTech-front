<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { governanceApi } from '../../api/governance.js'

const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const status = ref('pending')
const items = ref([])
const loading = ref(false)
const listError = ref('')
const actionErrors = ref({})
const notes = ref({})
const busyId = ref(null)

const load = async () => {
  loading.value = true
  listError.value = ''
  try {
    items.value = (await governanceApi.approvals(status.value)).data
  } catch (problem) {
    listError.value = problem.message
  } finally {
    loading.value = false
  }
}

const review = async (item, decision) => {
  busyId.value = item.id
  actionErrors.value[item.id] = ''
  try {
    await governanceApi.review(item.id, decision, notes.value[item.id] || '')
    await load()
  } catch (problem) {
    actionErrors.value[item.id] = problem.message
  } finally {
    busyId.value = null
  }
}

const changeSummary = (change) => {
  const fields = Object.keys(change.payload || {}).filter((key) => !key.startsWith('_'))
  return fields.length ? fields.join('، ') : tr('Status change', 'تغییر وضعیت')
}

const setStatus = (value) => {
  status.value = value
  load()
}

onMounted(load)
</script>

<template>
  <div class="max-w-5xl">
    <p class="admin-eyebrow">{{ tr('Principal review', 'بررسی مدیر اصلی') }}</p>
    <h2 class="admin-h1 mt-2">{{ tr('Approval registry', 'سامانه تأیید درخواست‌ها') }}</h2>
    <p class="mt-2 max-w-2xl text-sm text-ink-muted">{{ tr('Related edits are grouped into one review record so the full history stays visible.', 'تغییرات مرتبط در یک پرونده تجمیع می‌شوند تا تاریخچه کامل درخواست قابل بررسی باشد.') }}</p>

    <div class="mt-7 flex flex-wrap gap-2">
      <button v-for="tab in ['pending', 'approved', 'rejected']" :key="tab" type="button" class="admin-btn admin-btn-sm" :class="status === tab ? 'admin-btn-primary' : 'admin-btn-ghost'" @click="setStatus(tab)">
        {{ tr(tab[0].toUpperCase() + tab.slice(1), { pending: 'در انتظار', approved: 'تأییدشده', rejected: 'ردشده' }[tab]) }}
      </button>
    </div>

    <p v-if="listError" class="mt-5 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">{{ listError }}</p>
    <p v-if="loading" class="py-10 text-center text-sm text-ink-muted">{{ tr('Loading…', 'در حال دریافت…') }}</p>
    <div v-else-if="status === 'pending'" class="approval-ledger mt-7 space-y-5">
      <article v-for="item in items" :key="item.id" class="admin-card relative p-6 md:p-7">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <span class="admin-badge admin-badge-gold">{{ item.resource_type }}</span>
            <h3 class="admin-h2 mt-3 break-all">{{ item.resource_key }}</h3>
            <p class="mt-1 text-xs text-ink-muted">{{ item.requester?.name || '—' }} · {{ item.requester?.role || '—' }} · {{ item.change_count }} {{ tr('changes', 'تغییر') }}</p>
          </div>
          <time class="text-xs text-ink-muted">{{ new Date(item.updated_at).toLocaleString() }}</time>
        </div>

        <ol class="mt-6 space-y-3 border-s border-gold/30 ps-5">
          <li v-for="(change, index) in item.changes" :key="index" class="relative text-sm">
            <span class="absolute -start-[25px] top-1 h-2 w-2 rounded-full bg-gold"></span>
            <strong class="font-medium text-ink">{{ change.action }}</strong>
            <span class="block mt-1 text-xs text-ink-muted">{{ tr('Requested by', 'درخواست‌دهنده') }}: {{ change.requester_name || change.requested_by }} · {{ new Date(change.requested_at).toLocaleString() }}</span>
            <span class="block mt-1 text-xs text-ink-muted">{{ changeSummary(change) }}</span>
            <pre v-if="Object.keys(change.payload || {}).filter(key => !key.startsWith('_')).length" class="mt-2 max-h-48 overflow-auto rounded-lg bg-parchment-light p-3 text-xs whitespace-pre-wrap break-words" dir="ltr">{{ JSON.stringify(Object.fromEntries(Object.entries(change.payload).filter(([key]) => !key.startsWith('_'))), null, 2) }}</pre>
          </li>
        </ol>

        <div class="mt-6 border-t border-parchment-deep/60 pt-5">
          <label class="admin-label">{{ tr('Decision note', 'یادداشت تصمیم') }}</label>
          <textarea v-model="notes[item.id]" rows="2" class="admin-textarea" :placeholder="tr('Optional explanation…', 'توضیح اختیاری…')"></textarea>
          <p v-if="actionErrors[item.id]" class="mt-2 text-xs text-red-700" role="alert">{{ actionErrors[item.id] }}</p>
          <div class="mt-3 flex gap-2">
            <button type="button" class="admin-btn admin-btn-primary" :disabled="busyId === item.id" @click="review(item, 'approved')">{{ tr('Approve & apply', 'تأیید و اعمال') }}</button>
            <button type="button" class="admin-btn admin-btn-danger" :disabled="busyId === item.id" @click="review(item, 'rejected')">{{ tr('Reject', 'رد درخواست') }}</button>
          </div>
        </div>
      </article>
    </div>
    <div v-else class="admin-card admin-scroll mt-7">
      <table class="admin-table min-w-[760px] w-full">
        <thead><tr>
          <th>{{ tr('Resource', 'مورد') }}</th>
          <th>{{ tr('Requested by', 'درخواست‌دهنده') }}</th>
          <th>{{ tr('Changes', 'تغییرات') }}</th>
          <th>{{ tr('Reviewed by', 'بررسی‌کننده') }}</th>
          <th>{{ tr('Reviewed at', 'زمان بررسی') }}</th>
          <th>{{ tr('Decision', 'نتیجه') }}</th>
        </tr></thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td><strong class="block text-ink">{{ item.resource_type }}</strong><span class="block max-w-40 truncate text-xs text-ink-muted" :title="item.resource_key">{{ item.resource_key }}</span></td>
            <td>{{ item.requester?.name || '—' }}</td>
            <td>
              <details class="max-w-72"><summary class="cursor-pointer text-gold-dark">{{ item.change_count }} {{ tr('changes', 'تغییر') }}</summary>
                <ol class="mt-2 space-y-2 text-xs"><li v-for="(change, index) in item.changes" :key="index"><strong>{{ change.action }}</strong> · {{ change.requester_name || change.requested_by }}<br>{{ changeSummary(change) }}<pre class="mt-1 max-h-36 overflow-auto whitespace-pre-wrap break-words" dir="ltr">{{ JSON.stringify(Object.fromEntries(Object.entries(change.payload || {}).filter(([key]) => !key.startsWith('_'))), null, 2) }}</pre></li></ol>
              </details>
            </td>
            <td>{{ item.reviewer?.name || '—' }}</td>
            <td class="whitespace-nowrap">{{ item.reviewed_at ? new Date(item.reviewed_at).toLocaleString() : '—' }}</td>
            <td><span :class="['admin-badge', status === 'approved' ? 'admin-badge-green' : 'admin-badge-muted']">{{ status === 'approved' ? tr('Approved','تأییدشده') : tr('Rejected','ردشده') }}</span><p v-if="item.decision_note" class="mt-2 text-xs text-ink-muted">{{ item.decision_note }}</p></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!loading && !items.length" class="py-12 text-center text-sm italic text-ink-muted">{{ tr('No requests in this register.', 'در این فهرست درخواستی وجود ندارد.') }}</p>
  </div>
</template>

<style scoped>
.approval-ledger { position: relative; }
.approval-ledger::before { content: ''; position: absolute; inset-block: 1rem; inset-inline-start: -.7rem; width: 1px; background: color-mix(in srgb, #b68b3a 30%, transparent); }
</style>
