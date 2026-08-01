/**
 * Local course video catalogue.
 *
 * The Academy plays its lessons from real, locally-hosted .mp4 files — there is
 * NO external player and no embed. The video files live outside the
 * project at D:\Work\Video and are exposed to the dev server through a directory
 * junction at `public/course-media` (see .gitignore), so Vite serves them as
 * static assets:
 *
 *   public/course-media  →  D:\Work\Video
 *     ├─ Clinical/   …7 numbered clinical-neurology lessons
 *     └─ Anatomy/    …6 numbered brain-anatomy lessons
 *
 * ── Mapping ─────────────────────────────────────────────────────────────────
 * Each course maps to its lessons by NUMERIC ORDER: the trailing "-N" in every
 * filename is the lesson number, so lesson 1 → video 1, lesson 2 → video 2, …
 * The arrays below are already ordered, so the player consumes them directly.
 *
 * `videosForCourse(index)` returns `[{ title, src }]` for the course at that
 * academy index (matching `academy.courses[]`), or an empty array for courses
 * that have no local footage yet — the player shows a graceful fallback for
 * those rather than ever loading an external source.
 */

// Web path to the public junction. Files are referenced relative to this root;
// `encodeURI` handles spaces/parentheses in the original filenames so the
// browser requests a valid URL (the on-disk names are preserved as-is).
const MEDIA_ROOT = '/course-media'

const src = (folder, file) => encodeURI(`${MEDIA_ROOT}/${folder}/${file}`)

// ── Clinical Neurology (academy index 0) ────────────────────────────────────
// Files numbered 1–7 in D:\Work\Video\Clinical, in lesson order.
const clinical = [
  { title: 'Cranial Nerve Examination',                 file: 'Cranial Nerves Examination-1.mp4' },
  { title: 'The Neurological History',                  file: 'Neurological History Examination-2.mp4' },
  { title: 'Coordination & Movement Disorders Exam',    file: 'Incoordination Movement Disorders Examination-3.mp4' },
  { title: 'Motor System Examination',                  file: 'Motor Examination-4.mp4' },
  { title: 'Deep Tendon Reflexes Examination',          file: 'Deep tendon Reflexes Examination-5.mp4' },
  { title: 'Integrated Clinical Session — Part I',      file: 'Clinical Session-6.mp4' },
  { title: 'Integrated Clinical Session — Part II',     file: 'Clinical Session-7.mp4' },
].map((l) => ({ title: l.title, src: src('Clinical', l.file) }))

// ── Brain Anatomy (academy index 3) ─────────────────────────────────────────
// Files numbered 1–6 in D:\Work\Video\Anatomy, in lesson order.
const anatomy = [
  { title: 'Introduction to the Nervous System',        file: 'Nervous system anatomy introduction-1.mp4' },
  { title: 'Cerebral Lobes & Sulci',                    file: 'Cerebral lobes and sulci (basic anatomy)-2.mp4' },
  { title: 'Midline Neuroanatomy — Part I',             file: 'Brain - midline neuroanatomy part 1-3.mp4' },
  { title: 'Midline Neuroanatomy — Part II',            file: 'Brain - midline neuroanatomy part 2-4.mp4' },
  { title: 'Locating the Thalamus',                     file: 'Where is the thalamus-5.mp4' },
  { title: 'Anatomy of the Cerebellum',                 file: 'I love my cerebellum (anatomy)-6.mp4' },
].map((l) => ({ title: l.title, src: src('Anatomy', l.file) }))

// Keyed by academy course index (see academy.courses[] in the locale files).
const byCourseIndex = {
  0: clinical, // Clinical Neurology
  3: anatomy,  // Brain Anatomy
}

/** Ordered local lessons (`[{ title, src }]`) for the course at `index`. */
export function videosForCourse(index) {
  return byCourseIndex[index] || []
}

/** True when the course at `index` has local video footage available. */
export function hasLocalVideos(index) {
  return (byCourseIndex[index] || []).length > 0
}

export default videosForCourse
