/**
 * Catalog reference codes for the Academy.
 *
 * Courses are standalone and independent — they do NOT form a linear learning
 * path — so the library is addressed by stable "catalog IDs" rather than
 * sequential numbers. A code is derived only from locale-stable properties
 * (field + tier + position within the field), so it never shifts between
 * languages.
 *
 *   field    → prefix     clinicalNeurology = CLN · neuroimaging = NIM ·
 *                          neurosurgery = NSG · neuroscience = NSC ·
 *                          neurocriticalCare = NCC · brainAnatomy = ANA
 *   tier     → hundreds    free = 1 · premium = 2
 *   position → 2-digit running count within the field
 *
 *   e.g.  CLN-101 · NIM-201 · ANA-102
 */
const FIELD_PREFIX = {
  clinicalNeurology: 'CLN',
  neuroimaging: 'NIM',
  neurosurgery: 'NSG',
  neuroscience: 'NSC',
  neurocriticalCare: 'NCC',
  brainAnatomy: 'ANA',
}

/**
 * Stable catalog code for the course at `index` within `courses`.
 * @param {Array} courses  the full course list (stable order)
 * @param {number} index   the course's index in that list
 * @returns {string}       e.g. "NRO-101"
 */
export function courseCode(courses, index) {
  const course = courses?.[index]
  if (!course) return ''
  const prefix = FIELD_PREFIX[course.field] || 'GEN'
  const hundreds = course.tier === 'premium' ? 2 : 1

  // Running count of same-field courses up to and including this one.
  let seq = 0
  for (let i = 0; i <= index; i++) {
    if (courses[i]?.field === course.field) seq++
  }

  return `${prefix}-${hundreds}${String(seq).padStart(2, '0')}`
}

/**
 * Alphabetic section marker for a module within a course (A, B, C …).
 * Used so a course's modules read as independent reference sections rather
 * than a numbered 1→N sequence.
 */
export function sectionLetter(i) {
  return String.fromCharCode(65 + (i % 26))
}
