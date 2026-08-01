<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth, ROLES } from '../../composables/useAuth.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { t } = useI18n()
const { user, role, setRole } = useAuth()

// Mock member directory — admin-only (core user management, spec §7). Names are
// intentionally in-file mock data, like the rest of the panel: no backend.
const members = ref([
  { id: 1, name: 'Dr. Leila Farhadi', email: 'l.farhadi@neurotech.dev', role: ROLES.SPECIALIST, active: true, joined: '2025-11-03' },
  { id: 2, name: 'Prof. Ali Shalash', email: 'a.shalash@neurotech.dev', role: ROLES.SPECIALIST, active: true, joined: '2025-08-19' },
  { id: 3, name: 'Sina Rahimi', email: 'sina.r@gmail.com', role: ROLES.USER, active: true, joined: '2026-01-27' },
  { id: 4, name: 'Maryam Kord', email: 'm.kord@outlook.com', role: ROLES.USER, active: false, joined: '2026-02-14' },
  { id: 5, name: 'Admin Principal', email: 'root@neurotech.dev', role: ROLES.ADMIN, active: true, joined: '2025-06-01' },
  { id: 6, name: 'Dr. Kaveh Rostami', email: 'k.rostami@neurotech.dev', role: ROLES.SPECIALIST, active: true, joined: '2025-12-22' },
])

const query = ref('')
const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return members.value
  return members.value.filter(
    (m) => m.name.toLowerCase().includes(q) || m.email.toLowerCase().includes(q),
  )
})

const roleOptions = Object.values(ROLES)
const badgeFor = (r) =>
  r === ROLES.ADMIN ? 'admin-badge-gold' : r === ROLES.SPECIALIST ? 'admin-badge-green' : 'admin-badge-muted'
</script>

<template>
  <div class="max-w-5xl">
    <p class="admin-eyebrow">{{ t('admin.sections.users.label') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.users.title') }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.users.subtitle') }}</p>

    <!-- Demo role switcher — flips YOUR active session role so the RBAC guards
         and sidebar visibility can be exercised live. Switching away from
         `admin` immediately narrows your own access. -->
    <div class="admin-panel mt-7 p-5">
      <h3 class="admin-label">{{ t('admin.users.demoTitle') }}</h3>
      <p class="text-xs text-ink-muted font-light leading-relaxed mb-4">{{ t('admin.users.demoHint') }}</p>
      <div class="flex flex-wrap gap-2.5">
        <button
          v-for="r in roleOptions"
          :key="r"
          type="button"
          @click="setRole(r)"
          :class="['admin-btn admin-btn-sm', role === r ? 'admin-btn-primary' : 'admin-btn-ghost']"
        >{{ t('admin.roles.' + r) }}</button>
      </div>
      <p class="mt-3 text-[11px] text-ink-hint font-light italic">
        {{ t('admin.users.demoActive', { identity: user?.identity || '' }) }}
      </p>
    </div>

    <!-- Directory -->
    <div class="admin-card mt-7 p-6 md:p-7">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h3 class="admin-h2">{{ t('admin.users.directory') }}</h3>
        <input
          v-model="query"
          type="search"
          :placeholder="t('admin.users.search')"
          class="admin-input sm:max-w-[240px]"
        />
      </div>

      <div class="admin-scroll">
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
            <tr v-for="m in filtered" :key="m.id">
              <td>
                <span class="block text-ink font-normal">{{ m.name }}</span>
                <span class="block text-xs text-ink-muted" style="direction: ltr; text-align: start;">{{ m.email }}</span>
              </td>
              <td>
                <select v-model="m.role" class="admin-select !w-auto !py-1.5 !px-2.5 text-xs">
                  <option v-for="r in roleOptions" :key="r" :value="r">{{ t('admin.roles.' + r) }}</option>
                </select>
              </td>
              <td class="whitespace-nowrap text-ink-muted">{{ m.joined }}</td>
              <td><AdminToggle v-model="m.active" /></td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="!filtered.length" class="py-8 text-center text-sm text-ink-muted font-light italic">
        {{ t('admin.users.empty') }}
      </p>
    </div>
  </div>
</template>
