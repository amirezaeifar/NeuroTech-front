/**
 * Course media & learning outcomes.
 *
 * This module is the single source of truth for each Academy course's cover
 * image, theme-aware header background identity, and learning outcomes. It is
 * deliberately decoupled from the localized course copy (which lives under
 * `academy.courses` in the locale files) so the presentation assets can change
 * without touching any translations.
 *
 * Video lessons are NOT defined here — they are locally-hosted .mp4 files
 * resolved by numeric order in `src/data/courseVideos.js` and played by the
 * in-house, native-<video> CoursePlayer. There is no external/embedded player.
 *
 * ── How it maps ────────────────────────────────────────────────────────────
 * `courseMedia[i]` corresponds to `academy.courses[i]` (same index/order).
 *   slug       string    stable course identity feeding BOTH theme-aware image
 *                        resolvers (see src/data/courseBackgrounds.js): the
 *                        Academy thumbnail from src/assets/cover-course and the
 *                        course-detail header from src/assets/course_background.
 *                        A new course just needs matching light-/dark- assets.
 *   cover      string    pre-resolved (light/default) thumbnail URL, for any
 *                        consumer that does not wire the theme; theme-aware
 *                        views resolve from `slug` + `isDark` at render time.
 *   bgSlug     string    alias of `slug`, kept for existing header consumers.
 *   headerBg   string    pre-resolved (light/default) header background URL, for
 *                        any consumer that does not wire the theme; theme-aware
 *                        views resolve from `slug` + `isDark` at render time.
 *   outcomes[] string[]  "Learning Outcomes" bullet list
 */

// Course images are resolved automatically by theme from the two asset folders
// — no per-course imports. Each folder ships a light-<slug> and dark-<slug>
// variant; the resolver picks the one matching the active theme at render time.
import { resolveCourseCover, resolveCourseBackground } from './courseBackgrounds.js'

const course = (slug, outcomes) => ({
  slug,
  bgSlug: slug,
  // Pre-resolved light/default URLs for theme-agnostic consumers; theme-aware
  // views re-resolve from `slug` + `isDark` (see AcademyView / CourseDetailView).
  cover: resolveCourseCover(slug, false),
  headerBg: resolveCourseBackground(slug, false),
  outcomes,
})

// Order matches academy.courses[] in the locale files.
export const courseMedia = [
  // 0 · Clinical Neurology
  course('clinical-neurology', [
    'Perform a complete, systematic neurological examination.',
    'Localise lesions from history and examination findings.',
    'Differentiate the major primary and secondary headache disorders.',
    'Apply a structured approach to seizures and epilepsy.',
    'Recognise common movement and neurodegenerative disorders.',
    'Build and prioritise a clinical differential diagnosis.',
  ]),
  // 1 · Neuroscience
  course('neuroscience', [
    'Explain the ionic basis of resting and action potentials.',
    'Describe synaptic transmission and the major neurotransmitter systems.',
    'Relate neuroplasticity to learning, memory and recovery.',
    'Analyse how neural networks generate behaviour.',
    'Connect cognitive systems to their anatomical substrates.',
    'Link circuit dysfunction to neurological and psychiatric disease.',
  ]),
  // 2 · Neuroimaging
  course('neuroimaging', [
    'Select CT or MRI appropriately for a given clinical question.',
    'Interpret the core MRI sequences and their signal patterns.',
    'Identify acute ischaemia on diffusion-weighted imaging.',
    'Recognise vascular pathology on CT and MR angiography.',
    'Apply a systematic search pattern to every study.',
    'Avoid common interpretive pitfalls and imaging artefacts.',
  ]),
  // 3 · Brain Anatomy
  course('brain-anatomy', [
    'Identify the cerebral lobes and their functional regions.',
    'Locate the brainstem nuclei and their clinical correlates.',
    'Describe the organisation of the diencephalon and basal ganglia.',
    'Explain cerebellar anatomy and its functional divisions.',
    'Trace the major white-matter pathways of the brain.',
    'Relate neuroanatomy directly to bedside examination findings.',
  ]),
  // 4 · Neurocritical Care
  course('neurocritical-care', [
    'Apply structured neuromonitoring in the intensive care unit.',
    'Interpret and manage raised intracranial pressure.',
    'Deliver time-critical acute stroke management.',
    'Treat status epilepticus and seizure emergencies.',
    'Manage traumatic and hypoxic-ischaemic brain injury.',
    'Make evidence-based neurocritical-care decisions.',
  ]),
  // 5 · Neurosurgery
  course('neurosurgery', [
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
