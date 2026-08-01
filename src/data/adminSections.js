/**
 * Admin Panel navigation model — the single source of truth shared by BOTH the
 * router (to attach per-route role gates) and the AdminLayout sidebar (to render
 * the links a given role is allowed to see). Keeping one list means a section can
 * never appear in the sidebar without a matching guarded route, or vice-versa.
 *
 *   key    stable id + i18n key stem (admin.sections.<key>.{label,blurb})
 *   name   the vue-router route name
 *   path   child path under /admin ('' = the index/dashboard)
 *   icon   which glyph AdminLayout draws (see its ICONS map)
 *   roles  access levels allowed to reach the section
 *
 * `admin` sees every section; `specialist` is scoped to the educational /
 * clinical content sections and is intentionally denied Users and Settings
 * (core system/user management) — the "partial access" tier from the spec.
 */
import { ROLES } from '../composables/useAuth.js'

export const ADMIN_SECTIONS = [
  {
    key: 'dashboard',
    name: 'AdminDashboard',
    path: '',
    icon: 'grid',
    roles: [ROLES.ADMIN, ROLES.SPECIALIST],
  },
  {
    key: 'courses',
    name: 'AdminCourses',
    path: 'courses',
    icon: 'book',
    roles: [ROLES.ADMIN, ROLES.SPECIALIST],
  },
  {
    key: 'moderation',
    name: 'AdminModeration',
    path: 'moderation',
    icon: 'chat',
    roles: [ROLES.ADMIN, ROLES.SPECIALIST],
  },
  {
    key: 'content',
    name: 'AdminContent',
    path: 'content',
    icon: 'layers',
    roles: [ROLES.ADMIN, ROLES.SPECIALIST],
  },
  {
    key: 'users',
    name: 'AdminUsers',
    path: 'users',
    icon: 'users',
    roles: [ROLES.ADMIN],
  },
  {
    key: 'settings',
    name: 'AdminSettings',
    path: 'settings',
    icon: 'cog',
    roles: [ROLES.ADMIN],
  },
]

/** Sections a given role may see, in sidebar order. */
export function sectionsForRole(role) {
  return ADMIN_SECTIONS.filter((s) => s.roles.includes(role))
}
