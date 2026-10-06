import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'
import { ADMIN_SECTIONS, PANEL_ROLES } from '../data/adminSections.js'

const adminComponents = {
  AdminDashboard: () => import('../views/admin/AdminDashboard.vue'),
  AdminOrders: () => import('../views/admin/AdminOrders.vue'),
  AdminTickets: () => import('../views/admin/AdminTickets.vue'),
  AdminCourses: () => import('../views/admin/AdminCourses.vue'),
  AdminProducts: () => import('../views/admin/AdminProducts.vue'),
  AdminEvents: () => import('../views/admin/AdminEvents.vue'),
  AdminPartners: () => import('../views/admin/AdminPartners.vue'),
  AdminBlog: () => import('../views/admin/AdminBlog.vue'),
  AdminApprovals: () => import('../views/admin/AdminApprovals.vue'),
  AdminModeration: () => import('../views/admin/AdminModeration.vue'),
  AdminUsers: () => import('../views/admin/AdminUsers.vue'),
}

const adminRoutes = ADMIN_SECTIONS.map((section) => ({
  path: section.path,
  name: section.name,
  component: adminComponents[section.name],
  meta: { roles: section.roles },
}))

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/tickets/:token', name: 'TicketTracking', component: () => import('../views/TicketTracking.vue') },
    { path: '/', name: 'Home', component: () => import('../views/HomeView.vue') },
    { path: '/academy', name: 'Academy', component: () => import('../views/AcademyView.vue') },
    { path: '/articles', name: 'Articles', component: () => import('../views/ArticlesView.vue') },
    { path: '/articles/:slug', name: 'ArticleDetail', component: () => import('../views/ArticleDetailView.vue') },
    { path: '/pathway', name: 'Pathway', component: () => import('../views/PathwayView.vue'), meta: { requiresAuth: true } },
    { path: '/academy/course/:id', name: 'CourseDetail', component: () => import('../views/CourseDetailView.vue') },
    { path: '/events', name: 'Events', component: () => import('../views/EventsView.vue') },
    { path: '/events/archive/:id', name: 'PastEventDetail', component: () => import('../views/PastEventDetailView.vue') },
    { path: '/events/active/:type/:id', redirect: to => ({ name: 'EventLive', params: { slug: to.params.id } }) },
    { path: '/events/live/:slug', name: 'EventLive', component: () => import('../views/ActiveEventView.vue'), meta: { requiresAuth: true } },
    { path: '/events/reserve/:type/:id', name: 'EventReservation', component: () => import('../views/EventReservationView.vue') },
    { path: '/events/confirm', name: 'EventReservationConfirm', component: () => import('../views/EventReservationConfirmView.vue') },
    { path: '/checkout', name: 'Checkout', component: () => import('../views/CheckoutView.vue'), meta: { requiresAuth: true } },
    { path: '/account/courses', name: 'AccountCourses', component: () => import('../views/account/AccountCourses.vue'), meta: { requiresAuth: true } },
    { path: '/account/orders', name: 'AccountOrders', component: () => import('../views/account/AccountOrders.vue'), meta: { requiresAuth: true } },
    { path: '/account/payments', name: 'AccountPayments', component: () => import('../views/account/AccountPayments.vue'), meta: { requiresAuth: true } },
    { path: '/account/favorites', name: 'AccountFavorites', component: () => import('../views/account/AccountFavorites.vue'), meta: { requiresAuth: true } },
    { path: '/account/profile', name: 'AccountProfile', component: () => import('../views/account/AccountProfile.vue'), meta: { requiresAuth: true } },
    { path: '/login', name: 'Login', component: () => import('../views/AuthView.vue'), meta: { hideChrome: true } },
    { path: '/products', name: 'Products', component: () => import('../views/ProductsView.vue') },
    { path: '/products/:id', name: 'ProductDetail', component: () => import('../views/ProductDetailView.vue') },
    { path: '/global-trade', name: 'GlobalTrade', component: () => import('../views/GlobalTradeView.vue') },
    { path: '/global-trade/document/:id', name: 'DocumentDetail', component: () => import('../views/DocumentDetailView.vue') },
    { path: '/partners', name: 'Partners', component: () => import('../views/PartnersView.vue') },
    { path: '/partners/:id', name: 'PartnerProfile', component: () => import('../views/PartnerProfileView.vue') },
    { path: '/about', name: 'About', component: () => import('../views/AboutView.vue') },
    { path: '/contact', name: 'Contact', component: () => import('../views/ContactView.vue') },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, roles: PANEL_ROLES },
      children: adminRoutes,
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

// Auth guard — protected routes (e.g. Checkout) bounce unauthenticated visitors
// to the login page, preserving the intended destination so they land back there
// after signing in.
router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    const { ensureSession, isAuthenticated, role } = useAuth()
    await ensureSession()
    if (!isAuthenticated.value) {
      return { name: 'Login', query: { redirect: to.fullPath } }
    }
    if (to.meta.roles && !to.meta.roles.includes(role.value)) return { name: 'Home' }
  }
  return true
})

export default router
