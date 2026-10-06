<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { academyApi } from '../api/academy.js'
import { commerceApi } from '../api/commerce.js'
import { productsApi } from '../api/products.js'
import { userApi } from '../api/user.js'
import { resolveApiUrl } from '../api/client.js'
import { useCart } from '../composables/useCart.js'

const { t, locale } = useI18n()
const route = useRoute()
const { items, count, add, remove, updateQuantity, clearType } = useCart()
const step = ref('profile')
const stage = ref('form')
const error = ref('')
const profileLoading = ref(true)
const paymentMethod = ref('card')
const completedPurchaseType = ref(typeof route.query.product_order === 'string' ? 'product' : 'course')
const profile = reactive({
  full_name: '', email: '', phone: '', national_id: '', address: '',
})
const fieldErrors = reactive({ full_name: '', email: '', phone: '', national_id: '', address: '' })

const hasProducts = computed(() => items.value.some((item) => item.type === 'product'))
const courseItems = computed(() => items.value.filter((item) => item.type === 'course'))
const productItems = computed(() => items.value.filter((item) => item.type === 'product'))
const currency = computed(() => locale.value === 'fa' ? 'IRR' : 'USD')
const activeItems = computed(() => items.value.filter((item) => item.currency === currency.value))
const total = computed(() => activeItems.value.reduce(
  (sum, item) => sum + (Number(item.price) || 0) * (item.quantity || 1), 0,
))
const successDestination = computed(() => completedPurchaseType.value === 'product'
  ? '/products'
  : (courseItems.value[0]?.slug ? `/academy/course/${courseItems.value[0].slug}` : '/academy'))
const money = (amount, itemCurrency = currency.value) => new Intl.NumberFormat(locale.value, {
  style: 'currency', currency: itemCurrency, maximumFractionDigits: itemCurrency === 'USD' ? 2 : 0,
}).format(itemCurrency === 'USD' ? amount / 100 : amount)

const addLegacyCourse = async () => {
  if (typeof route.query.course !== 'string' || courseItems.value.length) return
  const course = (await academyApi.detail(route.query.course, locale.value)).data
  const price = course.prices?.find((item) => item.currency === currency.value) || course.prices?.[0]
  add({
    type: 'course', id: route.query.course, slug: route.query.course, title: course.title,
    price: price?.amount_minor, currency: price?.currency,
  })
}
const loadProfile = async () => {
  profileLoading.value = true
  try {
    const saved = (await userApi.profile()).data
    for (const key of Object.keys(profile)) profile[key] = saved[key] || ''
  } catch (problem) {
    error.value = problem.message
  } finally {
    profileLoading.value = false
  }
}
const clearFieldError = (key) => { fieldErrors[key] = '' }
const latinDigits = (value) => String(value || '')
  .replace(/[۰-۹]/g, (digit) => '۰۱۲۳۴۵۶۷۸۹'.indexOf(digit))
  .replace(/[٠-٩]/g, (digit) => '٠١٢٣٤٥٦٧٨٩'.indexOf(digit))
const validateProfile = () => {
  profile.phone = latinDigits(profile.phone)
  profile.national_id = latinDigits(profile.national_id)
  for (const key of Object.keys(fieldErrors)) fieldErrors[key] = ''
  if (profile.full_name.trim().length < 2) fieldErrors.full_name = t('checkout.fieldErrors.name')
  if (!/^\S+@\S+\.\S+$/.test(profile.email.trim())) fieldErrors.email = t('checkout.fieldErrors.email')
  if (!/^\+?[\d\s()-]{7,24}$/.test(profile.phone.trim())) fieldErrors.phone = t('checkout.fieldErrors.phone')
  if (profile.national_id.trim().length > 20) fieldErrors.national_id = t('checkout.fieldErrors.nationalId')
  if (hasProducts.value && !profile.address.trim()) fieldErrors.address = t('checkout.fieldErrors.address')
  return !Object.values(fieldErrors).some(Boolean)
}
const applyServerFieldErrors = (problem) => {
  const serialized = JSON.stringify(problem.problem?.errors || problem.problem?.invalid_params || {}).toLowerCase()
  const detail = String(problem.problem?.detail || problem.message || '').toLowerCase()
  const candidates = {
    full_name: ['full_name', 'full name'], email: ['email'], phone: ['phone'],
    national_id: ['national_id', 'national id'], address: ['address'],
  }
  let matched = false
  for (const [key, needles] of Object.entries(candidates)) {
    if (needles.some((needle) => serialized.includes(needle) || detail.includes(needle))) {
      fieldErrors[key] = t(`checkout.fieldErrors.${key === 'full_name' ? 'name' : key === 'national_id' ? 'nationalId' : key}`)
      matched = true
    }
  }
  return matched
}
const saveProfile = async () => {
  error.value = ''
  if (!validateProfile()) return
  stage.value = 'processing'
  try {
    await userApi.saveProfile({
      full_name: profile.full_name,
      email: profile.email,
      phone: profile.phone,
      national_id: profile.national_id || null,
      address: profile.address || null,
    })
    step.value = 'review'
  } catch (problem) {
    if (!applyServerFieldErrors(problem)) error.value = problem.message
  } finally {
    stage.value = 'form'
  }
}
const goPayment = () => {
  error.value = ''
  if (!count.value) { error.value = t('checkout.errors.empty'); return }
  if (activeItems.value.length !== items.value.length) { error.value = t('checkout.errors.currency'); return }
  if (courseItems.value.length > 1 || (courseItems.value.length && productItems.value.length)) {
    error.value = t('checkout.errors.separateOrders')
    return
  }
  step.value = 'payment'
}
const submit = async () => {
  error.value = ''
  stage.value = 'processing'
  try {
    let response
    if (productItems.value.length) {
      await Promise.all(productItems.value.map((item) => productsApi.setCartItem(item.id, item.quantity || 1)))
      response = await productsApi.createOrder(currency.value, {
        full_name: profile.full_name, phone: profile.phone, address: profile.address,
      })
    } else {
      response = await commerceApi.createOrder(courseItems.value[0].slug, currency.value)
    }
    window.location.assign(resolveApiUrl(response.data.payment_url))
  } catch (problem) {
    error.value = problem.message
    stage.value = 'form'
  }
}
const checkPaymentReturn = async () => {
  if (typeof route.query.product_order !== 'string') return
  try {
    const order = (await productsApi.order(route.query.product_order)).data
    if (order.status === 'paid') {
      completedPurchaseType.value = 'product'
      clearType('product')
      stage.value = 'success'
    }
    else if (order.status === 'cancelled') error.value = t('checkout.errors.cancelled')
    else if (order.status === 'failed') error.value = t('checkout.errors.failed')
  } catch (problem) {
    error.value = problem.message
  }
}
onMounted(async () => {
  await Promise.all([loadProfile(), addLegacyCourse().catch((problem) => { error.value = problem.message })])
  await checkPaymentReturn()
})
</script>

<template>
  <div class="checkout-page">
    <section class="checkout-hero">
      <div class="checkout-hero__signal" aria-hidden="true"></div>
      <div class="relative max-w-3xl mx-auto px-8 text-center">
        <p class="checkout-eyebrow">{{ t('checkout.hero.eyebrow') }}</p>
        <h1>{{ t('checkout.hero.title') }}</h1>
        <p>{{ t('checkout.heroSubtitle') }}</p>
      </div>
    </section>

    <section class="checkout-body">
      <div v-if="stage === 'success'" class="checkout-success" role="status">
        <span class="checkout-success__mark">✓</span>
        <h2>{{ t(`checkout.success.${completedPurchaseType}.title`) }}</h2>
        <p>{{ t(`checkout.success.${completedPurchaseType}.description`) }}</p>
        <router-link :to="successDestination">{{ t(`checkout.success.${completedPurchaseType}.cta`) }}</router-link>
      </div>

      <div v-else class="checkout-wrap">
        <ol class="checkout-steps" :aria-label="t('checkout.stepsLabel')">
          <li v-for="(name, index) in ['profile', 'review', 'payment']" :key="name" :class="{ active: step === name, done: ['review','payment'].indexOf(step) >= index }">
            <span>{{ index + 1 }}</span><strong>{{ t(`checkout.steps.${name}`) }}</strong>
          </li>
        </ol>
        <Transition name="checkout-shift" mode="out-in">
          <section v-if="step === 'profile'" key="profile" class="checkout-card">
            <header><span>01</span><div><h2>{{ t('checkout.profileTitle') }}</h2><p>{{ t('checkout.profileHint') }}</p></div></header>
            <p v-if="error" class="checkout-alert checkout-alert--inside" role="alert">{{ error }}</p>
            <div v-if="profileLoading" class="checkout-loading">{{ t('common.loading') }}</div>
            <form v-else class="profile-grid" @submit.prevent="saveProfile">
              <label :class="{ 'has-error': fieldErrors.full_name }">
                <span>{{ t('checkout.fields.name') }} *</span>
                <input v-model.trim="profile.full_name" autocomplete="name" minlength="2" maxlength="160" required :aria-invalid="Boolean(fieldErrors.full_name)" @input="clearFieldError('full_name')">
                <small v-if="fieldErrors.full_name" class="profile-field-error" role="alert">{{ fieldErrors.full_name }}</small>
              </label>
              <label :class="{ 'has-error': fieldErrors.email }">
                <span>{{ t('checkout.fields.email') }} *</span>
                <input v-model.trim="profile.email" type="email" autocomplete="email" maxlength="320" required :aria-invalid="Boolean(fieldErrors.email)" @input="clearFieldError('email')">
                <small v-if="fieldErrors.email" class="profile-field-error" role="alert">{{ fieldErrors.email }}</small>
              </label>
              <label :class="{ 'has-error': fieldErrors.phone }">
                <span>{{ t('checkout.fields.phone') }} *</span>
                <input v-model.trim="profile.phone" type="tel" autocomplete="tel" inputmode="tel" minlength="7" maxlength="24" required :aria-invalid="Boolean(fieldErrors.phone)" @input="clearFieldError('phone')">
                <small v-if="fieldErrors.phone" class="profile-field-error" role="alert">{{ fieldErrors.phone }}</small>
              </label>
              <label :class="{ 'has-error': fieldErrors.national_id }">
                <span>{{ t('checkout.fields.nationalId') }}</span>
                <input v-model.trim="profile.national_id" inputmode="numeric" maxlength="20" :aria-invalid="Boolean(fieldErrors.national_id)" @input="clearFieldError('national_id')">
                <small v-if="fieldErrors.national_id" class="profile-field-error" role="alert">{{ fieldErrors.national_id }}</small>
              </label>
              <label class="profile-grid__wide" :class="{ 'has-error': fieldErrors.address }">
                <span>{{ t('checkout.fields.address') }}<template v-if="hasProducts"> *</template></span>
                <textarea v-model.trim="profile.address" rows="3" autocomplete="street-address" maxlength="1000" :required="hasProducts" :aria-invalid="Boolean(fieldErrors.address)" @input="clearFieldError('address')"></textarea>
                <small v-if="fieldErrors.address" class="profile-field-error" role="alert">{{ fieldErrors.address }}</small>
              </label>
              <div class="checkout-actions profile-grid__wide"><button class="primary" :disabled="stage === 'processing'">{{ stage === 'processing' ? t('checkout.processing') : t('checkout.next') }}</button></div>
            </form>
          </section>

          <section v-else-if="step === 'review'" key="review" class="checkout-card">
            <header><span>02</span><div><h2>{{ t('checkout.cartTitle') }}</h2><p>{{ t('checkout.reviewHint') }}</p></div></header>
            <p v-if="error" class="checkout-alert checkout-alert--inside" role="alert">{{ error }}</p>
            <div v-if="!items.length" class="checkout-empty"><h3>{{ t('checkout.emptyTitle') }}</h3><p>{{ t('checkout.emptyDesc') }}</p></div>
            <div v-else class="order-lines">
              <article v-for="item in items" :key="item.key">
                <span class="order-lines__type">{{ item.type === 'course' ? t('cart.course') : t('cart.product') }}</span>
                <div>
                  <h3>{{ item.title }}</h3>
                  <div v-if="item.type === 'product'" class="order-lines__quantity" :aria-label="t('cart.quantity')">
                    <button type="button" :disabled="item.quantity <= 1" :aria-label="t('cart.decrease')" @click="updateQuantity(item.key, item.quantity - 1)">−</button>
                    <b>{{ item.quantity }}</b>
                    <button type="button" :disabled="item.quantity >= 99" :aria-label="t('cart.increase')" @click="updateQuantity(item.key, item.quantity + 1)">+</button>
                  </div>
                  <p v-else>{{ t('checkout.quantity', { count: item.quantity || 1 }) }}</p>
                </div>
                <strong>{{ money((item.price || 0) * (item.quantity || 1), item.currency) }}</strong>
                <button type="button" :aria-label="t('cart.remove')" @click="remove(item.key)">×</button>
              </article>
              <div class="order-total"><span>{{ t('checkout.totalLabel') }}</span><strong>{{ money(total) }}</strong></div>
            </div>
            <div class="checkout-actions"><button type="button" class="ghost" @click="step = 'profile'">{{ t('checkout.backProfile') }}</button><button type="button" class="primary" @click="goPayment">{{ t('checkout.proceedCta') }}</button></div>
          </section>

          <section v-else key="payment" class="checkout-card">
            <header><span>03</span><div><h2>{{ t('checkout.paymentTitle') }}</h2><p>{{ t('checkout.securedNote') }}</p></div></header>
            <p v-if="error" class="checkout-alert checkout-alert--inside" role="alert">{{ error }}</p>
            <form @submit.prevent="submit">
              <div class="payment-options">
                <label v-for="option in ['card', 'bank']" :key="option" :class="{ selected: paymentMethod === option }">
                  <input v-model="paymentMethod" type="radio" name="payment" :value="option"><span class="payment-radio"></span><strong>{{ t(`checkout.paymentOptions.${option}`) }}</strong>
                </label>
              </div>
              <div class="payment-seal"><svg viewBox="0 0 24 24"><path d="M12 3 4 6.5v5c0 4.5 3.2 7.8 8 9 4.8-1.2 8-4.5 8-9v-5zM9 12l2 2 4-4.5"/></svg><span>{{ t('checkout.gatewayNote') }}</span></div>
              <div class="checkout-actions"><button type="button" class="ghost" @click="step = 'review'">{{ t('checkout.back') }}</button><button class="primary" :disabled="stage === 'processing'">{{ stage === 'processing' ? t('checkout.processing') : t('checkout.submit') }}</button></div>
            </form>
          </section>
        </Transition>
      </div>
    </section>
  </div>
</template>

<style scoped>
.checkout-page{min-height:80vh;background:rgb(var(--c-parchment-light));color:rgb(var(--c-ink))}.checkout-hero{position:relative;overflow:hidden;padding:4.5rem 0;background:#171a20;color:#f2ede4}.checkout-hero__signal{position:absolute;inset:0;opacity:.45;background:radial-gradient(circle at 50% 120%,rgba(237,192,113,.28),transparent 45%),repeating-linear-gradient(90deg,transparent 0 69px,rgba(255,255,255,.035) 69px 70px);mask-image:linear-gradient(to bottom,#000,transparent)}.checkout-eyebrow{color:#edc071;font-size:.67rem;letter-spacing:.35em;text-transform:uppercase}.checkout-hero h1{margin-top:.9rem;font:300 clamp(2.5rem,6vw,4rem)/1 'Cormorant Garamond',Georgia,serif}.checkout-hero p:last-child{margin-top:1rem;color:rgba(242,237,228,.62);font-size:.85rem;font-weight:300}.checkout-body{padding:4rem 1.25rem 6rem}.checkout-wrap{width:min(58rem,100%);margin:auto}.checkout-steps{display:grid;grid-template-columns:repeat(3,1fr);margin-bottom:2rem;list-style:none;padding:0}.checkout-steps li{position:relative;display:flex;align-items:center;justify-content:center;gap:.55rem;color:rgb(var(--c-ink-muted));font-size:.64rem;letter-spacing:.12em;text-transform:uppercase}.checkout-steps li:not(:last-child)::after{content:'';position:absolute;inset-inline-start:calc(50% + 3.5rem);width:calc(100% - 7rem);height:1px;background:rgb(var(--c-parchment-deep))}.checkout-steps span{display:grid;place-items:center;width:1.8rem;height:1.8rem;border:1px solid rgb(var(--c-parchment-deep));border-radius:50%}.checkout-steps .active{color:rgb(var(--c-gold-dark))}.checkout-steps .active span,.checkout-steps .done span{border-color:rgb(var(--c-gold));background:rgb(var(--c-gold)/.09)}.checkout-alert{margin:0 auto 1rem;padding:.8rem 1rem;border-inline-start:3px solid #b44;background:rgba(180,68,68,.07);color:#933;font-size:.8rem}.checkout-card{overflow:hidden;border:1px solid rgb(var(--c-parchment-deep));border-radius:1rem;background:rgb(var(--c-parchment));box-shadow:0 28px 65px -45px rgba(0,0,0,.5)}.checkout-card>header{display:flex;gap:1rem;align-items:flex-start;padding:1.5rem 1.75rem;border-bottom:1px solid rgb(var(--c-parchment-deep))}.checkout-card>header>span{color:rgb(var(--c-gold-dark));font-size:.65rem;letter-spacing:.18em}.checkout-card h2{font:400 1.45rem 'Cormorant Garamond',Georgia,serif}.checkout-card header p{margin-top:.25rem;color:rgb(var(--c-ink-muted));font-size:.76rem}.checkout-loading,.checkout-empty{padding:3rem;text-align:center;color:rgb(var(--c-ink-muted))}.checkout-empty h3{color:rgb(var(--c-ink));font:400 1.2rem 'Cormorant Garamond',Georgia,serif}.checkout-empty p{margin-top:.5rem;font-size:.8rem}.profile-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1.1rem;padding:1.75rem}.profile-grid label{display:flex;flex-direction:column;gap:.45rem}.profile-grid label span{color:rgb(var(--c-ink-muted));font-size:.68rem}.profile-grid input,.profile-grid textarea{width:100%;border:1px solid rgb(var(--c-parchment-deep));border-radius:.5rem;background:rgb(var(--c-parchment-light));padding:.75rem .85rem;color:rgb(var(--c-ink));outline:none;font-size:.85rem}.profile-grid input:focus,.profile-grid textarea:focus{border-color:rgb(var(--c-gold));box-shadow:0 0 0 3px rgb(var(--c-gold)/.09)}.profile-grid__wide{grid-column:1/-1}.order-lines{padding:.5rem 1.75rem 0}.order-lines article{display:grid;grid-template-columns:auto minmax(0,1fr) auto auto;gap:1rem;align-items:center;padding:1.1rem 0;border-bottom:1px solid rgb(var(--c-parchment-deep)/.7)}.order-lines__type{padding:.3rem .55rem;border:1px solid rgb(var(--c-gold)/.4);color:rgb(var(--c-gold-dark));font-size:.58rem;text-transform:uppercase}.order-lines h3{font-size:.88rem;font-weight:400}.order-lines p{color:rgb(var(--c-ink-muted));font-size:.66rem}.order-lines strong{font-size:.83rem;font-weight:500}.order-lines article>button{color:rgb(var(--c-ink-muted));font-size:1.2rem}.order-lines__quantity{display:inline-flex;align-items:center;margin-top:.45rem;border:1px solid rgb(var(--c-parchment-deep));border-radius:999px;overflow:hidden}.order-lines__quantity button{display:grid;place-items:center;width:1.8rem;height:1.55rem;color:rgb(var(--c-gold-dark));font-size:.85rem}.order-lines__quantity button:hover:not(:disabled){background:rgb(var(--c-gold)/.1)}.order-lines__quantity button:disabled{opacity:.3;cursor:not-allowed}.order-lines__quantity b{min-width:1.5rem;text-align:center;font-size:.7rem;font-weight:500;font-variant-numeric:tabular-nums}.order-total{display:flex;justify-content:space-between;padding:1.4rem 0}.order-total span{color:rgb(var(--c-ink-muted));font-size:.73rem}.order-total strong{color:rgb(var(--c-gold-dark));font:400 1.25rem 'Cormorant Garamond',Georgia,serif}.payment-options{display:grid;gap:.75rem;padding:1.75rem}.payment-options label{display:flex;align-items:center;gap:.8rem;padding:1rem;border:1px solid rgb(var(--c-parchment-deep));border-radius:.65rem;cursor:pointer}.payment-options label.selected{border-color:rgb(var(--c-gold));background:rgb(var(--c-gold)/.07)}.payment-options input{position:absolute;opacity:0}.payment-radio{width:1rem;height:1rem;border:1px solid rgb(var(--c-gold));border-radius:50%}.selected .payment-radio{box-shadow:inset 0 0 0 3px rgb(var(--c-parchment)),inset 0 0 0 8px rgb(var(--c-gold))}.payment-options strong{font-size:.82rem;font-weight:400}.payment-seal{display:flex;align-items:center;gap:.7rem;margin:0 1.75rem;padding:.85rem;border:1px dashed rgb(var(--c-gold)/.45);color:rgb(var(--c-ink-muted));font-size:.72rem}.payment-seal svg{width:1.3rem;fill:none;stroke:rgb(var(--c-gold-dark));stroke-width:1.4}.checkout-actions{display:flex;justify-content:flex-end;gap:.75rem;padding:1.25rem 1.75rem 1.75rem}.checkout-actions button{padding:.8rem 1.25rem;border-radius:.5rem;font-size:.66rem;letter-spacing:.12em;text-transform:uppercase}.checkout-actions .primary{background:rgb(var(--c-ink));color:rgb(var(--c-parchment-light))}.checkout-actions .ghost{border:1px solid rgb(var(--c-parchment-deep));color:rgb(var(--c-ink-muted))}.checkout-actions button:disabled{opacity:.55}.checkout-success{width:min(30rem,100%);margin:auto;padding:3rem;border:1px solid rgb(var(--c-gold)/.4);border-radius:1rem;text-align:center;background:rgb(var(--c-parchment))}.checkout-success__mark{display:grid;place-items:center;width:3.5rem;height:3.5rem;margin:auto;border-radius:50%;background:rgb(var(--c-gold)/.12);color:rgb(var(--c-gold-dark));font-size:1.4rem}.checkout-success h2{margin-top:1rem;font:400 1.6rem 'Cormorant Garamond',Georgia,serif}.checkout-success p{margin:.7rem 0 1.5rem;color:rgb(var(--c-ink-muted));font-size:.85rem}.checkout-success a{color:rgb(var(--c-gold-dark));border-bottom:1px solid rgb(var(--c-gold));font-size:.75rem}.checkout-shift-enter-active,.checkout-shift-leave-active{transition:opacity 240ms ease,transform 340ms cubic-bezier(.16,1,.3,1)}.checkout-shift-enter-from{opacity:0;transform:translateX(18px)}.checkout-shift-leave-to{opacity:0;transform:translateX(-12px)}
.profile-grid label.has-error>span{color:#9f3f3f}.profile-grid label.has-error input,.profile-grid label.has-error textarea{border-color:#b64b4b;background:rgba(182,75,75,.035);box-shadow:0 0 0 3px rgba(182,75,75,.07)}.profile-field-error{display:flex;align-items:center;gap:.35rem;color:#a43e3e;font-size:.66rem;line-height:1.5}.profile-field-error::before{content:'!';display:grid;place-items:center;flex:none;width:1rem;height:1rem;border:1px solid currentColor;border-radius:50%;font-size:.58rem;font-weight:600}
.checkout-alert--inside{margin:1rem 1.75rem 0;border-radius:.35rem}
@media(max-width:640px){.checkout-steps strong{display:none}.profile-grid{grid-template-columns:1fr}.profile-grid__wide{grid-column:auto}.order-lines article{grid-template-columns:auto 1fr auto}.order-lines article>strong{grid-column:2}.checkout-actions{flex-direction:column-reverse}.checkout-actions button{width:100%}}
@media(prefers-reduced-motion:reduce){.checkout-shift-enter-active,.checkout-shift-leave-active{transition:none}}
</style>
