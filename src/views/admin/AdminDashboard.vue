<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { academyApi } from '../../api/academy.js'
import { authApi } from '../../api/auth.js'
import { useAuth } from '../../composables/useAuth.js'
import { useCourseAdmin } from '../../composables/useCourseAdmin.js'
import { sectionsForRole } from '../../data/adminSections.js'

const { t } = useI18n()
const { user, role, isAdmin } = useAuth()
const { courses } = useCourseAdmin()

const displayName = computed(() => {
  const id = user.value?.display_name || user.value?.email || user.value?.phone || 'member'
  return id.includes('@') ? id.split('@')[0] : id
})

const pending = ref(0)
const members = ref(null)
onMounted(async () => {
  const [commentsResult, usersResult] = await Promise.allSettled([
    academyApi.pendingComments(),
    isAdmin.value ? authApi.adminUsers() : Promise.resolve(null),
  ])
  if (commentsResult.status === 'fulfilled') {
    pending.value = commentsResult.value.data.length
  }
  if (usersResult.status === 'fulfilled' && usersResult.value) {
    members.value = usersResult.value.data.length
  }
})
const published = computed(() => courses.value.filter((c) => c.published).length)
const premium = computed(() => courses.value.filter((c) => c.tier === 'premium').length)
const documents = computed(() => courses.value.reduce((n, c) => n + c.documents.length, 0))

// Stat tiles. Admin-only ones are filtered out for a specialist.
const stats = computed(() =>
  [
    { key: 'courses', value: courses.value.length, icon: 'book' },
    { key: 'published', value: published.value, icon: 'check' },
    { key: 'pending', value: pending.value, icon: 'chat' },
    { key: 'documents', value: documents.value, icon: 'doc' },
    { key: 'premium', value: premium.value, icon: 'star', adminOnly: true },
    ...(members.value === null
      ? []
      : [{ key: 'members', value: members.value, icon: 'users', adminOnly: true }]),
  ].filter((s) => !s.adminOnly || isAdmin.value),
)

// Quick links = the very sections this role can open (minus the dashboard).
const quickLinks = computed(() => sectionsForRole(role.value).filter((s) => s.path !== ''))

const STAT_ICONS = {
  book: 'M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 0-2 2V4z',
  check: 'M20 6L9 17l-5-5',
  chat: 'M4 5h16v10H9l-4 4V5z',
  doc: 'M7 3h7l5 5v13H7zM14 3v5h5',
  star: 'M12 3l2.6 5.6L20 9.3l-4 4 1 6-5-2.8L7 19.3l1-6-4-4 5.4-.7z',
  users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 21a7 7 0 0 1 14 0',
}
const SECTION_ICONS = {
  book: 'M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 0-2 2V4z',
  chat: 'M4 5h16v10H9l-4 4V5z',
  layers: 'M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5',
  users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 21a7 7 0 0 1 14 0',
  cog: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
}
</script>

<template>
  <div>
    <p class="admin-eyebrow">{{ t('admin.eyebrow') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.dashboard.welcome', { name: displayName }) }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">
      {{ isAdmin ? t('admin.dashboard.subtitleAdmin') : t('admin.dashboard.subtitleSpecialist') }}
    </p>

    <!-- Stat tiles -->
    <div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="s in stats" :key="s.key" class="admin-card admin-card-hover p-5 flex items-center gap-4">
        <span class="admin-stat-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path :d="STAT_ICONS[s.icon]" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="flex flex-col">
          <span class="font-serif font-light text-3xl text-ink leading-none">{{ s.value }}</span>
          <span class="mt-1.5 text-[10.5px] uppercase tracking-[0.18em] text-ink-muted font-light">{{ t('admin.dashboard.stats.' + s.key) }}</span>
        </span>
      </div>
    </div>

    <!-- Quick actions -->
    <h3 class="admin-label mt-10">{{ t('admin.dashboard.quick') }}</h3>
    <div class="mt-3 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <router-link
        v-for="q in quickLinks"
        :key="q.name"
        :to="{ name: q.name }"
        class="admin-card admin-card-hover p-5 flex items-start gap-3.5 group"
      >
        <span class="admin-stat-icon shrink-0">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path :d="SECTION_ICONS[q.icon]" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="flex flex-col">
          <span class="text-sm text-ink font-medium group-hover:text-gold-dark transition-colors">{{ t('admin.sections.' + q.key + '.label') }}</span>
          <span class="mt-1 text-xs text-ink-muted font-light leading-relaxed">{{ t('admin.sections.' + q.key + '.blurb') }}</span>
        </span>
      </router-link>
    </div>

    <!-- Access note -->
    <div class="admin-panel mt-9 p-5 flex items-start gap-3">
      <svg class="text-gold-dark shrink-0 mt-0.5" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 3l7 3v5c0 4.2-2.9 7.6-7 8.8C7.9 18.6 5 15.2 5 11V6l7-3z" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <p class="text-xs text-ink-muted font-light leading-relaxed">
        {{ isAdmin ? t('admin.dashboard.accessAdmin') : t('admin.dashboard.accessSpecialist') }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.admin-stat-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgb(var(--c-gold) / 0.12);
  color: rgb(var(--c-gold-dark));
  flex-shrink: 0;
}
</style>
