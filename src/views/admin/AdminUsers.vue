<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { authApi } from '../../api/auth.js'
import { ROLES, useAuth } from '../../composables/useAuth.js'

const { t, locale } = useI18n()
const { role } = useAuth()
const isPrincipal = computed(() => role.value === ROLES.SUPER_ADMIN)
const members = ref([])
const query = ref('')
const loading = ref(false)
const listError = ref('')
const formError = ref('')
const inviteEmail = ref('')
const inviteRole = ref(ROLES.SPECIALIST)
const selectedUserId = ref(null)
const inviteOutcome = ref('')
const inviting = ref(false)
const detail = ref(null)
const detailName = ref('')
const detailStatus = ref('active')
const detailProfile = ref(null)
const detailError = ref('')
const savingDetail = ref(false)

const loadUsers = async () => {
  loading.value = true
  listError.value = ''
  try {
    members.value = (await authApi.adminUsers()).data
  } catch (problem) {
    listError.value = problem.message
  } finally {
    loading.value = false
  }
}
onMounted(loadUsers)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return members.value
  return members.value.filter((member) =>
    [member.display_name, member.email, member.phone]
      .filter(Boolean)
      .some((value) => value.toLowerCase().includes(q)),
  )
})

const selectMember = (member) => {
  if (selectedUserId.value === member.id) { clearSelection(); return }
  selectedUserId.value = member.id
  inviteEmail.value = member.email || member.phone || member.display_name
  inviteRole.value = member.role
  formError.value = ''
  inviteOutcome.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const openDetail = (member) => {
  detail.value = member
  detailName.value = member.display_name
  detailStatus.value = member.status
  detailProfile.value = member.profile ? { ...member.profile } : null
  detailError.value = ''
}
const saveDetail = async () => {
  savingDetail.value = true
  detailError.value = ''
  try {
    await authApi.updateUser(detail.value.id, { display_name: detailName.value, status: detailStatus.value, ...(detailProfile.value ? { profile: detailProfile.value } : {}) })
    detail.value = null
    await loadUsers()
  } catch (problem) { detailError.value = problem.message }
  finally { savingDetail.value = false }
}

const clearSelection = () => {
  selectedUserId.value = null
  inviteEmail.value = ''
  inviteRole.value = ROLES.SPECIALIST
  inviteOutcome.value = ''
  formError.value = ''
}

const submitAccess = async () => {
  if (inviting.value) return
  formError.value = ''
  inviteOutcome.value = ''
  inviting.value = true
  try {
    const identifier = inviteEmail.value.trim().toLowerCase()
    const matches = selectedUserId.value ? members.value.filter((member) => member.id === selectedUserId.value) : members.value.filter((member) =>
      [member.display_name, member.email, member.phone].some((value) => value?.toLowerCase() === identifier),
    )
    if (matches.length > 1) throw new Error(t('admin.users.ambiguousIdentifier'))
    const match = matches[0]
    if (match) {
      await authApi.updateRole(match.id, inviteRole.value)
      inviteOutcome.value = 'role_updated'
    } else {
      if (!identifier.includes('@')) throw new Error(t('admin.users.existingIdentifier'))
      const response = await authApi.invite({ email: inviteEmail.value, role: inviteRole.value })
      inviteOutcome.value = response.data.outcome
    }
    await loadUsers()
    if (!selectedUserId.value) inviteEmail.value = ''
  } catch (problem) {
    formError.value = problem.message
  } finally {
    inviting.value = false
  }
}

const badgeFor = (role) =>
  [ROLES.ADMIN, ROLES.SUPER_ADMIN].includes(role)
    ? 'admin-badge-gold'
    : role === ROLES.SPECIALIST
      ? 'admin-badge-green'
      : 'admin-badge-muted'
</script>

<template>
  <div class="max-w-5xl">
    <p class="admin-eyebrow">{{ t('admin.sections.users.label') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.users.title') }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.users.subtitle') }}</p>

    <form v-if="isPrincipal" class="admin-card mt-7 p-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_200px_auto] md:items-end" @submit.prevent="submitAccess">
      <div class="min-w-0">
        <label class="admin-label">{{ t('admin.users.inviteEmail') }}</label>
        <input v-model="inviteEmail" type="text" required class="admin-input w-full" :dir="selectedUserId ? 'auto' : 'ltr'" :readonly="Boolean(selectedUserId)" />
      </div>
      <div class="min-w-0">
        <label class="admin-label">{{ t('admin.users.inviteRole') }}</label>
        <select v-model="inviteRole" class="admin-select w-full">
          <option :value="ROLES.SPECIALIST">{{ t('admin.roles.specialist') }}</option>
          <option :value="ROLES.CONTENT_MANAGER">{{ t('admin.roles.content_manager') }}</option>
          <option :value="ROLES.ADMIN">{{ t('admin.roles.admin') }}</option>
          <option :value="ROLES.SUPER_ADMIN">{{ t('admin.roles.super_admin') }}</option>
          <option :value="ROLES.USER">{{ t('admin.roles.user') }}</option>
        </select>
      </div>
      <button type="submit" :disabled="inviting" class="admin-btn admin-btn-primary h-[42px] whitespace-nowrap">
        {{ selectedUserId ? t('admin.users.changeRole') : t('admin.users.sendInvite') }}
      </button>
      <p v-if="formError" class="sm:col-span-3 rounded-lg bg-red-50 px-4 py-3 text-xs text-red-700" role="alert">{{ formError }}</p>
      <p v-if="inviteOutcome" class="sm:col-span-3 text-xs text-ink-muted" role="status">
        {{ t('admin.users.outcomes.' + inviteOutcome) }}
      </p>
    </form>

    <div class="admin-card mt-7 p-6 md:p-7">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h3 class="admin-h2">{{ t('admin.users.directory') }}</h3>
        <input v-model="query" type="search" :placeholder="t('admin.users.search')" class="admin-input sm:max-w-[240px]" />
      </div>
      <p v-if="listError" class="mb-4 rounded-lg bg-red-50 px-4 py-3 text-xs text-red-700" role="alert">{{ listError }}</p>

      <p v-if="loading" class="py-6 text-center text-sm text-ink-muted">{{ t('academy.loading') }}</p>
      <div v-else class="admin-scroll">
        <table class="admin-table min-w-[640px]">
          <thead>
            <tr>
              <th>{{ t('admin.users.cols.member') }}</th>
              <th>{{ t('admin.users.cols.role') }}</th>
              <th>{{ t('admin.users.cols.joined') }}</th>
              <th>{{ t('admin.users.cols.active') }}</th>
              <th>{{ t('admin.users.cols.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in filtered" :key="member.id">
      <td>
                <button type="button" class="block text-ink font-normal hover:text-gold-dark text-start" @click="isPrincipal ? selectMember(member) : openDetail(member)">{{ member.display_name }}</button>
                <span class="block text-xs text-ink-muted" dir="ltr">{{ member.email || member.phone || '—' }}</span>
              </td>
              <td>
                <span :class="['admin-badge', badgeFor(member.role)]">{{ t('admin.roles.' + member.role) }}</span>
              </td>
              <td class="whitespace-nowrap text-ink-muted">{{ new Date(member.created_at).toLocaleDateString() }}</td>
              <td>
                <span :class="['admin-badge', member.status === 'active' ? 'admin-badge-green' : 'admin-badge-muted']">
                  {{ member.status === 'active' ? t('admin.users.active') : t('admin.users.inactive') }}
                </span>
              </td>
              <td><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="openDetail(member)">{{ t('admin.users.details') }}</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="!loading && !filtered.length" class="py-8 text-center text-sm text-ink-muted font-light italic">
        {{ t('admin.users.empty') }}
      </p>
    </div>
    <div v-if="detail" class="fixed inset-0 z-[100] bg-ink/60 grid place-items-center p-4" @click.self="detail = null">
      <form class="admin-card w-full max-w-xl p-6 space-y-4" role="dialog" aria-modal="true" :aria-label="t('admin.users.details')" @submit.prevent="saveDetail">
        <div class="flex justify-between items-center"><h3 class="admin-h2">{{ t('admin.users.details') }}</h3><button type="button" class="admin-btn admin-btn-ghost" @click="detail = null">×</button></div>
        <label class="block"><span class="admin-label">{{ t('admin.users.cols.member') }}</span><input v-model="detailName" class="admin-input w-full" required minlength="2" /></label>
        <div class="grid sm:grid-cols-2 gap-3 text-sm"><p><b>Email:</b> {{ detail.email || '—' }}</p><p><b>Phone:</b> {{ detail.phone || '—' }}</p><p><b>{{ t('admin.users.cols.role') }}:</b> {{ t('admin.roles.' + detail.role) }}</p><p><b>{{ t('admin.users.cols.joined') }}:</b> {{ new Date(detail.created_at).toLocaleString() }}</p><p><b>{{ t('admin.users.activatedAt') }}:</b> {{ detail.activated_at ? new Date(detail.activated_at).toLocaleString() : '—' }}</p><p><b>{{ t('admin.users.lastActiveAt') }}:</b> {{ detail.last_active_at ? new Date(detail.last_active_at).toLocaleString() : '—' }}</p></div>
        <div v-if="detailProfile" class="grid sm:grid-cols-2 gap-3"><label v-for="(label, key) in { full_name: ['Full name','نام کامل'], email: ['Email','ایمیل'], phone: ['Phone','تلفن'], national_id: ['National ID','کد ملی'], address: ['Address','آدرس'], city: ['City','شهر'], postal_code: ['Postal code','کد پستی'] }" :key="key"><span class="admin-label">{{ label[locale === 'fa' ? 1 : 0] }}</span><input v-model="detailProfile[key]" class="admin-input w-full" /></label></div>
        <label class="block"><span class="admin-label">{{ t('admin.users.cols.active') }}</span><select v-model="detailStatus" class="admin-select w-full"><option value="active">{{ t('admin.users.active') }}</option><option value="suspended">{{ t('admin.users.inactive') }}</option></select></label>
        <p v-if="detailError" class="text-red-700 text-sm" role="alert">{{ detailError }}</p>
        <button class="admin-btn admin-btn-primary" :disabled="savingDetail">{{ t('admin.users.save') }}</button>
      </form>
    </div>
  </div>
</template>
