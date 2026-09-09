<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth.js'
import { useTheme } from '../../composables/useTheme.js'
import { useLocale } from '../../composables/useLocale.js'
import { sectionsForRole } from '../../data/adminSections.js'
import { brandLogoUrl } from '../../data/brandAssets.js'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { user, role, logout } = useAuth()
const { isDark, toggle: toggleTheme } = useTheme()
const { locale, setLocale, locales } = useLocale()

// Only the sections this role is cleared for (spec §7 — conditional sidebar).
const navItems = computed(() => sectionsForRole(role.value))

// The section matching the current route drives the header title/blurb.
const current = computed(
  () => navItems.value.find((s) => s.name === route.name) || navItems.value[0] || null,
)

const drawerOpen = ref(false)
const closeDrawer = () => { drawerOpen.value = false }

const onLogout = async () => { await logout(); router.push('/') }

// A friendly display name from the stored identity (email/phone).
const displayName = computed(() => {
  const id = user.value?.display_name || user.value?.email || user.value?.phone || 'member'
  return id.includes('@') ? id.split('@')[0] : id
})
const roleLabel = computed(() => t(`admin.roles.${role.value}`))
const initial = computed(() => (displayName.value[0] || 'U').toUpperCase())

// Inline icon set — keyed by each section's `icon`. Kept here so the sidebar
// stays a single self-contained file.
const ICONS = {
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
  book: 'M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 0-2 2V4zM18 20H7',
  chat: 'M4 5h16v10H9l-4 4V5z',
  layers: 'M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5',
  users: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 21a7 7 0 0 1 14 0M17 7a3 3 0 0 1 0 6M18.5 21a6 6 0 0 0-3-5.2',
  cog: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19 12a7 7 0 0 0-.1-1.2l2-1.6-2-3.4-2.4 1a7 7 0 0 0-2-1.2L14 2h-4l-.5 2.6a7 7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.6A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.6 2 3.4 2.4-1a7 7 0 0 0 2 1.2L10 22h4l.5-2.6a7 7 0 0 0 2-1.2l2.4 1 2-3.4-2-1.6c.1-.4.1-.8.1-1.2z',
}
</script>

<template>
  <div class="admin-shell" :class="{ 'is-dark': isDark }">
    <!-- Mobile backdrop -->
    <Transition name="fade">
      <div v-if="drawerOpen" class="admin-backdrop" @click="closeDrawer" aria-hidden="true"></div>
    </Transition>

    <!-- ── Sidebar ─────────────────────────────────────────────────────────── -->
    <aside class="admin-sidebar" :class="{ 'is-open': drawerOpen }">
      <div class="admin-sidebar-inner">
        <router-link to="/admin" class="admin-brand" @click="closeDrawer">
          <img :src="brandLogoUrl" alt="" aria-hidden="true" class="admin-brand-logo" />
          <span class="admin-brand-text">
            <span class="admin-brand-name">Neuro Tech</span>
            <span class="admin-brand-sub">{{ t('admin.consoleTag') }}</span>
          </span>
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
      <!-- Top header -->
      <header class="admin-header">
        <div class="admin-header-lead">
          <button type="button" class="admin-burger" @click="drawerOpen = !drawerOpen" :aria-label="t('admin.menu')">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M3 6h18M3 12h18M3 18h18" stroke-linecap="round" /></svg>
          </button>
          <div>
            <p class="admin-eyebrow">{{ t('admin.eyebrow') }}</p>
            <h1 class="admin-header-title">{{ current ? t(`admin.sections.${current.key}.label`) : '' }}</h1>
          </div>
        </div>

        <div class="admin-header-tools">
          <!-- Language -->
          <div class="admin-lang" style="direction: ltr;">
            <button
              v-for="l in locales"
              :key="l.code"
              type="button"
              @click="setLocale(l.code)"
              :class="['admin-lang-btn', locale === l.code ? 'is-active' : '']"
            >{{ l.code.toUpperCase() }}</button>
          </div>

          <!-- Theme -->
        <button type="button" class="admin-icon-btn" @click="toggleTheme" :aria-label="isDark ? t('common.lightMode') : t('common.darkMode')">
            <svg v-if="!isDark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4" stroke-linecap="round"/></svg>
          </button>

          <!-- User profile chip -->
          <div class="admin-user">
            <span class="admin-user-avatar">{{ initial }}</span>
            <span class="admin-user-meta">
              <span class="admin-user-name">{{ displayName }}</span>
              <span class="admin-badge admin-badge-gold admin-user-role">{{ roleLabel }}</span>
            </span>
            <button type="button" class="admin-icon-btn admin-logout" @click="onLogout" :aria-label="t('nav.logout')" :title="t('nav.logout')">
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 12H4M11 8l-4 4 4 4M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </div>
      </header>

      <!-- Routed section -->
      <main class="admin-content">
        <RouterView v-slot="{ Component }">
          <Transition name="fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>

<style scoped>
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

.admin-nav { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; }
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
  html[dir='rtl'] .admin-sidebar { transform: translateX(100%); }
  .admin-sidebar.is-open { transform: translateX(0); }
  .admin-sidebar-inner { height: 100vh; }
  .admin-burger { display: inline-flex; }
  .admin-user-meta { display: none; }
}
@media (max-width: 560px) {
  .admin-lang { display: none; }
  .admin-header-title { font-size: 1.25rem; }
}
</style>
