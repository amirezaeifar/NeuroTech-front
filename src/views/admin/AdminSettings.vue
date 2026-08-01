<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { t } = useI18n()

// Core system settings (mock) — the admin-only tier a specialist can never
// reach (enforced by meta.roles on this route).
const settings = ref({
  siteName: 'Neuro Tech',
  supportEmail: 'neuro.tech.pishro@gmail.com',
  maintenance: false,
  registrations: true,
  autoApproveComments: false,
  premiumCheckout: true,
})

const saved = ref(false)
const save = () => {
  saved.value = true
  setTimeout(() => { saved.value = false }, 3200)
}
</script>

<template>
  <div class="max-w-3xl">
    <p class="admin-eyebrow">{{ t('admin.sections.settings.label') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.settings.title') }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.settings.subtitle') }}</p>

    <form class="mt-8 space-y-6" @submit.prevent="save">
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
        <button type="submit" class="admin-btn admin-btn-primary">{{ t('admin.settings.save') }}</button>
        <Transition name="fade">
          <span v-if="saved" class="text-xs text-ink-muted font-light italic">{{ t('admin.settings.saved') }}</span>
        </Transition>
      </div>
    </form>
  </div>
</template>
