import { ref } from 'vue'
import { courseMedia } from '../data/courseMedia.js'

/**
 * Course Management store (Admin Panel, spec §9).
 *
 * A mock, in-memory editable mirror of every Academy course. It seeds once from
 * the stable course identities in `courseMedia` (whose order matches
 * `academy.courses[]`) so the admin table lines up with the public catalogue,
 * then lets the admin edit metadata, pricing, media URLs, downloadable resources
 * and imagery — all client-side, no backend. Edits persist for the session via
 * the same shared-singleton pattern the rest of the app uses.
 *
 * The imagery `slug` is the course's stable identity: the light/dark thumbnail
 * and header background are resolved from it automatically (see
 * courseBackgrounds.js), so re-assigning a slug re-skins the course everywhere.
 */

let uid = 0
const nextId = () => `d${++uid}`

const doc = (name, type, url) => ({ id: nextId(), name, type, url })

// Per-slug seed for the fields that don't live in courseMedia. Mirrors the
// English academy copy closely enough to be recognisable in the table without
// coupling the admin store to i18n reactivity.
const SEED = {
  'clinical-neurology': {
    title: 'Introduction to Clinical Neurology',
    instructor: 'Prof. Ali Shalash',
    level: 'Intermediate',
    duration: '7 lessons · 4h 30m',
    tier: 'free',
    field: 'clinicalNeurology',
    category: 'Clinical',
    price: 0,
    videoUrl: '/course-media/Clinical/Cranial Nerves Examination-1.mp4',
    documents: [
      doc('Neurological Exam Checklist', 'pdf', '/resources/neuro-exam-checklist.pdf'),
      doc('Localisation Reference Chart', 'pdf', '/resources/localisation-chart.pdf'),
    ],
  },
  neuroscience: {
    title: 'Foundations of Neuroscience',
    instructor: 'Dr. Sara Nourani',
    level: 'Beginner',
    duration: '9 lessons · 5h 10m',
    tier: 'premium',
    field: 'neuroscience',
    category: 'Basic Science',
    price: 129,
    videoUrl: '',
    documents: [doc('Action Potential Study Notes', 'pdf', '/resources/action-potential.pdf')],
  },
  neuroimaging: {
    title: 'Principles of Neuroimaging',
    instructor: 'Dr. Reza Kamali',
    level: 'Advanced',
    duration: '8 lessons · 6h 00m',
    tier: 'premium',
    field: 'neuroimaging',
    category: 'Radiology',
    price: 149,
    videoUrl: '',
    documents: [
      doc('MRI Sequence Cheat Sheet', 'pdf', '/resources/mri-sequences.pdf'),
      doc('Stroke Imaging Protocol', 'slides', '/resources/stroke-protocol.pptx'),
    ],
  },
  'brain-anatomy': {
    title: 'Neuroanatomy of the Brain',
    instructor: 'Prof. Mona Ebrahimi',
    level: 'Intermediate',
    duration: '6 lessons · 3h 45m',
    tier: 'free',
    field: 'brainAnatomy',
    category: 'Anatomy',
    price: 0,
    videoUrl: '/course-media/Anatomy/Nervous system anatomy introduction-1.mp4',
    documents: [doc('Brain Atlas Plates', 'pdf', '/resources/brain-atlas.pdf')],
  },
  'neurocritical-care': {
    title: 'Neurocritical Care Essentials',
    instructor: 'Dr. Kaveh Rostami',
    level: 'Advanced',
    duration: '10 lessons · 7h 20m',
    tier: 'premium',
    field: 'neurocriticalCare',
    category: 'Critical Care',
    price: 179,
    videoUrl: '',
    documents: [doc('ICP Management Protocol', 'pdf', '/resources/icp-protocol.pdf')],
  },
  neurosurgery: {
    title: 'Operative Neurosurgery Foundations',
    instructor: 'Prof. Dariush Alavi',
    level: 'Advanced',
    duration: '12 lessons · 9h 00m',
    tier: 'premium',
    field: 'neurosurgery',
    category: 'Surgery',
    price: 199,
    videoUrl: '',
    documents: [doc('Operative Corridors Guide', 'slides', '/resources/operative-corridors.pptx')],
  },
}

const build = () =>
  courseMedia.map((m) => {
    const s = SEED[m.slug] || {}
    return {
      id: m.slug,
      slug: m.slug,
      title: s.title || m.slug,
      instructor: s.instructor || '',
      level: s.level || 'Intermediate',
      duration: s.duration || '',
      desc: '',
      tier: s.tier || 'free',
      field: s.field || 'clinicalNeurology',
      category: s.category || 'Clinical',
      price: s.price ?? 0,
      published: true,
      progressReset: false,
      videoUrl: s.videoUrl || '',
      documents: (s.documents || []).map((d) => ({ ...d })),
    }
  })

// Shared singleton — the table and the editor mutate the same reactive list.
const courses = ref(build())

// Every slug that ships a light/dark asset pair (see src/assets/*). Offered in
// the imagery picker so re-skinning a course is a constrained, valid choice.
const IMAGERY_SLUGS = courseMedia.map((m) => m.slug)

const DOC_TYPES = ['pdf', 'slides', 'protocol', 'dataset', 'link']

export function useCourseAdmin() {
  const findById = (id) => courses.value.find((c) => c.id === id) || null

  /** Persist edits from a working copy back onto the live course. */
  const saveCourse = (draft) => {
    const idx = courses.value.findIndex((c) => c.id === draft.id)
    if (idx === -1) return
    courses.value[idx] = { ...draft, documents: draft.documents.map((d) => ({ ...d })) }
  }

  const togglePublished = (id) => {
    const c = findById(id)
    if (c) c.published = !c.published
  }

  const addCourse = () => {
    const slug = IMAGERY_SLUGS[0]
    const c = {
      id: `new-${nextId()}`,
      slug,
      title: 'Untitled Course',
      instructor: '',
      level: 'Intermediate',
      duration: '',
      desc: '',
      tier: 'free',
      field: 'clinicalNeurology',
      category: 'Clinical',
      price: 0,
      published: false,
      progressReset: false,
      videoUrl: '',
      documents: [],
    }
    courses.value.unshift(c)
    return c
  }

  const removeCourse = (id) => {
    courses.value = courses.value.filter((c) => c.id !== id)
  }

  /** A deep-enough clone for the editor to mutate without touching the table. */
  const draftFrom = (course) => ({
    ...course,
    documents: course.documents.map((d) => ({ ...d })),
  })

  const newDocument = () => doc('New resource', 'pdf', '')

  return {
    courses,
    imagerySlugs: IMAGERY_SLUGS,
    docTypes: DOC_TYPES,
    findById,
    saveCourse,
    togglePublished,
    addCourse,
    removeCourse,
    draftFrom,
    newDocument,
  }
}
