<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { academyApi } from '../../api/academy.js'

const { t } = useI18n()

const queue = ref([])
const decided = ref([])
const error = ref('')
const loadQueue = async () => {
  try {
    queue.value = (await academyApi.pendingComments()).data.map((item) => ({
      ...item,
      _id: item.id,
      name: item.author,
      course: item.course_slug,
      time: new Date(item.created_at).toLocaleDateString(),
    }))
  } catch (problem) {
    error.value = problem.message
  }
}
onMounted(loadQueue)

const decide = async (item, decision) => {
  try {
    await academyApi.moderateComment(item.id, decision)
    queue.value = queue.value.filter((q) => q._id !== item._id)
    decided.value.unshift({ item, decision })
  } catch (problem) {
    error.value = problem.message
  }
}
</script>

<template>
  <div class="max-w-4xl">
    <p class="admin-eyebrow">{{ t('admin.sections.moderation.label') }}</p>
    <h2 class="admin-h1 mt-2">{{ t('admin.moderation.title') }}</h2>
    <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.moderation.subtitle') }}</p>
    <p v-if="error" class="mt-4 text-xs text-red-700" role="alert">{{ error }}</p>

    <div class="mt-8 space-y-5">
      <TransitionGroup name="fade">
        <article v-for="item in queue" :key="item._id" class="admin-card p-6">
          <div class="flex items-baseline justify-between gap-4">
            <span class="text-sm font-medium text-ink">{{ item.name }}</span>
            <span class="text-[11px] uppercase tracking-[0.2em] text-ink-hint font-light shrink-0">{{ item.time }}</span>
          </div>
          <p class="mt-1 text-[11px] uppercase tracking-[0.2em] text-gold-dark font-light">{{ item.course }}</p>
          <p class="mt-3 text-sm text-ink-soft font-light leading-relaxed">{{ item.body }}</p>
          <div class="mt-5 flex gap-3">
            <button @click="decide(item, 'approved')" class="admin-btn admin-btn-primary admin-btn-sm">
              {{ t('admin.moderation.approve') }}
            </button>
            <button @click="decide(item, 'rejected')" class="admin-btn admin-btn-ghost admin-btn-sm">
              {{ t('admin.moderation.reject') }}
            </button>
          </div>
        </article>
      </TransitionGroup>

      <p v-if="!queue.length" class="admin-card p-10 text-sm text-ink-muted font-light italic text-center">
        {{ t('admin.moderation.empty') }}
      </p>
    </div>

    <div v-if="decided.length" class="mt-10">
      <h3 class="admin-label">{{ t('admin.moderation.log') }}</h3>
      <ul class="space-y-2.5 mt-3">
        <li v-for="(d, i) in decided" :key="i" class="flex items-baseline justify-between gap-4 text-sm font-light">
          <span class="text-ink-soft">{{ d.item.name }} — <span class="italic text-ink-muted">{{ d.item.course }}</span></span>
          <span :class="d.decision === 'approved' ? 'admin-badge admin-badge-green' : 'admin-badge admin-badge-muted'">
            {{ d.decision === 'approved' ? t('admin.moderation.approved') : t('admin.moderation.rejected') }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>
