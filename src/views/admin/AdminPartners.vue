<script setup>
import { validateSection } from '../../utils/validation.js'
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { partnersApi } from '../../api/content.js'
import { academyApi } from '../../api/academy.js'
import { eventsApi } from '../../api/events.js'
import { productsApi } from '../../api/products.js'
import { resolveApiUrl } from '../../api/client.js'
import DetailFields from '../../components/admin/DetailFields.vue'
import { partnerSchema, emptyDetails } from '../../data/editorSchemas.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { locale } = useI18n()
const fa = computed(() => locale.value === 'fa')
const tr = (en, faText) => fa.value ? faText : en
const partners = ref([])
const courses = ref([])
const memberQuery = ref('')
const members = ref([])
const draft = ref(null)
const activeLanguage = ref('fa')
const busy = ref(false)
const notice = ref('')
const confirmingDelete = ref(null)
const page = ref(1)
const pageSize = 6

const pageCount = computed(() => Math.max(1, Math.ceil(partners.value.length / pageSize)))
const pagedPartners = computed(() => partners.value.slice((page.value - 1) * pageSize, page.value * pageSize))
const revealEditor = () => nextTick(() => document.getElementById('content-editor')?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
const emptyTranslation = (code) => ({ locale: code, name: '', title: '', qualification: '', location: '', affiliation: '', bio: '', details: { ...emptyDetails(partnerSchema), playlists: [] } })
const translation = (code) => draft.value?.translations.find((item) => item.locale === code)
const courseTitle = (course, code) => course.translations?.find((item) => item.locale === code)?.title || course.translations?.find((item) => item.locale === 'en')?.title || course.title || course.slug
const resolveCourseSlug = (item) => {
  if (typeof item === 'string') return courses.value.find((course) => course.slug === item)?.slug || ''
  if (item?.slug) return courses.value.find((course) => course.slug === item.slug)?.slug || item.slug
  const title = item?.title?.trim().toLocaleLowerCase()
  if (!title) return ''
  return courses.value.find((course) => course.translations?.some((entry) => entry.title?.trim().toLocaleLowerCase() === title))?.slug || ''
}
const normalizeDetails = (details = {}) => {
  const blanks = emptyDetails(partnerSchema)
  const normalized = Object.fromEntries(Object.keys(partnerSchema).map((key) => [key, details[key] ?? blanks[key]]))
  const legacyCourses = [...(Array.isArray(details.playlists) ? details.playlists : []), ...(Array.isArray(details.courses) ? details.courses : [])]
  normalized.playlists = [...new Set(legacyCourses.map(resolveCourseSlug).filter(Boolean))].map((slug) => ({ slug }))
  return normalized
}
const normalizeDraft = () => {
  draft.value.translations = ['en', 'fa'].map((code) => {
    const current = draft.value.translations?.find((item) => item.locale === code) || emptyTranslation(code)
    return { ...emptyTranslation(code), ...current, details: normalizeDetails(current.details) }
  })
}
const localizedPartner = (item) => item.translations?.find((entry) => entry.locale === locale.value) || item.translations?.find((entry) => entry.locale === 'en') || item
const selectedCourseSlugs = (code) => (translation(code)?.details?.playlists || []).map((item) => item.slug).filter(Boolean)
const toggleCourse = (slug, checked) => {
  const current = new Set(selectedCourseSlugs(activeLanguage.value))
  checked ? current.add(slug) : current.delete(slug)
  const selected = [...current]
  draft.value.translations.forEach((item) => { item.details.playlists = selected.map((slug) => ({ slug })) })
}
const load = async () => {
  busy.value = true
  const [partnerResponse, courseResponse] = await Promise.allSettled([partnersApi.adminList(), academyApi.adminList()])
  if (partnerResponse.status === 'fulfilled') partners.value = partnerResponse.value.data
  if (courseResponse.status === 'fulfilled') courses.value = courseResponse.value.data
  if (page.value > pageCount.value) page.value = pageCount.value
  const problem = [partnerResponse, courseResponse].find((result) => result.status === 'rejected')
  if (problem) notice.value = problem.reason.message
  busy.value = false
}
const findMembers = async () => {
  try { members.value = (await eventsApi.speakerOptions(memberQuery.value)).data.filter(item => item.user_id) }
  catch (error) { notice.value = error.message }
}
const createPartner = () => { activeLanguage.value = 'fa'; draft.value = { id: null, user_id: null, image_file_id: null, image_url: null, translations: [emptyTranslation('en'), emptyTranslation('fa')] }; revealEditor() }
const editPartner = (item) => { activeLanguage.value = 'fa'; draft.value = JSON.parse(JSON.stringify(item)); normalizeDraft(); revealEditor() }
const payload = () => ({ user_id: draft.value.user_id || null, image_file_id: draft.value.image_file_id || null, translations: draft.value.translations.map((item) => ({ ...item, details: normalizeDetails(item.details) })) })
const save = async () => {
  if (!validateSection(document.getElementById('content-editor'))) return
  busy.value = true
  notice.value = ''
  try {
    const result = draft.value.id ? await partnersApi.update(draft.value.id, payload()) : await partnersApi.create(payload())
    if (!result.data?.approval) {
      draft.value = result.data
      normalizeDraft()
    }
    notice.value = result.data?.approval
      ? tr('Sent to the principal approval queue.', 'درخواست به صف تأیید مدیر اصلی ارسال شد.')
      : tr('Partner saved.', 'پروفایل همکار ذخیره شد.')
    await load()
    revealEditor()
  } catch (error) { notice.value = error.message } finally { busy.value = false }
}
const toggle = async (item) => { const result = await (item.published ? partnersApi.unpublish(item.id) : partnersApi.publish(item.id)); if (result.data?.approval) notice.value = tr('Change sent for approval.', 'تغییر برای تأیید ارسال شد.'); await load() }
const archive = async (item) => { await partnersApi.archive(item.id); confirmingDelete.value = null; if (draft.value?.id === item.id) draft.value = null; await load() }
const uploadImage = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  busy.value = true
  try { const result = await productsApi.upload(file); draft.value.image_file_id = result.data.id; draft.value.image_url = result.data.url } catch (error) { notice.value = error.message } finally { busy.value = false; event.target.value = '' }
}
onMounted(() => { load(); findMembers() })
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div><p class="admin-eyebrow">{{ tr('Directory content', 'محتوای دایرکتوری') }}</p><h2 class="admin-h1 mt-2">{{ tr('Partners', 'همکاران') }}</h2><p class="mt-2 text-sm text-ink-muted">{{ tr('Manage bilingual public partner profiles.', 'پروفایل‌های عمومی دوزبانه همکاران را مدیریت کنید.') }}</p></div>
      <button class="admin-btn admin-btn-primary" @click="createPartner">{{ tr('Add partner', 'افزودن همکار') }}</button>
    </div>
    <div class="admin-card mt-7 p-6 overflow-x-auto">
      <table class="admin-table min-w-[680px]">
        <thead><tr><th>{{ tr('Profile', 'پروفایل') }}</th><th>Slug</th><th>{{ tr('Location', 'موقعیت') }}</th><th>{{ tr('Published', 'انتشار') }}</th><th></th></tr></thead>
        <tbody><tr v-for="item in pagedPartners" :key="item.id"><td><strong>{{ localizedPartner(item).name }}</strong><br><small>{{ localizedPartner(item).title }}</small></td><td dir="ltr">{{ item.slug }}</td><td>{{ localizedPartner(item).location }}</td><td><AdminToggle :model-value="item.published" @update:model-value="toggle(item)" /></td><td><div class="flex items-center justify-end gap-2"><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="editPartner(item)">{{ tr('Edit', 'ویرایش') }}</button><button class="admin-btn admin-btn-danger admin-btn-sm" @click="confirmingDelete === item.id ? archive(item) : confirmingDelete = item.id">{{ confirmingDelete === item.id ? tr('Confirm delete', 'تأیید حذف') : tr('Delete', 'حذف') }}</button></div></td></tr></tbody>
      </table>
      <p v-if="!busy && !partners.length" class="py-8 text-center text-ink-muted">{{ tr('No partner profiles yet.', 'هنوز پروفایلی وجود ندارد.') }}</p>
      <div v-if="partners.length > pageSize" class="mt-5 flex items-center justify-center gap-3 border-t border-parchment-deep pt-5"><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="page === 1" @click="page--">{{ tr('Previous', 'قبلی') }}</button><span class="text-xs text-ink-muted tabular-nums">{{ page }} / {{ pageCount }}</span><button class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="page === pageCount" @click="page++">{{ tr('Next', 'بعدی') }}</button></div>
    </div>

    <section id="content-editor" v-if="draft" class="admin-card mt-7 p-6 md:p-8 space-y-6 scroll-mt-8">
      <div class="flex justify-between gap-4"><h3 class="admin-h2">{{ draft.id ? tr('Edit partner', 'ویرایش همکار') : tr('New partner', 'همکار جدید') }}</h3><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="draft = null">{{ tr('Close', 'بستن') }}</button></div>
      <div class="admin-panel p-5">
        <div class="flex flex-wrap items-center gap-4"><img v-if="draft.image_url" :src="resolveApiUrl(draft.image_url)" class="w-24 h-24 rounded-full object-cover" alt=""><label class="admin-btn admin-btn-ghost cursor-pointer">{{ tr('Upload portrait', 'آپلود تصویر') }}<input type="file" accept="image/png,image/jpeg,image/webp" class="hidden" @change="uploadImage"></label><button v-if="draft.image_file_id" type="button" class="admin-btn admin-btn-danger" @click="draft.image_file_id = null; draft.image_url = null">{{ tr('Remove image', 'حذف تصویر') }}</button></div>
      </div>
      <div class="admin-panel p-5">
        <label class="admin-label">{{ tr('Linked member account (optional)', 'حساب عضو مرتبط (اختیاری)') }}</label>
        <div class="mt-2 flex gap-2"><input v-model="memberQuery" class="admin-input" :placeholder="tr('Search members by name','جست‌وجوی عضو با نام')" @keydown.enter.prevent="findMembers"><button type="button" class="admin-btn admin-btn-ghost" @click="findMembers">{{ tr('Search','جست‌وجو') }}</button></div>
        <select v-model="draft.user_id" class="admin-select mt-3"><option :value="null">{{ tr('No linked account','بدون حساب مرتبط') }}</option><option v-if="draft.user_id && !members.some(item => item.user_id === draft.user_id)" :value="draft.user_id">{{ tr('Currently linked member','عضو مرتبط فعلی') }}</option><option v-for="member in members" :key="member.user_id" :value="member.user_id">{{ member.name }}</option></select>
        <p class="mt-2 text-xs text-ink-muted">{{ tr('Link the same account used for this person’s courses, comments and live events.', 'همان حسابی را انتخاب کنید که برای دوره‌ها، دیدگاه‌ها و رویدادهای زندهٔ این فرد استفاده می‌شود.') }}</p>
      </div>
      <div class="flex gap-2 border-b border-parchment-deep" role="tablist">
        <button type="button" class="px-5 py-3 text-sm border-b-2 transition-colors" :class="activeLanguage === 'fa' ? 'border-gold text-gold-dark' : 'border-transparent text-ink-muted'" @click="activeLanguage = 'fa'">{{ tr('Persian information', 'اطلاعات فارسی') }}</button>
        <button type="button" class="px-5 py-3 text-sm border-b-2 transition-colors" :class="activeLanguage === 'en' ? 'border-gold text-gold-dark' : 'border-transparent text-ink-muted'" @click="activeLanguage = 'en'">{{ tr('English information', 'اطلاعات انگلیسی') }}</button>
      </div>
      <div v-for="code in ['fa', 'en']" v-show="activeLanguage === code" :key="code" class="admin-panel p-5 space-y-5" :dir="code === 'fa' ? 'rtl' : 'ltr'">
        <div class="grid md:grid-cols-2 gap-4">
          <label><span class="admin-label">{{ tr('Name', 'نام') }}</span><input required v-model="translation(code).name" class="admin-input" :placeholder="tr('Enter name', 'نام را وارد کنید')"></label>
          <label><span class="admin-label">{{ tr('Title', 'سمت') }}</span><input required v-model="translation(code).title" class="admin-input" :placeholder="tr('Enter title', 'سمت را وارد کنید')"></label>
          <label><span class="admin-label">{{ tr('Qualification', 'مدرک') }}</span><input v-model="translation(code).qualification" class="admin-input" :placeholder="tr('Enter qualification', 'مدرک را وارد کنید')"></label>
          <label><span class="admin-label">{{ tr('Location', 'موقعیت') }}</span><input v-model="translation(code).location" class="admin-input" :placeholder="tr('Enter location', 'موقعیت را وارد کنید')"></label>
          <label class="md:col-span-2"><span class="admin-label">{{ tr('Affiliation', 'سازمان') }}</span><input v-model="translation(code).affiliation" class="admin-input" :placeholder="tr('Enter affiliation', 'سازمان را وارد کنید')"></label>
        </div>
        <label class="block"><span class="admin-label">{{ tr('Biography', 'زندگی‌نامه') }}</span><textarea required v-model="translation(code).bio" rows="5" class="admin-textarea" :placeholder="tr('Enter biography', 'زندگی‌نامه را وارد کنید')"></textarea></label>
        <DetailFields v-model="translation(code).details" :schema="partnerSchema" :language="locale" schema-only />
        <fieldset class="block"><legend class="admin-label">{{ tr('Course', 'دوره') }}</legend><div class="admin-panel divide-y divide-parchment-deep overflow-hidden"><label v-for="course in courses" :key="course.id" class="flex cursor-pointer items-center gap-3 px-4 py-3 hover:bg-gold/5"><input type="checkbox" class="accent-gold" :checked="selectedCourseSlugs(code).includes(course.slug)" @change="toggleCourse(course.slug, $event.target.checked)"><span class="min-w-0 flex-1 text-sm text-ink">{{ courseTitle(course, locale) }}</span><small class="shrink-0 text-ink-muted">{{ course.lesson_count || 0 }} {{ tr('sessions', 'جلسه') }}</small></label><p v-if="!courses.length" class="px-4 py-5 text-sm text-ink-muted">{{ tr('No courses are available yet.', 'هنوز دوره‌ای ایجاد نشده است.') }}</p></div></fieldset>
      </div>
      <div class="flex gap-3"><button class="admin-btn admin-btn-primary" :disabled="busy" @click="save">{{ tr('Save', 'ذخیره') }}</button></div>
      <p v-if="notice" role="status" class="mt-3 text-sm text-ink-muted">{{ notice }}</p>
    </section>
  </div>
</template>
