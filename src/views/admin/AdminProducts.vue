<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { productsApi } from '../../api/products.js'
import { resolveApiUrl } from '../../api/client.js'
import { validateSection } from '../../utils/validation.js'
import DetailFields from '../../components/admin/DetailFields.vue'
import AdminToggle from '../../components/admin/AdminToggle.vue'
import ProductIcon from '../../components/ProductIcon.vue'
import { emptyDetails, productSchema } from '../../data/editorSchemas.js'
import { productIcons } from '../../data/productIcons.js'
import { documentTypes, documentTypeLabel } from '../../data/documentTypes.js'

const { locale, t } = useI18n()
const fa = computed(() => locale.value === 'fa')
const tr = (en, faText) => fa.value ? faText : en
const products = ref([])
const categories = ref([])
const draft = ref(null)
const activeLanguage = ref('fa')
const busy = ref(false)
const notice = ref('')
const saveNotice = ref('')
const showPriceError = ref(false)
const categoryDraft = ref({ en: '', fa: '' })
const confirmingCategoryDelete = ref(null)
const confirmingProductDelete = ref(null)
const currencies = ['IRR', 'USD']
const retiredDetailFields = new Set(['priceNote', 'ecosystemNote'])

const productFieldLabels = computed(() => ({
  availability: tr('Availability', 'وضعیت سفارش'),
  leadTime: tr('Lead time', 'زمان تحویل'),
  overviewLead: tr('Introduction title', 'عنوان معرفی'),
  overviewBody: tr('Overview description', 'توضیحات معرفی'),
  blueprintLead: tr('Technical blueprint description', 'توضیحات نقشهٔ فنی'),
  badges: tr('Product badges', 'نشان‌های محصول'),
  keyFeatures: t('products.detail.featuresTitle'),
  reviews: t('products.detail.reviewsTitle'),
}))

const detailGroups = computed(() => [
  { key: 'overview', title: t('products.detail.overviewTitle'), fields: ['overviewLead', 'overviewBody', 'badges'] },
  { key: 'blueprint', title: t('products.detail.blueprintTitle'), fields: ['blueprintLead', 'keyFeatures'] },
])
const availabilityOptions = (code) => code === 'fa'
  ? ['قابل سفارش', 'موجودی محدود', 'پیش‌سفارش', 'در حال حاضر ناموجود']
  : ['Available to order', 'Limited availability', 'Pre-order', 'Currently unavailable']
const detailSchema = (fields) => Object.fromEntries(fields.map((key) => [key, productSchema[key]]))
const detailValues = (code, fields) => Object.fromEntries(fields.map((key) => [key, translation(code).details[key]]))
const updateDetailGroup = (code, values) => { translation(code).details = { ...translation(code).details, ...values } }
const normalizeDetails = (details = {}) => {
  const normalized = Object.fromEntries(Object.entries(productSchema)
    .filter(([key]) => !retiredDetailFields.has(key))
    .map(([key, fallback]) => [key, details[key] ?? (Array.isArray(fallback) ? [] : '')]))
  const legacyIcons = { FDA: 'clinical', CE: 'shield', ISO: 'certificate', IEC: 'precision' }
  normalized.certs = (normalized.certs || []).map(({ mark, name, note }) => ({ mark: productIcons.some((icon) => icon.key === mark) ? mark : (legacyIcons[mark] || 'certificate'), name: name || '', note: note || '' }))
  normalized.trials = (normalized.trials || []).map(({ stat, note }) => ({ stat: stat || '', note: note || '' }))
  normalized.ecosystem = (normalized.ecosystem || []).map(({ name, desc }) => ({ name: name || '', desc: desc || '' }))
  normalized.docs = (normalized.docs || []).map(({ name, type, url }) => ({ name: name || '', type: documentTypes.includes(type) ? type : 'PDF', url: url || '' }))
  normalized.specs = (normalized.specs || []).map(({ label, value }) => ({ label: label || '', value: value || '' }))
  return normalized
}

const revealEditor = () => nextTick(() => document.getElementById('content-editor')?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
const emptyTranslation = (code) => ({ locale: code, name: '', short_description: '', description: '', details: { ...emptyDetails(productSchema), availability: availabilityOptions(code)[0] } })
const translation = (code) => draft.value?.translations.find((item) => item.locale === code)
const normalizeDraft = () => {
  draft.value.translations = ['en', 'fa'].map((code) => {
    const current = draft.value.translations?.find((item) => item.locale === code) || emptyTranslation(code)
    const details = normalizeDetails(current.details)
    details.availability ||= availabilityOptions(code)[0]
    return { ...emptyTranslation(code), ...current, details }
  })
}

const load = async () => {
  busy.value = true
  const [productResult, categoryResult] = await Promise.allSettled([productsApi.adminList(), productsApi.adminCategories()])
  if (productResult.status === 'fulfilled') products.value = productResult.value.data
  if (categoryResult.status === 'fulfilled') categories.value = categoryResult.value.data
  const problem = [productResult, categoryResult].find((result) => result.status === 'rejected')
  if (problem) notice.value = problem.reason.message
  busy.value = false
}

const createProduct = () => {
  saveNotice.value = ''
  showPriceError.value = false
  activeLanguage.value = 'fa'
  draft.value = { id: null, sku: '', category: categories.value[0]?.slug || '', sale_mode: 'inquiry', stock_quantity: null, published: false, translations: [emptyTranslation('en'), emptyTranslation('fa')], prices: [], media: [] }
  revealEditor()
}

const editProduct = (item) => {
  saveNotice.value = ''
  showPriceError.value = false
  activeLanguage.value = 'fa'
  draft.value = JSON.parse(JSON.stringify(item))
  normalizeDraft()
  revealEditor()
}

const normalizedPayload = () => {
  const item = draft.value
  const seenCurrencies = new Set()
  const prices = item.sale_mode === 'direct' ? item.prices
    .filter((price) => currencies.includes(price.currency) && !seenCurrencies.has(price.currency) && seenCurrencies.add(price.currency))
    .slice(0, 2)
    .map((price) => ({ currency: price.currency, amount_minor: Math.max(0, Number(price.amount_minor) || 0) })) : []
  return {
    sku: item.sku,
    category_slug: item.category,
    sale_mode: item.sale_mode,
    stock_quantity: item.sale_mode === 'direct' ? Number(item.stock_quantity || 0) : null,
    translations: item.translations.map(({ locale: code, name, short_description, details }) => ({ locale: code, name, short_description, details: normalizeDetails(details) })),
    prices,
    media: item.media.map((media, index) => ({ stored_file_id: media.stored_file_id, external_url: media.external_url || null, alt_text: media.alt_text || '', position: index })),
  }
}

const save = async () => {
  saveNotice.value = ''
  showPriceError.value = false
  if (draft.value.sale_mode === 'direct' && !draft.value.prices.length) {
    showPriceError.value = true
    return
  }
  const editor = document.getElementById('content-editor')
  if (!validateSection(editor)) {
    const step = editor?.querySelector('[aria-invalid="true"]')?.closest('[data-language-step]')?.dataset.languageStep
    if (step) activeLanguage.value = step
    return
  }
  busy.value = true
  notice.value = ''
  try {
    const result = draft.value.id ? await productsApi.adminUpdate(draft.value.id, normalizedPayload()) : await productsApi.adminCreate(normalizedPayload())
    if (result.data?.approval) {
      saveNotice.value = tr('Sent to the principal approval queue.', 'درخواست به صف تأیید مدیر اصلی ارسال شد.')
    } else {
      draft.value = result.data
      normalizeDraft()
      saveNotice.value = tr('Product saved.', 'محصول ذخیره شد.')
    }
    await load()
    revealEditor()
  } catch (error) { notice.value = error.message } finally { busy.value = false }
}

const togglePublished = async (item) => {
  try {
    const result = await (item.published ? productsApi.adminUnpublish(item.id) : productsApi.adminPublish(item.id))
    if (result.data?.approval) notice.value = tr('Change sent for approval.', 'تغییر برای تأیید ارسال شد.')
    await load()
  } catch (error) { notice.value = error.message }
}
const archive = async (item) => {
  if (!confirm(tr('Archive this product?', 'این محصول بایگانی شود؟'))) return
  await productsApi.adminArchive(item.id)
  draft.value = null
  await load()
}
const archiveFromList = async (item) => {
  if (confirmingProductDelete.value !== item.id) {
    confirmingProductDelete.value = item.id
    return
  }
  busy.value = true
  notice.value = ''
  try {
    await productsApi.adminArchive(item.id)
    if (draft.value?.id === item.id) draft.value = null
    confirmingProductDelete.value = null
    await load()
    notice.value = tr('Product deleted.', 'محصول حذف شد.')
  } catch (error) { notice.value = error.message } finally { busy.value = false }
}
const availableCurrencies = (index) => currencies.filter((currency) => currency === draft.value.prices[index].currency || !draft.value.prices.some((price, priceIndex) => priceIndex !== index && price.currency === currency))
const addPrice = () => {
  const currency = currencies.find((item) => !draft.value.prices.some((price) => price.currency === item))
  if (currency) {
    draft.value.prices.push({ currency, amount_minor: 0 })
    showPriceError.value = false
  }
}
const uploadImage = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  busy.value = true
  try {
    const result = await productsApi.upload(file)
    draft.value.media.push({ stored_file_id: result.data.id, file_url: result.data.url, alt_text: '', external_url: null })
  } catch (error) { notice.value = error.message } finally { busy.value = false; event.target.value = '' }
}
const addDetailItem = (code, key, item) => translation(code).details[key].push(item)
const removeDetailItem = (code, key, index) => translation(code).details[key].splice(index, 1)
const uploadDocument = async (event, code, index) => {
  const file = event.target.files?.[0]
  if (!file) return
  busy.value = true
  try {
    const result = await productsApi.upload(file)
    const document = translation(code).details.docs[index]
    document.url = resolveApiUrl(result.data.url)
    document.name ||= file.name.replace(/\.[^.]+$/, '')
    const extension = file.name.split('.').pop()?.toUpperCase()
    if (documentTypes.includes(extension)) document.type = extension
  } catch (error) { notice.value = error.message } finally { busy.value = false; event.target.value = '' }
}
const brochureUrl = computed(() => draft.value ? (translation('fa')?.details.brochureUrl || translation('en')?.details.brochureUrl || '') : '')
const uploadBrochure = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  busy.value = true
  try {
    const result = await productsApi.upload(file)
    const url = resolveApiUrl(result.data.url)
    draft.value.translations.forEach((item) => { item.details.brochureUrl = url })
    notice.value = tr('Brochure uploaded. Save the product to apply it.', 'بروشور آپلود شد؛ برای اعمال آن محصول را ذخیره کنید.')
  } catch (error) { notice.value = error.message } finally { busy.value = false; event.target.value = '' }
}
const removeBrochure = () => draft.value.translations.forEach((item) => { item.details.brochureUrl = '' })
const addCategory = async () => {
  busy.value = true
  notice.value = ''
  try {
    await productsApi.createCategory({ position: categories.value.length, translations: [{ locale: 'en', title: categoryDraft.value.en }, { locale: 'fa', title: categoryDraft.value.fa }] })
    categoryDraft.value = { en: '', fa: '' }
    categories.value = (await productsApi.adminCategories()).data
    notice.value = tr('Category added.', 'دسته‌بندی اضافه شد.')
  } catch (error) { notice.value = error.message } finally { busy.value = false }
}
const categoryTitle = (category, code) => category.translations?.find((item) => item.locale === code)?.title || category.translations?.find((item) => item.locale === 'en')?.title || category.slug
const productTitle = (product) => product.translations?.find((item) => item.locale === locale.value)?.name || product.name
const formatNumber = (value) => value == null ? '—' : new Intl.NumberFormat(locale.value).format(value)
const productCategory = (product) => {
  const category = categories.value.find((item) => item.slug === product.category)
  return category ? categoryTitle(category, locale.value) : product.category_title
}
const archiveCategory = async (category) => {
  if (confirmingCategoryDelete.value !== category.id) {
    confirmingCategoryDelete.value = category.id
    return
  }
  busy.value = true
  notice.value = ''
  try {
    await productsApi.archiveCategory(category.id)
    confirmingCategoryDelete.value = null
    categories.value = (await productsApi.adminCategories()).data
    if (draft.value?.category === category.slug) draft.value.category = categories.value[0]?.slug || ''
    notice.value = tr('Category deleted.', 'دسته‌بندی حذف شد.')
  } catch (error) {
    notice.value = error.status === 409
      ? tr('Archive this category’s products before deleting it.', 'پیش از حذف این دسته‌بندی، محصولات آن را بایگانی کنید.')
      : error.message
  } finally { busy.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div><p class="admin-eyebrow">{{ tr('Commerce content', 'محتوای فروشگاه') }}</p><h2 class="admin-h1 mt-2">{{ tr('Products', 'محصولات') }}</h2></div>
      <button class="admin-btn admin-btn-primary" type="button" @click="createProduct">{{ tr('Add product', 'افزودن محصول') }}</button>
    </div>

    <p v-if="notice" class="admin-panel mt-5 p-4 text-sm">{{ notice }}</p>

    <div class="admin-card mt-7 p-6 overflow-x-auto">
      <table class="admin-table min-w-[760px]">
        <thead><tr><th>{{ tr('Product', 'محصول') }}</th><th>{{ tr('Category', 'دسته‌بندی') }}</th><th>{{ tr('Mode', 'نوع فروش') }}</th><th>{{ tr('Stock', 'موجودی') }}</th><th>{{ tr('Published', 'انتشار') }}</th><th></th></tr></thead>
        <tbody><tr v-for="item in products" :key="item.id"><td><strong>{{ productTitle(item) }}</strong></td><td>{{ productCategory(item) }}</td><td>{{ item.sale_mode === 'direct' ? tr('Direct', 'مستقیم') : tr('Inquiry', 'استعلام') }}</td><td>{{ formatNumber(item.stock_quantity) }}</td><td><AdminToggle :model-value="item.published" @update:model-value="togglePublished(item)" /></td><td class="text-end"><div class="flex justify-end gap-2"><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="editProduct(item)">{{ tr('Edit', 'ویرایش') }}</button><button class="admin-btn admin-btn-danger admin-btn-sm" :disabled="busy" @click="archiveFromList(item)">{{ confirmingProductDelete === item.id ? tr('Confirm delete', 'تأیید حذف') : tr('Delete', 'حذف') }}</button></div></td></tr></tbody>
      </table>
      <p v-if="!busy && !products.length" class="py-8 text-center text-ink-muted">{{ tr('No products yet.', 'هنوز محصولی وجود ندارد.') }}</p>
    </div>

    <section id="content-editor" v-if="draft" class="admin-card mt-7 p-6 md:p-8 space-y-6 scroll-mt-8">
      <div class="flex items-start justify-between gap-4"><h3 class="admin-h2">{{ draft.id ? tr('Edit product', 'ویرایش محصول') : tr('New product', 'محصول جدید') }}</h3><button class="admin-btn admin-btn-ghost admin-btn-sm shrink-0" @click="draft = null">{{ tr('Close', 'بستن') }}</button></div>
      <div class="grid md:grid-cols-3 gap-4">
        <label><span class="admin-label">{{ t('products.detail.skuLabel') }}</span><input v-model.trim="draft.sku" required class="admin-input" dir="ltr"></label>
        <label><span class="admin-label">{{ tr('Category', 'دسته‌بندی') }}</span><select v-model="draft.category" required class="admin-select"><option v-for="category in categories" :key="category.id" :value="category.slug">{{ categoryTitle(category, locale) }}</option></select></label>
        <label><span class="admin-label">{{ tr('Sale mode', 'نوع فروش') }}</span><select v-model="draft.sale_mode" class="admin-select"><option value="direct">{{ tr('Direct sale', 'فروش مستقیم') }}</option><option value="inquiry">{{ tr('Contact for quote', 'استعلام از طریق تماس') }}</option></select></label>
      </div>
      <div v-if="draft.sale_mode === 'direct'" class="admin-panel p-5">
        <div class="mb-4 flex items-center justify-between gap-3"><h4 class="admin-h2">{{ tr('Inventory and prices', 'موجودی و قیمت‌ها') }}</h4><button v-if="draft.prices.length < 2" type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addPrice">{{ tr('Add price', 'افزودن قیمت') }}</button></div>
        <div class="grid gap-4 lg:grid-cols-[minmax(150px,220px),minmax(0,1fr)] lg:items-start">
          <label><span class="admin-label">{{ tr('Stock', 'موجودی') }}</span><input v-model.number="draft.stock_quantity" required type="number" min="0" class="admin-input"></label>
          <div>
            <div class="space-y-3">
              <div v-for="(price, index) in draft.prices" :key="index" class="grid gap-2 sm:grid-cols-[120px,minmax(0,1fr),auto] sm:items-end">
              <label><span class="admin-label">{{ tr('Currency', 'واحد') }}</span><select v-model="price.currency" required class="admin-select"><option v-for="currency in availableCurrencies(index)" :key="currency">{{ currency }}</option></select></label>
              <label><span class="admin-label">{{ tr('Amount', 'مبلغ') }}</span><input v-model.number="price.amount_minor" required type="number" min="1" class="admin-input"></label>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm self-end" @click="draft.prices.splice(index, 1)">{{ tr('Remove', 'حذف') }}</button>
              </div>
              <p v-if="showPriceError && !draft.prices.length" class="field-error" role="alert">{{ tr('Add an IRR or USD price.', 'یک قیمت ریالی یا دلاری اضافه کنید.') }}</p>
            </div>
          </div>
        </div>
      </div>

      <section class="border-t border-parchment-deep pt-5">
        <div class="flex items-center justify-between gap-3"><h4 class="admin-h2">{{ t('products.detail.galleryViews') }}</h4><label class="admin-btn admin-btn-ghost admin-btn-sm cursor-pointer">{{ tr('Upload image', 'آپلود تصویر') }}<input type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden" @change="uploadImage"></label></div>
        <div class="mt-4 grid gap-4 sm:grid-cols-3"><div v-for="(media, index) in draft.media" :key="media.id || index" class="admin-panel p-3"><img v-if="media.file_url" :src="resolveApiUrl(media.file_url)" class="w-full aspect-video object-cover rounded" alt=""><label class="mt-4 block"><span class="admin-label block">{{ tr('Image description', 'توضیح تصویر') }}</span><input v-model="media.alt_text" class="admin-input mt-2"></label><button class="admin-btn admin-btn-danger admin-btn-sm mt-3" @click="draft.media.splice(index, 1)">{{ tr('Remove', 'حذف') }}</button></div></div>
      </section>

      <div class="flex gap-2 border-b border-parchment-deep" role="tablist">
        <button type="button" class="px-5 py-3 text-sm border-b-2 transition-colors" :class="activeLanguage === 'fa' ? 'border-gold text-gold-dark' : 'border-transparent text-ink-muted'" @click="activeLanguage = 'fa'">{{ tr('Persian information', 'اطلاعات فارسی') }}</button>
        <button type="button" class="px-5 py-3 text-sm border-b-2 transition-colors" :class="activeLanguage === 'en' ? 'border-gold text-gold-dark' : 'border-transparent text-ink-muted'" @click="activeLanguage = 'en'">{{ tr('English information', 'اطلاعات انگلیسی') }}</button>
      </div>
      <div v-for="code in ['fa', 'en']" v-show="activeLanguage === code" :key="code" :data-language-step="code" class="admin-panel p-5 space-y-5" :dir="code === 'fa' ? 'rtl' : 'ltr'">
        <section class="space-y-4">
          <h4 class="admin-h2">{{ tr('Product introduction', 'معرفی محصول') }}</h4>
          <div class="grid gap-4 md:grid-cols-2">
            <label><span class="admin-label">{{ tr('Product name', 'نام محصول') }}</span><input required v-model.trim="translation(code).name" class="admin-input" :placeholder="tr('Enter the product name', 'نام محصول را وارد کنید')"></label>
            <label><span class="admin-label">{{ t('products.detail.essenceLabel') }}</span><input required v-model.trim="translation(code).short_description" class="admin-input" :placeholder="tr('Short description shown in the catalogue', 'توضیح کوتاه نمایش‌داده‌شده در کاتالوگ')"></label>
          </div>
        </section>

        <section v-for="group in detailGroups" :key="group.key" class="border-t border-parchment-deep pt-5 space-y-4">
          <h4 class="admin-h2">{{ group.title }}</h4>
          <DetailFields :model-value="detailValues(code, group.fields)" :schema="detailSchema(group.fields)" :language="locale" :field-labels="productFieldLabels" schema-only @update:model-value="updateDetailGroup(code, $event)" />
        </section>

        <section class="border-t border-parchment-deep pt-5 space-y-5">
          <h4 class="admin-h2">{{ t('products.detail.validationTitle') }}</h4>
          <label class="block"><span class="admin-label">{{ tr('Validation description', 'توضیحات اعتبارسنجی') }}</span><textarea v-model="translation(code).details.validationLead" class="admin-textarea mt-2" rows="3"></textarea></label>

          <div class="space-y-3">
            <div class="flex items-center justify-between gap-3"><span class="admin-label">{{ tr('Validation items', 'موارد اعتبارسنجی') }} · {{ translation(code).details.certs.length }}</span><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addDetailItem(code, 'certs', { mark: 'certificate', name: '', note: '' })">{{ tr('Add item', 'افزودن مورد') }}</button></div>
            <div v-for="(cert, index) in translation(code).details.certs" :key="index" class="admin-panel space-y-4 p-4">
              <div>
                <span class="admin-label">{{ tr('Icon', 'آیکون') }}</span>
                <div class="mt-2 flex flex-wrap gap-2">
                  <button v-for="icon in productIcons" :key="icon.key" type="button" class="flex h-9 w-9 items-center justify-center rounded-md border transition-colors" :class="cert.mark === icon.key ? 'border-gold bg-gold/10 text-gold-dark' : 'border-parchment-deep bg-white text-ink-muted hover:border-gold/60'" :title="icon[fa ? 'fa' : 'en']" :aria-label="icon[fa ? 'fa' : 'en']" @click="cert.mark = icon.key"><ProductIcon :name="icon.key" class="h-4 w-4" /></button>
                </div>
              </div>
              <div class="grid gap-4 md:grid-cols-2">
                <label><span class="admin-label">{{ tr('Title', 'عنوان') }}</span><input v-model="cert.name" required class="admin-input"></label>
                <label><span class="admin-label">{{ tr('Description', 'توضیحات') }}</span><textarea v-model="cert.note" required class="admin-textarea" rows="2"></textarea></label>
              </div>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeDetailItem(code, 'certs', index)">{{ tr('Remove', 'حذف') }}</button>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between gap-3"><span class="admin-label">{{ tr('Clinical evidence items', 'موارد شواهد بالینی') }} · {{ translation(code).details.trials.length }}</span><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addDetailItem(code, 'trials', { stat: '', note: '' })">{{ tr('Add item', 'افزودن مورد') }}</button></div>
            <div v-for="(trial, index) in translation(code).details.trials" :key="index" class="admin-panel p-4">
              <div class="grid gap-4 md:grid-cols-2">
                <label><span class="admin-label">{{ tr('Title', 'عنوان') }}</span><input v-model="trial.stat" required class="admin-input"></label>
                <label><span class="admin-label">{{ tr('Description', 'توضیحات') }}</span><textarea v-model="trial.note" required class="admin-textarea" rows="2"></textarea></label>
              </div>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm mt-3" @click="removeDetailItem(code, 'trials', index)">{{ tr('Remove', 'حذف') }}</button>
            </div>
          </div>
        </section>

        <section class="border-t border-parchment-deep pt-5 space-y-5">
          <h4 class="admin-h2">{{ t('products.detail.ecosystemTitle') }}</h4>
          <label class="block"><span class="admin-label">{{ tr('Ecosystem description', 'توضیحات زیست‌بوم') }}</span><textarea v-model="translation(code).details.ecosystemLead" class="admin-textarea mt-2" rows="3"></textarea></label>
          <div class="flex items-center justify-between gap-3"><span class="admin-label">{{ tr('Ecosystem items', 'موارد زیست‌بوم') }} · {{ translation(code).details.ecosystem.length }}</span><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addDetailItem(code, 'ecosystem', { name: '', desc: '' })">{{ tr('Add item', 'افزودن مورد') }}</button></div>
          <div v-for="(item, index) in translation(code).details.ecosystem" :key="index" class="admin-panel p-4">
            <div class="grid gap-4 md:grid-cols-2">
              <label><span class="admin-label">{{ tr('Title', 'عنوان') }}</span><input v-model="item.name" required class="admin-input"></label>
              <label><span class="admin-label">{{ tr('Description', 'توضیحات') }}</span><textarea v-model="item.desc" required class="admin-textarea" rows="2"></textarea></label>
            </div>
            <button type="button" class="admin-btn admin-btn-danger admin-btn-sm mt-3" @click="removeDetailItem(code, 'ecosystem', index)">{{ tr('Remove', 'حذف') }}</button>
          </div>
        </section>

        <section class="border-t border-parchment-deep pt-5 space-y-6">
          <h4 class="admin-h2">{{ t('products.detail.docsTitle') }}</h4>
          <div class="space-y-3">
            <div class="flex items-center justify-between gap-3"><span class="admin-label">{{ tr('Documentation items', 'موارد مستندات') }} · {{ translation(code).details.docs.length }}</span><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addDetailItem(code, 'docs', { name: '', type: 'PDF', url: '' })">{{ tr('Add item', 'افزودن مورد') }}</button></div>
            <div v-for="(doc, index) in translation(code).details.docs" :key="index" class="admin-panel p-4">
              <div class="grid gap-4 md:grid-cols-3 md:items-end">
                <label><span class="admin-label">{{ tr('Title', 'عنوان') }}</span><input v-model="doc.name" required class="admin-input"></label>
                <label><span class="admin-label">{{ tr('File type', 'نوع فایل') }}</span><select v-model="doc.type" required class="admin-select"><option v-for="type in documentTypes" :key="type" :value="type">{{ documentTypeLabel(type, locale) }}</option></select></label>
                <div><span class="admin-label">{{ tr('Local file', 'فایل محلی') }}</span><label class="admin-btn admin-btn-ghost min-h-[42px] w-full cursor-pointer justify-center">{{ doc.url ? tr('Replace file', 'تغییر فایل') : tr('Choose local file', 'انتخاب فایل محلی') }}<input type="file" class="hidden" :accept="documentTypes.map(type => `.${type.toLowerCase()}`).join(',')" :disabled="busy" @change="uploadDocument($event, code, index)"></label></div>
              </div>
              <div class="mt-3 flex flex-wrap items-center gap-3"><a v-if="doc.url" :href="doc.url" target="_blank" rel="noopener noreferrer" class="text-sm text-gold-dark underline">{{ tr('View uploaded file', 'مشاهده فایل آپلودشده') }}</a><button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeDetailItem(code, 'docs', index)">{{ tr('Remove', 'حذف') }}</button></div>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between gap-3"><span class="admin-label">{{ tr('Technical specification items', 'موارد مشخصات فنی') }} · {{ translation(code).details.specs.length }}</span><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="addDetailItem(code, 'specs', { label: '', value: '' })">{{ tr('Add item', 'افزودن مورد') }}</button></div>
            <div v-for="(spec, index) in translation(code).details.specs" :key="index" class="admin-panel p-4">
              <div class="grid gap-4 md:grid-cols-2">
                <label><span class="admin-label">{{ tr('Title', 'عنوان') }}</span><input v-model="spec.label" required class="admin-input"></label>
                <label><span class="admin-label">{{ tr('Description', 'توضیحات') }}</span><textarea v-model="spec.value" required class="admin-textarea" rows="2"></textarea></label>
              </div>
              <button type="button" class="admin-btn admin-btn-danger admin-btn-sm mt-3" @click="removeDetailItem(code, 'specs', index)">{{ tr('Remove', 'حذف') }}</button>
            </div>
          </div>
        </section>

        <section class="border-t border-parchment-deep pt-5 space-y-4">
          <h4 class="admin-h2">{{ tr('Ordering', 'سفارش') }}</h4>
          <div class="grid gap-4 md:grid-cols-2">
            <label><span class="admin-label">{{ tr('Availability', 'وضعیت سفارش') }}</span><select v-model="translation(code).details.availability" class="admin-select"><option v-for="option in availabilityOptions(code)" :key="option" :value="option">{{ option }}</option></select></label>
            <label><span class="admin-label">{{ tr('Lead time', 'زمان تحویل') }}</span><input v-model.trim="translation(code).details.leadTime" class="admin-input"></label>
          </div>
        </section>

        <section class="border-t border-parchment-deep pt-5 space-y-4">
          <h4 class="admin-h2">{{ t('products.detail.reviewsTitle') }}</h4>
          <DetailFields :model-value="detailValues(code, ['reviews'])" :schema="detailSchema(['reviews'])" :language="locale" :field-labels="productFieldLabels" schema-only @update:model-value="updateDetailGroup(code, $event)" />
        </section>
      </div>

      <section class="admin-panel p-5">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div><h4 class="admin-h2">{{ tr('Product brochure', 'بروشور محصول') }}</h4><p class="mt-1 text-sm text-ink-muted">{{ tr('This PDF is downloaded by the brochure button on the product page.', 'این فایل PDF با دکمه دریافت بروشور در صفحه محصول دانلود می‌شود.') }}</p></div>
          <div class="flex flex-wrap gap-2"><a v-if="brochureUrl" :href="brochureUrl" target="_blank" rel="noopener noreferrer" class="admin-btn admin-btn-ghost admin-btn-sm">{{ tr('View brochure', 'مشاهده بروشور') }}</a><label class="admin-btn admin-btn-ghost admin-btn-sm cursor-pointer">{{ brochureUrl ? tr('Replace PDF', 'تغییر PDF') : tr('Upload brochure PDF', 'آپلود PDF بروشور') }}<input type="file" accept="application/pdf,.pdf" class="hidden" :disabled="busy" @change="uploadBrochure"></label><button v-if="brochureUrl" type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="removeBrochure">{{ tr('Remove', 'حذف') }}</button></div>
        </div>
      </section>
      <div>
        <div class="flex gap-3"><button class="admin-btn admin-btn-primary" :disabled="busy" @click="save">{{ tr('Save', 'ذخیره') }}</button><button v-if="draft.id" class="admin-btn admin-btn-danger" @click="archive(draft)">{{ tr('Archive', 'بایگانی') }}</button></div>
        <p v-if="saveNotice" class="mt-3 text-sm text-emerald-700" role="status">{{ saveNotice }}</p>
      </div>
    </section>

    <section class="admin-card mt-7 p-6">
      <h3 class="admin-h2">{{ tr('Product categories', 'دسته‌بندی محصولات') }}</h3>
      <form class="grid md:grid-cols-[1fr,1fr,auto] gap-3 mt-5 items-end" @submit.prevent="addCategory">
        <label><span class="admin-label">{{ tr('English title', 'عنوان انگلیسی') }}</span><input v-model.trim="categoryDraft.en" required class="admin-input" dir="ltr"></label>
        <label><span class="admin-label">{{ tr('Persian title', 'عنوان فارسی') }}</span><input v-model.trim="categoryDraft.fa" required class="admin-input" dir="rtl"></label>
        <button class="admin-btn admin-btn-primary admin-btn-sm" :disabled="busy">{{ tr('Add category', 'افزودن دسته‌بندی') }}</button>
      </form>
      <div class="mt-6 divide-y divide-parchment-deep border-y border-parchment-deep">
        <div v-for="category in categories" :key="category.id" class="flex flex-wrap items-center justify-between gap-3 py-3">
          <div><strong class="text-sm text-ink">{{ categoryTitle(category, locale) }}</strong><p class="mt-1 text-xs text-ink-muted" dir="auto">{{ categoryTitle(category, locale === 'fa' ? 'en' : 'fa') }}</p></div>
          <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" :disabled="busy" @click="archiveCategory(category)">{{ confirmingCategoryDelete === category.id ? tr('Confirm delete', 'تأیید حذف') : tr('Delete', 'حذف') }}</button>
        </div>
        <p v-if="!categories.length" class="py-5 text-sm text-ink-muted">{{ tr('No categories yet.', 'هنوز دسته‌بندی‌ای وجود ندارد.') }}</p>
      </div>
    </section>
  </div>
</template>
