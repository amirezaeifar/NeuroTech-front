<script setup>
import { validateSection } from '../../utils/validation.js'
import { ref, computed, nextTick, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseAdmin } from '../../composables/useCourseAdmin.js'
import { resolveCourseCover } from '../../data/courseBackgrounds.js'
import { useTheme } from '../../composables/useTheme.js'
import { productsApi } from '../../api/products.js'
import { academyApi } from '../../api/academy.js'
import { partnersApi } from '../../api/content.js'
import { resolveApiUrl } from '../../api/client.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { t, locale } = useI18n()
const { isDark } = useTheme()
const tr = (en,fa) => locale.value === 'fa' ? fa : en
const saving = ref(false)
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
      [c.title, c.faTitle, c.instructor, c.faInstructor, c.category]
        .some((value) => String(value || '').toLowerCase().includes(q))
    )
  })
})
const courseTitle = (course) => locale.value === 'fa' ? (course.faTitle || course.title) : course.title
const courseInstructor = (course) => locale.value === 'fa' ? (course.faInstructor || course.instructor) : course.instructor
const formatPrice = (course) => {
  if (course.tier !== 'premium') return tr('Free', 'رایگان')
  const usd = course.prices?.find((item) => item.currency === 'USD')
  const irr = course.prices?.find((item) => item.currency === 'IRR')
  const values = []
  if (usd) values.push(`$${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(usd.amount_minor / 100)}`)
  if (irr) values.push(`${new Intl.NumberFormat(locale.value === 'fa' ? 'fa-IR' : 'en-US').format(irr.amount_minor)} ${tr('IRR', 'ریال')}`)
  return values.join(' · ') || '—'
}
const courseCover = (course) => {
  const preferredKind = `cover_${isDark.value ? 'dark' : 'light'}`
  const fallbackKind = `cover_${isDark.value ? 'light' : 'dark'}`
  const media = course.content?.media || []
  const uploaded = media.find((item) => item.kind === preferredKind)
    || media.find((item) => item.kind === fallbackKind)
  const source = uploaded?.external_url || uploaded?.storage_path
  return source ? resolveApiUrl(source) : resolveCourseCover(course.slug, isDark.value)
}
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
const formError = ref('')
const fieldErrors = ref({})
const editorTab = ref('metadata')
const editorTabs = ['metadata', 'curriculum', 'documents']
const commentStats = ref({})
const partners = ref([])
academyApi.commentSummary().then(result => { commentStats.value = Object.fromEntries(result.data.map(item => [item.course_slug,item])) }).catch(() => {})
onMounted(async () => { try { partners.value = (await partnersApi.adminList()).data.filter((partner) => partner.published) } catch (_) { partners.value = [] } })
const partnerTranslation = (partner, code = locale.value) => partner.translations?.find((item) => item.locale === code) || partner.translations?.find((item) => item.locale === 'en') || partner
const chooseInstructor = (partner) => {
  draft.value.instructorPartnerId = partner.id
  draft.value.instructorPartnerSlug = partner.slug
  draft.value.instructor = partnerTranslation(partner, 'en').name
  draft.value.faInstructor = partnerTranslation(partner, 'fa').name
  delete fieldErrors.value.instructorPartnerId
}

const openEditor = (course) => {
  draft.value = draftFrom(course)
  nextTick(() => document.getElementById('course-editor')?.scrollIntoView({behavior:'smooth',block:'start'}))
  editorTab.value = 'metadata'
  savedNotice.value = false
  formError.value = ''
  fieldErrors.value = {}
}
const closeEditor = () => { draft.value = null }

const requiredMessage = (label) => tr(`Enter ${label}.`, `«${label}» را وارد کنید.`)
const errorFor = (key) => fieldErrors.value[key]
const markError = (key, label, tab) => {
  if (!fieldErrors.value[key]) fieldErrors.value[key] = requiredMessage(label)
  return tab
}
const validateDraft = () => {
  fieldErrors.value = {}
  let firstTab = ''
  const requireValue = (key, value, label, tab = 'metadata') => {
    if (String(value ?? '').trim()) return
    const targetTab = markError(key, label, tab)
    if (!firstTab) firstTab = targetTab
  }
  requireValue('title', draft.value.title, tr('Title', 'عنوان'))
  requireValue('instructorPartnerId', draft.value.instructorPartnerId, tr('Instructor', 'مدرس'))
  requireValue('duration', draft.value.duration, tr('Duration', 'مدت دوره'))
  requireValue('desc', draft.value.desc, tr('Description', 'توضیحات'))
  requireValue('faTitle', draft.value.faTitle, tr('Title', 'عنوان'))
  requireValue('faDuration', draft.value.faDuration, tr('Duration', 'مدت دوره'))
  requireValue('faDesc', draft.value.faDesc, tr('Description', 'توضیحات'))
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(draft.value.slug)) {
    fieldErrors.value.slug = tr('Use lowercase letters, numbers and hyphens only.', 'فقط از حروف کوچک انگلیسی، عدد و خط تیره استفاده کنید.')
    if (!firstTab) firstTab = 'documents'
  }
  if (draft.value.playlistId && draft.value.playlistId.trim().length < 10) {
    fieldErrors.value.playlistId = tr('The playlist ID must contain at least 10 characters.', 'شناسه پلی‌لیست باید حداقل ۱۰ نویسه داشته باشد.')
    if (!firstTab) firstTab = 'curriculum'
  }
  draft.value.content.sections.forEach((section, sectionIndex) => {
    requireValue(`section-${sectionIndex}-en`, translation(section, 'en').title, tr('Section title', 'عنوان بخش'), 'curriculum')
    requireValue(`section-${sectionIndex}-fa`, translation(section, 'fa').title, tr('Section title', 'عنوان بخش'), 'curriculum')
    if (draft.value.published && !section.lessons.length) {
      fieldErrors.value[`section-${sectionIndex}-lessons`] = tr('Add at least one lesson before publishing.', 'پیش از انتشار حداقل یک درس اضافه کنید.')
      if (!firstTab) firstTab = 'curriculum'
    }
    section.lessons.forEach((lesson, lessonIndex) => {
      requireValue(`lesson-${sectionIndex}-${lessonIndex}-en`, translation(lesson, 'en').title, tr('Title', 'عنوان'), 'curriculum')
      requireValue(`lesson-${sectionIndex}-${lessonIndex}-fa`, translation(lesson, 'fa').title, tr('Title', 'عنوان'), 'curriculum')
      requireValue(`lesson-${sectionIndex}-${lessonIndex}-reference`, lesson.video_reference, tr('Video reference', 'شناسه ویدئو'), 'curriculum')
    })
  })
  outcomePositions.value.forEach((position) => {
    requireValue(`outcome-${position}-en`, outcome(position, 'en').text, tr('Title', 'عنوان'), 'curriculum')
    requireValue(`outcome-${position}-fa`, outcome(position, 'fa').text, tr('Title', 'عنوان'), 'curriculum')
  })
  if (draft.value.published && !draft.value.content.sections.length) {
    fieldErrors.value.sections = tr('Add at least one section with a lesson before publishing.', 'پیش از انتشار حداقل یک بخش همراه با درس اضافه کنید.')
    if (!firstTab) firstTab = 'curriculum'
  }
  if (draft.value.published && !outcomePositions.value.length) {
    fieldErrors.value.outcomes = tr('Add learning achievements in both languages before publishing.', 'پیش از انتشار دستاوردهای یادگیری را در هر دو زبان اضافه کنید.')
    if (!firstTab) firstTab = 'curriculum'
  }
  draft.value.documents.forEach((document, index) => {
    if (document.name || document.url) {
      requireValue(`document-${index}-name`, document.name, tr('Resource name', 'نام منبع'), 'documents')
      requireValue(`document-${index}-url`, document.url, tr('Resource URL', 'نشانی منبع'), 'documents')
    }
  })
  if (firstTab) {
    editorTab.value = firstTab
    nextTick(() => document.querySelector('#course-editor [aria-invalid="true"], #course-editor .field-error')?.scrollIntoView({ block: 'center', behavior: 'smooth' }))
  }
  return !firstTab
}

const save = async () => {
  if (saving.value) return
  formError.value = ''
  if (!validateDraft()) return
  await nextTick()
  if (!validateSection(document.getElementById('course-editor'))) return
  saving.value = true
  try {
    const saved = await saveCourse(draft.value)
    if (saved && !saved._approvalPending) draft.value = draftFrom(saved)
    fieldErrors.value = {}
    formError.value = ''
    savedNotice.value = saved?._approvalPending
      ? tr('Sent to the principal approval queue.', 'درخواست به صف تأیید مدیر اصلی ارسال شد.')
      : t('admin.courses.saved')
    setTimeout(() => { savedNotice.value = false }, 2800)
  } catch (problem) {
    if (/slug|نشانی/i.test(problem.message)) {
      fieldErrors.value.slug = problem.message
      editorTab.value = 'documents'
    } else if (/playlist|پلی.?لیست/i.test(problem.message)) {
      fieldErrors.value.playlistId = problem.message
      editorTab.value = 'curriculum'
    } else {
      formError.value = problem.message
    }
    savedNotice.value = false
  } finally { saving.value = false }
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

const imageKinds = ['cover_light','cover_dark','header_light','header_dark']
const imageUrl = (kind) => { const item = draft.value?.content.media.find(m => m.kind === kind); return item ? resolveApiUrl(item.external_url || item.storage_path) : '' }
const uploadCourseImage = async (event, kind) => {
  const file = event.target.files?.[0]; if (!file) return
  saving.value = true
  try {
    const result = await productsApi.upload(file)
    draft.value.content.media = draft.value.content.media.filter(item => item.kind !== kind)
    draft.value.content.media.push({kind,position:Math.max(0,...draft.value.content.media.map(item=>item.position))+1,locale:null,mime_type:file.type,storage_path:result.data.url,external_url:null})
  } catch (problem) { formError.value = problem.message } finally { saving.value = false; event.target.value = '' }
}

const uploadResource = async (event, document) => {
 const file=event.target.files?.[0];if(!file)return
 saving.value=true
 try { const result=await productsApi.upload(file);document.url=resolveApiUrl(result.data.url);if(!document.name)document.name=file.name }
 catch(problem){formError.value=problem.message}finally{saving.value=false;event.target.value=''}
}
const FIELD_OPTIONS = [
  'clinicalNeurology',
  'neuroscience',
  'neuroimaging',
  'brainAnatomy',
  'neurocriticalCare',
  'neurosurgery',
]
const LEVEL_OPTIONS = ['beginner', 'intermediate', 'advanced']
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
      <p v-if="error && !draft" class="mb-5 text-xs text-red-700" role="alert">{{ error }}</p>
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
                    :src="courseCover(c)"
                    alt=""
                    class="w-14 h-9 object-cover rounded-md border border-parchment-deep/60 shrink-0"
                  />
                  <div class="min-w-0">
                    <span class="block text-ink font-normal truncate">{{ courseTitle(c) }}</span>
                    <span class="block text-xs text-ink-muted truncate">{{ courseInstructor(c) || '—' }} · {{ locale === 'fa' ? (c.faDuration || c.duration) : c.duration || '—' }}</span>
                  </div>
                </div>
              </td>
              <td class="whitespace-nowrap">{{ t('academy.fields.' + c.field) }}</td>
              <td>
                <span :class="['admin-badge', c.tier === 'premium' ? 'admin-badge-gold' : 'admin-badge-muted']">
                  {{ t('academy.filters.' + c.tier) }}
                </span>
              </td>
              <td class="whitespace-nowrap">
                <span>{{ formatPrice(c) }}</span>
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
      <div id="course-editor" v-if="draft" class="admin-card mt-8 p-6 md:p-8">
        <div class="flex flex-wrap items-center justify-between gap-4 pb-5 border-b border-parchment-deep/60">
          <div class="min-w-0">
            <p class="admin-eyebrow">{{ t('admin.courses.editing') }}</p>
            <h3 class="admin-h2 mt-1 truncate">{{ courseTitle(draft) }}</h3>
          </div>
        </div>

        <!-- Editor tabs -->
        <div class="flex flex-wrap gap-2 mt-6 pb-5 border-b border-parchment-deep/60">
          <button
            v-for="tab in editorTabs"
            :key="tab"
            type="button"
            @click="editorTab = tab"
            :class="['admin-btn admin-btn-sm', editorTab === tab ? 'admin-btn-primary' : 'admin-btn-ghost']"
          >{{ t('admin.courses.tabs.' + tab) }}</button>
        </div>
        <router-link :to="{name:'AdminModeration',query:{course:draft.slug}}" class="admin-panel mt-5 p-4 flex flex-wrap items-center justify-between gap-3 hover:border-gold/50">
          <span><strong>{{ tr('Comments for this course','دیدگاه‌های این دوره') }}</strong><small class="block mt-1 text-ink-muted">{{ commentStats[draft.slug]?.new||0 }} {{ tr('new','دیدگاه جدید') }} · {{ commentStats[draft.slug]?.needs_reply||0 }} {{ tr('need replies','نیازمند پاسخ') }}</small></span><span class="text-gold-dark">{{ tr('View and manage comments →','مشاهده و مدیریت دیدگاه‌ها ←') }}</span>
        </router-link>
        <p v-if="formError" role="alert" class="field-error mt-4">{{ formError }}</p>

        <!-- ── Metadata ── -->
        <div v-if="editorTab === 'metadata'" class="mt-7 space-y-6">
          <section class="admin-panel p-5 space-y-4">
            <h4 class="admin-h2">{{ tr('Course instructor', 'مدرس دوره') }}</h4>
            <div class="grid md:grid-cols-2 gap-3">
              <div v-for="partner in partners" :key="partner.id" class="flex items-center gap-3 rounded-lg border border-parchment-deep/60 p-3" :class="{ 'border-gold/70 bg-gold/5': draft.instructorPartnerId === partner.id }">
                <label class="flex min-w-0 flex-1 cursor-pointer items-center gap-3"><input type="radio" name="course-instructor" class="accent-gold" :checked="draft.instructorPartnerId === partner.id" @change="chooseInstructor(partner)"><img v-if="partner.image_url" :src="resolveApiUrl(partner.image_url)" class="h-10 w-10 shrink-0 rounded-full object-cover" alt=""><span class="min-w-0"><strong class="block truncate text-sm text-ink">{{ partnerTranslation(partner).name }}</strong><small class="block truncate text-ink-muted">{{ partnerTranslation(partner).title }}</small></span></label>
                <router-link :to="{ name: 'PartnerProfile', params: { id: partner.slug } }" target="_blank" class="admin-btn admin-btn-ghost admin-btn-sm">{{ tr('Profile', 'پروفایل') }}</router-link>
              </div>
            </div>
            <p v-if="errorFor('instructorPartnerId')" class="field-error">{{ errorFor('instructorPartnerId') }}</p>
            <p v-if="!partners.length" class="text-sm text-ink-muted">{{ tr('No published partners are available.', 'همکار منتشرشده‌ای برای انتخاب وجود ندارد.') }}</p>
          </section>
          <div class="grid xl:grid-cols-2 gap-6 items-start">
            <section class="admin-panel p-5 space-y-4" lang="en" dir="ltr">
              <h4 class="admin-h2">{{ tr('English content', 'بخش انگلیسی') }}</h4>
              <div><label class="admin-label">{{ tr('Title','عنوان') }}</label><input required v-model="draft.title" type="text" class="admin-input" :aria-invalid="Boolean(errorFor('title'))" /><p v-if="errorFor('title')" class="field-error">{{ errorFor('title') }}</p></div>
              <div><label class="admin-label">{{ tr('Duration','مدت دوره') }}</label><input required v-model="draft.duration" type="text" class="admin-input" :placeholder="tr('7 sessions · 4h 30m', '۷ جلسه · ۴ ساعت و ۳۰ دقیقه')" :aria-invalid="Boolean(errorFor('duration'))" /><p v-if="errorFor('duration')" class="field-error">{{ errorFor('duration') }}</p></div>
              <div><label class="admin-label">{{ tr('Description','توضیحات') }}</label><textarea required v-model="draft.desc" rows="4" class="admin-textarea" :placeholder="t('admin.courses.fields.descHint')" :aria-invalid="Boolean(errorFor('desc'))"></textarea><p v-if="errorFor('desc')" class="field-error">{{ errorFor('desc') }}</p></div>
              <div><label class="admin-label">{{ tr('Summary','خلاصه') }}</label><textarea v-model="draft.summary" class="admin-textarea" rows="3" maxlength="2000"></textarea></div>
            </section>
            <section class="admin-panel p-5 space-y-4" lang="fa" dir="rtl">
              <h4 class="admin-h2">{{ tr('Persian content', 'بخش فارسی') }}</h4>
              <div><label class="admin-label">{{ tr('Title','عنوان') }}</label><input required v-model="draft.faTitle" type="text" class="admin-input" :aria-invalid="Boolean(errorFor('faTitle'))" /><p v-if="errorFor('faTitle')" class="field-error">{{ errorFor('faTitle') }}</p></div>
              <div><label class="admin-label">{{ tr('Duration','مدت دوره') }}</label><input required v-model="draft.faDuration" type="text" class="admin-input" :placeholder="tr('7 sessions · 4h 30m', '۷ جلسه · ۴ ساعت و ۳۰ دقیقه')" :aria-invalid="Boolean(errorFor('faDuration'))" /><p v-if="errorFor('faDuration')" class="field-error">{{ errorFor('faDuration') }}</p></div>
              <div><label class="admin-label">{{ tr('Description','توضیحات') }}</label><textarea required v-model="draft.faDesc" rows="4" class="admin-textarea" :aria-invalid="Boolean(errorFor('faDesc'))"></textarea><p v-if="errorFor('faDesc')" class="field-error">{{ errorFor('faDesc') }}</p></div>
              <div><label class="admin-label">{{ tr('Summary','خلاصه') }}</label><textarea v-model="draft.faSummary" class="admin-textarea" rows="3" maxlength="2000"></textarea></div>
            </section>
          </div>

          <section class="admin-panel p-5">
            <h4 class="admin-h2 mb-4">{{ tr('Course classification', 'دسته‌بندی دوره') }}</h4>
            <div class="grid sm:grid-cols-2 gap-5">
              <div><label class="admin-label">{{ t('admin.courses.fields.field') }}</label><select v-model="draft.field" class="admin-select"><option v-for="f in FIELD_OPTIONS" :key="f" :value="f">{{ t('academy.fields.' + f) }}</option></select></div>
              <div><label class="admin-label">{{ t('admin.courses.fields.level') }}</label><select v-model="draft.level" class="admin-select"><option v-for="l in LEVEL_OPTIONS" :key="l" :value="l">{{ locale==='fa' ? {beginner:'مقدماتی',intermediate:'متوسط',advanced:'پیشرفته'}[l] : l.charAt(0).toUpperCase()+l.slice(1) }}</option></select></div>
            </div>
          </section>

          <section class="admin-panel p-5">
            <h4 class="admin-h2 mb-4">{{ tr('Access and pricing', 'دسترسی و قیمت‌گذاری') }}</h4>
            <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 items-end">
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
          </section>
        </div>

        <!-- ── Curriculum ── -->
        <div v-else-if="editorTab === 'curriculum'" class="mt-7 space-y-7">
          <section class="admin-panel p-5 space-y-5">
            <h4 class="admin-h2">{{ tr('Syllabus','سرفصل‌ها') }}</h4>
            <p v-if="errorFor('sections')" class="field-error">{{ errorFor('sections') }}</p>
            <article v-for="(section, sectionIndex) in draft.content.sections" :key="section.id || section.position" class="relative rounded-lg border border-parchment-deep/60 p-4 pt-12 space-y-4">
              <div class="flex items-center justify-between gap-3">
                <span class="admin-eyebrow">{{ tr('Syllabus item','سرفصل') }} {{ section.position }}</span>
                <button type="button" class="admin-icon-remove admin-remove-corner" :aria-label="tr('Remove syllabus item','حذف سرفصل')" @click="removeSection(sectionIndex)">×</button>
              </div>
              <div class="grid md:grid-cols-2 gap-4">
                <div lang="en" dir="ltr"><p class="admin-eyebrow mb-3">{{ tr('English content', 'بخش انگلیسی') }}</p><label class="admin-label">{{ tr('Title', 'عنوان') }}</label><input required v-model="translation(section, 'en').title" type="text" class="admin-input" :aria-invalid="Boolean(errorFor(`section-${sectionIndex}-en`))" /><p v-if="errorFor(`section-${sectionIndex}-en`)" class="field-error">{{ errorFor(`section-${sectionIndex}-en`) }}</p></div>
                <div lang="fa" dir="rtl"><p class="admin-eyebrow mb-3">{{ tr('Persian content', 'بخش فارسی') }}</p><label class="admin-label">{{ tr('Title', 'عنوان') }}</label><input required v-model="translation(section, 'fa').title" type="text" class="admin-input" :aria-invalid="Boolean(errorFor(`section-${sectionIndex}-fa`))" /><p v-if="errorFor(`section-${sectionIndex}-fa`)" class="field-error">{{ errorFor(`section-${sectionIndex}-fa`) }}</p></div>
              </div>
            </article>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addSection">{{ t('admin.courses.curriculum.addSection') }}</button>
          </section>

          <section class="admin-panel p-5 space-y-4">
            <h4 class="admin-h2">{{ tr('Learning achievements','دستاوردهای یادگیری') }}</h4>
            <p v-if="errorFor('outcomes')" class="field-error mb-4">{{ errorFor('outcomes') }}</p>
            <div v-for="position in outcomePositions" :key="position" class="admin-panel relative p-4 pt-12 grid md:grid-cols-2 gap-4 items-end mb-3">
              <div lang="en" dir="ltr">
                <p class="admin-eyebrow mb-2">{{ tr('English content', 'بخش انگلیسی') }}</p>
                <label class="admin-label">{{ tr('Title', 'عنوان') }}</label>
                <input required v-model="outcome(position, 'en').text" type="text" class="admin-input" :aria-invalid="Boolean(errorFor(`outcome-${position}-en`))" />
                <p v-if="errorFor(`outcome-${position}-en`)" class="field-error">{{ errorFor(`outcome-${position}-en`) }}</p>
              </div>
              <div lang="fa" dir="rtl">
                <p class="admin-eyebrow mb-2">{{ tr('Persian content', 'بخش فارسی') }}</p>
                <label class="admin-label">{{ tr('Title', 'عنوان') }}</label>
                <input required v-model="outcome(position, 'fa').text" type="text" dir="rtl" class="admin-input" :aria-invalid="Boolean(errorFor(`outcome-${position}-fa`))" />
                <p v-if="errorFor(`outcome-${position}-fa`)" class="field-error">{{ errorFor(`outcome-${position}-fa`) }}</p>
              </div>
              <button type="button" class="admin-icon-remove admin-remove-corner" :aria-label="tr('Remove achievement','حذف دستاورد')" @click="removeOutcome(position)">×</button>
            </div>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addOutcome">{{ t('admin.courses.curriculum.addOutcome') }}</button>
          </section>

          <section class="admin-panel p-5 space-y-4">
            <h4 class="admin-h2">{{ tr('Course video playlist','پلی‌لیست ویدئوهای دوره') }}</h4>
            <div><label class="admin-label">{{ t('admin.courses.fields.videoUrl') }}</label><input v-model="draft.playlistId" type="text" class="admin-input" minlength="10" maxlength="100" :aria-invalid="Boolean(errorFor('playlistId'))" placeholder="PLxxxxxxxxxxxxxxxx" style="direction:ltr;text-align:start"><p v-if="errorFor('playlistId')" class="field-error">{{ errorFor('playlistId') }}</p><p class="mt-2 text-[11px] text-ink-hint">{{ t('admin.courses.fields.videoUrlHint') }}</p></div>
            <iframe v-if="draft.playlistId" :src="`https://www.youtube.com/embed/videoseries?list=${encodeURIComponent(draft.playlistId)}`" class="w-full aspect-video rounded-lg bg-black/80" title="YouTube playlist preview" allowfullscreen></iframe>
          </section>

          <section class="admin-panel p-5 space-y-5">
            <h4 class="admin-h2">{{ tr('Course sessions','جلسات دوره') }}</h4>
            <p v-if="!draft.content.sections.length" class="text-sm text-ink-muted">{{ tr('Add a syllabus item before adding sessions.','برای افزودن جلسه، ابتدا یک سرفصل اضافه کنید.') }}</p>
            <div v-for="(section, sectionIndex) in draft.content.sections" :key="`sessions-${section.id || section.position}`" class="rounded-lg border border-parchment-deep/60 p-4 space-y-4">
              <h5 class="admin-h2 text-base">{{ tr('Syllabus item','سرفصل') }} {{ section.position }}</h5>
              <p v-if="errorFor(`section-${sectionIndex}-lessons`)" class="field-error">{{ errorFor(`section-${sectionIndex}-lessons`) }}</p>
              <div v-for="(lesson, lessonIndex) in section.lessons" :key="lesson.id || lesson.position" class="relative rounded-lg border border-parchment-deep/60 p-4 pt-12 space-y-4">
                <div class="grid md:grid-cols-2 gap-4">
                  <div lang="en" dir="ltr"><p class="admin-eyebrow mb-2">{{ tr('English content', 'بخش انگلیسی') }}</p><label class="admin-label">{{ tr('Title', 'عنوان') }}</label><input required v-model="translation(lesson, 'en').title" type="text" class="admin-input" :aria-invalid="Boolean(errorFor(`lesson-${sectionIndex}-${lessonIndex}-en`))" /><p v-if="errorFor(`lesson-${sectionIndex}-${lessonIndex}-en`)" class="field-error">{{ errorFor(`lesson-${sectionIndex}-${lessonIndex}-en`) }}</p></div>
                  <div lang="fa" dir="rtl"><p class="admin-eyebrow mb-2">{{ tr('Persian content', 'بخش فارسی') }}</p><label class="admin-label">{{ tr('Title', 'عنوان') }}</label><input required v-model="translation(lesson, 'fa').title" type="text" class="admin-input" :aria-invalid="Boolean(errorFor(`lesson-${sectionIndex}-${lessonIndex}-fa`))" /><p v-if="errorFor(`lesson-${sectionIndex}-${lessonIndex}-fa`)" class="field-error">{{ errorFor(`lesson-${sectionIndex}-${lessonIndex}-fa`) }}</p></div>
                </div>
                <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
                  <div><label class="admin-label">{{ t('admin.courses.curriculum.provider') }}</label><select v-model="lesson.video_provider" class="admin-select"><option value="youtube">YouTube</option></select></div>
                  <div><label class="admin-label">{{ t('admin.courses.curriculum.reference') }}</label><input required v-model="lesson.video_reference" type="text" dir="ltr" class="admin-input" :aria-invalid="Boolean(errorFor(`lesson-${sectionIndex}-${lessonIndex}-reference`))" /><p v-if="errorFor(`lesson-${sectionIndex}-${lessonIndex}-reference`)" class="field-error">{{ errorFor(`lesson-${sectionIndex}-${lessonIndex}-reference`) }}</p></div>
                  <div><label class="admin-label">{{ t('admin.courses.curriculum.durationSeconds') }}</label><input v-model.number="lesson.duration_seconds" type="number" min="0" class="admin-input" /></div>
                  <div><AdminToggle v-model="lesson.free_preview" :label="t('admin.courses.curriculum.freePreview')" /></div>
                </div>
                <button type="button" class="admin-icon-remove admin-remove-corner" :aria-label="tr('Remove session','حذف جلسه')" @click="removeLesson(section, lessonIndex)">×</button>
              </div>
              <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addLesson(section)">{{ t('admin.courses.curriculum.addLesson') }}</button>
            </div>
          </section>
        </div>

        <!-- ── Documents & clinical resources ── -->
        <div v-else class="mt-7 space-y-8">
          <section class="space-y-6">
            <h4 class="admin-h2">{{ tr('Course images','تصاویر دوره') }}</h4>
            <div class="max-w-md">
              <label class="admin-label">{{ t('admin.courses.fields.imagerySlug') }}</label>
              <input required v-model="draft.slug" pattern="[a-z0-9]+(?:-[a-z0-9]+)*" maxlength="160" list="course-imagery-slugs" class="admin-input" :disabled="!String(draft.id).startsWith('draft-')" :aria-invalid="Boolean(errorFor('slug'))" />
              <p v-if="errorFor('slug')" class="field-error">{{ errorFor('slug') }}</p>
              <datalist id="course-imagery-slugs"><option v-for="s in imagerySlugs" :key="s" :value="s"></option></datalist>
              <p class="mt-2 text-[11px] text-ink-hint font-light leading-relaxed">{{ t('admin.courses.fields.imageryHint') }}</p>
            </div>
            <div class="grid md:grid-cols-2 gap-5">
              <label v-for="(kind,i) in imageKinds" :key="kind" class="admin-panel p-5">
                <span class="admin-label">{{ [tr('Cover · light','کاور · روشن'),tr('Cover · dark','کاور · تیره'),tr('Header · light','سربرگ · روشن'),tr('Header · dark','سربرگ · تیره')][i] }}</span>
                <img v-if="imageUrl(kind)" :src="imageUrl(kind)" class="aspect-video object-cover w-full rounded mb-3">
                <input class="admin-file-input" type="file" accept="image/png,image/jpeg,image/webp" :disabled="saving" @change="uploadCourseImage($event,kind)">
                <button v-if="imageUrl(kind)" type="button" class="admin-icon-remove mt-3" :aria-label="tr('Remove image','حذف تصویر')" @click.prevent="draft.content.media=draft.content.media.filter(m=>m.kind!==kind)">×</button>
              </label>
            </div>
          </section>

          <section class="pt-7 border-t border-parchment-deep/60 space-y-4">
            <h4 class="admin-h2">{{ tr('Downloadable resources','منابع قابل دریافت') }}</h4>
            <div v-for="d in draft.documents" :key="d.id" class="admin-panel relative p-4 pt-12 grid gap-3 md:grid-cols-[1fr,160px,1.2fr] md:items-end">
              <div><label class="admin-label">{{ t('admin.courses.fields.docName') }}</label><input v-model="d.name" type="text" class="admin-input" :aria-invalid="Boolean(errorFor(`document-${draft.documents.indexOf(d)}-name`))" /><p v-if="errorFor(`document-${draft.documents.indexOf(d)}-name`)" class="field-error">{{ errorFor(`document-${draft.documents.indexOf(d)}-name`) }}</p></div>
              <div><label class="admin-label">{{ t('admin.courses.fields.docType') }}</label><select v-model="d.type" class="admin-select"><option v-for="dt in docTypes" :key="dt" :value="dt">{{ t('admin.courses.docTypes.' + dt) }}</option></select></div>
              <div><label class="admin-label">{{ t('admin.courses.fields.docUrl') }}</label><input class="admin-file-input" type="file" accept=".pdf,.doc,.docx,.txt,.rtf,.ppt,.pptx,.xls,.xlsx,.csv,.json,.zip,.rar,.7z,.png,.jpg,.jpeg,.gif,.webp,.mp4,.webm,.mov,.mp3,.wav,.ogg" :disabled="saving" @change="uploadResource($event,d)"><p v-if="errorFor(`document-${draft.documents.indexOf(d)}-url`)" class="field-error">{{ errorFor(`document-${draft.documents.indexOf(d)}-url`) }}</p></div>
              <button type="button" class="admin-icon-remove admin-remove-corner" :aria-label="tr('Remove resource','حذف منبع')" @click="removeDoc(d.id)">×</button>
            </div>
            <p v-if="!draft.documents.length" class="admin-panel p-8 text-center text-sm text-ink-muted font-light italic">{{ t('admin.courses.fields.noDocuments') }}</p>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addDoc">{{ t('admin.courses.fields.addDocument') }}</button>
          </section>
        </div>
        <div class="mt-8 pt-6 border-t border-parchment-deep/60 flex items-center justify-end gap-3">
          <button type="button" class="admin-btn admin-btn-ghost" @click="closeEditor">{{ t('admin.courses.close') }}</button>
          <button type="button" class="admin-btn admin-btn-primary" :disabled="saving" @click="save">{{ t('admin.courses.save') }}</button>
        </div>
        <p v-if="savedNotice" role="status" class="mt-3 text-end text-xs text-ink-muted">{{ savedNotice }}</p>
      </div>
    </Transition>
  </div>
</template>
<style scoped>
.admin-icon-remove{display:inline-grid;place-items:center;width:2rem;height:2rem;flex:0 0 2rem;border:1px solid rgb(185 28 28/.35);border-radius:50%;color:rgb(185 28 28);font-size:1.15rem;line-height:1;transition:background-color .2s,border-color .2s}.admin-icon-remove:hover{background:rgb(185 28 28/.08);border-color:rgb(185 28 28/.65)}.admin-remove-corner{position:absolute;top:.75rem;left:.75rem;z-index:1}.admin-file-input{display:block;width:100%;padding:.55rem;border:1px solid rgb(var(--c-ink)/.16);border-radius:.5rem;background:rgb(var(--c-parchment-light)/.75);color:rgb(var(--c-ink-muted));font-size:.78rem}.admin-file-input::file-selector-button{margin-inline-end:.75rem;border:1px solid rgb(var(--c-gold)/.45);border-radius:.35rem;padding:.45rem .75rem;background:rgb(var(--c-gold)/.1);color:rgb(var(--c-ink));cursor:pointer}.admin-file-input:focus-visible{outline:2px solid rgb(var(--c-gold)/.55);outline-offset:2px}
</style>
