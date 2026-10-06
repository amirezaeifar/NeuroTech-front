import { ref } from 'vue'
import { academyApi } from '../api/academy.js'
import { courseMedia } from '../data/courseMedia.js'

let uid = 0
const nextId = () => `draft-${++uid}`
const courses = ref([])
const loading = ref(false)
const error = ref('')
let initialized = false

const imagerySlugs = courseMedia.map((item) => item.slug)
const docTypes = ['pdf', 'document', 'slides', 'spreadsheet', 'archive', 'image', 'video', 'audio', 'protocol', 'dataset']

const mapCourse = (course) => {
  const english = course.translations?.find((item) => item.locale === 'en') || {}
  const persian = course.translations?.find((item) => item.locale === 'fa') || {}
  const usd = course.prices?.find((item) => item.currency === 'USD')
  const irr = course.prices?.find((item) => item.currency === 'IRR')
  return {
    id: course.id,
    slug: course.slug,
    title: english.title || course.title,
    instructor: english.instructor_name || course.instructor_name || '',
    instructorPartnerId: course.instructor_partner_id || null,
    instructorPartnerSlug: course.instructor_partner_slug || null,
    level: course.level,
    duration: english.duration_label || course.duration_label || '',
    desc: english.description || course.description || '',
    summary: english.summary || '',
    faSummary: persian.summary || '',
    faTitle: persian.title || '',
    faInstructor: persian.instructor_name || '',
    faDuration: persian.duration_label || '',
    faDesc: persian.description || '',
    tier: course.tier,
    field: course.field,
    category: course.field,
    price: usd ? usd.amount_minor / 100 : 0,
    irrPrice: irr ? irr.amount_minor : 0,
    published: Boolean(course.published),
    playlistId: course.youtube_playlist_id || '',
    documents: (course.content?.resources || []).map((item) => ({
      id: nextId(),
      name: item.name,
      type: item.kind,
      url: item.external_url || item.storage_path || '',
    })),
    content: course.content || { sections: [], outcomes: [], media: [], resources: [] },
    translations: course.translations || [],
    prices: course.prices || [],
    _published: Boolean(course.published),
  }
}

const loadCourses = async (force = false) => {
  if (initialized && !force) return
  loading.value = true
  error.value = ''
  try {
    courses.value = (await academyApi.adminList()).data.map(mapCourse)
    initialized = true
  } catch (problem) {
    error.value = problem.message
  } finally {
    loading.value = false
  }
}

const mutationPayload = (draft) => {
  const english = {
    locale: 'en',
    title: draft.title,
    description: draft.desc || draft.title,
    summary: draft.summary || '',
    instructor_name: draft.instructor,
    duration_label: draft.duration,
  }
  const persian = {
    locale: 'fa',
    title: draft.faTitle,
    description: draft.faDesc || draft.faTitle,
    summary: draft.faSummary || '',
    instructor_name: draft.faInstructor,
    duration_label: draft.faDuration,
  }
  const translations = [english, persian]
  const prices = draft.tier === 'premium'
    ? [
        { currency: 'IRR', amount_minor: Math.round(Number(draft.irrPrice || 0)) },
        { currency: 'USD', amount_minor: Math.round(Number(draft.price || 0) * 100) },
      ]
    : []
  return {
    tier: draft.tier,
    field: draft.field,
    level: String(draft.level).toLowerCase(),
    youtube_playlist_id: draft.playlistId.trim() || null,
    instructor_partner_id: draft.instructorPartnerId || null,
    translations,
    prices,
  }
}

const sourceFields = (url) => String(url).startsWith('http://') || String(url).startsWith('https://')
  ? { external_url: url, storage_path: null }
  : { storage_path: url, external_url: null }

const contentPayload = (draft) => {
  const retainedMedia = (draft.content?.media || [])
    .filter((item) => item.kind !== 'video')
    .map(({ kind, position, locale, mime_type, storage_path, external_url }) => ({
      kind,
      position,
      locale,
      mime_type,
      storage_path,
      external_url,
    }))
  return {
    sections: (draft.content?.sections || []).map((section) => ({
      position: section.position,
      translations: section.translations.map(({ locale, title }) => ({ locale, title })),
      lessons: section.lessons.map((lesson) => ({
        position: lesson.position,
        duration_seconds: lesson.duration_seconds,
        video_provider: lesson.video_provider,
        video_reference: lesson.video_reference,
        free_preview: Boolean(lesson.free_preview),
        translations: lesson.translations.map(({ locale, title }) => ({ locale, title })),
      })),
    })),
    outcomes: (draft.content?.outcomes || []).map(({ locale, position, text }) => ({
      locale,
      position,
      text,
    })),
    resources: draft.documents
      .filter((document) => document.name.trim() && document.url.trim())
      .map((document) => ({
        name: document.name,
        kind: document.type,
        ...sourceFields(document.url),
      })),
    media: retainedMedia,
  }
}

export function useCourseAdmin() {
  loadCourses()

  const findById = (id) => courses.value.find((course) => course.id === id) || null
  const saveCourse = async (draft) => {
    error.value = ''
    let unpublishedForMutation = false
    let approvalPending = false
    try {
      const isNew = String(draft.id).startsWith('draft-')
      const payload = mutationPayload(draft)
      const content = contentPayload(draft)
      const contentChanged = isNew || JSON.stringify(content) !== draft._contentSnapshot
      if (!isNew && draft._published && (!draft.published || contentChanged)) {
        const unpublishResponse = await academyApi.adminUnpublish(draft.id)
        approvalPending ||= Boolean(unpublishResponse.data?.approval)
        unpublishedForMutation = true
      }
      const response = isNew
        ? await academyApi.adminCreate({
          ...payload,
          slug: draft.slug,
          content,
          published: draft.published,
        })
        : await academyApi.adminUpdate(draft.id, payload)
      approvalPending ||= Boolean(response.data?.approval)
      if (isNew && response.data?.approval) {
        await loadCourses(true)
        return { _approvalPending: true }
      }
      const id = isNew ? response.data.id : draft.id
      if (isNew) draft.id = id
      if (!isNew && contentChanged) {
        const contentResponse = await academyApi.adminReplaceContent(id, content)
        approvalPending ||= Boolean(contentResponse.data?.approval)
      }
      if (draft.published && (!draft._published || contentChanged)) {
        const publishResponse = await academyApi.adminPublish(id)
        approvalPending ||= Boolean(publishResponse.data?.approval)
      }
      await loadCourses(true)
      if (approvalPending) return { _approvalPending: true }
      return findById(id)
    } catch (problem) {
      if (unpublishedForMutation) {
        await academyApi.adminPublish(draft.id).catch(() => {})
      }
      error.value = problem.message
      throw problem
    }
  }

  const togglePublished = async (id) => {
    const course = findById(id)
    if (!course) return
    try {
      if (course.published) await academyApi.adminUnpublish(id)
      else await academyApi.adminPublish(id)
      await loadCourses(true)
    } catch (problem) {
      error.value = problem.message
    }
  }

  const addCourse = () => {
    const draft = {
      id: nextId(),
      slug: `untitled-course-${Date.now()}`,
      title: '',
      instructor: '',
      instructorPartnerId: null,
      instructorPartnerSlug: null,
      level: 'beginner',
      duration: '',
      summary: '',
      desc: '',
      faTitle: '',
      faInstructor: '',
      faDuration: '',
      faDesc: '',
      faSummary: '',
      tier: 'free',
      field: 'clinicalNeurology',
      category: 'Clinical',
      price: 0,
      irrPrice: 0,
      published: false,
      _published: false,
      playlistId: '',
      documents: [newDocument()],
      translations: [],
      prices: [],
      content: { sections: [], outcomes: [], media: [], resources: [] },
    }
    return draft
  }

  const removeCourse = async (id) => {
    if (String(id).startsWith('draft-')) {
      courses.value = courses.value.filter((course) => course.id !== id)
      return
    }
    await academyApi.adminArchive(id)
    await loadCourses(true)
  }

  const reorderCourse = async (id, direction) => {
    const persisted = courses.value.filter((course) => !String(course.id).startsWith('draft-'))
    const index = persisted.findIndex((course) => course.id === id)
    const target = index + direction
    if (index < 0 || target < 0 || target >= persisted.length) return
    ;[persisted[index], persisted[target]] = [persisted[target], persisted[index]]
    try {
      await academyApi.adminReorder(persisted.map((course) => course.id))
      await loadCourses(true)
    } catch (problem) {
      error.value = problem.message
      await loadCourses(true)
    }
  }

  const draftFrom = (course) => {
    const draft = {
      ...course,
      documents: course.documents.length
        ? course.documents.map((document) => ({ ...document }))
        : [newDocument()],
      translations: course.translations.map((translation) => ({ ...translation })),
      prices: course.prices.map((price) => ({ ...price })),
      content: JSON.parse(JSON.stringify(course.content)),
    }
    draft._contentSnapshot = JSON.stringify(contentPayload(draft))
    return draft
  }

  const newDocument = () => ({ id: nextId(), name: '', type: 'pdf', url: '' })
  const newLesson = (position) => ({
    id: nextId(),
    position,
    duration_seconds: 0,
    video_provider: 'youtube',
    video_reference: '',
    free_preview: false,
    translations: [
      { locale: 'en', title: '' },
      { locale: 'fa', title: '' },
    ],
  })
  const newSection = (position) => ({
    id: nextId(),
    position,
    translations: [
      { locale: 'en', title: '' },
      { locale: 'fa', title: '' },
    ],
    lessons: [newLesson(1)],
  })

  return {
    courses,
    loading,
    error,
    imagerySlugs,
    docTypes,
    loadCourses,
    saveCourse,
    togglePublished,
    addCourse,
    removeCourse,
    reorderCourse,
    draftFrom,
    newDocument,
    newLesson,
    newSection,
  }
}
