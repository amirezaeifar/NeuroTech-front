import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuth } from '../composables/useAuth.js'

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
    { path: '/admin', name: 'Admin', component: () => import('../views/AdminPanel.vue') },
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
router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const { isAuthenticated } = useAuth()
    if (!isAuthenticated.value) {
      return { name: 'Login', query: { redirect: to.fullPath } }
    }
  }
  return true
})

export default router
