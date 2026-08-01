import daisyui from 'daisyui'

/** Colors are driven by CSS custom properties (RGB triplets) defined in
 *  src/style.css. The `.dark` class on <html> swaps the triplets, so every
 *  Tailwind utility (bg-parchment-light, text-ink, border-parchment-deep …)
 *  becomes dark-mode aware automatically — no per-element dark: variants needed.
 */
const withVar = (name) => `rgb(var(${name}) / <alpha-value>)`

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        parchment: {
          DEFAULT: withVar('--c-parchment'),
          light: withVar('--c-parchment-light'),
          dark: withVar('--c-parchment-dark'),
          deep: withVar('--c-parchment-deep'),
        },
        gold: {
          DEFAULT: withVar('--c-gold'),
          light: withVar('--c-gold-light'),
          dark: withVar('--c-gold-dark'),
          line: 'rgb(var(--c-gold) / 0.25)',
        },
        ink: {
          DEFAULT: withVar('--c-ink'),
          soft: withVar('--c-ink-soft'),
          muted: withVar('--c-ink-muted'),
          hint: withVar('--c-ink-hint'),
        },
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        sans: ['Inter', 'sans-serif'],
        persian: ['YekanBakh', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgb(var(--c-ink) / 0.04), 0 8px 24px -12px rgb(var(--c-ink) / 0.12)',
        'card-hover': '0 2px 4px rgb(var(--c-ink) / 0.06), 0 18px 40px -16px rgb(var(--c-ink) / 0.22)',
        soft: '0 10px 30px -18px rgb(var(--c-ink) / 0.25)',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.4', transform: 'scale(0.7)' },
        },
      },
      animation: {
        marquee: 'marquee 45s linear infinite',
        'pulse-dot': 'pulseDot 1.6s ease-in-out infinite',
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        cartier: {
          primary: '#B8922A',
          'primary-content': '#FAF7F2',
          secondary: '#8A6A1A',
          'secondary-content': '#FAF7F2',
          accent: '#D4AE5A',
          'accent-content': '#1A1714',
          neutral: '#3D3830',
          'neutral-content': '#F5F0E8',
          'base-100': '#F5F0E8',
          'base-200': '#EAE3D6',
          'base-300': '#D6CCBA',
          'base-content': '#1A1714',
          info: '#3ABFF8',
          success: '#36D399',
          warning: '#FBBD23',
          error: '#F87272',
        },
      },
    ],
  },
}
