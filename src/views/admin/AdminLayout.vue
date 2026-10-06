<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth.js'
import { useTheme } from '../../composables/useTheme.js'
import { useLocale } from '../../composables/useLocale.js'
import { sectionsForRole } from '../../data/adminSections.js'

const { t } = useI18n()
const route = useRoute()
const { role } = useAuth()
const { isDark } = useTheme()
const { locale } = useLocale()

// Only the sections this role is cleared for (spec §7 — conditional sidebar).
const navItems = computed(() => sectionsForRole(role.value))

// The section matching the current route drives the header title/blurb.
const current = computed(
  () => navItems.value.find((s) => s.name === route.name) || navItems.value[0] || null,
)

const drawerOpen = ref(false)
const closeDrawer = () => { drawerOpen.value = false }


// Inline icon set — keyed by each section's `icon`. Kept here so the sidebar
// stays a single self-contained file.
const ICONS = {
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
  receipt: 'M6 3h12v18l-3-2-3 2-3-2-3 2V3zM9 8h6M9 12h6M9 16h3',
  book: 'M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 0-2 2V4zM18 20H7',
  chat: 'M4 5h16v10H9l-4 4V5z',
  layers: 'M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5',
  users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 21a7 7 0 0 1 14 0M17 7a3 3 0 0 1 0 6M18.5 21a6 6 0 0 0-3-5.2',
  box: 'M4 7l8-4 8 4v10l-8 4-8-4V7zM4 7l8 4 8-4M12 11v10',
  calendar: 'M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2zM8 2v4M16 2v4M3 9h18',
  doc: 'M7 3h7l5 5v13H7zM14 3v5h5',
  cog: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 12a7 7 0 0 0-.1-1.2l2-1.6-2-3.4-2.4 1a7 7 0 0 0-2-1.2L14 2h-4l-.5 2.6a7 7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.6A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.6 2 3.4 2.4-1a7 7 0 0 0 2 1.2L10 22h4l.5-2.6a7 7 0 0 0 2-1.2l2.4 1 2-3.4-2-1.6c.1-.4.1-.8.1-1.2z',
}
</script>

<template>
  <div class="admin-shell" :class="{ 'is-dark': isDark, 'is-rtl': locale === 'fa' }">
    <!-- Mobile backdrop -->
    <Transition name="fade">
      <div v-if="drawerOpen" class="admin-backdrop" @click="closeDrawer" aria-hidden="true"></div>
    </Transition>

    <!-- ── Sidebar ─────────────────────────────────────────────────────────── -->
    <aside class="admin-sidebar" :class="{ 'is-open': drawerOpen }">
      <div class="admin-sidebar-inner">
        <router-link to="/admin" class="admin-brand" @click="closeDrawer">
          <span class="console-title">{{ t('admin.consoleTag') }}</span>
        </router-link>

        <nav class="admin-nav">
          <router-link
            v-for="item in navItems"
            :key="item.name"
            :to="{ name: item.name }"
            class="admin-nav-link"
            :class="{ 'is-active': route.name === item.name }"
            @click="closeDrawer"
          >
            <svg class="admin-nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path :d="ICONS[item.icon]" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span>{{ t(`admin.sections.${item.key}.label`) }}</span>
          </router-link>
        </nav>

        <div class="admin-sidebar-foot">
          <router-link to="/" class="admin-back-site" @click="closeDrawer">
            <span class="dir-arrow-back" aria-hidden="true"></span>
            <span>{{ t('admin.backToSite') }}</span>
          </router-link>
        </div>
      </div>
    </aside>

    <!-- ── Main column ─────────────────────────────────────────────────────── -->
    <div class="admin-main">
      <!-- Mobile navigation -->
      <header class="admin-header admin-mobile-header">
        <div class="admin-header-lead">
          <button type="button" class="admin-burger" @click="drawerOpen = !drawerOpen" :aria-label="t('admin.menu')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M3 6h18M3 12h18M3 18h18" stroke-linecap="round" /></svg>
          </button>
          <div>

            <h1 class="admin-header-title">{{ current ? t(`admin.sections.${current.key}.label`) : '' }}</h1>
          </div>
        </div>

      </header>

      <!-- Routed section -->
      <main class="admin-content">
        <RouterView v-slot="{ Component }">
          <Transition name="admin-page" mode="out-in">
            <div :key="route.path" class="admin-page-view"><component :is="Component" /></div>
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<style scoped>
.console-title{font-size:.9rem;font-weight:600;line-height:1.7;letter-spacing:.02em}
.admin-page-enter-active,.admin-page-leave-active{transition:opacity .18s ease,transform .18s ease}.admin-page-enter-from{opacity:0;transform:translateY(8px)}.admin-page-leave-to{opacity:0;transform:translateY(-4px)}
@media(prefers-reduced-motion:reduce){.admin-page-enter-active,.admin-page-leave-active{transition:none}.admin-sidebar{transition:none!important}}
.admin-mobile-header { display: none !important; }
.admin-menu-settings { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1rem; }
@media(max-width:900px){ .admin-mobile-header { display:flex !important; } .admin-header-tools { display:none !important; } }
.admin-shell {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
  background: rgb(var(--c-parchment-light));
  color: rgb(var(--c-ink));
}

/* ── Sidebar ── */
.admin-sidebar {
  width: 260px;
  flex-shrink: 0;
  border-inline-end: 1px solid rgb(var(--c-parchment-deep) / 0.6);
  background: rgb(var(--c-parchment));
}
.admin-sidebar-inner {
  position: sticky;
  top: 0;
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: 1.6rem 1.1rem;
}
.admin-brand {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.25rem 0.6rem 1.4rem;
  border-bottom: 1px solid rgb(var(--c-parchment-deep) / 0.5);
  margin-bottom: 1.2rem;
}
.admin-brand-logo { height: 34px; width: auto; }
.admin-brand-text { display: flex; flex-direction: column; line-height: 1; direction: ltr; }
.admin-brand-name {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 19px;
  font-weight: 300;
  letter-spacing: 0.06em;
  color: rgb(var(--c-ink));
}
.admin-brand-sub {
  font-family: 'Inter', sans-serif;
  font-size: 7.5px;
  font-weight: 300;
  letter-spacing: 0.42em;
  text-transform: uppercase;
  color: rgb(var(--c-ink-muted));
  margin-top: 4px;
}

.admin-nav { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; overflow-y: auto; min-height: 0; }
.admin-nav-link {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 300;
  letter-spacing: 0.02em;
  color: rgb(var(--c-ink-muted));
  transition: background 200ms ease, color 200ms ease;
  position: relative;
}
.admin-nav-link:hover { background: rgb(var(--c-ink) / 0.04); color: rgb(var(--c-ink)); }
.admin-nav-link.is-active {
  background: rgb(var(--c-gold) / 0.1);
  color: rgb(var(--c-ink));
}
.admin-nav-link.is-active::before {
  content: '';
  position: absolute;
  inset-inline-start: 0;
  top: 20%;
  bottom: 20%;
  width: 3px;
  border-radius: 3px;
  background: rgb(var(--c-gold));
}
.admin-nav-icon { flex-shrink: 0; color: rgb(var(--c-gold-dark)); opacity: 0.85; }
.admin-nav-link.is-active .admin-nav-icon { opacity: 1; }

.admin-sidebar-foot { padding-top: 1rem; border-top: 1px solid rgb(var(--c-parchment-deep) / 0.5); }
.admin-back-site {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 300;
  color: rgb(var(--c-ink-muted));
  padding: 0.4rem 0.9rem;
  transition: color 200ms ease;
}
.admin-back-site:hover { color: rgb(var(--c-gold-dark)); }
html[lang='fa'] .admin-back-site { letter-spacing: 0; }

/* ── Main column ── */
.admin-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.admin-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: rgb(var(--c-parchment-light) / 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgb(var(--c-parchment-deep) / 0.6);
}
.admin-header-lead { display: flex; align-items: center; gap: 0.9rem; min-width: 0; }
.admin-header-title {
  font-family: 'Cormorant Garamond', 'Mikhak', Georgia, serif;
  font-weight: 300;
  font-size: 1.55rem;
  line-height: 1.1;
  color: rgb(var(--c-ink));
  margin-top: 2px;
}
.admin-burger { display: none; color: rgb(var(--c-ink)); padding: 0.2rem; }

.admin-header-tools { display: flex; align-items: center; gap: 0.85rem; }
.admin-lang { display: inline-flex; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: 8px; overflow: hidden; }
.admin-lang-btn {
  padding: 0.3rem 0.55rem;
  font-size: 10px;
  letter-spacing: 0.12em;
  font-weight: 400;
  color: rgb(var(--c-ink-muted));
  transition: background 200ms ease, color 200ms ease;
}
.admin-lang-btn.is-active { background: rgb(var(--c-gold) / 0.15); color: rgb(var(--c-gold-dark)); }

.admin-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 9px;
  color: rgb(var(--c-ink-muted));
  transition: background 200ms ease, color 200ms ease;
}
.admin-icon-btn:hover { background: rgb(var(--c-ink) / 0.05); color: rgb(var(--c-gold-dark)); }

.admin-user {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding-inline-start: 0.6rem;
  border-inline-start: 1px solid rgb(var(--c-parchment-deep) / 0.7);
}
.admin-user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgb(var(--c-gold-light)), rgb(var(--c-gold)));
  color: #1a1714;
  font-weight: 500;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.admin-user-meta { display: flex; flex-direction: column; gap: 3px; align-items: flex-start; }
.admin-user-name { font-size: 0.8rem; font-weight: 400; color: rgb(var(--c-ink)); line-height: 1; }
.admin-user-role { padding: 0.1rem 0.45rem; font-size: 8.5px; }

.admin-content { padding: 1.75rem 1.5rem 3rem; }

.admin-backdrop {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgb(2 6 12 / 0.5);
  backdrop-filter: blur(2px);
}

/* ── Responsive: sidebar → off-canvas drawer ── */
@media (max-width: 900px) {
  .admin-sidebar {
    position: fixed;
    z-index: 50;
    inset-block: 0;
    inset-inline-start: 0;
    transform: translateX(-100%);
    transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 8px 0 40px -20px rgb(2 6 12 / 0.6);
  }
  .admin-shell.is-rtl .admin-sidebar:not(.is-open) { transform: translateX(100%); }
  .admin-sidebar:not(.is-open) { visibility: hidden; pointer-events: none; }
  .admin-sidebar.is-open { transform: translateX(0); visibility: visible; }
  .admin-sidebar-inner { height: 100vh; }
  .admin-burger { display: inline-flex; }
  .admin-user-meta { display: none; }
}
@media (max-width: 560px) {
  .admin-lang { display: none; }
  .admin-header-title { font-size: 1.25rem; }
}
</style>
