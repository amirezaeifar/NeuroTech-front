<script setup>
import { computed, ref } from 'vue'
import { productsApi } from '../../api/products.js'
import { renderArticle } from '../../utils/articleMarkdown.js'

const props = defineProps({ modelValue: { type: String, default: '' }, lang: { type: String, default: 'en' } })
const emit = defineEmits(['update:modelValue'])
const input = ref(null)
const uploading = ref(false)
const error = ref('')
const preview = computed(() => renderArticle(props.modelValue))
const insert = (before, after = before, placeholder = '') => {
  const el = input.value
  const start = el.selectionStart, end = el.selectionEnd
  const selected = props.modelValue.slice(start, end) || placeholder
  const value = props.modelValue.slice(0, start) + before + selected + after + props.modelValue.slice(end)
  emit('update:modelValue', value)
  requestAnimationFrame(() => { el.focus(); el.setSelectionRange(start + before.length, start + before.length + selected.length) })
}
const line = (prefix) => {
  const el = input.value, start = el.selectionStart, end = el.selectionEnd
  const beginning = props.modelValue.lastIndexOf('\n', start - 1) + 1
  const finish = props.modelValue.indexOf('\n', end)
  const stop = finish < 0 ? props.modelValue.length : finish
  const block = props.modelValue.slice(beginning, stop) || (props.lang === 'fa' ? 'متن' : 'Text')
  const value = props.modelValue.slice(0, beginning) + block.split('\n').map(row => prefix + row.replace(/^(?:#{1,3}\s+|[-*+]\s+|\d+\.\s+|>\s+)/, '')).join('\n') + props.modelValue.slice(stop)
  emit('update:modelValue', value)
  requestAnimationFrame(() => { el.focus(); el.setSelectionRange(beginning + prefix.length, beginning + prefix.length + block.length) })
}
const link = () => { const url = window.prompt(props.lang === 'fa' ? 'آدرس لینک (https://)' : 'Link URL (https://)'); if (url && /^https?:\/\//i.test(url)) insert('[', `](${url})`, props.lang === 'fa' ? 'متن لینک' : 'Link text') }
const uploadImage = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value = true; error.value = ''
  try { const response = await productsApi.upload(file); const url = response.data.url; insert('![', `](${url})`, file.name.replace(/\.[^.]+$/, '')) }
  catch (problem) { error.value = problem.message }
  finally { uploading.value = false; event.target.value = '' }
}
</script>
<template>
  <div>
    <div class="flex flex-wrap gap-1 rounded-t-lg border border-parchment-deep bg-parchment p-2" :dir="lang === 'fa' ? 'rtl' : 'ltr'">
      <button type="button" class="editor-tool" :title="lang === 'fa' ? 'عنوان اصلی' : 'Heading 1'" @click="line('# ')">H1</button>
      <button type="button" class="editor-tool" :title="lang === 'fa' ? 'عنوان بخش' : 'Heading 2'" @click="line('## ')">H2</button>
      <button type="button" class="editor-tool" :title="lang === 'fa' ? 'عنوان فرعی' : 'Heading 3'" @click="line('### ')">H3</button>
      <button type="button" class="editor-tool font-bold" title="Bold" @click="insert('**', '**', lang === 'fa' ? 'متن' : 'Text')">B</button>
      <button type="button" class="editor-tool italic" title="Italic" @click="insert('*', '*', lang === 'fa' ? 'متن' : 'Text')">I</button>
      <button type="button" class="editor-tool underline" :title="lang === 'fa' ? 'متن خط‌خورده' : 'Strikethrough'" @click="insert('~~', '~~', lang === 'fa' ? 'متن' : 'Text')">S</button>
      <button type="button" class="editor-tool" title="List" @click="line('- ')">☷</button>
      <button type="button" class="editor-tool" :title="lang === 'fa' ? 'فهرست شماره‌دار' : 'Numbered list'" @click="line('1. ')">1.</button>
      <button type="button" class="editor-tool" :title="lang === 'fa' ? 'نقل‌قول' : 'Quote'" @click="line('> ')">❝</button>
      <button type="button" class="editor-tool" :title="lang === 'fa' ? 'جداکننده' : 'Divider'" @click="insert('\n---\n', '', '')">—</button>
      <button type="button" class="editor-tool" title="Link" @click="link">↗</button>
      <label class="editor-tool cursor-pointer" :title="lang === 'fa' ? 'افزودن تصویر' : 'Insert image'">{{ uploading ? '…' : '▧' }}<input type="file" accept="image/png,image/jpeg,image/webp" class="sr-only" @change="uploadImage"></label>
    </div>
    <textarea ref="input" :value="modelValue" rows="13" required class="admin-textarea !rounded-t-none" :dir="lang === 'fa' ? 'rtl' : 'ltr'" @input="emit('update:modelValue', $event.target.value)"></textarea>
    <p v-if="error" class="mt-1 text-xs text-red-700">{{ error }}</p>
    <details class="mt-2 rounded-lg border border-parchment-deep p-3"><summary class="cursor-pointer text-xs text-ink-muted">{{ lang === 'fa' ? 'پیش‌نمایش مقاله' : 'Article preview' }}</summary><div class="article-prose mt-4" v-html="preview"></div></details>
  </div>
</template>
<style scoped>
.editor-tool { min-width: 2.2rem; padding: .35rem .55rem; border-radius: .35rem; color: rgb(var(--c-ink)); font-size: .8rem; }
.editor-tool:hover, .editor-tool:focus-visible { background: rgb(var(--c-gold) / .16); }
.article-prose :deep(h1) { font-size: 1.6rem; font-weight: 700; }
.article-prose :deep(h2) { font-size: 1.35rem; font-weight: 700; }
.article-prose :deep(h3) { font-size: 1.15rem; font-weight: 700; }
.article-prose :deep(p), .article-prose :deep(ul), .article-prose :deep(ol), .article-prose :deep(blockquote) { margin: .8rem 0; line-height: 1.8; }
.article-prose :deep(ul) { list-style: disc; padding-inline-start: 1.5rem; }
.article-prose :deep(ol) { list-style: decimal; padding-inline-start: 1.5rem; }
.article-prose :deep(blockquote) { border-inline-start: 3px solid rgb(var(--c-gold)); padding-inline-start: 1rem; }
.article-prose :deep(hr) { border-color: rgb(var(--c-gold) / .5); margin: 1.5rem 0; }
.article-prose :deep(img) { max-width: 100%; border-radius: .5rem; }
.article-prose :deep(a) { color: rgb(var(--c-gold-dark)); text-decoration: underline; }
</style>
