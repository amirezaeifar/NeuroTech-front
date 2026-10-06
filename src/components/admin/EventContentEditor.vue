<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { productsApi } from '../../api/products.js'
import { resolveApiUrl } from '../../api/client.js'

const props = defineProps({ content: { type: Object, required: true } })
const emit = defineEmits(['uploading'])
const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const uploading = ref(false), error = ref('')
const sections = computed(() => [
  { key: 'gallery', name: tr('Photo gallery', 'گالری تصاویر'), accept: 'image/png,image/jpeg,image/webp', template: { name: '', url: '', type: '', size: '' } },
  { key: 'videos', name: tr('Recordings', 'ویدئوهای رویداد'), accept: 'video/mp4,video/webm', template: { name: '', url: '', type: '', size: '' } },
  { key: 'documents', name: tr('Downloads', 'فایل‌های قابل دریافت'), accept: '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.zip,.txt,.csv', template: { name: '', url: '', type: '', size: '' } },
  { key: 'agenda', name: tr('Programme', 'برنامهٔ رویداد'), template: { time: '', title: '', detail: '' } },
  { key: 'faq', name: tr('Questions and answers', 'پرسش و پاسخ'), template: { q: '', a: '' } },
])
const add = (section) => { (props.content[section.key] ||= []).push({ ...section.template }) }
const move = (items, index, direction) => { const next = index + direction; if (next >= 0 && next < items.length) [items[index], items[next]] = [items[next], items[index]] }
const upload = async (event, item) => {
  const file = event.target.files?.[0]; if (!file) return
  uploading.value = true; emit('uploading', true); error.value = ''
  try {
    const response = await productsApi.upload(file)
    item.url = response.data.url; item.name ||= file.name
    item.type = file.name.split('.').pop().toUpperCase()
    item.size = file.size >= 1048576 ? `${(file.size / 1048576).toFixed(1)} MB` : `${Math.ceil(file.size / 1024)} KB`
  } catch (problem) { error.value = problem.message }
  finally { uploading.value = false; emit('uploading', false); event.target.value = '' }
}
const asset = (url) => url?.startsWith('/api/') ? resolveApiUrl(url) : url
</script>

<template>
  <div class="space-y-6">
    <p class="text-sm text-ink-muted">{{ tr('Manage the existing page sections. Files become public when uploaded; save the event to attach them.', 'بخش‌های همین صفحهٔ رویداد را مدیریت کنید. فایل بارگذاری‌شده عمومی است؛ برای اتصال آن به رویداد، تغییرات را ذخیره کنید.') }}</p>
    <p v-if="error" role="alert" class="text-sm text-red-600">{{ error }}</p>
    <section v-for="section in sections" :key="section.key" class="admin-panel p-4 md:p-5">
      <div class="flex items-center justify-between gap-3"><h4 class="admin-h2">{{ section.name }}</h4><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="add(section)">{{ tr('Add', 'افزودن') }}</button></div>
      <p v-if="!content[section.key]?.length" class="mt-3 text-xs text-ink-muted">{{ tr('This section is hidden until content is added.', 'تا زمان افزودن محتوا، این بخش نمایش داده نمی‌شود.') }}</p>
      <div v-for="(item, index) in content[section.key]" :key="index" class="mt-4 border-t border-parchment-deep pt-4 space-y-3">
        <div class="flex justify-between items-center"><span class="text-xs text-ink-muted">{{ index + 1 }}</span><div class="flex gap-2"><button type="button" :disabled="index===0" class="admin-btn admin-btn-ghost admin-btn-sm" :aria-label="tr('Move up','انتقال به بالا')" @click="move(content[section.key],index,-1)">↑</button><button type="button" :disabled="index===content[section.key].length-1" class="admin-btn admin-btn-ghost admin-btn-sm" :aria-label="tr('Move down','انتقال به پایین')" @click="move(content[section.key],index,1)">↓</button><button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="content[section.key].splice(index,1)">{{ tr('Remove','حذف') }}</button></div></div>
        <template v-if="section.accept">
          <input required maxlength="240" v-model="item.name" class="admin-input" :aria-label="tr('Title or caption','عنوان یا توضیح تصویر')" :placeholder="tr('Title or caption','عنوان یا توضیح تصویر')">
          <div class="flex flex-wrap gap-3"><input required pattern="(https://.*|/api/v1/files/[0-9a-fA-F-]{36})" v-model="item.url" class="admin-input flex-1 min-w-0" dir="ltr" :aria-label="tr('Media address','آدرس رسانه')" placeholder="https://…"><label class="admin-btn admin-btn-ghost cursor-pointer">{{ uploading ? tr('Uploading…','در حال بارگذاری…') : tr('Upload','بارگذاری') }}<input :disabled="uploading" type="file" :accept="section.accept" class="sr-only" @change="upload($event,item)"></label></div>
          <img v-if="section.key==='gallery' && item.url" :src="asset(item.url)" :alt="item.name" class="h-24 w-40 rounded-lg object-cover">
          <div v-if="section.key==='documents'" class="flex gap-3"><input v-model="item.type" class="admin-input" :placeholder="tr('File type','نوع فایل')"><input v-model="item.size" class="admin-input" :placeholder="tr('File size','حجم فایل')"></div>
        </template>
        <template v-else-if="section.key==='agenda'"><input v-model="item.time" class="admin-input" :placeholder="tr('Time','زمان')"><input required v-model="item.title" class="admin-input" :placeholder="tr('Session title','عنوان برنامه')"><textarea v-model="item.detail" class="admin-textarea" :placeholder="tr('Details','توضیحات')"></textarea></template>
        <template v-else><input required v-model="item.q" class="admin-input" :placeholder="tr('Question','پرسش')"><textarea required v-model="item.a" class="admin-textarea" :placeholder="tr('Answer','پاسخ')"></textarea></template>
      </div>
    </section>
    <label class="block"><span class="admin-label">{{ tr('Closing note','یادداشت پایانی') }}</span><textarea v-model="content.closing_note" rows="3" class="admin-textarea"></textarea></label>
  </div>
</template>
