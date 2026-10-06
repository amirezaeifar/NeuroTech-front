import { ROLES } from '../composables/useAuth.js'

const PRINCIPAL = ROLES.SUPER_ADMIN
const ADMINISTRATORS = [ROLES.ADMIN, PRINCIPAL]
const CONTENT_STAFF = [ROLES.CONTENT_MANAGER, ...ADMINISTRATORS]

export const ADMIN_SECTIONS = [
  {
    key: 'dashboard', name: 'AdminDashboard', path: '', icon: 'grid',
    roles: [ROLES.SPECIALIST, ROLES.CONTENT_MANAGER, ...ADMINISTRATORS],
  },
  { key: 'orders', name: 'AdminOrders', path: 'orders', icon: 'receipt', roles: ADMINISTRATORS },
  { key: 'tickets', name: 'AdminTickets', path: 'tickets', icon: 'chat', roles: ADMINISTRATORS },
  {
    key: 'courses', name: 'AdminCourses', path: 'courses', icon: 'book',
    roles: [ROLES.SPECIALIST, ROLES.CONTENT_MANAGER, ...ADMINISTRATORS],
  },
  { key: 'products', name: 'AdminProducts', path: 'products', icon: 'box', roles: CONTENT_STAFF },
  { key: 'events', name: 'AdminEvents', path: 'events', icon: 'calendar', roles: CONTENT_STAFF },
  { key: 'partners', name: 'AdminPartners', path: 'partners', icon: 'users', roles: CONTENT_STAFF },
  { key: 'blog', name: 'AdminBlog', path: 'articles', icon: 'doc', roles: CONTENT_STAFF },
  {
    key: 'approvals', name: 'AdminApprovals', path: 'approvals', icon: 'layers',
    roles: [PRINCIPAL],
  },
  {
    key: 'moderation', name: 'AdminModeration', path: 'moderation', icon: 'chat',
    roles: [ROLES.SPECIALIST, PRINCIPAL],
  },
  { key: 'users', name: 'AdminUsers', path: 'users', icon: 'users', roles: ADMINISTRATORS },
]

export const PANEL_ROLES = [
  ROLES.SPECIALIST,
  ROLES.CONTENT_MANAGER,
  ROLES.ADMIN,
  ROLES.SUPER_ADMIN,
]

export function sectionsForRole(role) {
  return ADMIN_SECTIONS.filter((section) => section.roles.includes(role))
}
