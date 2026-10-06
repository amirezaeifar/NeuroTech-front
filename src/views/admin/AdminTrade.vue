<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { tradeApi } from '../../api/content.js'
import { productsApi } from '../../api/products.js'
import AdminToggle from '../../components/admin/AdminToggle.vue'

const { locale } = useI18n()
const fa = computed(() => locale.value === 'fa')
const tr = (en, faText) => fa.value ? faText : en
const documents = ref([])
const draft = ref(null)
const busy = ref(false)
const notice = ref('')
const emptyTranslation = (code) => ({ locale: code, title: '', doc_type: '', partner_name: '', category: '', location: null, region: null, summary: '', groups: [], groupsText: '[]' })
const translation = (code) => draft.value.translations.find((item) => item.locale === code)
const load = async () => { busy.value = true; try { documents.value = (await tradeApi.adminList()).data } finally { busy.value = false } }
const createDocument = () => { draft.value = { record_id: null, slug: '', id: '', position: documents.value.length, attachment_file_id: null, translations: [emptyTranslation('en'), emptyTranslation('fa')] } }
const editDocument = (item) => { draft.value = JSON.parse(JSON.stringify(item)); draft.value.translations.forEach((t) => { t.groupsText = JSON.stringify(t.groups || [], null, 2) }) }
const payload = () => ({
  ...(draft.value.record_id ? {} : { slug: draft.value.slug }), document_code: draft.value.id,
  position: Number(draft.value.position || 0), attachment_file_id: draft.value.attachment_file_id || null,
  translations: draft.value.translations.map(({ groupsText, ...item }) => ({ ...item, groups: JSON.parse(groupsText || '[]') })),
})
const save = async () => { busy.value = true; notice.value = ''; try { const result = draft.value.record_id ? await tradeApi.update(draft.value.record_id, payload()) : await tradeApi.create(payload()); editDocument(result.data); notice.value = tr('Document saved.', 'سند ذخیره شد.'); await load() } catch (error) { notice.value = error instanceof SyntaxError ? tr('Groups JSON is invalid.', 'JSON بخش‌ها معتبر نیست.') : error.message } finally { busy.value = false } }
const toggle = async (item) => { await (item.published ? tradeApi.unpublish(item.record_id) : tradeApi.publish(item.record_id)); await load() }
const archive = async (item) => { if (!confirm(tr('Archive this document?', 'این سند بایگانی شود؟'))) return; await tradeApi.archive(item.record_id); draft.value = null; await load() }
const uploadPdf = async (event) => { const file = event.target.files?.[0]; if (!file) return; busy.value = true; try { const result = await productsApi.upload(file); draft.value.attachment_file_id = result.data.id } catch (error) { notice.value = error.message } finally { busy.value = false; event.target.value = '' } }
onMounted(load)
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4"><div><p class="admin-eyebrow">{{ tr('Knowledge content', 'محتوای دانش') }}</p><h2 class="admin-h1 mt-2">{{ tr('Global trade documents', 'اسناد تجارت جهانی') }}</h2><p class="mt-2 text-sm text-ink-muted">{{ tr('Manage technical documents, market records and optional PDF attachments.', 'اسناد فنی، گزارش‌های بازار و فایل PDF اختیاری را مدیریت کنید.') }}</p></div><button class="admin-btn admin-btn-primary" @click="createDocument">{{ tr('Add document', 'افزودن سند') }}</button></div>
    <div class="admin-card mt-7 p-6 overflow-x-auto"><table class="admin-table min-w-[760px]"><thead><tr><th>{{ tr('Document', 'سند') }}</th><th>{{ tr('Code', 'کد') }}</th><th>{{ tr('Partner', 'همکار') }}</th><th>{{ tr('Category', 'دسته') }}</th><th>{{ tr('Published', 'انتشار') }}</th><th></th></tr></thead><tbody><tr v-for="item in documents" :key="item.record_id"><td><strong>{{ item.title }}</strong><br><small>{{ item.docType }}</small></td><td class="font-mono">{{ item.id }}</td><td>{{ item.partner }}</td><td>{{ item.category }}</td><td><AdminToggle :model-value="item.published" @update:model-value="toggle(item)" /></td><td><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="editDocument(item)">{{ tr('Edit', 'ویرایش') }}</button></td></tr></tbody></table><p v-if="!busy&&!documents.length" class="py-8 text-center text-ink-muted">{{ tr('No documents yet.', 'هنوز سندی وجود ندارد.') }}</p></div>
    <section v-if="draft" class="admin-card mt-7 p-6 md:p-8 space-y-6">
      <div class="flex justify-between"><h3 class="admin-h2">{{ draft.record_id ? tr('Edit document', 'ویرایش سند') : tr('New document', 'سند جدید') }}</h3><button class="admin-btn admin-btn-ghost admin-btn-sm" @click="draft=null">{{ tr('Close', 'بستن') }}</button></div>
      <div class="grid md:grid-cols-3 gap-4"><label><span class="admin-label">Slug</span><input v-model="draft.slug" :disabled="!!draft.record_id" class="admin-input" dir="ltr"></label><label><span class="admin-label">{{ tr('Document code', 'کد سند') }}</span><input v-model="draft.id" class="admin-input" dir="ltr"></label><label><span class="admin-label">{{ tr('Order', 'ترتیب') }}</span><input v-model.number="draft.position" type="number" min="0" class="admin-input"></label></div>
      <div class="flex gap-3 items-center"><label class="admin-btn admin-btn-ghost cursor-pointer">{{ tr('Upload PDF', 'آپلود PDF') }}<input type="file" accept="application/pdf" class="hidden" @change="uploadPdf"></label><span v-if="draft.attachment_file_id" class="admin-badge admin-badge-green">{{ tr('PDF attached', 'PDF پیوست شد') }}</span><button v-if="draft.attachment_file_id" class="admin-btn admin-btn-danger admin-btn-sm" @click="draft.attachment_file_id=null">{{ tr('Remove', 'حذف') }}</button></div>
      <div v-for="code in ['en','fa']" :key="code" class="admin-panel p-5 space-y-4" :dir="code==='fa'?'rtl':'ltr'"><h4 class="admin-label">{{ code.toUpperCase() }}</h4><div class="grid md:grid-cols-2 gap-4"><input v-model="translation(code).title" class="admin-input" :placeholder="tr('Title','عنوان')"><input v-model="translation(code).doc_type" class="admin-input" :placeholder="tr('Document type','نوع سند')"><input v-model="translation(code).partner_name" class="admin-input" :placeholder="tr('Partner','همکار')"><input v-model="translation(code).category" class="admin-input" :placeholder="tr('Category','دسته')"><input v-model="translation(code).location" class="admin-input" :placeholder="tr('Location','موقعیت')"><input v-model="translation(code).region" class="admin-input" :placeholder="tr('Region','منطقه')"></div><textarea v-model="translation(code).summary" rows="3" class="admin-textarea" :placeholder="tr('Summary','خلاصه')"></textarea><label class="block"><span class="admin-label">{{ tr('Document sections (JSON)', 'بخش‌های سند (JSON)') }}</span><textarea v-model="translation(code).groupsText" rows="12" class="admin-textarea font-mono text-xs" dir="ltr" placeholder='[{"label":"Scope","kind":"list","items":[]}]'></textarea></label></div>
      <div class="flex gap-3"><button class="admin-btn admin-btn-primary" :disabled="busy" @click="save">{{ tr('Save', 'ذخیره') }}</button><button v-if="draft.record_id" class="admin-btn admin-btn-danger" @click="archive(draft)">{{ tr('Archive', 'بایگانی') }}</button></div>
      <p v-if="notice" role="status" class="mt-3 text-sm text-ink-muted">{{ notice }}</p>
    </section>
  </div>
</template>
