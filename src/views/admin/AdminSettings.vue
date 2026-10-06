<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminToggle from '../../components/admin/AdminToggle.vue'
import { governanceApi } from '../../api/governance.js'

const { t } = useI18n()

const settings = ref({
  siteName: 'Neuro Tech',
  supportEmail: 'neuro.tech.pishro@gmail.com',
  maintenance: false,
  registrations: true,
  autoApproveComments: false,
  premiumCheckout: true,
})

const saved = ref(false)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await governanceApi.settings()
    settings.value = {
      siteName: data.site_name,
      supportEmail: data.support_email,
      maintenance: data.maintenance,
      registrations: data.registrations,
      autoApproveComments: data.auto_approve_comments,
      premiumCheckout: data.premium_checkout,
    }
  } catch (problem) {
    error.value = problem.message
  } finally {
    loading.value = false
  }
}

const save = async () => {
  saving.value = true
  saved.value = false
  error.value = ''
  try {
    await governanceApi.saveSettings({
      site_name: settings.value.siteName,
      support_email: settings.value.supportEmail,
      maintenance: settings.value.maintenance,
      registrations: settings.value.registrations,
      auto_approve_comments: settings.value.autoApproveComments,
      premium_checkout: settings.value.premiumCheckout,
    })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3200)
  } catch (problem) {
    error.value = problem.message
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="max-w-3xl">
    <p class="admin-eyebrow">{{ t('admin.sections.settings.label') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.settings.title') }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.settings.subtitle') }}</p>

    <p v-if="loading" class="mt-8 text-sm text-ink-muted">{{ t('academy.loading') }}</p>
    <form v-else class="mt-8 space-y-6" @submit.prevent="save">
      <p v-if="error" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">{{ error }}</p>
      <div class="admin-card p-7 space-y-5">
        <h3 class="admin-h2">{{ t('admin.settings.identity') }}</h3>
        <div class="grid sm:grid-cols-2 gap-5">
          <div>
            <label class="admin-label">{{ t('admin.settings.fields.siteName') }}</label>
            <input v-model="settings.siteName" type="text" class="admin-input" />
          </div>
          <div>
            <label class="admin-label">{{ t('admin.settings.fields.supportEmail') }}</label>
            <input v-model="settings.supportEmail" type="email" class="admin-input" style="direction: ltr; text-align: start;" />
          </div>
        </div>
      </div>

      <div class="admin-card p-7 space-y-5">
        <h3 class="admin-h2">{{ t('admin.settings.platform') }}</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm text-ink font-normal">{{ t('admin.settings.fields.maintenance') }}</p>
              <p class="text-xs text-ink-muted font-light mt-0.5">{{ t('admin.settings.fields.maintenanceHint') }}</p>
            </div>
            <AdminToggle v-model="settings.maintenance" />
          </div>
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm text-ink font-normal">{{ t('admin.settings.fields.registrations') }}</p>
              <p class="text-xs text-ink-muted font-light mt-0.5">{{ t('admin.settings.fields.registrationsHint') }}</p>
            </div>
            <AdminToggle v-model="settings.registrations" />
          </div>
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm text-ink font-normal">{{ t('admin.settings.fields.autoApprove') }}</p>
              <p class="text-xs text-ink-muted font-light mt-0.5">{{ t('admin.settings.fields.autoApproveHint') }}</p>
            </div>
            <AdminToggle v-model="settings.autoApproveComments" />
          </div>
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm text-ink font-normal">{{ t('admin.settings.fields.premiumCheckout') }}</p>
              <p class="text-xs text-ink-muted font-light mt-0.5">{{ t('admin.settings.fields.premiumCheckoutHint') }}</p>
            </div>
            <AdminToggle v-model="settings.premiumCheckout" />
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button type="submit" :disabled="saving" class="admin-btn admin-btn-primary">{{ t('admin.settings.save') }}</button>
      </div>
      <p v-if="saved" role="status" class="mt-3 text-xs text-ink-muted font-light italic">{{ t('admin.settings.saved') }}</p>
    </form>
  </div>
</template>
