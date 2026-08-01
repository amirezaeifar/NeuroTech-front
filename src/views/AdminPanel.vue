<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import GoldRule from '../components/GoldRule.vue'
import { useReveal } from '../composables/useReveal.js'

const { t, tm } = useI18n()

const tabs = [
  { key: 'moderation', label: 'admin.nav.moderation' },
  { key: 'content', label: 'admin.nav.content' },
]
const activeTab = ref('moderation')

// --- Moderation queue (mock, in-memory only) ---
const initialQueue = computed(() => tm('admin.moderation.queue'))
const queue = ref([])
const decided = ref([]) // { item, decision: 'approved' | 'rejected' }
let seeded = false
const ensureSeeded = () => {
  if (!seeded && initialQueue.value?.length) {
    queue.value = initialQueue.value.map((q, i) => ({ ...q, _id: i }))
    seeded = true
  }
}
ensureSeeded()

const decide = (item, decision) => {
  queue.value = queue.value.filter((q) => q._id !== item._id)
  decided.value.unshift({ item, decision })
}

// --- Content management (mock form, no backend) ---
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

useReveal()
</script>

<template>
  <div>
    <section class="bg-ink py-20 md:py-28">
      <div class="max-w-5xl mx-auto px-8 text-center">
        <p class="text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light mb-6">
          {{ t('admin.hero.eyebrow') }}
        </p>
        <h1 class="font-serif font-light text-parchment-light text-5xl md:text-6xl tracking-wide">
          {{ t('admin.hero.title') }}
        </h1>
        <div class="mx-auto mt-10 h-px w-24 bg-gold"></div>
      </div>
    </section>

    <section class="py-16 md:py-24 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8">
        <p class="reveal max-w-2xl mx-auto text-center font-serif italic font-light text-2xl text-ink-soft leading-relaxed">
          {{ t('admin.intro') }}
        </p>

        <!-- Section tabs -->
        <div class="mt-14 flex flex-wrap justify-center gap-x-10 gap-y-3">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'relative text-[11px] uppercase tracking-[0.25em] font-light pb-1 transition-colors',
              activeTab === tab.key ? 'text-ink' : 'text-ink-muted hover:text-ink'
            ]"
          >
            {{ t(tab.label) }}
            <span
              class="absolute left-0 right-0 -bottom-px h-px bg-gold transition-transform duration-200"
              :class="activeTab === tab.key ? 'scale-x-100' : 'scale-x-0'"
            ></span>
          </button>
        </div>

        <!-- Moderation -->
        <div v-if="activeTab === 'moderation'" class="mt-14 max-w-3xl mx-auto">
          <h2 class="font-serif font-light text-2xl text-ink">{{ t('admin.moderation.title') }}</h2>
          <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed">{{ t('admin.moderation.subtitle') }}</p>

          <div class="mt-8 space-y-6">
            <TransitionGroup name="fade">
              <LuxeCard v-for="item in queue" :key="item._id" class="reveal">
                <div class="flex items-baseline justify-between gap-4">
                  <span class="text-sm font-medium text-ink">{{ item.name }}</span>
                  <span class="text-[11px] uppercase tracking-[0.2em] text-ink-hint font-light shrink-0">{{ item.time }}</span>
                </div>
                <p class="mt-1 text-[11px] uppercase tracking-[0.2em] text-gold-dark font-light">{{ item.course }}</p>
                <p class="mt-3 text-sm text-ink-soft font-light leading-relaxed">{{ item.body }}</p>
                <div class="mt-5 flex gap-4">
                  <button
                    @click="decide(item, 'approved')"
                    class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1"
                  >
                    {{ t('admin.moderation.approve') }} <span aria-hidden="true">✓</span>
                  </button>
                  <button
                    @click="decide(item, 'rejected')"
                    class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink-muted hover:text-ink transition-colors border-b border-parchment-deep pb-1"
                  >
                    {{ t('admin.moderation.reject') }} <span aria-hidden="true">✕</span>
                  </button>
                </div>
              </LuxeCard>
            </TransitionGroup>

            <p v-if="!queue.length" class="reveal text-sm text-ink-muted font-light italic text-center py-10">
              {{ t('admin.moderation.empty') }}
            </p>
          </div>

          <div v-if="decided.length" class="mt-12">
            <GoldRule />
            <ul class="space-y-3">
              <li v-for="(d, i) in decided" :key="i" class="flex items-baseline justify-between gap-4 text-sm font-light">
                <span class="text-ink-soft">{{ d.item.name }} — <span class="italic text-ink-muted">{{ d.item.course }}</span></span>
                <span :class="d.decision === 'approved' ? 'text-gold-dark' : 'text-ink-hint'">
                  {{ d.decision === 'approved' ? t('admin.moderation.approved') : t('admin.moderation.rejected') }}
                </span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Content management -->
        <div v-else class="mt-14 max-w-2xl mx-auto">
          <h2 class="font-serif font-light text-2xl text-ink">{{ t('admin.content.title') }}</h2>
          <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed">{{ t('admin.content.subtitle') }}</p>

          <div class="mt-8 flex flex-wrap gap-3">
            <button
              v-for="s in sections"
              :key="s.key"
              @click="switchSection(s.key)"
              :class="[
                'text-[11px] uppercase tracking-[0.2em] font-light px-4 py-2 border transition-colors',
                activeSection === s.key ? 'text-gold border-gold/50' : 'text-ink-muted border-parchment-deep hover:text-ink'
              ]"
            >
              {{ t(s.label) }}
            </button>
          </div>

          <form class="mt-10 space-y-5" @submit.prevent="saveDraft">
            <div>
              <label class="block text-[11px] uppercase tracking-[0.2em] text-ink-muted font-light mb-2">{{ t('admin.content.fields.title') }}</label>
              <input v-model="form.title" type="text" class="w-full bg-parchment border border-parchment-deep px-5 py-3 text-sm font-light text-ink focus:outline-none focus:border-gold/60 transition-colors" />
            </div>
            <div>
              <label class="block text-[11px] uppercase tracking-[0.2em] text-ink-muted font-light mb-2">{{ t('admin.content.fields.summary') }}</label>
              <input v-model="form.summary" type="text" class="w-full bg-parchment border border-parchment-deep px-5 py-3 text-sm font-light text-ink focus:outline-none focus:border-gold/60 transition-colors" />
            </div>
            <div>
              <label class="block text-[11px] uppercase tracking-[0.2em] text-ink-muted font-light mb-2">{{ t('admin.content.fields.body') }}</label>
              <textarea v-model="form.body" rows="4" class="w-full bg-parchment border border-parchment-deep px-5 py-3 text-sm font-light text-ink focus:outline-none focus:border-gold/60 transition-colors resize-none"></textarea>
            </div>
            <div class="grid sm:grid-cols-2 gap-5">
              <div>
                <label class="block text-[11px] uppercase tracking-[0.2em] text-ink-muted font-light mb-2">{{ t('admin.content.fields.date') }}</label>
                <input v-model="form.date" type="text" class="w-full bg-parchment border border-parchment-deep px-5 py-3 text-sm font-light text-ink focus:outline-none focus:border-gold/60 transition-colors" />
              </div>
              <div>
                <label class="block text-[11px] uppercase tracking-[0.2em] text-ink-muted font-light mb-2">{{ t('admin.content.fields.tier') }}</label>
                <select v-model="form.tier" class="w-full bg-parchment border border-parchment-deep px-5 py-3 text-sm font-light text-ink focus:outline-none focus:border-gold/60 transition-colors">
                  <option value="free">{{ t('academy.filters.free') }}</option>
                  <option value="premium">{{ t('academy.filters.premium') }}</option>
                </select>
              </div>
            </div>

            <div class="flex flex-col md:flex-row md:items-center gap-4 pt-2">
              <button type="submit" class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1 self-start">
                {{ t('admin.content.fields.save') }} <span class="dir-arrow" aria-hidden="true"></span>
              </button>
              <button type="button" class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink-muted hover:text-ink transition-colors border-b border-parchment-deep pb-1 self-start">
                {{ t('admin.content.fields.publish') }}
              </button>
              <Transition name="fade">
                <span v-if="savedNotice" class="text-xs text-ink-muted font-light italic">{{ t('admin.content.saved') }}</span>
              </Transition>
            </div>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>
