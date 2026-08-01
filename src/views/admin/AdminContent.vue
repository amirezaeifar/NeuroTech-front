<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Dynamic site-content editor (mock form, no backend) — carried over from the
// original teacher dashboard.
const sections = [
  { key: 'announcement', label: 'admin.content.sections.announcement' },
  { key: 'course', label: 'admin.content.sections.course' },
  { key: 'event', label: 'admin.content.sections.event' },
]
const activeSection = ref('announcement')
const form = ref({ title: '', summary: '', body: '', date: '', tier: 'free' })
const savedNotice = ref(false)
const saveDraft = () => {
  savedNotice.value = true
  setTimeout(() => { savedNotice.value = false }, 3200)
}
const switchSection = (key) => {
  activeSection.value = key
  form.value = { title: '', summary: '', body: '', date: '', tier: 'free' }
  savedNotice.value = false
}
</script>

<template>
  <div class="max-w-3xl">
    <p class="admin-eyebrow">{{ t('admin.sections.content.label') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.content.title') }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.content.subtitle') }}</p>

    <div class="mt-7 flex flex-wrap gap-2.5">
      <button
        v-for="s in sections"
        :key="s.key"
        @click="switchSection(s.key)"
        :class="['admin-btn admin-btn-sm', activeSection === s.key ? 'admin-btn-primary' : 'admin-btn-ghost']"
      >{{ t(s.label) }}</button>
    </div>

    <form class="admin-card p-7 md:p-8 mt-6 space-y-5" @submit.prevent="saveDraft">
      <div>
        <label class="admin-label">{{ t('admin.content.fields.title') }}</label>
        <input v-model="form.title" type="text" class="admin-input" />
      </div>
      <div>
        <label class="admin-label">{{ t('admin.content.fields.summary') }}</label>
        <input v-model="form.summary" type="text" class="admin-input" />
      </div>
      <div>
        <label class="admin-label">{{ t('admin.content.fields.body') }}</label>
        <textarea v-model="form.body" rows="4" class="admin-textarea"></textarea>
      </div>
      <div class="grid sm:grid-cols-2 gap-5">
        <div>
          <label class="admin-label">{{ t('admin.content.fields.date') }}</label>
          <input v-model="form.date" type="text" class="admin-input" />
        </div>
        <div>
          <label class="admin-label">{{ t('admin.content.fields.tier') }}</label>
          <select v-model="form.tier" class="admin-select">
            <option value="free">{{ t('academy.filters.free') }}</option>
            <option value="premium">{{ t('academy.filters.premium') }}</option>
          </select>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3 pt-1">
        <button type="submit" class="admin-btn admin-btn-primary">{{ t('admin.content.fields.save') }}</button>
        <button type="button" class="admin-btn admin-btn-ghost">{{ t('admin.content.fields.publish') }}</button>
        <Transition name="fade">
          <span v-if="savedNotice" class="text-xs text-ink-muted font-light italic">{{ t('admin.content.saved') }}</span>
        </Transition>
      </div>
    </form>
  </div>
</template>
