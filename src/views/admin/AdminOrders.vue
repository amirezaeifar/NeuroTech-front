<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ordersApi } from '../../api/orders.js'

const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en

const rows = ref([])
const selected = ref(null)
const counts = ref({ pending: 0, paid: 0, cancelled: 0, failed: 0 })
const total = ref(0)
const busy = ref(false)
const saving = ref(false)
const error = ref('')
const kind = ref('')
const payment = ref('')

const paymentLabels = {
  pending: ['Pending', 'در انتظار پرداخت'],
  paid: ['Paid', 'پرداخت‌شده'],
  cancelled: ['Cancelled', 'لغوشده'],
  failed: ['Failed', 'ناموفق'],
}
const fulfillmentLabels = {
  automatic: ['Unlocks after payment', 'بازشدن خودکار پس از پرداخت'],
  access_granted: ['Access granted', 'دسترسی فعال شده'],
  awaiting_payment: ['Awaiting payment', 'در انتظار پرداخت'],
  awaiting_confirmation: ['Awaiting confirmation', 'در انتظار تأیید'],
  confirmed: ['Confirmed', 'تأیید شده'],
  shipped: ['Shipped', 'ارسال شده'],
  closed: ['Closed', 'بسته شده'],
}
const productFlow = ['awaiting_confirmation', 'confirmed', 'shipped', 'closed']
const nextActions = {
  awaiting_confirmation: { status: 'confirmed', en: 'Confirm order', fa: 'تأیید سفارش' },
  confirmed: { status: 'shipped', en: 'Mark as shipped', fa: 'ثبت ارسال سفارش' },
  shipped: { status: 'closed', en: 'Close order', fa: 'بستن سفارش' },
}

const label = (labels, key) => labels[key] ? tr(...labels[key]) : key
const paymentLabel = (key) => label(paymentLabels, key)
const fulfillmentLabel = (key) => label(fulfillmentLabels, key)
const activeAction = computed(() => selected.value?.kind === 'product'
  ? nextActions[selected.value.fulfillment_status]
  : null)
const date = (value) => value ? new Date(value).toLocaleString(locale.value) : '—'
const shortId = (value) => `#${String(value).slice(0, 8).toUpperCase()}`
const money = (amount, currency) => new Intl.NumberFormat(locale.value, {
  style: 'currency', currency, maximumFractionDigits: currency === 'USD' ? 2 : 0,
}).format(currency === 'USD' ? amount / 100 : amount)

let requestId = 0
async function load() {
  const id = ++requestId
  busy.value = true
  error.value = ''
  try {
    const result = await ordersApi.adminList({ kind: kind.value, payment_status: payment.value })
    if (id !== requestId) return
    rows.value = result.data
    total.value = result.meta.total
    counts.value = result.meta.payment_counts
    if (selected.value) {
      selected.value = rows.value.find((row) => row.id === selected.value.id) || null
    }
  } catch (problem) {
    if (id === requestId) error.value = problem.message
  } finally {
    if (id === requestId) busy.value = false
  }
}

async function advance() {
  if (!activeAction.value || !selected.value) return
  saving.value = true
  error.value = ''
  try {
    const result = await ordersApi.advanceProduct(selected.value.id, activeAction.value.status)
    const index = rows.value.findIndex((row) => row.id === result.data.id)
    if (index >= 0) rows.value[index] = result.data
    selected.value = result.data
  } catch (problem) {
    error.value = problem.message
  } finally {
    saving.value = false
  }
}

let filterTimer
watch([kind, payment], () => {
  clearTimeout(filterTimer)
  filterTimer = setTimeout(load, 180)
})
onMounted(load)
</script>

<template>
  <div class="orders-page">
    <header class="orders-intro">
      <div>
        <p class="admin-eyebrow">{{ tr('Order control', 'کنترل سفارش‌ها') }}</p>
        <h1 class="admin-h1 mt-2">{{ tr('Orders', 'سفارشات') }}</h1>
        <p>{{ tr('Track payments and move physical products through confirmation, shipping and closure.', 'پرداخت‌ها را پیگیری کنید و محصولات فیزیکی را تا تأیید، ارسال و بسته‌شدن پیش ببرید.') }}</p>
      </div>
      <button class="admin-btn admin-btn-ghost" :disabled="busy" @click="load">
        {{ busy ? tr('Loading…', 'در حال دریافت…') : tr('Refresh', 'به‌روزرسانی') }}
      </button>
    </header>

    <p v-if="error" class="orders-alert" role="alert">{{ error }}</p>

    <section class="payment-pulse" aria-label="Payment status summary">
      <button v-for="status in ['pending', 'paid', 'cancelled', 'failed']" :key="status" type="button" :class="['pulse-card', `is-${status}`, { active: payment === status }]" @click="payment = payment === status ? '' : status">
        <span class="pulse-dot"></span>
        <strong>{{ counts[status] ?? 0 }}</strong>
        <small>{{ paymentLabel(status) }}</small>
      </button>
    </section>

    <div class="order-filters">
      <div class="filter-tabs" role="group" :aria-label="tr('Order type', 'نوع سفارش')">
        <button v-for="option in [{value:'',en:'All orders',fa:'همه سفارش‌ها'},{value:'course',en:'Courses',fa:'دوره‌ها'},{value:'product',en:'Products',fa:'محصولات'}]" :key="option.value" type="button" :class="{ active: kind === option.value }" @click="kind = option.value">{{ tr(option.en, option.fa) }}</button>
      </div>
      <span>{{ total }} {{ tr('orders', 'سفارش') }}</span>
    </div>

    <div class="orders-workspace">
      <section class="orders-list admin-card">
        <div class="order-row order-row--head">
          <span>{{ tr('Order', 'سفارش') }}</span><span>{{ tr('Customer', 'مشتری') }}</span><span>{{ tr('Amount', 'مبلغ') }}</span><span>{{ tr('Payment', 'پرداخت') }}</span><span>{{ tr('Process', 'فرآیند') }}</span>
        </div>
        <button v-for="order in rows" :key="order.id" type="button" class="order-row" :class="{ selected: selected?.id === order.id }" @click="selected = order">
          <span class="order-identity"><bdi>{{ shortId(order.id) }}</bdi><small>{{ order.kind === 'course' ? tr('Course', 'دوره') : tr('Product', 'محصول') }} · {{ date(order.created_at) }}</small></span>
          <span><strong>{{ order.customer.name || tr('Unnamed user', 'کاربر بدون نام') }}</strong><small>{{ order.items[0]?.title }}<template v-if="order.items.length > 1"> +{{ order.items.length - 1 }}</template></small></span>
          <strong class="order-amount">{{ money(order.total_minor, order.currency) }}</strong>
          <span :class="['status-chip', `is-${order.payment_status}`]">{{ paymentLabel(order.payment_status) }}</span>
          <span class="flow-label">{{ fulfillmentLabel(order.fulfillment_status) }}</span>
        </button>
        <div v-if="!rows.length" class="orders-empty">
          <span>◎</span><h2>{{ tr('No matching orders', 'سفارشی با این وضعیت پیدا نشد') }}</h2><p>{{ tr('New customer orders will appear here automatically.', 'سفارش‌های جدید کاربران به‌صورت خودکار اینجا نمایش داده می‌شوند.') }}</p>
        </div>
      </section>

      <Transition name="detail-slide" mode="out-in">
        <aside v-if="selected" :key="selected.id" class="order-detail admin-card">
          <header>
            <div><p class="admin-eyebrow">{{ selected.kind === 'course' ? tr('Course order', 'سفارش دوره') : tr('Product order', 'سفارش محصول') }}</p><h2><bdi>{{ shortId(selected.id) }}</bdi></h2></div>
            <button type="button" :aria-label="tr('Close details', 'بستن جزئیات')" @click="selected = null">×</button>
          </header>

          <section class="detail-block customer-card">
            <span class="block-index">01</span><div><small>{{ tr('Customer', 'مشتری') }}</small><strong>{{ selected.customer.name || '—' }}</strong><p><bdi>{{ selected.customer.email || '—' }}</bdi></p><p><bdi>{{ selected.customer.phone || '—' }}</bdi></p></div>
          </section>

          <section v-if="selected.kind === 'product'" class="detail-block">
            <span class="block-index">02</span><div><small>{{ tr('Shipping address', 'نشانی ارسال') }}</small><p class="shipping-address">{{ selected.shipping_address || tr('No address was recorded.', 'نشانی ثبت نشده است.') }}</p></div>
          </section>

          <section class="detail-items">
            <article v-for="item in selected.items" :key="item.id">
              <div><strong>{{ item.title }}</strong><small>{{ tr('Quantity', 'تعداد') }}: {{ item.quantity }}</small></div><bdi>{{ money(item.unit_amount_minor * item.quantity, selected.currency) }}</bdi>
            </article>
            <div class="detail-total"><span>{{ tr('Total', 'مجموع') }}</span><strong>{{ money(selected.total_minor, selected.currency) }}</strong></div>
          </section>

          <section class="status-rail payment-rail">
            <div class="rail-heading"><span>{{ tr('Payment status', 'وضعیت پرداخت') }}</span><strong :class="`text-${selected.payment_status}`">{{ paymentLabel(selected.payment_status) }}</strong></div>
            <div class="rail-track"><i :class="`is-${selected.payment_status}`"></i></div>
            <small>{{ selected.payment_provider || tr('Payment gateway not selected', 'درگاه پرداخت انتخاب نشده') }} · {{ date(selected.paid_at || selected.updated_at) }}</small>
          </section>

          <section v-if="selected.kind === 'course'" class="automatic-note">
            <span>↯</span><div><strong>{{ tr('Automatic access', 'دسترسی سیستمی') }}</strong><p>{{ selected.payment_status === 'paid' ? tr('The course was unlocked immediately after successful payment.', 'دوره بلافاصله پس از پرداخت موفق برای کاربر باز شده است.') : tr('Access will be granted automatically after a successful payment.', 'پس از پرداخت موفق، دسترسی به‌صورت خودکار فعال می‌شود.') }}</p></div>
          </section>

          <section v-else class="fulfillment-flow">
            <h3>{{ tr('Fulfillment', 'روند آماده‌سازی و ارسال') }}</h3>
            <ol>
              <li v-for="(status, index) in productFlow" :key="status" :class="{ done: productFlow.indexOf(selected.fulfillment_status) >= index, current: selected.fulfillment_status === status }">
                <i>{{ productFlow.indexOf(selected.fulfillment_status) > index ? '✓' : index + 1 }}</i><span>{{ fulfillmentLabel(status) }}</span>
              </li>
            </ol>
            <p v-if="selected.payment_status !== 'paid'" class="flow-warning">{{ tr('Fulfillment becomes available after payment is completed.', 'فرآیند ارسال پس از تکمیل پرداخت فعال می‌شود.') }}</p>
            <button v-if="activeAction" class="admin-btn admin-btn-primary fulfillment-action" :disabled="saving" @click="advance">
              {{ saving ? tr('Saving…', 'در حال ثبت…') : tr(activeAction.en, activeAction.fa) }}
            </button>
          </section>
        </aside>
        <aside v-else class="detail-placeholder admin-card">
          <span>↗</span><h2>{{ tr('Select an order', 'یک سفارش را انتخاب کنید') }}</h2><p>{{ tr('Customer, payment and delivery details will appear here.', 'اطلاعات مشتری، پرداخت و ارسال در این بخش نمایش داده می‌شود.') }}</p>
        </aside>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.orders-page{max-width:1480px;margin:auto}.orders-intro{display:flex;align-items:flex-start;justify-content:space-between;gap:2rem}.orders-intro>div>p:last-child{max-width:720px;margin-top:.75rem;color:rgb(var(--c-ink-muted));font-size:.85rem;line-height:1.9}.orders-alert{margin-top:1rem;padding:.9rem 1rem;border-inline-start:3px solid #a44646;background:rgba(164,70,70,.08);color:#9d3d3d;font-size:.78rem}.payment-pulse{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin-top:2rem}.pulse-card{position:relative;display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;gap:.05rem .8rem;overflow:hidden;padding:1rem 1.1rem;border:1px solid rgb(var(--c-ink)/.11);border-radius:14px;background:rgb(var(--c-parchment));text-align:start;transition:transform .2s,border-color .2s}.pulse-card:hover,.pulse-card.active{transform:translateY(-2px);border-color:var(--status-color)}.pulse-card::after{content:'';position:absolute;inset-inline-end:-25px;bottom:-40px;width:90px;height:90px;border:1px solid var(--status-color);border-radius:50%;opacity:.12}.pulse-dot{grid-row:1/3;align-self:center;width:.55rem;height:.55rem;border-radius:50%;background:var(--status-color);box-shadow:0 0 0 5px color-mix(in srgb,var(--status-color) 14%,transparent)}.pulse-card strong{font-size:1.35rem;font-weight:500;line-height:1}.pulse-card small{color:rgb(var(--c-ink-muted));font-size:.68rem}.is-pending{--status-color:#b98736}.is-paid{--status-color:#367b60}.is-cancelled{--status-color:#77736c}.is-failed{--status-color:#a44646}.order-filters{display:flex;align-items:center;justify-content:space-between;margin:1.5rem 0 .85rem;color:rgb(var(--c-ink-muted));font-size:.72rem}.filter-tabs{display:flex;gap:.35rem;padding:.25rem;border:1px solid rgb(var(--c-ink)/.1);border-radius:10px;background:rgb(var(--c-parchment))}.filter-tabs button{padding:.5rem .85rem;border-radius:7px}.filter-tabs button.active{background:rgb(var(--c-ink));color:rgb(var(--c-parchment-light))}.orders-workspace{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(320px,.75fr);gap:1rem;align-items:start}.orders-list{overflow:hidden}.order-row{display:grid;grid-template-columns:minmax(170px,1.2fr) minmax(170px,1.35fr) minmax(115px,.8fr) minmax(120px,.75fr) minmax(140px,1fr);gap:1rem;align-items:center;width:100%;padding:1rem 1.15rem;border-bottom:1px solid rgb(var(--c-ink)/.085);text-align:start;transition:background .18s}.order-row:not(.order-row--head):hover,.order-row.selected{background:rgb(var(--c-gold)/.075)}.order-row.selected{box-shadow:inset 3px 0 rgb(var(--c-gold))}.order-row--head{color:rgb(var(--c-ink-muted));font-size:.62rem;letter-spacing:.08em;text-transform:uppercase}.order-row strong{font-size:.78rem;font-weight:500}.order-row small{display:block;overflow:hidden;margin-top:.35rem;color:rgb(var(--c-ink-muted));font-size:.62rem;text-overflow:ellipsis;white-space:nowrap}.order-identity>bdi{font-size:.72rem;font-variant-numeric:tabular-nums}.order-amount{font-variant-numeric:tabular-nums}.status-chip{justify-self:start;padding:.34rem .55rem;border:1px solid color-mix(in srgb,var(--status-color) 38%,transparent);border-radius:999px;background:color-mix(in srgb,var(--status-color) 8%,transparent);color:var(--status-color);font-size:.64rem}.flow-label{font-size:.68rem;color:rgb(var(--c-ink-soft))}.orders-empty,.detail-placeholder{padding:4rem 2rem;text-align:center;color:rgb(var(--c-ink-muted))}.orders-empty>span,.detail-placeholder>span{display:block;color:rgb(var(--c-gold-dark));font-size:2rem}.orders-empty h2,.detail-placeholder h2{margin-top:.8rem;color:rgb(var(--c-ink));font-size:1.05rem;font-weight:500}.orders-empty p,.detail-placeholder p{margin-top:.45rem;font-size:.72rem}.order-detail{position:sticky;top:1rem;overflow:hidden}.order-detail>header{display:flex;justify-content:space-between;gap:1rem;padding:1.25rem 1.35rem;border-bottom:1px solid rgb(var(--c-ink)/.1);background:rgb(var(--c-ink));color:rgb(var(--c-parchment-light))}.order-detail header h2{margin-top:.45rem;font-size:1.15rem;font-weight:400}.order-detail header button{align-self:start;color:rgb(var(--c-parchment-light)/.65);font-size:1.35rem}.detail-block{display:grid;grid-template-columns:28px 1fr;gap:.8rem;padding:1.15rem 1.35rem;border-bottom:1px solid rgb(var(--c-ink)/.085)}.block-index{color:rgb(var(--c-gold-dark));font-size:.58rem}.detail-block small{display:block;margin-bottom:.4rem;color:rgb(var(--c-ink-muted));font-size:.62rem;text-transform:uppercase;letter-spacing:.08em}.detail-block strong{font-size:.85rem;font-weight:500}.detail-block p{margin-top:.25rem;color:rgb(var(--c-ink-muted));font-size:.7rem}.shipping-address{line-height:1.85;white-space:pre-line}.detail-items{padding:.5rem 1.35rem}.detail-items article,.detail-total{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.85rem 0;border-bottom:1px solid rgb(var(--c-ink)/.08);font-size:.72rem}.detail-items article strong{font-weight:500}.detail-items article small{display:block;margin-top:.28rem;color:rgb(var(--c-ink-muted));font-size:.62rem}.detail-total{border-bottom:0}.detail-total strong{color:rgb(var(--c-gold-dark));font-size:1rem}.status-rail,.fulfillment-flow,.automatic-note{margin:0 1.35rem 1.25rem;padding:1rem;border:1px solid rgb(var(--c-ink)/.1);border-radius:11px}.rail-heading{display:flex;justify-content:space-between;gap:1rem;font-size:.7rem}.rail-heading strong{font-weight:500}.text-paid{color:#367b60}.text-pending{color:#a16e1c}.text-cancelled{color:#77736c}.text-failed{color:#a44646}.rail-track{height:4px;margin:.8rem 0;background:rgb(var(--c-ink)/.08);border-radius:99px;overflow:hidden}.rail-track i{display:block;width:34%;height:100%;background:var(--status-color)}.rail-track i.is-paid{width:100%}.rail-track i.is-cancelled,.rail-track i.is-failed{width:100%}.status-rail>small{color:rgb(var(--c-ink-muted));font-size:.6rem}.automatic-note{display:flex;gap:.8rem;border-color:rgb(var(--c-gold)/.35);background:rgb(var(--c-gold)/.07)}.automatic-note>span{color:rgb(var(--c-gold-dark));font-size:1.3rem}.automatic-note strong{font-size:.75rem}.automatic-note p{margin-top:.4rem;color:rgb(var(--c-ink-muted));font-size:.67rem;line-height:1.7}.fulfillment-flow h3{font-size:.75rem;font-weight:500}.fulfillment-flow ol{display:grid;gap:.1rem;margin-top:.85rem}.fulfillment-flow li{position:relative;display:flex;align-items:center;gap:.7rem;min-height:2rem;color:rgb(var(--c-ink-muted));font-size:.67rem}.fulfillment-flow li:not(:last-child)::after{content:'';position:absolute;top:1.5rem;inset-inline-start:.68rem;width:1px;height:1.1rem;background:rgb(var(--c-ink)/.15)}.fulfillment-flow li i{display:grid;place-items:center;z-index:1;width:1.4rem;height:1.4rem;border:1px solid rgb(var(--c-ink)/.18);border-radius:50%;background:rgb(var(--c-parchment));font-size:.58rem}.fulfillment-flow li.done{color:rgb(var(--c-ink))}.fulfillment-flow li.done i{border-color:rgb(var(--c-gold));background:rgb(var(--c-gold)/.13);color:rgb(var(--c-gold-dark))}.fulfillment-flow li.current i{box-shadow:0 0 0 5px rgb(var(--c-gold)/.09)}.flow-warning{margin-top:.8rem;padding:.65rem;background:rgba(185,135,54,.08);color:#946a28;font-size:.65rem;line-height:1.7}.fulfillment-action{width:100%;margin-top:1rem}.detail-slide-enter-active,.detail-slide-leave-active{transition:opacity .2s,transform .3s cubic-bezier(.16,1,.3,1)}.detail-slide-enter-from,.detail-slide-leave-to{opacity:0;transform:translateX(12px)}
@media(max-width:1100px){.orders-workspace{grid-template-columns:1fr}.order-detail{position:static}.detail-placeholder{display:none}}@media(max-width:760px){.orders-intro{flex-direction:column}.payment-pulse{grid-template-columns:repeat(2,1fr)}.order-row--head{display:none}.order-row{grid-template-columns:1fr 1fr}.order-row>*:nth-child(2){grid-column:1/-1;grid-row:2}.order-row>*:nth-child(5){text-align:end}.order-filters{align-items:flex-end}.filter-tabs{overflow:auto;max-width:80%}}@media(prefers-reduced-motion:reduce){.pulse-card,.detail-slide-enter-active,.detail-slide-leave-active{transition:none}}
</style>
