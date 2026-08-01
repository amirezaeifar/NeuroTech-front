import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuth, ROLES } from '../composables/useAuth.js'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'Home', component: () => import('../views/HomeView.vue') },
    { path: '/academy', name: 'Academy', component: () => import('../views/AcademyView.vue') },
    { path: '/pathway', name: 'Pathway', component: () => import('../views/PathwayView.vue') },
    { path: '/academy/course/:id', name: 'CourseDetail', component: () => import('../views/CourseDetailView.vue') },
    { path: '/events', name: 'Events', component: () => import('../views/EventsView.vue') },
    { path: '/events/archive/:id', name: 'PastEventDetail', component: () => import('../views/PastEventDetailView.vue') },
    { path: '/events/active/:type/:id', name: 'ActiveEvent', component: () => import('../views/ActiveEventView.vue') },
    { path: '/events/reserve/:type/:id', name: 'EventReservation', component: () => import('../views/EventReservationView.vue') },
    { path: '/checkout', name: 'Checkout', component: () => import('../views/CheckoutView.vue'), meta: { requiresAuth: true } },
    { path: '/login', name: 'Login', component: () => import('../views/AuthView.vue'), meta: { hideChrome: true } },
    { path: '/products', name: 'Products', component: () => import('../views/ProductsView.vue') },
    { path: '/products/:id', name: 'ProductDetail', component: () => import('../views/ProductDetailView.vue') },
    { path: '/global-trade', name: 'GlobalTrade', component: () => import('../views/GlobalTradeView.vue') },
    { path: '/global-trade/document/:id', name: 'DocumentDetail', component: () => import('../views/DocumentDetailView.vue') },
    { path: '/partners', name: 'Partners', component: () => import('../views/PartnersView.vue') },
    { path: '/partners/:id', name: 'PartnerProfile', component: () => import('../views/PartnerProfileView.vue') },
    { path: '/about', name: 'About', component: () => import('../views/AboutView.vue') },
    { path: '/contact', name: 'Contact', component: () => import('../views/ContactView.vue') },

    // ── Admin Panel (spec §7–9) ──────────────────────────────────────────────
    // A dedicated, secure area behind its own AdminLayout chrome (hideChrome
    // suppresses the public navbar/footer). The parent gates the whole subtree to
    // privileged roles; each child narrows further via meta.roles, so a
    // `specialist` can reach the educational sections but never Users/Settings.
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { hideChrome: true, requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', name: 'AdminDashboard', component: () => import('../views/admin/AdminDashboard.vue'), meta: { roles: [ROLES.ADMIN, ROLES.SPECIALIST] } },
        { path: 'courses', name: 'AdminCourses', component: () => import('../views/admin/AdminCourses.vue'), meta: { roles: [ROLES.ADMIN, ROLES.SPECIALIST] } },
        { path: 'moderation', name: 'AdminModeration', component: () => import('../views/admin/AdminModeration.vue'), meta: { roles: [ROLES.ADMIN, ROLES.SPECIALIST] } },
        { path: 'content', name: 'AdminContent', component: () => import('../views/admin/AdminContent.vue'), meta: { roles: [ROLES.ADMIN, ROLES.SPECIALIST] } },
        { path: 'users', name: 'AdminUsers', component: () => import('../views/admin/AdminUsers.vue'), meta: { roles: [ROLES.ADMIN] } },
        { path: 'settings', name: 'AdminSettings', component: () => import('../views/admin/AdminSettings.vue'), meta: { roles: [ROLES.ADMIN] } },
      ],
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    // Deep-link to a specific Partners profile (e.g. from an event speaker
    // card): scroll to that card with an offset for the sticky navbar.
    if (to.name === 'Partners' && to.query.focus != null) {
      return { el: `#partner-${to.query.focus}`, top: 100, behavior: 'smooth' }
    }
    return { top: 0, behavior: 'smooth' }
  },
})

// Navigation guard (spec §7) — enforces authentication and role-based access.
// `to.meta` is the merge of every matched record, so parent flags (requiresAuth,
// requiresAdmin) and the child's `roles` are all visible here.
router.beforeEach((to) => {
  const { isAuthenticated, canAccessAdmin, hasRole } = useAuth()

  // 1) Must be signed in — bounce to login, preserving the destination.
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  // 2) Admin subtree — must hold a privileged role. A signed-in `user` who lacks
  //    access is sent home rather than to login (they don't need to re-auth).
  if (to.meta.requiresAdmin && !canAccessAdmin.value) {
    return isAuthenticated.value
      ? { name: 'Home' }
      : { name: 'Login', query: { redirect: to.fullPath } }
  }

  // 3) Section-level role gate — e.g. a `specialist` reaching an admin-only page
  //    (Users/Settings) is redirected to a section they can see.
  if (to.meta.roles && !hasRole(to.meta.roles)) {
    return { name: 'AdminDashboard' }
  }

  return true
})

export default router
