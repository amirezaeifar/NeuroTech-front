<script setup>
import { ref, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import BrandLogo from '../components/BrandLogo.vue'
import { useAuth } from '../composables/useAuth.js'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const { login } = useAuth()

// Writing direction — drives the back-chevron glyph and the slide-transition
// direction natively, without scaleX mirroring or unreliable :global() rules.
const isRtl = computed(() => locale.value === 'fa')
const backChevron = computed(() => (isRtl.value ? 'M9 6l6 6-6 6' : 'M15 6l-6 6 6 6'))
const modeSwapName = computed(() => (isRtl.value ? 'auth-mode-swap-rtl' : 'auth-mode-swap'))
// The sliding tab pill is anchored to the inline-start edge; in Register mode it
// glides to the other half. Driven by the logical inset-inline-start (reactive
// inline) rather than a transform or a [data-mode] cascade, both of which proved
// unreliable on this element in this build. Being logical, it flips for RTL on
// its own — no direction-specific math needed.
const pillStyle = computed(() => (mode.value === 'register' ? { insetInlineStart: '50%' } : {}))

// mode: 'login' | 'register'   ·   method: 'password' | 'sms'
const mode = ref('login')
const method = ref('password')

const form = reactive({ name: '', email: '', password: '', phone: '', code: '' })

// SMS passwordless flow: request a code, then verify it.
const codeSent = ref(false)
const submitting = ref(false)

const isLogin = computed(() => mode.value === 'login')
const title = computed(() => (isLogin.value ? t('auth.loginTitle') : t('auth.registerTitle')))
const subtitle = computed(() => (isLogin.value ? t('auth.loginSubtitle') : t('auth.registerSubtitle')))

const setMode = (m) => { mode.value = m }
const setMethod = (m) => { method.value = m; codeSent.value = false }

const finish = (identity, usedMethod) => {
  submitting.value = true
  // Simulate a network round-trip, then sign in and honour ?redirect=.
  window.setTimeout(() => {
    login(identity, usedMethod)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect)
  }, 700)
}

const submitPassword = () => finish(form.email, 'password')

const sendCode = () => {
  if (!form.phone.trim()) return
  codeSent.value = true
}

const verifyCode = () => {
  if (form.code.replace(/\D/g, '').length < 6) return
  finish(form.phone, 'sms')
}
</script>

<template>
  <section class="auth-stage">
    <!-- Ambient, slowly-drifting light orbs for a premium, living backdrop -->
    <div class="auth-orb auth-orb--1" aria-hidden="true"></div>
    <div class="auth-orb auth-orb--2" aria-hidden="true"></div>
    <div class="auth-grid" aria-hidden="true"></div>

    <!-- Back to site (no global navbar on this route) -->
    <router-link to="/" class="auth-back" :aria-label="t('nav.home')">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path :d="backChevron" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span>{{ t('nav.home') }}</span>
    </router-link>

    <!-- Card -->
    <div class="auth-card auth-rise" style="--d: 0ms">
      <div class="auth-card-glow" aria-hidden="true"></div>

      <!-- Brand -->
      <div class="auth-brand flex items-center justify-center mb-5 auth-rise" style="--d: 120ms">
        <BrandLogo :width="186" :height="50" tone="gold" />
      </div>

      <!-- Animated title -->
      <div class="text-center auth-rise" style="--d: 200ms">
        <Transition name="auth-swap" mode="out-in">
          <h1 :key="title" class="auth-title">{{ title }}</h1>
        </Transition>
        <Transition name="auth-swap" mode="out-in">
          <p :key="subtitle" class="auth-subtitle">{{ subtitle }}</p>
        </Transition>
      </div>

      <!-- Mode switch with a sliding indicator -->
      <div class="auth-tabs auth-rise" :data-mode="mode" style="--d: 280ms">
        <span class="auth-tabs-pill" :style="pillStyle" aria-hidden="true"></span>
        <button type="button" class="auth-tab" :class="{ 'is-active': isLogin }" @click="setMode('login')">{{ t('auth.tabLogin') }}</button>
        <button type="button" class="auth-tab" :class="{ 'is-active': !isLogin }" @click="setMode('register')">{{ t('auth.tabRegister') }}</button>
      </div>

      <!-- Method toggle -->
      <div class="auth-methods auth-rise" style="--d: 340ms">
        <button type="button" class="auth-method" :class="{ 'is-active': method === 'password' }" @click="setMethod('password')">{{ t('auth.methodPassword') }}</button>
        <button type="button" class="auth-method" :class="{ 'is-active': method === 'sms' }" @click="setMethod('sms')">{{ t('auth.methodSms') }}</button>
      </div>

      <div class="auth-rise" style="--d: 400ms">
        <Transition :name="modeSwapName" mode="out-in">
        <!-- ── Password flow ── -->
        <form v-if="method === 'password'" key="password" class="auth-form" @submit.prevent="submitPassword">
          <Transition name="auth-field">
            <div v-if="!isLogin" class="auth-field">
              <input id="name" v-model="form.name" type="text" required class="auth-input" placeholder=" " />
              <label for="name" class="auth-flabel">{{ t('auth.fields.name') }}</label>
            </div>
          </Transition>

          <div class="auth-field">
            <input id="email" v-model="form.email" type="email" required class="auth-input" placeholder=" " autocomplete="email" />
            <label for="email" class="auth-flabel">{{ t('auth.fields.email') }}</label>
          </div>

          <div class="auth-field">
            <input id="password" v-model="form.password" type="password" required class="auth-input" placeholder=" " autocomplete="current-password" />
            <label for="password" class="auth-flabel">{{ t('auth.fields.password') }}</label>
          </div>

          <div v-if="isLogin" class="auth-meta">
            <label class="auth-check">
              <input type="checkbox" /> <span>{{ t('auth.rememberMe') }}</span>
            </label>
            <a href="#" class="auth-link">{{ t('auth.forgot') }}</a>
          </div>

          <button type="submit" :disabled="submitting" class="auth-submit">
            <svg v-if="submitting" class="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9" stroke-opacity="0.25" /><path d="M21 12a9 9 0 0 0-9-9" stroke-linecap="round" /></svg>
            <span>{{ isLogin ? t('auth.loginCta') : t('auth.registerCta') }}</span>
          </button>
        </form>

        <!-- ── SMS passwordless flow ── -->
        <form v-else key="sms" class="auth-form" @submit.prevent="codeSent ? verifyCode() : sendCode()">
          <Transition name="auth-field">
            <div v-if="!isLogin" class="auth-field">
              <input id="sms-name" v-model="form.name" type="text" required class="auth-input" placeholder=" " />
              <label for="sms-name" class="auth-flabel">{{ t('auth.fields.name') }}</label>
            </div>
          </Transition>

          <!-- Strict single-row layout: the field and the Send Code button
               stretch to the SAME height and sit flush on one row. The field's
               default 1.1rem bottom margin (which threw the vertical centring
               off) is zeroed here via .auth-phone-field. -->
          <div class="auth-phone-row">
            <div class="auth-field auth-phone-field flex-1">
              <input id="phone" v-model="form.phone" type="tel" required class="auth-input" placeholder=" " :disabled="codeSent" autocomplete="tel" />
              <label for="phone" class="auth-flabel">{{ t('auth.fields.phone') }}</label>
            </div>
            <button v-if="!codeSent" type="submit" class="auth-ghost auth-phone-send shrink-0">{{ t('auth.sendCode') }}</button>
          </div>

          <Transition name="auth-field">
            <div v-if="codeSent">
              <p class="auth-hint mb-3">{{ t('auth.codeSent', { phone: form.phone }) }}</p>
              <div class="auth-field">
                <input id="code" v-model="form.code" inputmode="numeric" maxlength="6" required class="auth-input auth-input--code" placeholder=" " />
                <label for="code" class="auth-flabel">{{ t('auth.fields.code') }}</label>
              </div>
              <div class="auth-meta">
                <button type="button" class="auth-mini" @click="codeSent = false">{{ t('auth.changeNumber') }}</button>
                <button type="button" class="auth-link" @click="sendCode">{{ t('auth.resendCode') }}</button>
              </div>
              <p class="auth-hint auth-hint--italic mt-2">{{ t('auth.codeHint') }}</p>
            </div>
          </Transition>

          <button v-if="codeSent" type="submit" :disabled="submitting" class="auth-submit">
            <svg v-if="submitting" class="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9" stroke-opacity="0.25" /><path d="M21 12a9 9 0 0 0-9-9" stroke-linecap="round" /></svg>
            <span>{{ t('auth.verifyCta') }}</span>
          </button>
        </form>
        </Transition>
      </div>

      <!-- ── Social sign-in ──────────────────────────────────────────────
           A clean "or continue with" hairline divider, then two flat 2D
           provider buttons with monochrome brand-aligned marks. No shadows,
           no 3D — they sit flush on the dark card. -->
      <div class="auth-divider auth-rise" style="--d: 440ms" role="separator">
        <span>{{ t('auth.continueWith') }}</span>
      </div>

      <div class="auth-social auth-rise" style="--d: 480ms">
        <button type="button" class="auth-social-btn" @click="finish('google.user', 'google')">
          <svg class="auth-social-icon" width="17" height="17" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M21.35 11.1H12v3.2h5.35a4.57 4.57 0 0 1-1.98 3l3.2 2.48c1.87-1.73 2.95-4.28 2.95-7.32 0-.7-.06-1.37-.17-2.04z"/>
            <path fill="currentColor" d="M12 22c2.7 0 4.96-.9 6.62-2.42l-3.2-2.48c-.9.6-2.05.96-3.42.96-2.63 0-4.86-1.78-5.66-4.17l-3.3 2.55A9.99 9.99 0 0 0 12 22z"/>
            <path fill="currentColor" d="M6.34 13.89A5.99 5.99 0 0 1 6.02 12c0-.66.11-1.3.3-1.89L3.02 7.56A9.99 9.99 0 0 0 2 12c0 1.61.39 3.14 1.04 4.44l3.3-2.55z"/>
            <path fill="currentColor" d="M12 5.94c1.48 0 2.8.51 3.85 1.5l2.84-2.84A9.6 9.6 0 0 0 12 2 9.99 9.99 0 0 0 3.02 7.56l3.3 2.55C7.14 7.72 9.37 5.94 12 5.94z"/>
          </svg>
          <span>{{ t('auth.continueGoogle') }}</span>
        </button>

        <button type="button" class="auth-social-btn" @click="finish('apple.user', 'apple')">
          <svg class="auth-social-icon" width="17" height="17" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="currentColor" d="M16.37 12.78c.03 3.02 2.65 4.02 2.68 4.04-.02.07-.42 1.43-1.38 2.84-.83 1.21-1.69 2.42-3.05 2.45-1.33.02-1.76-.79-3.28-.79-1.52 0-2 .76-3.26.81-1.31.05-2.31-1.31-3.15-2.52-1.71-2.47-3.02-6.99-1.26-10.04.87-1.51 2.43-2.47 4.12-2.5 1.29-.02 2.5.86 3.28.86.79 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.27-2.15 3.79zM13.9 4.6c.69-.84 1.16-2 1.03-3.16-.99.04-2.2.66-2.91 1.49-.64.74-1.2 1.92-1.05 3.05 1.11.09 2.24-.56 2.93-1.38z"/>
          </svg>
          <span>{{ t('auth.continueApple') }}</span>
        </button>
      </div>

      <!-- Switch link -->
      <p class="auth-switch">
        {{ isLogin ? t('auth.noAccount') : t('auth.haveAccount') }}
        <button type="button" class="auth-link" @click="setMode(isLogin ? 'register' : 'login')">
          {{ isLogin ? t('auth.switchToRegister') : t('auth.switchToLogin') }}
        </button>
      </p>

      <p class="auth-terms">{{ t('auth.terms') }}</p>
    </div>
  </section>
</template>

<style scoped>
/* ───────────────────────── Stage: always-dark charcoal ───────────────────────── */
.auth-stage {
  position: relative;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Trimmed vertical padding so the card clears the viewport on shorter
     screens without scrolling. */
  padding: 1.25rem 1.25rem;
  overflow: hidden;
  background:
    radial-gradient(120% 80% at 50% -10%, #221E19 0%, #16130F 45%, #100D0A 100%);
  color: #F2EDE4;
}

/* Drifting ambient orbs — soft gold/teal light pools that slowly breathe. */
.auth-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(70px);
  pointer-events: none;
  opacity: 0.55;
}
.auth-orb--1 {
  width: 46vw; height: 46vw; max-width: 620px; max-height: 620px;
  top: -12%; left: -8%;
  background: radial-gradient(circle, rgba(237, 192, 113, 0.30), transparent 68%);
  animation: orb-drift-a 17s ease-in-out infinite;
}
.auth-orb--2 {
  width: 40vw; height: 40vw; max-width: 540px; max-height: 540px;
  bottom: -14%; right: -10%;
  background: radial-gradient(circle, rgba(120, 150, 168, 0.22), transparent 70%);
  animation: orb-drift-b 21s ease-in-out infinite;
}
@keyframes orb-drift-a {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(6%, 8%) scale(1.12); }
}
@keyframes orb-drift-b {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-7%, -6%) scale(1.1); }
}

/* Whisper-fine hairline grid for depth. */
.auth-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: repeating-linear-gradient(90deg, transparent 0, transparent 119px, rgba(244, 215, 145, 0.035) 119px, rgba(244, 215, 145, 0.035) 120px);
}

.auth-back {
  position: absolute;
  top: 1.6rem;
  inset-inline-start: 1.8rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-weight: 300;
  color: rgba(242, 237, 228, 0.55);
  transition: color 220ms ease;
  z-index: 3;
}
.auth-back:hover { color: #EDC071; }

/* ───────────────────────────── Card ───────────────────────────── */
.auth-card {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 27rem;
  padding: 1.85rem 2.5rem 1.6rem;
  border-radius: 20px;
  background: linear-gradient(165deg, rgba(38, 33, 28, 0.78), rgba(24, 20, 17, 0.82));
  border: 1px solid rgba(237, 192, 113, 0.14);
  box-shadow: 0 40px 90px -30px rgba(0, 0, 0, 0.75), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(18px) saturate(120%);
  -webkit-backdrop-filter: blur(18px) saturate(120%);
  overflow: hidden;
}
.auth-card-glow {
  position: absolute;
  top: -40%;
  inset-inline-start: 50%;
  transform: translateX(-50%);
  width: 120%;
  height: 60%;
  background: radial-gradient(closest-side, rgba(237, 192, 113, 0.16), transparent 75%);
  pointer-events: none;
}

/* The BrandLogo's image optically sits a few px above the wordmark's
   centre-line; nudge it down so the mark — and the tab control beneath it —
   share one clean vertical centre axis. */
.auth-brand :deep(img) { transform: translateY(3px); }

.auth-eyebrow {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.36em;
  font-weight: 300;
  color: #EDC071;
  margin-bottom: 0.65rem;
}
.auth-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: 1.95rem;
  line-height: 1.15;
  letter-spacing: 0.02em;
  color: #F6F3EC;
}
.auth-subtitle {
  margin-top: 0.45rem;
  font-size: 0.825rem;
  font-weight: 300;
  line-height: 1.6;
  color: rgba(242, 237, 228, 0.55);
}

/* ── Mode tabs with sliding pill ── */
.auth-tabs {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: 1.3rem;
  padding: 4px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(237, 192, 113, 0.1);
}
.auth-tabs-pill {
  position: absolute;
  top: 4px;
  bottom: 4px;
  inset-inline-start: 4px;
  width: calc(50% - 4px);
  border-radius: 7px;
  /* Warm parchment #F2EDE4 active tab — brings light balance to the dark card. */
  background: linear-gradient(135deg, #F2EDE4, #E2D7C4);
  box-shadow: 0 6px 18px -6px rgba(242, 237, 228, 0.4);
  /* Slide via the logical inset (not transform): it animates reliably here and
     flips automatically under dir="rtl" with no direction-specific code. */
  transition: inset-inline-start 420ms cubic-bezier(0.16, 1, 0.3, 1);
}
/* The pill's slide transform is applied inline (see pillStyle) so it survives
   this build's quirky attribute-selector cascade. Only the transition lives
   here, on the base .auth-tabs-pill rule above. */
.auth-tab {
  position: relative;
  z-index: 1;
  padding: 0.7rem 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 400;
  color: rgba(242, 237, 228, 0.6);
  transition: color 300ms ease;
}
.auth-tab.is-active { color: #1A1714; }

/* ── Method toggle ── */
.auth-methods {
  display: flex;
  justify-content: center;
  gap: 1.75rem;
  margin-top: 1rem;
}
.auth-method {
  position: relative;
  padding-bottom: 0.3rem;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 300;
  color: rgba(242, 237, 228, 0.45);
  transition: color 260ms ease;
}
.auth-method::after {
  content: '';
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 1px;
  background: #F2EDE4;
  transform: scaleX(0);
  transition: transform 300ms cubic-bezier(0.16, 1, 0.3, 1);
}
.auth-method.is-active { color: #F2EDE4; }
.auth-method.is-active::after { transform: scaleX(1); }

/* ── Form & floating-label inputs ── */
.auth-form { margin-top: 1.25rem; }
.auth-field {
  position: relative;
  margin-bottom: 0.85rem;
}
.auth-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.25);
  /* Soft parchment #F2EDE4 hairline border for a calmer, more balanced field. */
  border: 1px solid rgba(242, 237, 228, 0.18);
  border-radius: 10px;
  padding: 1.05rem 1rem 0.55rem;
  font-size: 0.9rem;
  font-weight: 300;
  color: #F6F3EC;
  outline: none;
  transition: border-color 240ms ease, box-shadow 240ms ease, background 240ms ease;
}
.auth-input:hover { border-color: rgba(242, 237, 228, 0.35); }
.auth-input:focus {
  border-color: rgba(242, 237, 228, 0.75);
  box-shadow: 0 0 0 3px rgba(242, 237, 228, 0.12);
  background: rgba(0, 0, 0, 0.35);
}
.auth-input:disabled { opacity: 0.55; }
.auth-input--code { letter-spacing: 0.55em; text-align: center; padding-inline: 0.5rem; }

.auth-flabel {
  position: absolute;
  inset-inline-start: 1rem;
  top: 0.95rem;
  font-size: 0.9rem;
  font-weight: 300;
  color: rgba(242, 237, 228, 0.45);
  pointer-events: none;
  transform-origin: inline-start top;
  transition: transform 200ms ease, color 200ms ease;
}
.auth-input:focus + .auth-flabel,
.auth-input:not(:placeholder-shown) + .auth-flabel {
  transform: translateY(-0.7rem) scale(0.74);
  color: #EDC071;
}

.auth-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -0.2rem 0 0.4rem;
  font-size: 11px;
  font-weight: 300;
}
.auth-check {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(242, 237, 228, 0.55);
  cursor: pointer;
}
.auth-check input { accent-color: #EDC071; }
.auth-link {
  color: #EDC071;
  letter-spacing: 0.04em;
  transition: color 200ms ease;
}
.auth-link:hover { color: #F6D79A; }
.auth-mini { color: rgba(242, 237, 228, 0.5); transition: color 200ms ease; }
.auth-mini:hover { color: #F2EDE4; }

.auth-hint { font-size: 0.75rem; font-weight: 300; line-height: 1.6; color: rgba(242, 237, 228, 0.55); }
.auth-hint--italic { font-style: italic; font-size: 0.7rem; color: rgba(242, 237, 228, 0.4); }

/* ── Buttons ── */
.auth-submit {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-top: 0.6rem;
  padding: 0.95rem 1.5rem;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #EDC071, #C99A4E);
  color: #1A1714;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.28em;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 14px 30px -12px rgba(237, 192, 113, 0.55);
  transition: transform 200ms ease, box-shadow 240ms ease, filter 240ms ease;
}
.auth-submit:hover { transform: translateY(-1px); box-shadow: 0 18px 38px -12px rgba(237, 192, 113, 0.7); filter: brightness(1.04); }
.auth-submit:active { transform: translateY(0); }
.auth-submit:disabled { opacity: 0.65; cursor: wait; transform: none; }

/* Compact, modern "Send Code" — sized to balance against the phone field
   rather than stretch the full input height. Parchment #F2EDE4 on hover. */
.auth-ghost {
  align-self: center;
  display: inline-flex;
  align-items: center;
  height: 2.5rem;
  padding: 0 0.9rem;
  border: 1px solid rgba(242, 237, 228, 0.3);
  border-radius: 9px;
  background: rgba(242, 237, 228, 0.05);
  color: #F2EDE4;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 400;
  white-space: nowrap;
  cursor: pointer;
  transition: background 220ms ease, color 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}
.auth-ghost:hover {
  background: #F2EDE4;
  color: #1A1714;
  border-color: #F2EDE4;
  box-shadow: 0 8px 20px -10px rgba(242, 237, 228, 0.5);
}

/* Strict phone + Send Code row — both items the SAME height, on one row. */
.auth-phone-row {
  display: flex;
  align-items: stretch;
  gap: 1rem;
}
.auth-phone-field {
  margin-bottom: 0 !important;
}
/* The button stretches to the field's full height instead of its fixed 2.5rem,
   so the two are identical in height and perfectly flush. */
.auth-phone-send {
  align-self: stretch;
  height: auto;
}

.auth-switch {
  margin-top: 1.15rem;
  text-align: center;
  font-size: 0.78rem;
  font-weight: 300;
  color: rgba(242, 237, 228, 0.5);
}
.auth-switch .auth-link { margin-inline-start: 0.4rem; text-transform: uppercase; letter-spacing: 0.12em; font-size: 0.72rem; }
.auth-terms {
  margin-top: 0.9rem;
  text-align: center;
  font-size: 0.62rem;
  font-weight: 300;
  letter-spacing: 0.04em;
  line-height: 1.5;
  color: rgba(242, 237, 228, 0.3);
}

/* ── "or continue with" divider — a centred caption between two hairlines.
   Logical flex so it reverses cleanly under RTL. */
.auth-divider {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-top: 1.15rem;
}
.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(242, 237, 228, 0.14);
}
.auth-divider span {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 300;
  white-space: nowrap;
  color: rgba(242, 237, 228, 0.4);
}

/* ── Social provider buttons — flat 2D, monochrome marks ── */
.auth-social {
  margin-top: 0.85rem;
  display: grid;
  gap: 0.6rem;
}
.auth-social-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  border: 1px solid rgba(242, 237, 228, 0.18);
  background: rgba(242, 237, 228, 0.04);
  color: #F2EDE4;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-weight: 400;
  cursor: pointer;
  transition: background 220ms ease, border-color 220ms ease, color 220ms ease;
}
.auth-social-btn:hover {
  background: rgba(242, 237, 228, 0.09);
  border-color: rgba(242, 237, 228, 0.4);
}
.auth-social-icon {
  flex-shrink: 0;
  color: rgba(242, 237, 228, 0.85);
  transition: color 220ms ease;
}
.auth-social-btn:hover .auth-social-icon { color: #EDC071; }

html[lang='fa'] .auth-eyebrow,
html[lang='fa'] .auth-tab,
html[lang='fa'] .auth-method,
html[lang='fa'] .auth-submit,
html[lang='fa'] .auth-divider span,
html[lang='fa'] .auth-social-btn,
html[lang='fa'] .auth-back { letter-spacing: 0; }

/* ───────────────────────── Entrance ─────────────────────────
   CSS-driven (not rAF/JS), so the resting state is always VISIBLE — the page
   can never get stuck hidden if animation is throttled. Each element plays a
   staggered fade-up via its own `--d` delay. */
.auth-rise {
  animation: auth-rise 700ms cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: var(--d, 0ms);
}
@keyframes auth-rise {
  from { opacity: 0; transform: translateY(22px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ───────────────────────── Transitions ───────────────────────── */
/* Title / subtitle crossfade when switching login ↔ register. */
.auth-swap-enter-active, .auth-swap-leave-active { transition: opacity 260ms ease, transform 260ms ease; }
.auth-swap-enter-from { opacity: 0; transform: translateY(8px); }
.auth-swap-leave-to { opacity: 0; transform: translateY(-8px); }

/* Password ↔ SMS method swap — a gentle horizontal slide + fade so the two
   login modes glide past each other instead of snapping. */
.auth-mode-swap-enter-active { transition: opacity 340ms ease, transform 380ms cubic-bezier(0.16, 1, 0.3, 1); }
.auth-mode-swap-leave-active { transition: opacity 200ms ease, transform 200ms ease; }
.auth-mode-swap-enter-from { opacity: 0; transform: translateX(18px); }
.auth-mode-swap-leave-to { opacity: 0; transform: translateX(-14px); }
/* RTL slide — mirrored horizontally. Driven by a dynamic transition name
   (modeSwapName) rather than a :global(html[dir]) ancestor, so it always
   applies regardless of scoped-:global quirks in this build. */
.auth-mode-swap-rtl-enter-active { transition: opacity 340ms ease, transform 380ms cubic-bezier(0.16, 1, 0.3, 1); }
.auth-mode-swap-rtl-leave-active { transition: opacity 200ms ease, transform 200ms ease; }
.auth-mode-swap-rtl-enter-from { opacity: 0; transform: translateX(-18px); }
.auth-mode-swap-rtl-leave-to { opacity: 0; transform: translateX(14px); }

/* Expanding/collapsing fields (name, SMS code block). */
.auth-field-enter-active, .auth-field-leave-active {
  transition: opacity 320ms ease, transform 320ms cubic-bezier(0.16, 1, 0.3, 1), max-height 320ms ease, margin 320ms ease;
  overflow: hidden;
  max-height: 140px;
}
.auth-field-enter-from, .auth-field-leave-to {
  opacity: 0;
  transform: translateY(-6px);
  max-height: 0;
  margin-bottom: 0;
}

@media (prefers-reduced-motion: reduce) {
  .auth-orb { animation: none; }
  .auth-rise { animation: none; }
}
</style>
