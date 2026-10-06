<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { pageContentApi } from '../../api/content.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'
import enMessages from '../../locales/en.json'
import faMessages from '../../locales/fa.json'

const { locale } = useI18n()
const fa = computed(() => locale.value === 'fa')
const tr = (en, faText) => fa.value ? faText : en
const pages = ref([])
const activeKey = ref('academy')
const enContent = ref({})
const faContent = ref({})
const notice = ref('')
const busy = ref(false)
const localeRoot = { academy: 'academy', products: 'products', events: 'events', partners: 'partners', 'global-trade': 'globalTrade' }
const pageLabels = {
  academy: ['Academy', 'آکادمی'],
  products: ['Products', 'محصولات'],
  events: ['Events', 'رویدادها'],
  partners: ['Partners', 'همکاران'],
  'global-trade': ['Global Trade', 'تجارت جهانی'],
}
const active = computed(() => pages.value.find((page) => page.page_key === activeKey.value))

const clone = (value) => JSON.parse(JSON.stringify(value ?? {}))
const isObject = (value) => value && typeof value === 'object' && !Array.isArray(value)
const mergeContent = (base, override) => {
  if (!isObject(base) || !isObject(override)) return clone(override ?? base)
  const result = clone(base)
  Object.entries(override).forEach(([key, value]) => {
    result[key] = isObject(value) && isObject(result[key]) ? mergeContent(result[key], value) : clone(value)
  })
  return result
}
const fieldEntries = (value, path = [], result = []) => {
  if (Array.isArray(value)) {
    value.forEach((item, index) => fieldEntries(item, [...path, index], result))
  } else if (isObject(value)) {
    Object.entries(value).forEach(([key, item]) => fieldEntries(item, [...path, key], result))
  } else {
    result.push({
      key: path.join('.'),
      path,
      label: path.map((part) => typeof part === 'number' ? `#${part + 1}` : part.replaceAll('_', ' ')).join(' › '),
      value: value ?? '',
      type: typeof value,
      multiline: typeof value === 'string' && (value.length > 90 || value.includes('\n')),
    })
  }
  return result
}
const enFields = computed(() => fieldEntries(enContent.value))
const faFields = computed(() => fieldEntries(faContent.value))
const setField = (content, field, rawValue) => {
  let target = content
  field.path.slice(0, -1).forEach((part) => { target = target[part] })
  const key = field.path.at(-1)
  if (field.type === 'number') target[key] = Number(rawValue)
  else if (field.type === 'boolean') target[key] = Boolean(rawValue)
  else target[key] = rawValue
}
const bundledContent = (language) => {
  const root = localeRoot[activeKey.value]
  return clone((language === 'fa' ? faMessages : enMessages)[root] || {})
}
const fillEditor = () => {
  const page = active.value
  const enDraft = page?.translations?.find((item) => item.locale === 'en')?.content || {}
  const faDraft = page?.translations?.find((item) => item.locale === 'fa')?.content || {}
  enContent.value = mergeContent(bundledContent('en'), enDraft)
  faContent.value = mergeContent(bundledContent('fa'), faDraft)
  notice.value = ''
}
const load = async () => {
  busy.value = true
  try {
    pages.value = (await pageContentApi.adminList()).data
    fillEditor()
  } finally {
    busy.value = false
  }
}
const selectPage = (key) => { activeKey.value = key; fillEditor() }
const resetToBundledCopy = () => {
  enContent.value = bundledContent('en')
  faContent.value = bundledContent('fa')
  notice.value = tr('The editor was reset to the built-in website copy. Save to keep it as a draft.', 'ویرایشگر به متن اصلی سایت برگشت. برای نگهداری آن، پیش‌نویس را ذخیره کنید.')
}
const save = async () => {
  busy.value = true
  notice.value = ''
  try {
    await pageContentApi.save(activeKey.value, [
      { locale: 'en', content: enContent.value },
      { locale: 'fa', content: faContent.value },
    ])
    notice.value = tr('Page copy saved as a draft.', 'متن صفحه به‌صورت پیش‌نویس ذخیره شد.')
    await load()
  } catch (error) {
    notice.value = error.message
  } finally {
    busy.value = false
  }
}
const toggle = async (published) => {
  try {
    await (published ? pageContentApi.publish(activeKey.value) : pageContentApi.unpublish(activeKey.value))
    await load()
  } catch (error) {
    notice.value = error.message
  }
}
onMounted(load)
</script>

<template>
  <div>
    <p class="admin-eyebrow">{{ tr('Page copy', 'متن صفحات') }}</p>
    <h2 class="admin-h1 mt-2">{{ tr('Managed page content', 'مدیریت محتوای صفحات') }}</h2>
    <p class="mt-2 max-w-3xl text-sm text-ink-muted leading-relaxed">{{ tr('Edit the Persian and English copy used by the dynamic website sections. Home, About and Contact intentionally remain static.', 'متن فارسی و انگلیسی بخش‌های داینامیک سایت را ویرایش کنید. صفحات خانه، درباره ما و تماس عمداً ثابت می‌مانند.') }}</p>

    <div class="mt-7 flex flex-wrap gap-2">
      <button v-for="page in pages" :key="page.page_key" class="admin-btn admin-btn-sm" :class="activeKey === page.page_key ? 'admin-btn-primary' : 'admin-btn-ghost'" @click="selectPage(page.page_key)">
        {{ tr(...pageLabels[page.page_key]) }}
      </button>
    </div>

    <section v-if="active" class="admin-card mt-6 p-6 md:p-8 space-y-6">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 class="admin-h2">{{ tr(...pageLabels[active.page_key]) }}</h3>
          <p class="mt-1 text-xs text-ink-muted">{{ tr('Save changes as a draft, then publish when they are ready.', 'تغییرات را ابتدا به‌صورت پیش‌نویس ذخیره و پس از آماده‌شدن منتشر کنید.') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <AdminToggle :model-value="active.published" :label="tr('Published', 'منتشرشده')" @update:model-value="toggle" />
          <button class="admin-btn admin-btn-ghost admin-btn-sm" @click="resetToBundledCopy">{{ tr('Reset copy', 'بازگشت به متن اصلی') }}</button>
        </div>
      </div>

      <div class="grid xl:grid-cols-2 gap-6 items-start">
        <div class="admin-panel p-5 space-y-4">
          <h4 class="font-semibold">English</h4>
          <label v-for="field in enFields" :key="field.key" class="block">
            <span class="admin-label">{{ field.label }}</span>
            <textarea v-if="field.multiline" :value="field.value" rows="4" class="admin-textarea" dir="ltr" @input="setField(enContent, field, $event.target.value)"></textarea>
            <input v-else-if="field.type !== 'boolean'" :value="field.value" :type="field.type === 'number' ? 'number' : 'text'" class="admin-input" dir="ltr" @input="setField(enContent, field, $event.target.value)" />
            <input v-else :checked="field.value" type="checkbox" class="toggle toggle-sm" @change="setField(enContent, field, $event.target.checked)" />
          </label>
        </div>

        <div class="admin-panel p-5 space-y-4">
          <h4 class="font-semibold">فارسی</h4>
          <label v-for="field in faFields" :key="field.key" class="block">
            <span class="admin-label">{{ field.label }}</span>
            <textarea v-if="field.multiline" :value="field.value" rows="4" class="admin-textarea" dir="rtl" @input="setField(faContent, field, $event.target.value)"></textarea>
            <input v-else-if="field.type !== 'boolean'" :value="field.value" :type="field.type === 'number' ? 'number' : 'text'" class="admin-input" dir="rtl" @input="setField(faContent, field, $event.target.value)" />
            <input v-else :checked="field.value" type="checkbox" class="toggle toggle-sm" @change="setField(faContent, field, $event.target.checked)" />
          </label>
        </div>
      </div>

      <button class="admin-btn admin-btn-primary" :disabled="busy" @click="save">{{ tr('Save draft', 'ذخیره پیش‌نویس') }}</button>
      <p v-if="notice" role="status" class="mt-3 text-sm text-ink-muted">{{ notice }}</p>
    </section>
  </div>
</template>
