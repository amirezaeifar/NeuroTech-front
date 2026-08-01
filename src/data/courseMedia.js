/**
 * Course media & learning outcomes — REPLACEABLE DEMO CONTENT.
 *
 * This module is the single source of truth for the video lessons and learning
 * outcomes shown on each Academy course page. It is deliberately decoupled from
 * the localized course copy (which lives under `academy.courses` in the locale
 * files) so that the academy's real, proprietary lectures can be dropped in here
 * without touching any view code or translations.
 *
 * ── How it maps ────────────────────────────────────────────────────────────
 * `courseMedia[i]` corresponds to `academy.courses[i]` (same index/order).
 *   cover      string    course cover image (card thumbnail), by filename in
 *                        src/assets/cover-course
 *   headerBg   string    cinematic header background, by filename in
 *                        src/assets/course_background
 *   videoIds[] string[]  raw lesson video ids, in playlist order — consumed by
 *                        the in-house CoursePlayer (never shown in the UI)
 *   featured   string    embed URL (legacy fallback player)
 *   lessons[]  string[]  one embed URL per lesson (legacy fallback player)
 *   outcomes[] string[]  "Learning Outcomes" bullet list
 *
 * ── Replacing the videos ───────────────────────────────────────────────────
 * The ids in `IDS` are PLACEHOLDERS. To go live, drop the real lesson ids — in
 * playlist order — into the matching `IDS` entry; the player and the legacy
 * embed URLs both derive from them, so no other change is needed. Source
 * playlists are noted beside each entry for the maintainer only and are never
 * surfaced in the interface (lessons are presented as internal resources).
 *
 * ── Future integration (LMS / enrollment / progress) ───────────────────────
 * This static array is shaped to be replaced by a live API payload of the same
 * form. A future learning-management backend can return, per enrolled user:
 * signed lesson URLs (premium/DRM), completion + resume state, quiz/certificate
 * status. Keep this contract — `{ featured, lessons[], outcomes[] }` per course
 * — and the UI continues to work against real data unchanged.
 */

// Course cover images — matched to each course by filename. Imported so Vite
// fingerprints and optimises them; swap a file here to re-skin a course.
import coverClinicalNeurology from '../assets/cover-course/cover-course-clinical-neurology.png'
import coverNeuroscience from '../assets/cover-course/cover-course-neurosience.png'
import coverNeuroimaging from '../assets/cover-course/cover-course-neuroimaging.png'
import coverBrainAnatomy from '../assets/cover-course/cover-course-brainanatomy.png'
import coverNeurocriticalCare from '../assets/cover-course/cover-course-neurociticalcare.png'
import coverNeurosurgery from '../assets/cover-course/cover-course-neurosurgery.png'

// Cinematic course header backgrounds — matched by filename. Neuroscience has no
// dedicated artwork, so it falls back to the generic course background.
import bgClinicalNeurology from '../assets/course_background/course_background-cover-course-clinical-neurology.png'
import bgGeneric from '../assets/course_background/course_background.png'
import bgNeuroimaging from '../assets/course_background/course_background-neuroimaging.png'
import bgBrainAnatomy from '../assets/course_background/course_background-brainanatomy.png'
import bgNeurocriticalCare from '../assets/course_background/course_background-neurociticalca.png'
import bgNeurosurgery from '../assets/course_background/course_background-neurosurgery.png'

// Build a privacy-friendly embed URL for the legacy fallback player.
const embed = (id) => `https://www.youtube-nocookie.com/embed/${id}?rel=0&modestbranding=1`

// Lesson video ids in playlist order.
//
// These are KNOWN-EMBEDDABLE demo ids so the player works end-to-end out of the
// box; the lesson list cycles through them. To go live, replace each course's
// array with the real lesson ids — in playlist order — from its source series
// (maintainer note only, never shown in the UI):
//   clinicalNeurology → "(COMPLETE) Clinical Neurology (Allam)" — All About Clinical Medicine
//   neuroscience      → "Neuroplasticity…" — Therapy in a Nutshell
//   brainAnatomy      → "Sam Webster — brain anatomy"
const DEMO = ['M7lc1UVf-VE', 'aqz-KE-bpKQ']
const IDS = {
  clinicalNeurology: [...DEMO],
  neuroscience: [...DEMO],
  neuroimaging: [...DEMO],
  brainAnatomy: [...DEMO],
  neurocriticalCare: [...DEMO],
  neurosurgery: [...DEMO],
}

const course = (cover, headerBg, ids, outcomes) => ({
  cover,
  headerBg,
  videoIds: ids,
  featured: embed(ids[0]),
  lessons: ids.map(embed),
  outcomes,
})

// Order matches academy.courses[] in the locale files.
export const courseMedia = [
  // 0 · Clinical Neurology
  course(coverClinicalNeurology, bgClinicalNeurology, IDS.clinicalNeurology, [
    'Perform a complete, systematic neurological examination.',
    'Localise lesions from history and examination findings.',
    'Differentiate the major primary and secondary headache disorders.',
    'Apply a structured approach to seizures and epilepsy.',
    'Recognise common movement and neurodegenerative disorders.',
    'Build and prioritise a clinical differential diagnosis.',
  ]),
  // 1 · Neuroscience
  course(coverNeuroscience, bgGeneric, IDS.neuroscience, [
    'Explain the ionic basis of resting and action potentials.',
    'Describe synaptic transmission and the major neurotransmitter systems.',
    'Relate neuroplasticity to learning, memory and recovery.',
    'Analyse how neural networks generate behaviour.',
    'Connect cognitive systems to their anatomical substrates.',
    'Link circuit dysfunction to neurological and psychiatric disease.',
  ]),
  // 2 · Neuroimaging
  course(coverNeuroimaging, bgNeuroimaging, IDS.neuroimaging, [
    'Select CT or MRI appropriately for a given clinical question.',
    'Interpret the core MRI sequences and their signal patterns.',
    'Identify acute ischaemia on diffusion-weighted imaging.',
    'Recognise vascular pathology on CT and MR angiography.',
    'Apply a systematic search pattern to every study.',
    'Avoid common interpretive pitfalls and imaging artefacts.',
  ]),
  // 3 · Brain Anatomy
  course(coverBrainAnatomy, bgBrainAnatomy, IDS.brainAnatomy, [
    'Identify the cerebral lobes and their functional regions.',
    'Locate the brainstem nuclei and their clinical correlates.',
    'Describe the organisation of the diencephalon and basal ganglia.',
    'Explain cerebellar anatomy and its functional divisions.',
    'Trace the major white-matter pathways of the brain.',
    'Relate neuroanatomy directly to bedside examination findings.',
  ]),
  // 4 · Neurocritical Care
  course(coverNeurocriticalCare, bgNeurocriticalCare, IDS.neurocriticalCare, [
    'Apply structured neuromonitoring in the intensive care unit.',
    'Interpret and manage raised intracranial pressure.',
    'Deliver time-critical acute stroke management.',
    'Treat status epilepticus and seizure emergencies.',
    'Manage traumatic and hypoxic-ischaemic brain injury.',
    'Make evidence-based neurocritical-care decisions.',
  ]),
  // 5 · Neurosurgery
  course(coverNeurosurgery, bgNeurosurgery, IDS.neurosurgery, [
    'Describe the surgical anatomy of common operative corridors.',
    'Select appropriate cranial approaches for a given lesion.',
    'Apply neuronavigation and intra-operative neuromonitoring.',
    'Outline the principles of intracranial tumour resection.',
    'Explain core vascular neurosurgical techniques.',
    'Describe the indications for functional neurosurgery.',
  ]),
]

/** Media bundle for the course at `index` (safe to call out of range). */
export const courseMediaAt = (index) => courseMedia[index] || null

export default courseMedia
