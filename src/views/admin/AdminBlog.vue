<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { governanceApi } from '../../api/governance.js'
import { productsApi } from '../../api/products.js'
import ArticleEditor from '../../components/admin/ArticleEditor.vue'
import { resolveApiUrl } from '../../api/client.js'
import { validateSection } from '../../utils/validation.js'

const { locale } = useI18n()
const tr = (en, fa) => locale.value === 'fa' ? fa : en
const posts = ref([])
const loading = ref(false)
const listError = ref('')
const formError = ref('')
const notice = ref('')
const saving = ref(false)
const uploadingCover = ref(false)
const editingId = ref(null)
const form = ref(null)
const confirmingDelete = ref(null)
const blank = () => ({
  slug: '', category: 'scientific', cover_url: '', cover_alt: '',
  en: { locale: 'en', title: '', excerpt: '', body: '', seo_title: '', seo_description: '', seo_keywords: '' },
  fa: { locale: 'fa', title: '', excerpt: '', body: '', seo_title: '', seo_description: '', seo_keywords: '' },
})
const draft = ref(blank())
const isEditing = computed(() => Boolean(editingId.value))

const load = async () => {
  loading.value = true
  listError.value = ''
  try { posts.value = (await governanceApi.blogs()).data }
  catch (problem) { listError.value = problem.message }
  finally { loading.value = false }
}

const edit = (post) => {
  const translations = Object.fromEntries((post.translations || []).map((item) => [item.locale, item]))
  editingId.value = post.id
  draft.value = {
    slug: post.slug, category: post.category || 'blog', cover_url: post.cover_url || '', cover_alt: post.cover_alt || '',
    en: { ...blank().en, ...translations.en },
    fa: { ...blank().fa, ...translations.fa },
  }
  formError.value = ''
  notice.value = ''
}

const reset = () => { editingId.value = null; draft.value = blank(); formError.value = ''; notice.value = '' }
const payload = () => ({
  slug: draft.value.slug.trim(),
  category: draft.value.category,
  cover_alt: draft.value.cover_alt.trim(),
  cover_url: draft.value.cover_url.trim() || null,
  translations: [draft.value.en, draft.value.fa],
})
const uploadCover = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  uploadingCover.value = true; formError.value = ''
  try { draft.value.cover_url = (await productsApi.upload(file)).data.url; if (!draft.value.cover_alt) draft.value.cover_alt = file.name.replace(/\.[^.]+$/, '') }
  catch (problem) { formError.value = problem.message }
  finally { uploadingCover.value = false; event.target.value = '' }
}
const cover = (url) => url?.startsWith('/api/') ? resolveApiUrl(url) : url

const save = async () => {
  if (!validateSection(form.value)) return
  saving.value = true
  formError.value = ''
  notice.value = ''
  try {
    const response = isEditing.value
      ? await governanceApi.updateBlog(editingId.value, payload())
      : await governanceApi.createBlog(payload())
    notice.value = response.data?.approval
      ? tr('Sent to the principal approval queue.', 'درخواست به صف تأیید مدیر اصلی ارسال شد.')
      : tr('Article saved.', 'مطلب ذخیره شد.')
    await load()
    if (!isEditing.value) draft.value = blank()
  } catch (problem) { formError.value = problem.message }
  finally { saving.value = false }
}

const changeState = async (post, action) => {
  listError.value = ''
  try {
    const response = await governanceApi[action](post.id)
    notice.value = response?.data?.approval
      ? tr('Change sent for approval.', 'تغییر برای تأیید ارسال شد.')
      : action === 'deleteBlog' ? tr('Article deleted.', 'مطلب حذف شد.') : tr('Status updated.', 'وضعیت به‌روزرسانی شد.')
    await load()
    return true
  } catch (problem) { listError.value = problem.message; return false }
}
const remove = async (post) => {
  if (confirmingDelete.value !== post.id) { confirmingDelete.value = post.id; return }
  confirmingDelete.value = null
  const deleted = await changeState(post, 'deleteBlog')
  if (deleted && editingId.value === post.id) { editingId.value = null; draft.value = blank() }
}

onMounted(load)
</script>

<template>
  <div class="max-w-6xl">
    <p class="admin-eyebrow">{{ tr('Editorial desk', 'میز تحریریه') }}</p>
    <h2 class="admin-h1 mt-2">{{ tr('Articles', 'مقالات') }}</h2>
    <p class="mt-2 text-sm text-ink-muted">{{ tr('Publish scientific articles and blog stories in two languages.', 'مقاله‌های علمی و یادداشت‌های بلاگ را به دو زبان منتشر کنید.') }}</p>

    <form ref="form" class="admin-card mt-7 p-6 md:p-8" novalidate @submit.prevent="save">
      <div class="flex items-center justify-between gap-3"><h3 class="admin-h2">{{ isEditing ? tr('Edit article', 'ویرایش مطلب') : tr('New article', 'مطلب جدید') }}</h3><button v-if="isEditing" type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="reset">{{ tr('Cancel', 'انصراف') }}</button></div>
      <div class="mt-5 grid gap-4 md:grid-cols-3">
        <label><span class="admin-label">Slug</span><input v-model="draft.slug" required pattern="[a-z0-9]+(?:-[a-z0-9]+)*" class="admin-input" dir="ltr"></label>
        <label><span class="admin-label">{{ tr('Section', 'دسته‌بندی') }}</span><select v-model="draft.category" class="admin-select"><option value="scientific">{{ tr('Scientific articles', 'محتوای علمی') }}</option><option value="blog">{{ tr('Blog', 'بلاگ') }}</option></select></label>
        <label><span class="admin-label">{{ tr('Cover URL', 'آدرس تصویر کاور') }}</span><input v-model="draft.cover_url" type="text" pattern="(https?://.*|/api/v1/files/[0-9a-fA-F-]{36})" class="admin-input" dir="ltr"></label>
      </div>
      <div class="mt-4 flex flex-wrap items-center gap-4"><label class="admin-btn admin-btn-ghost cursor-pointer">{{ uploadingCover ? tr('Uploading…', 'در حال بارگذاری…') : tr('Upload cover', 'بارگذاری تصویر اصلی') }}<input type="file" accept="image/png,image/jpeg,image/webp" class="sr-only" @change="uploadCover"></label><img v-if="draft.cover_url" :src="cover(draft.cover_url)" alt="" class="h-16 w-24 rounded-lg object-cover"><label class="flex-1"><span class="admin-label">{{ tr('Cover image alt text', 'متن جایگزین تصویر') }}</span><input v-model="draft.cover_alt" class="admin-input"></label></div>
      <div class="mt-6 grid gap-5 lg:grid-cols-2">
        <fieldset v-for="lang in ['en', 'fa']" :key="lang" class="rounded-xl border border-parchment-deep p-5">
          <legend class="px-2 text-sm font-medium text-gold-dark">{{ lang === 'en' ? 'English' : 'فارسی' }}</legend>
          <label><span class="admin-label">{{ tr('Title', 'عنوان') }}</span><input v-model="draft[lang].title" required maxlength="240" class="admin-input" :dir="lang === 'fa' ? 'rtl' : 'ltr'"></label>
          <label class="mt-4 block"><span class="admin-label">{{ tr('Excerpt', 'خلاصه') }}</span><textarea v-model="draft[lang].excerpt" required maxlength="600" rows="2" class="admin-textarea" :dir="lang === 'fa' ? 'rtl' : 'ltr'"></textarea></label>
          <label class="mt-4 block"><span class="admin-label">{{ tr('Body', 'متن') }}</span><ArticleEditor v-model="draft[lang].body" :lang="lang" /></label>
          <details class="mt-5 border-t border-parchment-deep pt-4"><summary class="cursor-pointer text-sm text-gold-dark">SEO</summary><div class="mt-4 space-y-3"><label class="block"><span class="admin-label">SEO title</span><input v-model="draft[lang].seo_title" maxlength="240" class="admin-input"></label><label class="block"><span class="admin-label">Meta description</span><textarea v-model="draft[lang].seo_description" maxlength="600" rows="2" class="admin-textarea"></textarea></label><label class="block"><span class="admin-label">Keywords</span><input v-model="draft[lang].seo_keywords" maxlength="500" class="admin-input"></label></div></details>
        </fieldset>
      </div>
      <button type="submit" :disabled="saving" class="admin-btn admin-btn-primary mt-5">{{ tr('Save article', 'ذخیره مطلب') }}</button>
      <p v-if="formError" class="mt-3 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">{{ formError }}</p>
      <p v-if="notice" class="mt-3 text-sm text-emerald-700" role="status">{{ notice }}</p>
    </form>

    <section class="admin-card mt-7 p-6 md:p-8">
      <h3 class="admin-h2">{{ tr('Articles', 'مطالب') }}</h3>
      <p v-if="listError" class="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">{{ listError }}</p>
      <p v-if="loading" class="py-8 text-center text-sm text-ink-muted">{{ tr('Loading…', 'در حال دریافت…') }}</p>
      <div v-else class="mt-5 space-y-3">
        <article v-for="post in posts" :key="post.id" class="flex flex-col gap-3 rounded-xl border border-parchment-deep p-4 md:flex-row md:items-center md:justify-between">
          <div><h4 class="font-medium text-ink">{{ post.title }}</h4><p class="mt-1 text-xs text-ink-muted" dir="ltr">/{{ post.slug }} · {{ post.category === 'scientific' ? tr('Scientific', 'علمی') : tr('Blog', 'بلاگ') }}</p></div>
          <div class="flex flex-wrap items-center gap-2">
            <span :class="['admin-badge', post.published ? 'admin-badge-green' : 'admin-badge-muted']">{{ post.published ? tr('Published', 'منتشرشده') : tr('Draft', 'پیش‌نویس') }}</span>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="edit(post)">{{ tr('Edit', 'ویرایش') }}</button>
            <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="changeState(post, post.published ? 'unpublishBlog' : 'publishBlog')">{{ post.published ? tr('Unpublish', 'لغو انتشار') : tr('Publish', 'انتشار') }}</button>
            <button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="remove(post)">{{ confirmingDelete === post.id ? tr('Are you sure? Confirm delete', 'مطمئنی؟ تأیید حذف') : tr('Delete', 'حذف') }}</button>
          </div>
        </article>
        <p v-if="!posts.length" class="py-8 text-center text-sm italic text-ink-muted">{{ tr('No articles yet.', 'هنوز مطلبی ثبت نشده است.') }}</p>
      </div>
    </section>
  </div>
</template>
