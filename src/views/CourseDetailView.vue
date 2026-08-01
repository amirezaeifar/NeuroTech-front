<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LuxeCard from '../components/LuxeCard.vue'
import SectionEyebrow from '../components/SectionEyebrow.vue'
import StratumStack from '../components/StratumStack.vue'
import CoursePlayer from '../components/CoursePlayer.vue'
import { courseCode, sectionLetter } from '../utils/catalog.js'
import { courseMediaAt } from '../data/courseMedia.js'
import { courseDiscussionsAt } from '../data/courseDiscussions.js'
import { useReveal } from '../composables/useReveal.js'

const { t, tm, locale } = useI18n()
const route = useRoute()
const router = useRouter()

// Writing direction — drives native RTL chevron glyphs (no scaleX mirroring).
const isRtl = computed(() => locale.value === 'fa')
// Chevron pointing toward the carousel's start / end edge in the current
// direction. In LTR the start edge is the left; in RTL it is the right.
const chevronToStart = computed(() => (isRtl.value ? 'M9 6l6 6-6 6' : 'M15 6l-6 6 6 6'))
const chevronToEnd = computed(() => (isRtl.value ? 'M15 6l-6 6 6 6' : 'M9 6l6 6-6 6'))

const courses = computed(() => tm('academy.courses'))
const courseIndex = computed(() => Number(route.params.id))
const course = computed(() => courses.value[courseIndex.value])
const isFree = computed(() => course.value?.tier === 'free')

// Derive lesson count from duration string.
const lessonCount = computed(() => {
  const match = (course.value?.duration || '').match(/(\d+)\s*lesson/i)
  return match ? Number(match[1]) : 6
})

// Per-course video lesson lists (full curriculum, neurology education).
// Length matches the lesson count in each course's `duration` string, and the
// order matches academy.courses[] / src/data/courseMedia.js.
const videoTitleSets = [
  // 0: Clinical Neurology (16 lessons)
  [
    'The Neurological History',
    'Cranial Nerve Examination',
    'Motor & Sensory Examination',
    'Reflexes, Coordination & Gait',
    'Principles of Lesion Localization',
    'Localizing the Common Syndromes',
    'Approach to the Headache Patient',
    'Migraine & Tension-Type Headache',
    'Secondary & Red-Flag Headaches',
    'Seizure Semiology & Classification',
    'Epilepsy Diagnosis & the Role of EEG',
    'Principles of Antiseizure Therapy',
    'Parkinsonism & Tremor',
    'Hyperkinetic Movement Disorders',
    'Dementia & Neurodegenerative Disease',
    'Integrated Clinical Case Discussions',
  ],
  // 1: Neuroscience (14 lessons)
  [
    'The Neuron: Structure & Function',
    'Glial Cells & the Neural Environment',
    'The Resting Membrane Potential',
    'The Action Potential',
    'Synaptic Structure & Neurotransmitter Release',
    'Receptors & Postsynaptic Signalling',
    'Excitatory & Inhibitory Neurotransmission',
    'Mechanisms of Neuroplasticity',
    'Long-Term Potentiation & Depression',
    'Principles of Neural Networks',
    'Sensory & Motor Network Organisation',
    'Functional Specialisation of the Cortex',
    'Attention, Memory & Executive Systems',
    'Language & Higher Cognitive Function',
  ],
  // 2: Neuroimaging (14 lessons)
  [
    'Principles of CT Image Formation',
    'Systematic CT Head Interpretation',
    'CT in Acute Stroke & Haemorrhage',
    'MRI Physics for Clinicians',
    'Core MRI Sequences: T1, T2 & FLAIR',
    'Contrast Enhancement & Its Patterns',
    'Diffusion-Weighted Imaging & the ADC Map',
    'Diffusion in Stroke & Beyond',
    'CT & MR Angiography',
    'Venous Imaging & Perfusion',
    'Principles of Functional MRI',
    'Spectroscopy & Advanced Techniques',
    'Common Pitfalls & Artefacts',
    'Integrated Imaging Case Review',
  ],
  // 3: Brain Anatomy (18 lessons)
  [
    'Surface Anatomy of the Cerebrum',
    'The Frontal Lobe',
    'The Parietal Lobe',
    'The Temporal Lobe',
    'The Occipital & Limbic Cortex',
    'Organisation of the Brainstem',
    'The Midbrain',
    'The Pons',
    'The Medulla Oblongata',
    'The Thalamus',
    'The Hypothalamus & Epithalamus',
    'Basal Ganglia: Structure',
    'Basal Ganglia: Circuitry',
    'Cerebellar Anatomy',
    'Cerebellar Functional Divisions',
    'Association & Commissural Fibres',
    'Projection Fibres & the Internal Capsule',
    'Clinical Neuroanatomy Review',
  ],
  // 4: Neurocritical Care (12 lessons)
  [
    'The Neurocritical Care Unit',
    'Multimodal Neuromonitoring',
    'ICP Physiology & Monitoring',
    'Managing Raised Intracranial Pressure',
    'Acute Ischaemic Stroke in the ICU',
    'Intracerebral & Subarachnoid Haemorrhage',
    'Status Epilepticus',
    'Refractory Seizure Emergencies',
    'Traumatic Brain Injury',
    'Hypoxic-Ischaemic Brain Injury',
    'Brain Death & Prognostication',
    'Neurocritical Decision-Making',
  ],
  // 5: Neurosurgery (16 lessons)
  [
    'Principles of Neurosurgical Practice',
    'Operative Surgical Anatomy',
    'Patient Positioning & Planning',
    'The Craniotomy',
    'Supratentorial Approaches',
    'Skull Base & Posterior Fossa Approaches',
    'Frameless Neuronavigation',
    'Intra-operative Imaging',
    'Intra-operative Neuromonitoring',
    'Principles of Tumour Resection',
    'Gliomas & Metastases',
    'Cerebral Aneurysm Surgery',
    'Arteriovenous Malformations',
    'Functional Neurosurgery & DBS',
    'Spinal Neurosurgery Fundamentals',
    'Peri-operative Complication Management',
  ],
]

// Per-course syllabus (high-level reference sections shown in the sidebar).
const moduleSets = [
  ['Neurological Examination', 'Localization Principles', 'Headache Disorders', 'Epilepsy', 'Movement Disorders', 'Neurodegenerative Diseases', 'Clinical Case Discussions'],
  ['Cellular Neuroscience', 'Synaptic Transmission', 'Neuroplasticity', 'Neural Networks', 'Brain Function', 'Cognitive Systems'],
  ['CT Interpretation', 'MRI Fundamentals', 'Diffusion Imaging', 'Vascular Imaging', 'Functional Imaging', 'Case Review'],
  ['Cerebral Lobes', 'Brainstem', 'Diencephalon', 'Basal Ganglia', 'Cerebellum', 'White Matter Pathways'],
  ['ICU Monitoring', 'Intracranial Pressure', 'Stroke Management', 'Seizure Emergencies', 'Brain Injury', 'Neurocritical Decision Making'],
  ['Surgical Anatomy', 'Cranial Approaches', 'Navigation Systems', 'Tumor Surgery', 'Vascular Neurosurgery', 'Functional Neurosurgery'],
]

// Course descriptions (academic, CME-style). Order matches academy.courses[].
// Replace with the academy's own course copy as needed.
const longDescriptions = [
  // 0: Clinical Neurology
  `Clinical Neurology develops the structured reasoning that distinguishes confident neurological practice: the disciplined progression from history and examination to anatomical localisation and a prioritised differential diagnosis. The course is built around the bedside and revisits the neurological examination not as a checklist but as a hypothesis-driven investigation.\n\nThe curriculum then works through the disorders a neurologist meets most often — headache, epilepsy, movement disorders and the neurodegenerative diseases — emphasising pattern recognition, appropriate investigation and current principles of management. A closing block of integrated case discussions consolidates the method, asking the learner to localise, differentiate and plan as they would in clinic.\n\nThe course is intended for neurology residents, medical students and clinicians seeking a systematic foundation in clinical neurological decision-making.`,

  // 1: Neuroscience
  `Neuroscience provides the mechanistic foundation on which clinical neurology rests. Beginning at the level of the single neuron, the course establishes the cellular and electrical principles of neural signalling before advancing to synaptic transmission and the neurotransmitter systems that are the targets of much of modern therapeutics.\n\nLater modules move from cell to circuit, examining neuroplasticity, the organisation of neural networks, and the cognitive systems — attention, memory, language and executive function — that emerge from them. Each concept is linked to its clinical correlate so that mechanism continually informs practice.\n\nThe course suits students and clinicians who want a rigorous, concept-led grounding in cellular and systems neuroscience.`,

  // 2: Neuroimaging
  `Neuroimaging teaches a systematic, transferable approach to interpreting the studies that now underpin almost every neurological decision. The course begins with the physical principles of CT and MRI, to the depth a clinician requires, then builds disciplined search patterns for reading the head CT and the core MRI sequences.\n\nDedicated modules address the techniques that most often determine management — diffusion imaging in acute stroke, CT and MR angiography in vascular disease, and the principles of functional imaging — before a concluding case-based review. Throughout, emphasis falls on recognising critical findings and avoiding common interpretive pitfalls.\n\nIt is designed for trainees in neurology, emergency medicine and radiology who wish to read studies with confidence.`,

  // 3: Brain Anatomy
  `Brain Anatomy presents functional neuroanatomy as the working language of clinical neurology, with every structure tied to its function and to the deficit produced when it fails. The course is organised regionally, progressing from the cerebral lobes through the brainstem, diencephalon, basal ganglia and cerebellum.\n\nA final block traces the major white-matter pathways that connect these regions into functional systems, and a clinical review relates the anatomy directly to examination findings and lesion localisation.\n\nThe detailed, region-by-region structure makes the course suitable both as a first systematic course in neuroanatomy and as a focused revision resource ahead of postgraduate examinations.`,

  // 4: Neurocritical Care
  `Neurocritical Care addresses the management of patients with life-threatening neurological illness, where decisions are made in minutes and physiological monitoring guides every intervention. The course opens with the organisation of the neurocritical care unit and the principles of multimodal neuromonitoring.\n\nSubsequent modules cover the conditions that define the specialty — raised intracranial pressure, acute stroke, status epilepticus, and traumatic and hypoxic-ischaemic brain injury — each presented with current, protocol-driven management. A concluding module on neurocritical decision-making, including prognostication, draws the threads together.\n\nThe course is aimed at neurology and intensive-care trainees and the wider neuro-ICU team.`,

  // 5: Neurosurgery
  `Neurosurgery introduces the principles, anatomy and core procedures of the specialty for surgical trainees and for the clinicians who work alongside the operating team. The early modules establish safe operative practice and the surgical anatomy of the corridors through which the brain and spine are approached.\n\nThe course then covers the cranial approaches, image-guided navigation and intra-operative monitoring that define modern surgery, before surveying the major subspecialties: tumour, vascular and functional neurosurgery, together with the fundamentals of spinal surgery and peri-operative complication management.\n\nThe emphasis throughout is on sound operative reasoning rather than technique in isolation.`,
]

const courseDesc = computed(() => longDescriptions[courseIndex.value] || course.value?.desc || '')

// Replaceable video embeds, cover image + learning outcomes (courseMedia.js).
const media = computed(() => courseMediaAt(courseIndex.value))
const cover = computed(() => media.value?.cover || '')
// Cinematic header background (course_background art); falls back to the cover.
const headerBg = computed(() => media.value?.headerBg || media.value?.cover || '')
const outcomes = computed(() => media.value?.outcomes || [])
// Per-course discussion thread (see src/data/courseDiscussions.js).
const discussions = computed(() => courseDiscussionsAt(courseIndex.value))
// The course playlist fed to the in-house player: clean lesson titles paired
// with internal resource ids (cycled, since the demo id pool is shorter than
// the lesson list — drop the real ids into courseMedia.js for production).
const playlist = computed(() => {
  const ids = media.value?.videoIds || []
  const titles = videoTitleSets[courseIndex.value] || []
  return Array.from({ length: lessonCount.value }, (_, i) => ({
    title: titles[i] || `Lesson ${i + 1}`,
    id: ids.length ? ids[i % ids.length] : '',
  }))
})

// Get video lesson titles for a given course
const videoLessons = computed(() => {
  const titles = videoTitleSets[courseIndex.value] || []
  return Array.from({ length: lessonCount.value }, (_, i) => ({
    index: i + 1,
    title: titles[i] ? `${t('academy.courseDetail.lesson')} ${i + 1}: ${titles[i]}` : `${t('academy.courseDetail.lesson')} ${String(i + 1).padStart(2, '0')}`,
  }))
})

// Syllabus modules — the course's high-level reference sections. These are
// independent of the (larger) lesson count: the syllabus lists topics, the
// "Course Videos" list enumerates the individual lessons.
const modules = computed(() =>
  (moduleSets[courseIndex.value] || []).map((name, i) => ({ index: i + 1, name })))

// Stable catalog code for this course (e.g. "CLN-101").
const code = computed(() => courseCode(courses.value, courseIndex.value))

// How many syllabus topics read as "done", mapped from lesson-level progress.
const topicsDone = computed(() => {
  const total = modules.value.length
  if (!total || !lessonCount.value) return 0
  return Math.round((completed.value / lessonCount.value) * total)
})

// Strata for the syllabus: modules as independent reference sections (A, B, C…)
// rather than a numbered path. State (done / current) is derived here.
const strata = computed(() => modules.value.map((m, i) => ({
  index: m.index,
  ref: sectionLetter(i),
  name: m.name,
  done: m.index <= topicsDone.value,
  current: m.index === topicsDone.value + 1 && topicsDone.value < modules.value.length,
})))

// Mock progress
const completed = computed(() => (isFree.value ? Math.min(2, lessonCount.value) : 0))
const progressPct = computed(() => Math.round((completed.value / Math.max(lessonCount.value, 1)) * 100))

// Premium gating: the player stays unrendered for premium courses until the
// user has paid. There is NO instant unlock — purchase is confirmed only by
// returning from a completed checkout with ?purchased=true on the URL (mocking
// a real post-payment redirect). Free courses always show the player.
const isPurchased = computed(() => route.query.purchased === 'true')
const showPlayer = computed(() => isFree.value || isPurchased.value)

// "Subscribe" routes straight to the Checkout flow — it no longer unlocks the
// player in place. The course index is carried through so Checkout can send the
// user back here as ?purchased=true on success.
const goToCheckout = () => {
  router.push({ path: '/checkout', query: { course: courseIndex.value } })
}

const playing = ref(isFree.value ? 1 : null)
// Dismissible post-purchase banner (sits below the hero). Re-shown whenever a
// fresh purchase is confirmed.
const showUnlocked = ref(true)
watch(isPurchased, (v) => { if (v) showUnlocked.value = true })
// When the user lands back with the purchase confirmed, auto-select lesson 1.
watch(isPurchased, (v) => { if (v && playing.value === null) playing.value = 1 }, { immediate: true })
const playLesson = (n) => { if (showPlayer.value) playing.value = n }

// Every other course in the catalogue feeds the "Browse the Library" carousel.
const related = computed(() => courses.value
  .map((c, i) => ({ ...c, i }))
  .filter((c) => c.i !== courseIndex.value))

// ── Browse-the-Library carousel ──────────────────────────────────────────────
// Shows `perView` cards (3 on desktop, 1 on mobile) and slides one card per
// arrow click along the X-axis. The track itself stays LTR so the prev/next
// direction is consistent across locales.
const carouselIndex = ref(0)
const perView = ref(3)
const maxIndex = computed(() => Math.max(0, related.value.length - perView.value))
const canPrev = computed(() => carouselIndex.value > 0)
const canNext = computed(() => carouselIndex.value < maxIndex.value)
const slidePrev = () => { if (canPrev.value) carouselIndex.value-- }
const slideNext = () => { if (canNext.value) carouselIndex.value++ }
const trackStyle = computed(() => ({
  transform: `translateX(-${(carouselIndex.value * 100) / perView.value}%)`,
}))
const slideStyle = computed(() => ({ flex: `0 0 ${100 / perView.value}%` }))

let mq = null
const applyPerView = () => {
  perView.value = mq && mq.matches ? 3 : 1
  if (carouselIndex.value > maxIndex.value) carouselIndex.value = maxIndex.value
}
onMounted(() => {
  mq = window.matchMedia('(min-width: 768px)')
  applyPerView()
  mq.addEventListener('change', applyPerView)
})
onUnmounted(() => { if (mq) mq.removeEventListener('change', applyPerView) })

// Thumbnail gradients for the library preview cards (warm parchment/gold tones)
const thumbGradients = [
  'linear-gradient(135deg, #3a342a 0%, #1c1915 100%)',
  'linear-gradient(135deg, #4a3f24 0%, #2a2418 100%)',
  'linear-gradient(135deg, #2e2a22 0%, #14110d 100%)',
  'linear-gradient(135deg, #463b22 0%, #221d12 100%)',
  'linear-gradient(135deg, #353026 0%, #1a1610 100%)',
  'linear-gradient(135deg, #4a4128 0%, #26201400 100%)',
]
const thumbStyle = (i) => ({ background: thumbGradients[i % thumbGradients.length] })

// Comments
const draft = ref('')
const justSubmitted = ref(false)
const submitComment = () => {
  if (!draft.value.trim()) return
  justSubmitted.value = true
  draft.value = ''
}

useReveal()
</script>

<template>
  <div v-if="course" class="course-detail-page">
    <!-- Hero / course header — cinematic background under a dark gradient. -->
    <section class="relative overflow-hidden bg-ink py-16 md:py-24">
      <template v-if="headerBg">
        <img :src="headerBg" alt="" class="course-hero-cover" />
        <div class="course-hero-overlay" aria-hidden="true"></div>
      </template>
      <div class="relative z-10 max-w-5xl mx-auto px-8">
        <router-link to="/academy" class="text-[11px] uppercase tracking-[0.25em] text-gold/80 hover:text-gold transition-colors inline-flex items-center gap-2">
          <span class="dir-arrow-back" aria-hidden="true"></span> {{ t('academy.courseDetail.back') }}
        </router-link>
        <p class="mt-8 text-[11px] uppercase tracking-[0.35em] text-gold/80 font-light">{{ t('academy.courseDetail.eyebrow') }}</p>
        <h1 class="course-hero-title mt-3 font-serif text-4xl md:text-5xl tracking-wide leading-snug">{{ course.title }}</h1>
        <p class="course-hero-instructor mt-4 text-sm uppercase tracking-[0.2em] font-light">{{ course.instructor }}</p>
      </div>
    </section>

    <!-- Post-purchase notification — dismissible banner sitting directly below the
         hero and above the Description / Syllabus grid. Mirrors the "You're
         registered" alert: an X collapses it out with a fade + slide-up. -->
    <Transition name="alert-collapse">
      <div v-if="!isFree && isPurchased && showUnlocked" class="bg-gold/10 border-b border-gold/30">
        <div class="max-w-5xl mx-auto px-8 py-3 flex items-center justify-between gap-4 text-sm text-ink-soft font-light">
          <span class="flex items-center gap-3">
            <span class="shrink-0 grid place-items-center w-7 h-7 rounded-full border border-gold/50 text-gold-dark">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            <span>{{ t('academy.courseDetail.unlockedNotice') }}</span>
          </span>
          <button
            type="button"
            @click="showUnlocked = false"
            :aria-label="t('academy.courseDetail.dismiss')"
            class="shrink-0 p-1 text-ink-muted hover:text-gold-dark transition-colors"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M6 6l12 12M6 18L18 6" stroke-linecap="round"/></svg>
          </button>
        </div>
      </div>
    </Transition>

    <!-- Description + Syllabus side by side -->
    <section class="py-16 md:py-24 bg-parchment-light border-b border-parchment-deep/70">
      <div class="max-w-5xl mx-auto px-8 grid lg:grid-cols-3 gap-x-16 gap-y-14 lg:items-start">
        <!-- Syllabus (one-third) — static, stays in its original position -->
        <aside class="reveal lg:col-span-1">
          <div class="bg-parchment border border-parchment-deep/70 rounded-lg shadow-card p-7">
            <SectionEyebrow :text="t('academy.courseDetail.syllabusTitle')" align="center" />
            <p class="mt-3 text-center text-[11px] uppercase tracking-[0.25em] text-gold-dark font-light tabular-nums">REF&nbsp;·&nbsp;{{ code }}</p>
            <div class="mt-6">
              <StratumStack :items="strata" @select="playLesson" />
            </div>
          </div>
        </aside>

        <!-- Course Description (two-thirds) — now on the right -->
        <div class="reveal lg:col-span-2" style="transition-delay: 80ms;">
          <SectionEyebrow :text="t('academy.courseDetail.descriptionTitle')" align="center" />
          <div class="mt-6 space-y-4 text-[15px] text-ink-soft font-light leading-loose">
            <p v-for="(para, i) in courseDesc.split('\n\n').filter(Boolean)" :key="i">{{ para }}</p>
          </div>

          <!-- Learning Outcomes -->
          <div v-if="outcomes.length" class="mt-12">
            <SectionEyebrow :text="t('academy.courseDetail.outcomesTitle')" align="center" />
            <ul class="mt-6 grid sm:grid-cols-2 gap-x-8 gap-y-4">
              <li v-for="(o, i) in outcomes" :key="'outcome-' + i" class="flex items-start gap-3">
                <span class="shrink-0 mt-0.5 grid place-items-center w-5 h-5 rounded-full border border-gold/50 text-gold-dark">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12l5 5L19 8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <span class="text-sm text-ink-soft font-light leading-relaxed">{{ o }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- Course Info + Videos -->
    <section class="py-16 md:py-28 bg-parchment-light">
      <div class="max-w-5xl mx-auto px-8">
        <SectionEyebrow :text="t('academy.courseDetail.videosTitle')" align="center" />

        <!-- Subscription box ↔ active player. The premium box crossfades out on
             purchase and the full-width player + playlist takes its place. -->
        <Transition name="purchase-swap" mode="out-in" :duration="{ enter: 520, leave: 260 }">
          <!-- Premium subscription / paywall box -->
          <div
            v-if="!isFree && !isPurchased"
            key="subbox"
            class="mt-8 border border-gold/40 bg-gold/5 rounded-lg px-8 py-9 text-center"
          >
            <div class="mx-auto w-12 h-12 rounded-full border border-gold/50 flex items-center justify-center text-gold-dark">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V8a4 4 0 0 1 8 0v3" stroke-linecap="round"/></svg>
            </div>
            <p class="mt-5 text-sm text-ink-soft font-light leading-relaxed max-w-sm mx-auto">{{ t('academy.courseDetail.lockedNotice') }}</p>
            <button
              type="button"
              @click="goToCheckout"
              class="mt-6 inline-flex items-center justify-center gap-2.5 text-[11px] uppercase tracking-[0.3em] font-light px-7 py-3.5 rounded-md border border-gold/60 bg-ink text-parchment-light hover:bg-gold hover:text-ink hover:border-gold transition-colors"
            >
              {{ t('academy.courseDetail.subscribeCta') }} <span class="dir-arrow" aria-hidden="true"></span>
            </button>
            <p class="mt-4 text-[11px] text-ink-muted font-light italic">{{ t('academy.courseDetail.simulateHint') }}</p>
          </div>

          <!-- In-house LMS player + playlist (free courses, or after purchase) -->
          <CoursePlayer
            v-else-if="showPlayer"
            key="player"
            class="mt-8"
            :lessons="playlist"
            :course-key="'course-' + courseIndex"
            :subtitle="course.instructor + ' · ' + course.title"
            :model-value="playing || 1"
            @update:model-value="playing = $event"
          />
        </Transition>

        <!-- Locked preview list — shown only while a premium course is gated;
             once unlocked, the player's own playlist sidebar takes over. -->
        <ul v-if="!showPlayer" class="mt-7 space-y-3">
          <li
            v-for="lesson in videoLessons"
            :key="'video-' + lesson.index"
            class="flex items-center justify-between gap-4 px-5 py-4 border border-parchment-deep/70 rounded-md"
          >
            <div class="flex items-center gap-4 min-w-0">
              <span class="shrink-0 flex items-center justify-center w-8 h-8 border border-parchment-deep text-ink-muted rounded text-xs">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="5" y="11" width="14" height="9" rx="1"/><path d="M8 11V8a4 4 0 0 1 8 0v3" stroke-linecap="round"/></svg>
              </span>
              <span class="text-sm font-light leading-snug text-ink">{{ lesson.title }}</span>
            </div>
            <span class="shrink-0 text-[11px] uppercase tracking-[0.2em] font-light text-gold">
              {{ t('academy.courseDetail.locked') }}
            </span>
          </li>
        </ul>

        <!-- Course information + progress, below the player. -->
        <div class="mt-12 grid sm:grid-cols-2 gap-6 lg:gap-8">
          <LuxeCard class="reveal" :title="t('academy.courseDetail.infoTitle')">
            <dl class="space-y-5 text-sm">
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('academy.courseDetail.instructorLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ course.instructor }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('academy.courseDetail.levelLabel') }}</dt>
                <dd class="text-ink font-light">{{ course.level }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('academy.courseDetail.durationLabel') }}</dt>
                <dd class="text-ink font-light text-right">{{ course.duration }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('academy.courseDetail.fieldLabel') }}</dt>
                <dd class="text-ink font-light">{{ t(`academy.fields.${course.field}`) }}</dd>
              </div>
              <div class="flex items-center justify-between gap-4 pt-5 border-t border-parchment-deep">
                <dt class="text-ink-muted uppercase tracking-[0.15em] text-[11px] font-light">{{ t('academy.courseDetail.tierLabel') }}</dt>
                <dd :class="['uppercase tracking-[0.2em] text-[11px] font-light px-2.5 py-1 border', isFree ? 'text-ink border-parchment-deep' : 'text-gold border-gold/50']">
                  {{ t(`academy.filters.${course.tier}`) }}
                </dd>
              </div>
            </dl>
          </LuxeCard>

          <LuxeCard class="reveal" :title="t('academy.courseDetail.progressTitle')" style="transition-delay: 60ms;">
            <div class="flex items-baseline justify-between text-sm">
              <span class="text-ink font-light">{{ completed }} / {{ lessonCount }}</span>
              <span class="text-ink-muted text-[11px] uppercase tracking-[0.2em] font-light">{{ t('academy.courseDetail.progressLabel') }}</span>
            </div>
            <div class="mt-4 h-1.5 w-full bg-parchment-deep overflow-hidden">
              <div class="h-full bg-gold transition-all duration-500" :style="{ width: progressPct + '%' }"></div>
            </div>
          </LuxeCard>
        </div>
      </div>
    </section>

    <!-- Comments -->
    <section class="py-16 md:py-24 bg-parchment border-t border-parchment-deep">
      <div class="max-w-3xl mx-auto px-8">
        <SectionEyebrow :text="t('academy.comments.title')" />

        <div class="mt-10 space-y-7">
          <div v-for="(c, i) in discussions" :key="i" class="border-b border-parchment-deep pb-7">
            <div class="flex items-baseline justify-between gap-4">
              <span class="flex items-center gap-2.5 flex-wrap">
                <span class="text-sm text-ink font-light uppercase tracking-[0.15em]">{{ c.name }}</span>
                <span
                  v-if="c.role"
                  :class="['text-[9px] uppercase tracking-[0.2em] font-light px-2 py-0.5 rounded-full border', c.role === 'Instructor' ? 'text-gold-dark border-gold/50' : 'text-ink-muted border-parchment-deep']"
                >{{ c.role }}</span>
              </span>
              <span class="shrink-0 text-xs text-ink-muted font-light">{{ c.time }}</span>
            </div>
            <p class="mt-2.5 text-sm text-ink-soft font-light leading-relaxed">{{ c.body }}</p>
          </div>
        </div>

        <form class="mt-10" @submit.prevent="submitComment">
          <textarea
            v-model="draft"
            rows="3"
            :placeholder="t('academy.comments.placeholder')"
            class="w-full bg-parchment-light border border-parchment-deep px-5 py-4 text-sm font-light text-ink placeholder:text-ink-muted focus:outline-none focus:border-gold/60 transition-colors"
          ></textarea>
          <div class="mt-4 flex items-center justify-end gap-4">
            <p v-if="justSubmitted" class="text-xs text-gold-dark font-light italic me-auto">✓ Posted</p>
            <button
              type="submit"
              class="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.25em] text-ink hover:text-gold-dark transition-colors border-b border-gold/50 pb-1"
            >{{ t('academy.comments.submit') }} <span class="dir-arrow" aria-hidden="true"></span></button>
          </div>
        </form>
      </div>
    </section>

    <!-- Browse the Library -->
    <section class="py-16 md:py-24 bg-parchment-light border-t border-parchment-deep">
      <div class="max-w-5xl mx-auto px-8">
        <SectionEyebrow :text="t('academy.courseDetail.relatedTitle')" align="center" />
        <p class="mt-4 text-center text-sm text-ink-soft font-light leading-relaxed max-w-xl mx-auto">{{ t('academy.courseDetail.relatedSubtitle') }}</p>

        <div class="lib-carousel mt-12">
          <!-- Prev -->
          <button
            type="button"
            class="lib-arrow"
            :class="{ 'is-disabled': !canPrev }"
            :disabled="!canPrev"
            @click="slidePrev"
            :aria-label="t('academy.courseDetail.relatedTitle') + ' — previous'"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path :d="chevronToStart" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>

          <!-- Viewport: clips the track; the track slides one card per click. -->
          <div class="lib-carousel-viewport">
            <div class="lib-carousel-track" :style="trackStyle">
              <div
                v-for="rc in related"
                :key="'related-' + rc.i"
                class="lib-slide"
                :style="slideStyle"
              >
                <router-link :to="`/academy/course/${rc.i}`" class="group block h-full">
            <article class="bg-parchment border border-parchment-deep/70 rounded-lg overflow-hidden h-full flex flex-col shadow-card transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-card-hover group-hover:border-gold/50">
              <!-- Thumbnail -->
              <div class="relative aspect-video w-full overflow-hidden" :style="thumbStyle(rc.i)">
                <img v-if="courseMediaAt(rc.i)?.cover" :src="courseMediaAt(rc.i).cover" alt="" loading="lazy" class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
                <div class="absolute inset-0 bg-gradient-to-t from-black/55 via-black/15 to-black/30"></div>
                <div class="absolute inset-0 opacity-[0.08]" style="background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px); background-size: 28px 28px;"></div>
                <span class="absolute top-3 left-3 text-[9px] uppercase tracking-[0.25em] font-light px-2 py-1 rounded-sm border"
                      :class="rc.tier === 'free' ? 'text-parchment-light/90 border-parchment-light/40' : 'text-gold-light border-gold-light/50 bg-black/20'">
                  {{ t(`academy.filters.${rc.tier}`) }}
                </span>
                <span class="absolute inset-0 m-auto w-11 h-11 rounded-full bg-gold/90 group-hover:bg-gold flex items-center justify-center text-ink transition-colors">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                </span>
                <span class="absolute bottom-3 right-3 text-[10px] tracking-[0.1em] font-light text-parchment-light/90 bg-black/40 px-2 py-0.5 rounded">{{ (rc.duration || '').split('·').pop().trim() }}</span>
              </div>
              <!-- Body -->
              <div class="p-6 flex flex-col flex-1">
                <span class="text-[10px] uppercase tracking-[0.3em] text-gold-dark font-light">{{ t(`academy.fields.${rc.field}`) }}</span>
                <h3 class="font-serif font-light text-lg text-ink mt-2 leading-snug group-hover:text-gold-dark transition-colors">{{ rc.title }}</h3>
                <p class="mt-2 text-xs text-ink-muted font-light uppercase tracking-[0.15em]">{{ rc.instructor }}</p>
                <div class="mt-4 pt-4 border-t border-parchment-deep/60 flex items-center justify-between text-[11px] text-ink-muted font-light">
                  <span class="inline-flex items-center gap-1.5">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 7v5l3 2" stroke-linecap="round"/><circle cx="12" cy="12" r="9"/></svg>
                    {{ rc.duration }}
                  </span>
                  <span class="inline-flex items-center gap-1.5 uppercase tracking-[0.15em] text-gold-dark">{{ rc.level }}</span>
                </div>
              </div>
            </article>
                </router-link>
              </div>
            </div>
          </div>

          <!-- Next -->
          <button
            type="button"
            class="lib-arrow"
            :class="{ 'is-disabled': !canNext }"
            :disabled="!canNext"
            @click="slideNext"
            :aria-label="t('academy.courseDetail.relatedTitle') + ' — next'"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path :d="chevronToEnd" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </div>
    </section>
  </div>

  <div v-else class="py-32 text-center">
    <p class="text-sm text-ink-muted font-light">{{ t('academy.courseDetail.back') }}</p>
    <button class="mt-4 text-[11px] uppercase tracking-[0.25em] text-gold-dark border-b border-gold/50 pb-1" @click="router.push('/academy')">
      {{ t('academy.courseDetail.back') }}
    </button>
  </div>
</template>

<style scoped>
/* ── Course header cover ──────────────────────────────────────────────────────
   The cover fills the hero band (object-fit: cover, no crop of the focal
   subject) under a charcoal wash so the gold eyebrow and serif title stay
   legible — preserving the dark luxury aesthetic. */
.course-hero-cover {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.course-hero-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  /* Cinematic dark wash — rgba(0,0,0,0.55) → rgba(0,0,0,0.75), warmed slightly
     toward the inline-start so the gold eyebrow and serif title stay crisp. */
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.55) 0%, rgba(0, 0, 0, 0.75) 100%),
    linear-gradient(90deg, rgba(0, 0, 0, 0.35) 0%, rgba(0, 0, 0, 0) 60%);
}

/* Course title — readable gold above the background image + overlay, regardless
   of theme. Weight + text-shadow guarantee contrast on bright artwork. */
.course-hero-title {
  color: #F4D791;
  font-weight: 600;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
}
.course-hero-instructor {
  color: rgba(255, 255, 255, 0.85);
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.55);
}

/* ── Subscription box ↔ player crossfade ─────────────────────────────────────
   A soft fade + lift so the paywall hands off to the player (and the unlocked
   notice slides in) without any jarring snap. */
.purchase-swap-enter-active { transition: opacity 480ms ease, transform 520ms cubic-bezier(0.22, 1, 0.36, 1); }
.purchase-swap-leave-active { transition: opacity 260ms ease, transform 260ms ease; }
.purchase-swap-enter-from { opacity: 0; transform: translateY(14px) scale(0.985); }
.purchase-swap-leave-to { opacity: 0; transform: translateY(-10px) scale(0.99); }

/* ── Post-purchase banner dismiss ─────────────────────────────────────────────
   Fades + slides up while collapsing its height, so the page below glides into
   place rather than snapping. */
.alert-collapse-leave-active {
  transition: opacity 300ms ease, transform 360ms cubic-bezier(0.4, 0, 0.2, 1), max-height 360ms ease;
  overflow: hidden;
  max-height: 120px;
}
.alert-collapse-leave-to {
  opacity: 0;
  transform: translateY(-12px);
  max-height: 0;
}
@media (prefers-reduced-motion: reduce) {
  .alert-collapse-leave-active { transition: opacity 200ms ease; }
  .alert-collapse-leave-to { transform: none; }
}

/* ── Browse-the-Library carousel ─────────────────────────────────────────────
   Arrows flank a clipped viewport; the flex track slides one card-width per
   click along the X-axis with a long, high-end easing curve. */
.lib-carousel {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 2vw, 1.25rem);
}
.lib-carousel-viewport {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  /* Track is LTR so prev/next stay consistent regardless of page direction. */
  direction: ltr;
}
.lib-carousel-track {
  display: flex;
  will-change: transform;
  transition: transform 720ms cubic-bezier(0.22, 1, 0.36, 1);
}
.lib-slide {
  /* flex-basis is set inline (100% / perView) so 1-up on mobile, 3-up on md+. */
  box-sizing: border-box;
  padding-inline: clamp(0.5rem, 1.4vw, 1rem);
}
/* The viewport forces LTR for a consistent prev/next; restore RTL text flow
   inside each card so Persian course content reads in its natural direction. */
:global(html[dir='rtl']) .lib-slide { direction: rtl; }

/* Round, restrained arrow buttons that echo the gold accent on hover. */
.lib-arrow {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px;
  border: 1px solid rgb(var(--c-gold) / 0.45);
  color: rgb(var(--c-ink) / 0.85);
  background: rgb(var(--c-parchment-light) / 0.6);
  cursor: pointer;
  transition: color 240ms ease, background 240ms ease, border-color 240ms ease, transform 240ms ease, box-shadow 240ms ease;
}
.lib-arrow:hover {
  color: rgb(var(--c-parchment-light));
  background: rgb(var(--c-ink));
  border-color: rgb(var(--c-ink));
  box-shadow: 0 10px 24px -12px rgb(var(--c-ink) / 0.6);
  transform: translateY(-1px);
}
.lib-arrow.is-disabled {
  opacity: 0.3;
  cursor: not-allowed;
  pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
  .lib-carousel-track { transition: none; }
  .purchase-swap-enter-active, .purchase-swap-leave-active { transition: opacity 200ms ease; }
}
</style>
