<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseAdmin } from '../../composables/useCourseAdmin.js'
import { resolveCourseCover, resolveCourseBackground } from '../../data/courseBackgrounds.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { t } = useI18n()
const {
  courses,
  loading,
  error,
  imagerySlugs,
  docTypes,
  saveCourse,
  togglePublished,
  addCourse,
  removeCourse,
  reorderCourse,
  draftFrom,
  newDocument,
  newLesson,
  newSection,
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
const persistedCourses = computed(() => courses.value.filter((course) => !String(course.id).startsWith('draft-')))
const canMove = (id, direction) => {
  const index = persistedCourses.value.findIndex((course) => course.id === id)
  const target = index + direction
  return index >= 0 && target >= 0 && target < persistedCourses.value.length
}

// ── Editor state ─────────────────────────────────────────────────────────────
// `draft` is a working copy; nothing touches the live table until Save.
const draft = ref(null)
const savedNotice = ref(false)
const editorTab = ref('metadata')
const editorTabs = ['metadata', 'curriculum', 'media', 'documents', 'imagery']

const openEditor = (course) => {
  draft.value = draftFrom(course)
  editorTab.value = 'metadata'
  savedNotice.value = false
}
const closeEditor = () => { draft.value = null }

const save = async () => {
  try {
    const saved = await saveCourse(draft.value)
    if (saved) draft.value = draftFrom(saved)
    savedNotice.value = true
    setTimeout(() => { savedNotice.value = false }, 2800)
  } catch (_) {
    savedNotice.value = false
  }
}

const createCourse = () => { openEditor(addCourse()) }

const confirmingDelete = ref(null)
const askDelete = (id) => { confirmingDelete.value = id }
const doDelete = async (id) => {
  await removeCourse(id)
  confirmingDelete.value = null
  if (draft.value?.id === id) closeEditor()
}

// Documents inside the draft
const addDoc = () => { draft.value.documents.push(newDocument()) }
const removeDoc = (id) => {
  draft.value.documents = draft.value.documents.filter((d) => d.id !== id)
}

const translation = (record, locale) => {
  let value = record.translations.find((item) => item.locale === locale)
  if (!value) {
    value = { locale, title: '' }
    record.translations.push(value)
  }
  return value
}

const addSection = () => {
  draft.value.content.sections.push(newSection(draft.value.content.sections.length + 1))
}
const removeSection = (index) => {
  draft.value.content.sections.splice(index, 1)
  draft.value.content.sections.forEach((section, position) => { section.position = position + 1 })
}
const addLesson = (section) => {
  section.lessons.push(newLesson(section.lessons.length + 1))
}
const removeLesson = (section, index) => {
  section.lessons.splice(index, 1)
  section.lessons.forEach((lesson, position) => { lesson.position = position + 1 })
}
const outcome = (position, locale) => {
  let value = draft.value.content.outcomes.find(
    (item) => item.position === position && item.locale === locale,
  )
  if (!value) {
    value = { position, locale, text: '' }
    draft.value.content.outcomes.push(value)
  }
  return value
}
const outcomePositions = computed(() => [
  ...new Set((draft.value?.content.outcomes || []).map((item) => item.position)),
].sort((a, b) => a - b))
const addOutcome = () => {
  const position = Math.max(0, ...outcomePositions.value) + 1
  draft.value.content.outcomes.push(
    { position, locale: 'en', text: '' },
    { position, locale: 'fa', text: '' },
  )
}
const removeOutcome = (position) => {
  draft.value.content.outcomes = draft.value.content.outcomes
    .filter((item) => item.position !== position)
  const positions = [...new Set(draft.value.content.outcomes.map((item) => item.position))]
    .sort((a, b) => a - b)
  const remap = new Map(positions.map((value, index) => [value, index + 1]))
  draft.value.content.outcomes.forEach((item) => { item.position = remap.get(item.position) })
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
      <p v-if="error" class="mb-5 text-xs text-red-700" role="alert">{{ error }}</p>
      <p v-if="loading" class="mb-5 text-xs text-ink-muted">{{ t('academy.loading') }}</p>
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
                  <button
                    type="button"
                    class="admin-btn admin-btn-ghost admin-btn-sm"
                    :disabled="!canMove(c.id, -1)"
                    :aria-label="t('admin.courses.moveUp')"
                    @click="reorderCourse(c.id, -1)"
                  >↑</button>
                  <button
                    type="button"
                    class="admin-btn admin-btn-ghost admin-btn-sm"
                    :disabled="!canMove(c.id, 1)"
                    :aria-label="t('admin.courses.moveDown')"
                    @click="reorderCourse(c.id, 1)"
                  >↓</button>
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
          <div class="pt-5 border-t border-parchment-deep/60">
            <p class="admin-eyebrow mb-4">{{ t('admin.courses.fields.persianMetadata') }}</p>
            <div class="grid md:grid-cols-2 gap-5">
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.titleFa') }}</label>
                <input v-model="draft.faTitle" type="text" dir="rtl" class="admin-input" />
              </div>
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.instructorFa') }}</label>
                <input v-model="draft.faInstructor" type="text" dir="rtl" class="admin-input" />
              </div>
            </div>
            <div class="grid md:grid-cols-[1fr,220px] gap-5 mt-5">
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.descFa') }}</label>
                <textarea v-model="draft.faDesc" rows="3" dir="rtl" class="admin-textarea"></textarea>
              </div>
              <div>
                <label class="admin-label">{{ t('admin.courses.fields.durationFa') }}</label>
                <input v-model="draft.faDuration" type="text" dir="rtl" class="admin-input" />
              </div>
            </div>
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
              <label class="admin-label">{{ t('admin.courses.fields.priceUsd') }}</label>
              <input
                v-model.number="draft.price"
                type="number"
                min="0"
                class="admin-input"
                :disabled="draft.tier === 'free'"
                :class="{ 'opacity-50': draft.tier === 'free' }"
              />
            </div>
            <div>
              <label class="admin-label">{{ t('admin.courses.fields.priceIrr') }}</label>
              <input
                v-model.number="draft.irrPrice"
                type="number"
                min="0"
                step="1"
                class="admin-input"
                :disabled="draft.tier === 'free'"
                :class="{ 'opacity-50': draft.tier === 'free' }"
              />
            </div>
            <AdminToggle v-model="draft.published" :label="t('admin.courses.fields.published')" />
          </div>
        </div>

        <!-- ── Curriculum ── -->
        <div v-else-if="editorTab === 'curriculum'" class="mt-7 space-y-7">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h4 class="admin-h2">{{ t('admin.courses.curriculum.sections') }}</h4>
              <p class="mt-1 text-xs text-ink-muted">{{ t('admin.courses.curriculum.hint') }}</p>
            </div>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addSection">
              {{ t('admin.courses.curriculum.addSection') }}
            </button>
          </div>

          <article
            v-for="(section, sectionIndex) in draft.content.sections"
            :key="section.id || section.position"
            class="admin-panel p-5 space-y-5"
          >
            <div class="flex items-center justify-between gap-3">
              <span class="admin-eyebrow">{{ t('admin.courses.curriculum.section') }} {{ section.position }}</span>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeSection(sectionIndex)">
                {{ t('admin.courses.remove') }}
              </button>
            </div>
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="admin-label">{{ t('admin.courses.curriculum.titleEn') }}</label>
                <input v-model="translation(section, 'en').title" type="text" class="admin-input" />
              </div>
              <div>
                <label class="admin-label">{{ t('admin.courses.curriculum.titleFa') }}</label>
                <input v-model="translation(section, 'fa').title" type="text" dir="rtl" class="admin-input" />
              </div>
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between gap-3">
                <h5 class="text-sm text-ink">{{ t('admin.courses.curriculum.lessons') }}</h5>
                <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addLesson(section)">
                  {{ t('admin.courses.curriculum.addLesson') }}
                </button>
              </div>
              <div
                v-for="(lesson, lessonIndex) in section.lessons"
                :key="lesson.id || lesson.position"
                class="rounded-lg border border-parchment-deep/60 p-4 space-y-4"
              >
                <div class="grid md:grid-cols-2 gap-4">
                  <div>
                    <label class="admin-label">{{ t('admin.courses.curriculum.lessonTitleEn') }}</label>
                    <input v-model="translation(lesson, 'en').title" type="text" class="admin-input" />
                  </div>
                  <div>
                    <label class="admin-label">{{ t('admin.courses.curriculum.lessonTitleFa') }}</label>
                    <input v-model="translation(lesson, 'fa').title" type="text" dir="rtl" class="admin-input" />
                  </div>
                </div>
                <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
                  <div>
                    <label class="admin-label">{{ t('admin.courses.curriculum.provider') }}</label>
                    <select v-model="lesson.video_provider" class="admin-select">
                      <option value="youtube">YouTube</option>
                    </select>
                  </div>
                  <div>
                    <label class="admin-label">{{ t('admin.courses.curriculum.reference') }}</label>
                    <input v-model="lesson.video_reference" type="text" dir="ltr" class="admin-input" />
                  </div>
                  <div>
                    <label class="admin-label">{{ t('admin.courses.curriculum.durationSeconds') }}</label>
                    <input v-model.number="lesson.duration_seconds" type="number" min="0" class="admin-input" />
                  </div>
                  <div class="flex items-center justify-between gap-3">
                    <AdminToggle v-model="lesson.free_preview" :label="t('admin.courses.curriculum.freePreview')" />
                    <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeLesson(section, lessonIndex)">×</button>
                  </div>
                </div>
              </div>
            </div>
          </article>

          <div class="pt-6 border-t border-parchment-deep/60">
            <div class="flex items-center justify-between gap-4 mb-4">
              <h4 class="admin-h2">{{ t('admin.courses.curriculum.outcomes') }}</h4>
              <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addOutcome">
                {{ t('admin.courses.curriculum.addOutcome') }}
              </button>
            </div>
            <div v-for="position in outcomePositions" :key="position" class="admin-panel p-4 grid md:grid-cols-[1fr,1fr,auto] gap-4 items-end mb-3">
              <div>
                <label class="admin-label">{{ t('admin.courses.curriculum.outcomeEn') }}</label>
                <input v-model="outcome(position, 'en').text" type="text" class="admin-input" />
              </div>
              <div>
                <label class="admin-label">{{ t('admin.courses.curriculum.outcomeFa') }}</label>
                <input v-model="outcome(position, 'fa').text" type="text" dir="rtl" class="admin-input" />
              </div>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeOutcome(position)">×</button>
            </div>
          </div>
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
            <input
              v-model="draft.slug"
              list="course-imagery-slugs"
              class="admin-input"
              :disabled="!String(draft.id).startsWith('draft-')"
            />
            <datalist id="course-imagery-slugs">
              <option v-for="s in imagerySlugs" :key="s" :value="s"></option>
            </datalist>
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
