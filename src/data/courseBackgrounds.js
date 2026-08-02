/**
 * Theme-aware course image resolver (spec §6).
 *
 * Two independent asset folders, each holding BOTH a light- and a dark-theme
 * variant of every course image, keyed by course identity:
 *
 *   src/assets/cover-course/        Academy card THUMBNAILS
 *                                   light-<slug>.png · dark-<slug>.png
 *   src/assets/course_background/   Course-detail HEADER backgrounds
 *                                   light_<slug>.png · dark_<slug>.png
 *
 * Both resolvers pick the variant that matches the active colour theme
 * (`isDark`): dark artwork in dark mode, light artwork in light mode. A course
 * is addressed by a stable `slug`; every filename token and the slug are
 * normalised to a tolerant match key (lowercase, alphanumerics only) so that
 * hyphens, underscores and spaces all line up
 * (e.g. "brain-anatomy" ≡ "brainanatomy" ≡ "Brain Anatomy").
 *
 * Resolution is deliberately strict about theme boundaries:
 *   1. requested theme's variant for this slug
 *   2. requested theme's explicit `course_background` default
 *   3. an empty string when neither exists
 *
 * A light asset is never returned in dark mode (or vice versa).
 */

// Eagerly glob both folders so Vite fingerprints/optimises the assets and we
// resolve to real, hashed URLs synchronously (equivalent to
// `new URL(<path>, import.meta.url).href`, but for the whole folder at once).
const coverFiles = import.meta.glob(
  '../assets/cover-course/*.{png,jpg,jpeg,webp,avif}',
  { eager: true, import: 'default' },
)
const backgroundFiles = import.meta.glob(
  '../assets/course_background/*.{png,jpg,jpeg,webp,avif}',
  { eager: true, import: 'default' },
)

// Normalise any course name / slug / filename token to a stable match key.
const normalize = (s) => String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '')

// Slug used by the generic, theme-agnostic default placeholder image.
const DEFAULT_KEY = normalize('course_background')

const basename = (path) => path.split('/').pop().replace(/\.[^.]+$/, '')

/**
 * Split a filename into its theme variant and slug. Understands both separator
 * styles used across the two folders:
 *   light-<slug> / dark-<slug>   (cover-course)
 *   light_<slug> / dark_<slug>   (course_background)
 * Anything without a recognised theme prefix is ignored. Course artwork must
 * declare whether it belongs to light or dark mode in its filename.
 */
function parse(name) {
  const m = /^(dark|light)[_-](.+)$/i.exec(name)
  if (m) return { theme: m[1].toLowerCase(), slug: m[2] }
  return { theme: '', slug: name }
}

/**
 * Build per-theme `{ slug → url }` indices for one folder, plus each theme's
 * explicit `course_background` default when one is present.
 */
function buildFolder(files) {
  const light = {}
  const dark = {}

  for (const [path, url] of Object.entries(files)) {
    const { theme, slug } = parse(basename(path))
    const key = normalize(slug)
    if (theme === 'dark') {
      dark[key] = url
    } else if (theme === 'light') {
      light[key] = url
    }
  }

  return {
    light,
    dark,
    lightDefault: light[DEFAULT_KEY] || '',
    darkDefault: dark[DEFAULT_KEY] || '',
  }
}

const covers = buildFolder(coverFiles)
const backgrounds = buildFolder(backgroundFiles)

/** Core same-theme lookup for one folder. */
function resolve(folder, slug, isDark) {
  const key = normalize(slug)
  const themeFiles = isDark ? folder.dark : folder.light
  const themeDefault = isDark ? folder.darkDefault : folder.lightDefault
  return themeFiles[key] || themeDefault || ''
}

/**
 * Academy card thumbnail (from src/assets/cover-course) for a course `slug`
 * under the active theme. `isDark` is the current `isDark` boolean.
 */
export function resolveCourseCover(slug, isDark = false) {
  return resolve(covers, slug, isDark)
}

/**
 * Course-detail header background (from src/assets/course_background) for a
 * course `slug` under the active theme. `isDark` is the current `isDark`.
 */
export function resolveCourseBackground(slug, isDark = false) {
  return resolve(backgrounds, slug, isDark)
}

/** Same-theme generic placeholders (for `@error` image fallbacks). */
export const resolveCourseCoverPlaceholder = (isDark = false) =>
  isDark ? covers.darkDefault : covers.lightDefault
export const resolveCourseBackgroundPlaceholder = (isDark = false) =>
  isDark ? backgrounds.darkDefault : backgrounds.lightDefault

export default resolveCourseBackground
