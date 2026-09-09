<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { authApi } from '../../api/auth.js'
import { ROLES } from '../../composables/useAuth.js'

const { t } = useI18n()
const members = ref([])
const query = ref('')
const loading = ref(false)
const error = ref('')
const inviteEmail = ref('')
const inviteRole = ref(ROLES.SPECIALIST)
const invited = ref(false)

const loadUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    members.value = (await authApi.adminUsers()).data
  } catch (problem) {
    error.value = problem.message
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

const sendInvitation = async () => {
  error.value = ''
  invited.value = false
  try {
    await authApi.invite({ email: inviteEmail.value, role: inviteRole.value })
    inviteEmail.value = ''
    invited.value = true
  } catch (problem) {
    error.value = problem.message
  }
}

const badgeFor = (role) =>
  role === ROLES.ADMIN
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
    <p v-if="error" class="mt-4 text-xs text-red-700" role="alert">{{ error }}</p>

    <form class="admin-card mt-7 p-6 grid gap-4 sm:grid-cols-[1fr,180px,auto] sm:items-end" @submit.prevent="sendInvitation">
      <div>
        <label class="admin-label">{{ t('admin.users.inviteEmail') }}</label>
        <input v-model="inviteEmail" type="email" required class="admin-input" dir="ltr" />
      </div>
      <div>
        <label class="admin-label">{{ t('admin.users.inviteRole') }}</label>
        <select v-model="inviteRole" class="admin-select">
          <option :value="ROLES.SPECIALIST">{{ t('admin.roles.specialist') }}</option>
          <option :value="ROLES.ADMIN">{{ t('admin.roles.admin') }}</option>
        </select>
      </div>
      <button type="submit" class="admin-btn admin-btn-primary">{{ t('admin.users.sendInvite') }}</button>
      <p v-if="invited" class="sm:col-span-3 text-xs text-ink-muted" role="status">
        {{ t('admin.users.invited') }}
      </p>
    </form>

    <div class="admin-card mt-7 p-6 md:p-7">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h3 class="admin-h2">{{ t('admin.users.directory') }}</h3>
        <input v-model="query" type="search" :placeholder="t('admin.users.search')" class="admin-input sm:max-w-[240px]" />
      </div>

      <p v-if="loading" class="py-6 text-center text-sm text-ink-muted">{{ t('academy.loading') }}</p>
      <div v-else class="admin-scroll">
        <table class="admin-table min-w-[640px]">
          <thead>
            <tr>
              <th>{{ t('admin.users.cols.member') }}</th>
              <th>{{ t('admin.users.cols.role') }}</th>
              <th>{{ t('admin.users.cols.joined') }}</th>
              <th>{{ t('admin.users.cols.active') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in filtered" :key="member.id">
              <td>
                <span class="block text-ink font-normal">{{ member.display_name }}</span>
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
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="!loading && !filtered.length" class="py-8 text-center text-sm text-ink-muted font-light italic">
        {{ t('admin.users.empty') }}
      </p>
    </div>
  </div>
</template>
