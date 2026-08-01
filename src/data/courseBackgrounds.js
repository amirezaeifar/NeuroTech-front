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
 * Resolution + fallback chain — always returns a usable URL so an <img> can
 * never render a broken link:
 *   1. requested theme's variant for this slug
 *   2. opposite theme's variant for this slug   (cross-theme fallback)
 *   3. requested theme's folder default          (light-/dark_course_background)
 *   4. opposite theme's default / any placeholder in the folder
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
 * Anything without a recognised theme prefix is treated as a theme-agnostic
 * "base" asset that can serve either theme.
 */
function parse(name) {
  const m = /^(dark|light)[_-](.+)$/i.exec(name)
  if (m) return { theme: m[1].toLowerCase(), slug: m[2] }
  return { theme: 'base', slug: name }
}

/**
 * Build per-theme `{ slug → url }` indices for one folder, plus each theme's
 * default (the `course_background` placeholder, or the first file seen).
 */
function buildFolder(files) {
  const light = {}
  const dark = {}
  let firstLight = ''
  let firstDark = ''
  let firstAny = ''

  for (const [path, url] of Object.entries(files)) {
    if (!firstAny) firstAny = url
    const { theme, slug } = parse(basename(path))
    const key = normalize(slug)
    if (theme === 'dark') {
      dark[key] = url
      if (!firstDark) firstDark = url
    } else if (theme === 'light') {
      light[key] = url
      if (!firstLight) firstLight = url
    } else {
      // Base (no theme prefix) serves either theme unless a themed file wins.
      if (!(key in light)) light[key] = url
      if (!(key in dark)) dark[key] = url
    }
  }

  const lightDefault = light[DEFAULT_KEY] || firstLight || firstAny || ''
  const darkDefault = dark[DEFAULT_KEY] || firstDark || firstAny || ''
  return { light, dark, lightDefault, darkDefault, placeholder: lightDefault || darkDefault }
}

const covers = buildFolder(coverFiles)
const backgrounds = buildFolder(backgroundFiles)

/** Core theme-aware lookup with the full fallback chain for one folder. */
function resolve(folder, slug, isDark) {
  const key = normalize(slug)
  const want = isDark ? folder.dark : folder.light
  const other = isDark ? folder.light : folder.dark

  // 1) requested theme  2) opposite theme (cross-fallback)
  const hit = want[key] || other[key]
  if (hit) return hit

  // 3) requested theme default  4) opposite default / placeholder
  const wantDefault = isDark ? folder.darkDefault : folder.lightDefault
  const otherDefault = isDark ? folder.lightDefault : folder.darkDefault
  return wantDefault || otherDefault || folder.placeholder || ''
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

/** Generic placeholders (for `@error` image fallbacks). */
export const courseCoverPlaceholder = covers.placeholder
export const courseBackgroundPlaceholder = backgrounds.placeholder

export default resolveCourseBackground
