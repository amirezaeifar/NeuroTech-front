# NeuroTech
> Neurology Devices, Academy, Events, Import & Export, Global Partnerships.

[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-4FC08D?style=flat&logo=vue.js)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=flat&logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat&logo=tailwind-css)](https://tailwindcss.com/)

---

## Overview

NeuroTech is a comprehensive web platform built for neurology-focused global trade, an academic course library, and event management. The interface is crafted with a minimalist and luxury aesthetic using Vue 3, Vite, and Tailwind CSS.

### Key Features
* **Multi-language Support:** Integrated with `vue-i18n` for global accessibility.
* **Performance:** Lightning-fast HMR and optimized builds powered by Vite.
* **Modern UI:** Styled with Tailwind CSS and DaisyUI, featuring custom fonts and a refined color palette.
* **Modular Architecture:** Structured views for Academy, Active/Past Events, Global Trade, and an Admin Panel.

### Project Setup

**1. Install Dependencies**

npm install

2. Compile and Hot-Reload for Development

npm run dev

3. Compile and Minify for Production

npm run build

📁 Repository Folder Structure

```
├── public/
│   ├── fonts/             # Custom typography (YekanBakh)
│   └── favicon-new.png
├── src/
│   ├── assets/
│   │   └── fonts.css      # Font-face declarations
│   ├── components/        # Reusable UI Atoms & Molecules
│   │   ├── AppFooter.vue
│   │   ├── AppNavbar.vue
│   │   ├── AtlasLayout.vue
│   │   ├── BrandLogo.vue
│   │   ├── BrandMark.vue
│   │   ├── FieldMap.vue
│   │   ├── GoldRule.vue
│   │   ├── IndexSpine.vue
│   │   ├── LuxeCard.vue
│   │   ├── SectionEyebrow.vue
│   │   ├── SpecimenPlate.vue
│   │   ├── StratumStack.vue
│   │   └── VideoPlayer.vue
│   ├── composables/       # Shared state & logic hooks
│   │   ├── useLocale.js
│   │   ├── useReveal.js
│   │   └── useTheme.js
│   ├── locales/           # Localization dictionaries (i18n)
│   │   ├── ar.json | de.json | en.json | fa.json
│   │   └── fr.json | ru.json | tr.json | zh.json
│   ├── router/
│   │   └── index.js       # Vue Router configuration
│   ├── utils/
│   │   └── catalog.js     # Structured data/mock data for products & courses
│   ├── views/             # Page components
│   │   ├── AboutView.vue
│   │   ├── AcademyView.vue
│   │   ├── ActiveEventView.vue
│   │   ├── AdminPanel.vue
│   │   ├── AgenciesView.vue
│   │   ├── CheckoutView.vue
│   │   ├── ContactView.vue
│   │   ├── CourseDetailView.vue
│   │   ├── EventReservationView.vue
│   │   ├── EventsView.vue
│   │   ├── GlobalTradeView.vue
│   │   ├── HomeView.vue
│   │   ├── PartnersView.vue
│   │   ├── ProductsView.vue
│   │   └── TradeReportDetailView.vue
│   ├── App.vue            # Root component
│   ├── main.js            # App entry point
│   └── style.css          # Global styles & CSS variables
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js     # Design system & theme overrides
└── vite.config.js
```

🤖 Developer & AI Guidelines (Context for AI)
To maintain consistency across the codebase, any AI or developer contributing to this project must strictly adhere to the following rules:

1. UI/UX & Design System (Evolutionary Design)
Design Philosophy: The project centers on a minimalist, luxury aesthetic. While it establishes a clean baseline layout, the design system is intentionally flexible to allow for progressive refinements, structural updates, and gradual visual evolutions over time.
Style Cohesion: Maintain a sophisticated visual hierarchy. Any modifications to shadows, borders, effects, or layout systems must be applied globally and systematically using Tailwind utility classes or global variables in src/style.css to keep the interface perfectly cohesive.
Color Palette: The UI relies on a specific premium palette. Use the predefined Tailwind configuration variables for:
Metallic Gold & Deep Silver (gold, gold-light, gold-dark)
Charcoal Black (for dark mode backgrounds)
Jade Green (for specific accents)
Parchment/Ink tones (parchment, ink) for elegant contrast.

2. Code Architecture (Vue 3)
Use Vue 3 Composition API with <script setup>.
Avoid Options API entirely.
Use ref and computed from vue for reactivity.

3. Internationalization (i18n)
Never hardcode text strings in templates or scripts.
Always use vue-i18n (e.g., {{ t('key.name') }} in templates and const { t } = useI18n() in scripts).
Supported locales: en, fr, de, zh, ru, tr, fa, ar.
Handled dynamically via src/composables/useLocale.js.

4. Styling & Typography
Use Tailwind CSS utility classes exclusively.
Use font-persian (YekanBakh) for Persian/Arabic contexts and font-sans (Inter) / font-serif (Cormorant Garamond) for Latin scripts.

---

## Backend Phase 1

The repository now includes a Flask backend under `backend/` while the Vue frontend remains in its original root layout.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
flask --app app.main create-roles
flask --app app.main run --debug
```

See [backend/README.md](backend/README.md) for architecture, environment, MariaDB, Redis, authentication, OTP, migration, testing, and Docker documentation.
