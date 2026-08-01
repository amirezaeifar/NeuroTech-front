<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseAdmin } from '../../composables/useCourseAdmin.js'
import { resolveCourseCover, resolveCourseBackground } from '../../data/courseBackgrounds.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { t } = useI18n()
const {
  courses,
  imagerySlugs,
  docTypes,
  saveCourse,
  togglePublished,
  addCourse,
  removeCourse,
  draftFrom,
  newDocument,
} = useCourseAdmin()

// ── Table state ──────────────────────────────────────────────────────────────
const query = ref('')
const tierFilter = ref('all')
const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return courses.value.filter((c) => {
    if (tierFilter.value !== 'all' && c.tier !== tierFilter.value) return false
    if (!q) return true
    return (
      c.title.toLowerCase().includes(q) ||
      c.instructor.toLowerCase().includes(q) ||
      c.category.toLowerCase().includes(q)
    )
  })
})

// ── Editor state ─────────────────────────────────────────────────────────────
// `draft` is a working copy; nothing touches the live table until Save.
const draft = ref(null)
const savedNotice = ref(false)
const editorTab = ref('metadata') // metadata | media | documents | imagery
const editorTabs = ['metadata', 'media', 'documents', 'imagery']

const openEditor = (course) => {
  draft.value = draftFrom(course)
  editorTab.value = 'metadata'
  savedNotice.value = false
}
const closeEditor = () => { draft.value = null }

const save = () => {
  saveCourse(draft.value)
  savedNotice.value = true
  setTimeout(() => { savedNotice.value = false }, 2800)
}

const createCourse = () => { openEditor(addCourse()) }

const confirmingDelete = ref(null)
const askDelete = (id) => { confirmingDelete.value = id }
const doDelete = (id) => {
  removeCourse(id)
  confirmingDelete.value = null
  if (draft.value?.id === id) closeEditor()
}

// Documents inside the draft
const addDoc = () => { draft.value.documents.push(newDocument()) }
const removeDoc = (id) => {
  draft.value.documents = draft.value.documents.filter((d) => d.id !== id)
}

// Imagery previews — resolved live from the slug so the admin sees exactly the
// light/dark pair the public pages will use.
const previews = computed(() => {
  if (!draft.value) return null
  const slug = draft.value.slug
  return {
    coverLight: resolveCourseCover(slug, false),
    coverDark: resolveCourseCover(slug, true),
    headerLight: resolveCourseBackground(slug, false),
    headerDark: resolveCourseBackground(slug, true),
  }
})

const FIELD_OPTIONS = [
  'clinicalNeurology',
  'neuroscience',
  'neuroimaging',
  'brainAnatomy',
  'neurocriticalCare',
  'neurosurgery',
]
const LEVEL_OPTIONS = ['Beginner', 'Intermediate', 'Advanced']
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="admin-eyebrow">{{ t('admin.sections.courses.label') }}</p>
        <h2 class="admin-h1 mt-2">{{ t('admin.courses.title') }}</h2>
        <p class="mt-2 text-sm text-ink-muted font-light leading-relaxed max-w-2xl">{{ t('admin.courses.subtitle') }}</p>
      </div>
      <button type="button" class="admin-btn admin-btn-primary" @click="createCourse">
        {{ t('admin.courses.add') }}
      </button>
    </div>

    <!-- ── Catalogue table ─────────────────────────────────────────────────── -->
    <div class="admin-card mt-7 p-6 md:p-7">
      <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
        <input
          v-model="query"
          type="search"
          :placeholder="t('admin.courses.search')"
          class="admin-input sm:max-w-[260px]"
        />
        <div class="flex gap-2">
          <button
            v-for="tf in ['all', 'free', 'premium']"
            :key="tf"
            type="button"
            @click="tierFilter = tf"
            :class="['admin-btn admin-btn-sm', tierFilter === tf ? 'admin-btn-primary' : 'admin-btn-ghost']"
          >{{ t('academy.filters.' + tf) }}</button>
        </div>
      </div>

      <div class="admin-scroll">
        <table class="admin-table min-w-[760px]">
          <thead>
            <tr>
              <th>{{ t('admin.courses.cols.course') }}</th>
              <th>{{ t('admin.courses.cols.category') }}</th>
              <th>{{ t('admin.courses.cols.tier') }}</th>
              <th>{{ t('admin.courses.cols.price') }}</th>
              <th>{{ t('admin.courses.cols.published') }}</th>
              <th class="text-end">{{ t('admin.courses.cols.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filtered" :key="c.id" :class="{ 'opacity-95': !c.published }">
              <td>
                <div class="flex items-center gap-3">
                  <img
                    :src="resolveCourseCover(c.slug, false)"
                    alt=""
                    class="w-14 h-9 object-cover rounded-md border border-parchment-deep/60 shrink-0"
                  />
                  <div class="min-w-0">
                    <span class="block text-ink font-normal truncate">{{ c.title }}</span>
                    <span class="block text-xs text-ink-muted truncate">{{ c.instructor || '—' }} · {{ c.duration || '—' }}</span>
                  </div>
                </div>
              </td>
              <td class="whitespace-nowrap">{{ c.category }}</td>
              <td>
                <span :class="['admin-badge', c.tier === 'premium' ? 'admin-badge-gold' : 'admin-badge-muted']">
                  {{ t('academy.filters.' + c.tier) }}
                </span>
              </td>
              <td class="whitespace-nowrap">
                <span v-if="c.tier === 'premium'">${{ c.price }}</span>
                <span v-else class="text-ink-hint">—</span>
              </td>
              <td><AdminToggle :model-value="c.published" @update:model-value="togglePublished(c.id)" /></td>
              <td>
                <div class="flex items-center justify-end gap-2">
                  <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="openEditor(c)">
                    {{ t('admin.courses.edit') }}
                  </button>
                  <button
                    v-if="confirmingDelete !== c.id"
                    type="button"
                    class="admin-btn admin-btn-danger admin-btn-sm"
                    @click="askDelete(c.id)"
                  >{{ t('admin.courses.remove') }}</button>
                  <button
                    v-else
                    type="button"
                    class="admin-btn admin-btn-danger admin-btn-sm"
                    @click="doDelete(c.id)"
                  >{{ t('admin.courses.confirm') }}</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="!filtered.length" class="py-8 text-center text-sm text-ink-muted font-light italic">
        {{ t('admin.courses.empty') }}
      </p>
    </div>

    <!-- ── Editor ──────────────────────────────────────────────────────────── -->
    <Transition name="fade">
      <div v-if="draft" class="admin-card mt-8 p-6 md:p-8">
        <div class="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-parchment-deep/60">
          <div class="min-w-0">
            <p class="admin-eyebrow">{{ t('admin.courses.editing') }}</p>
            <h3 class="admin-h2 mt-1 truncate">{{ draft.title }}</h3>
          </div>
          <div class="flex items-center gap-3">
            <Transition name="fade">
              <span v-if="savedNotice" class="text-xs text-ink-muted font-light italic">{{ t('admin.courses.saved') }}</span>
            </Transition>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="closeEditor">{{ t('admin.courses.close') }}</button>
            <button type="button" class="admin-btn admin-btn-primary admin-btn-sm" @click="save">{{ t('admin.courses.save') }}</button>
          </div>
        </div>

        <!-- Editor tabs -->
        <div class="flex flex-wrap gap-2 mt-6">
          <button
            v-for="tab in editorTabs"
            :key="tab"
            type="button"
            @click="editorTab = tab"
            :class="['admin-btn admin-btn-sm', editorTab === tab ? 'admin-btn-primary' : 'admin-btn-ghost']"
          >{{ t('admin.courses.tabs.' + tab) }}</button>
        </div>

        <!-- ── Metadata ── -->
        <div v-if="editorTab === 'metadata'" class="mt-7 space-y-5">
          <div class="grid md:grid-cols-2 gap-5">
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.title') }}</label>
              <input v-model="draft.title" type="text" class="admin-input" />
            </div>
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.instructor') }}</label>
              <input v-model="draft.instructor" type="text" class="admin-input" />
            </div>
          </div>
          <div>
            <label class="admin-label">{{ t('admin.courses.fields.desc') }}</label>
            <textarea v-model="draft.desc" rows="3" class="admin-textarea" :placeholder="t('admin.courses.fields.descHint')"></textarea>
          </div>
          <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.category') }}</label>
              <input v-model="draft.category" type="text" class="admin-input" />
            </div>
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.field') }}</label>
              <select v-model="draft.field" class="admin-select">
                <option v-for="f in FIELD_OPTIONS" :key="f" :value="f">{{ t('academy.fields.' + f) }}</option>
              </select>
            </div>
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.level') }}</label>
              <select v-model="draft.level" class="admin-select">
                <option v-for="l in LEVEL_OPTIONS" :key="l" :value="l">{{ l }}</option>
              </select>
            </div>
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.duration') }}</label>
              <input v-model="draft.duration" type="text" class="admin-input" placeholder="7 lessons · 4h 30m" />
            </div>
          </div>

          <div class="admin-panel p-5 grid sm:grid-cols-2 lg:grid-cols-4 gap-5 items-end">
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.tier') }}</label>
              <select v-model="draft.tier" class="admin-select">
                <option value="free">{{ t('academy.filters.free') }}</option>
                <option value="premium">{{ t('academy.filters.premium') }}</option>
              </select>
            </div>
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.price') }}</label>
              <input
                v-model.number="draft.price"
                type="number"
                min="0"
                class="admin-input"
                :disabled="draft.tier === 'free'"
                :class="{ 'opacity-50': draft.tier === 'free' }"
              />
            </div>
            <AdminToggle v-model="draft.published" :label="t('admin.courses.fields.published')" />
            <AdminToggle v-model="draft.progressReset" :label="t('admin.courses.fields.progressReset')" />
          </div>
          <p class="text-[11px] text-ink-hint font-light italic">{{ t('admin.courses.fields.progressResetHint') }}</p>
        </div>

        <!-- ── Media ── -->
        <div v-else-if="editorTab === 'media'" class="mt-7 space-y-5 max-w-2xl">
          <div>
            <label class="admin-label">{{ t('admin.courses.fields.videoUrl') }}</label>
            <input
              v-model="draft.videoUrl"
              type="text"
              class="admin-input"
              placeholder="/course-media/…/lesson-1.mp4"
              style="direction: ltr; text-align: start;"
            />
            <p class="mt-2 text-[11px] text-ink-hint font-light leading-relaxed">{{ t('admin.courses.fields.videoUrlHint') }}</p>
          </div>
          <div v-if="draft.videoUrl" class="admin-panel p-4">
            <p class="admin-label">{{ t('admin.courses.fields.videoPreview') }}</p>
            <video :src="draft.videoUrl" controls preload="metadata" class="w-full rounded-lg bg-black/80 max-h-64"></video>
          </div>
        </div>

        <!-- ── Documents & clinical resources ── -->
        <div v-else-if="editorTab === 'documents'" class="mt-7">
          <div class="flex items-center justify-between gap-4 mb-4">
            <p class="text-sm text-ink-muted font-light">{{ t('admin.courses.fields.documentsHint') }}</p>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm shrink-0" @click="addDoc">
              {{ t('admin.courses.fields.addDocument') }}
            </button>
          </div>

          <div class="space-y-3">
            <div
              v-for="d in draft.documents"
              :key="d.id"
              class="admin-panel p-4 grid gap-3 md:grid-cols-[1fr,140px,1fr,auto] md:items-end"
            >
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.docName') }}</label>
                <input v-model="d.name" type="text" class="admin-input" />
              </div>
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.docType') }}</label>
                <select v-model="d.type" class="admin-select">
                  <option v-for="dt in docTypes" :key="dt" :value="dt">{{ t('admin.courses.docTypes.' + dt) }}</option>
                </select>
              </div>
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.docUrl') }}</label>
                <input v-model="d.url" type="text" class="admin-input" style="direction: ltr; text-align: start;" placeholder="/resources/…" />
              </div>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeDoc(d.id)">
                {{ t('admin.courses.remove') }}
              </button>
            </div>
          </div>

          <p v-if="!draft.documents.length" class="admin-panel p-8 text-center text-sm text-ink-muted font-light italic">
            {{ t('admin.courses.fields.noDocuments') }}
          </p>
        </div>

        <!-- ── Imagery ── -->
        <div v-else class="mt-7 space-y-6">
          <div class="max-w-md">
            <label class="admin-label">{{ t('admin.courses.fields.imagerySlug') }}</label>
            <select v-model="draft.slug" class="admin-select">
              <option v-for="s in imagerySlugs" :key="s" :value="s">{{ s }}</option>
            </select>
            <p class="mt-2 text-[11px] text-ink-hint font-light leading-relaxed">{{ t('admin.courses.fields.imageryHint') }}</p>
          </div>

          <div v-if="previews" class="grid sm:grid-cols-2 gap-5">
            <figure class="admin-panel p-4">
              <figcaption class="admin-label">{{ t('admin.courses.fields.coverLight') }}</figcaption>
              <img :src="previews.coverLight" alt="" class="w-full aspect-video object-cover rounded-lg border border-parchment-deep/50" />
            </figure>
            <figure class="admin-panel p-4">
              <figcaption class="admin-label">{{ t('admin.courses.fields.coverDark') }}</figcaption>
              <img :src="previews.coverDark" alt="" class="w-full aspect-video object-cover rounded-lg border border-parchment-deep/50" />
            </figure>
            <figure class="admin-panel p-4">
              <figcaption class="admin-label">{{ t('admin.courses.fields.headerLight') }}</figcaption>
              <img :src="previews.headerLight" alt="" class="w-full aspect-[3/1] object-cover rounded-lg border border-parchment-deep/50" />
            </figure>
            <figure class="admin-panel p-4">
              <figcaption class="admin-label">{{ t('admin.courses.fields.headerDark') }}</figcaption>
              <img :src="previews.headerDark" alt="" class="w-full aspect-[3/1] object-cover rounded-lg border border-parchment-deep/50" />
            </figure>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>
