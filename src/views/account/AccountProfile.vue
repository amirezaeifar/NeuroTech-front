<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AccountShell from '../../components/account/AccountShell.vue'
import { userApi } from '../../api/user.js'
import { useAuth } from '../../composables/useAuth.js'
import { resolveApiUrl } from '../../api/client.js'

const { locale } = useI18n()
const { user } = useAuth()
const profile = reactive({ full_name: '', email: '', phone: '', national_id: '', address: '' })
const saved = ref(null)
const loading = ref(true), saving = ref(false), editing = ref(false), error = ref(''), success = ref('')
const avatarBusy = ref(false)
const avatar = computed(() => user.value?.avatar_url ? resolveApiUrl(user.value.avatar_url) : '')
const initial = computed(() => (user.value?.display_name || '?').trim().charAt(0).toLocaleUpperCase(locale.value))
const fields = {
  full_name: ['Full name', 'نام و نام خانوادگی'],
  email: ['Email', 'ایمیل'],
  phone: ['Phone', 'شماره تلفن'],
  national_id: ['National ID', 'کد ملی'],
  address: ['Address', 'نشانی'],
}
const label = (key) => fields[key][locale.value === 'fa' ? 1 : 0]
const apply = (data) => { Object.keys(profile).forEach((key) => { profile[key] = data[key] || '' }); saved.value = { ...profile } }
onMounted(async () => {
  try { apply((await userApi.profile()).data) }
  catch (problem) { error.value = problem.message }
  finally { loading.value = false }
})
const cancel = () => { if (saved.value) apply(saved.value); editing.value = false; error.value = '' }
const uploadAvatar = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 1024 * 1024) {
    error.value = locale.value === 'fa' ? 'عکس باید PNG، JPEG یا WebP و حداکثر ۱ مگابایت باشد.' : 'Use a PNG, JPEG or WebP image up to 1 MB.'
    return
  }
  avatarBusy.value = true; error.value = ''; success.value = ''
  try {
    const response = await userApi.uploadAvatar(file)
    if (user.value) user.value = { ...user.value, avatar_url: response.data.avatar_url }
    success.value = locale.value === 'fa' ? 'عکس پروفایل ذخیره شد.' : 'Profile photo saved.'
  } catch (problem) { error.value = problem.message }
  finally { avatarBusy.value = false }
}
const removeAvatar = async () => {
  avatarBusy.value = true; error.value = ''; success.value = ''
  try {
    await userApi.removeAvatar()
    if (user.value) user.value = { ...user.value, avatar_url: null }
    success.value = locale.value === 'fa' ? 'عکس پروفایل حذف شد.' : 'Profile photo removed.'
  } catch (problem) { error.value = problem.message }
  finally { avatarBusy.value = false }
}
const save = async () => {
  saving.value = true; error.value = ''; success.value = ''
  try {
    const response = await userApi.saveProfile({ ...profile, national_id: profile.national_id || null, address: profile.address || null })
    apply(response.data)
    if (user.value) user.value = { ...user.value, display_name: response.data.full_name }
    editing.value = false
    success.value = locale.value === 'fa' ? 'اطلاعات پروفایل ذخیره شد.' : 'Profile saved.'
  } catch (problem) { error.value = problem.message }
  finally { saving.value = false }
}
</script>

<template>
  <AccountShell section="profile">
    <div class="profile-photo-row">
      <div class="profile-photo" aria-hidden="true"><img v-if="avatar" :src="avatar" alt="" /><span v-else>{{ initial }}</span></div>
      <div class="profile-photo-copy"><strong>{{ locale === 'fa' ? 'عکس پروفایل' : 'Profile photo' }}</strong></div>
      <div class="profile-photo-actions"><label class="profile-photo-button" :class="{ 'is-busy': avatarBusy }">{{ locale === 'fa' ? 'انتخاب عکس' : 'Choose photo' }}<input type="file" accept="image/png,image/jpeg,image/webp" :disabled="avatarBusy" @change="uploadAvatar" /></label><button v-if="avatar" type="button" :disabled="avatarBusy" @click="removeAvatar">{{ locale === 'fa' ? 'حذف عکس' : 'Remove photo' }}</button></div>
    </div>
    <div class="profile-intro">
      <p>{{ locale === 'fa' ? 'اطلاعات فعلی شما در این بخش نمایش داده می‌شود. هر زمان لازم بود می‌توانید آن را ویرایش کنید.' : 'Your current details are shown here. Edit them whenever you need to.' }}</p>
      <button v-if="!editing && !loading" type="button" class="profile-edit" @click="editing = true; success = ''">{{ locale === 'fa' ? 'ویرایش اطلاعات' : 'Edit details' }} <span aria-hidden="true">↗</span></button>
    </div>
    <p v-if="error" class="profile-message is-error" role="alert">{{ error }}</p>
    <p v-if="success" class="profile-message" role="status">{{ success }}</p>
    <p v-if="loading" class="profile-message">{{ locale === 'fa' ? 'در حال دریافت اطلاعات…' : 'Loading your details…' }}</p>

    <dl v-else-if="!editing" class="profile-details">
      <div v-for="key in Object.keys(fields)" :key="key" class="profile-field" :class="{ 'is-wide': key === 'address' }">
        <dt>{{ label(key) }}</dt><dd>{{ profile[key] || '—' }}</dd>
      </div>
    </dl>

    <form v-else class="profile-form" @submit.prevent="save">
      <label v-for="key in Object.keys(fields)" :key="key" class="profile-input" :class="{ 'is-wide': key === 'address' }">
        <span>{{ label(key) }}</span>
        <textarea v-if="key === 'address'" v-model="profile[key]" rows="3"></textarea>
        <input v-else v-model="profile[key]" :required="key === 'full_name'" :type="key === 'email' ? 'email' : key === 'phone' ? 'tel' : 'text'" />
      </label>
      <div class="profile-actions"><button type="submit" :disabled="saving">{{ saving ? (locale === 'fa' ? 'در حال ذخیره…' : 'Saving…') : (locale === 'fa' ? 'ذخیره تغییرات' : 'Save changes') }}</button><button type="button" @click="cancel">{{ locale === 'fa' ? 'انصراف' : 'Cancel' }}</button></div>
    </form>
  </AccountShell>
</template>

<style scoped>
.profile-photo-row { display: flex; flex-wrap: wrap; align-items: center; gap: .9rem; margin-top: 1.25rem; padding: 1rem 1.1rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .65rem; background: rgb(var(--c-parchment-light)); }
.profile-photo { display: grid; flex: none; place-items: center; overflow: hidden; width: 3.25rem; height: 3.25rem; border-radius: 50%; background: rgb(var(--c-gold) / .15); color: rgb(var(--c-gold-dark)); font: 400 1.45rem Georgia,serif; }.profile-photo img { width: 100%; height: 100%; object-fit: cover; }
.profile-photo-copy { display: grid; gap: .2rem; flex: 1; min-width: 12rem; }.profile-photo-copy strong { font-size: .85rem; font-weight: 600; }.profile-photo-copy small { color: rgb(var(--c-ink-muted)); font-size: .7rem; }
.profile-photo-actions { display: flex; align-items: center; gap: .45rem; }.profile-photo-button, .profile-photo-actions button { display: inline-flex; align-items: center; padding: .55rem .75rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .4rem; color: rgb(var(--c-gold-dark)); font-size: .75rem; cursor: pointer; }.profile-photo-button:hover, .profile-photo-actions button:hover { border-color: rgb(var(--c-gold)); }.profile-photo-button input { position: absolute; width: 1px; height: 1px; opacity: 0; }.profile-photo-button:focus-within { outline: 2px solid rgb(var(--c-gold-dark)); outline-offset: 2px; }.profile-photo-button.is-busy, .profile-photo-actions button:disabled { opacity: .5; cursor: wait; }
.profile-intro { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem; margin: 1.3rem 0 1rem; color: rgb(var(--c-ink-muted)); font-size: .82rem; }
.profile-edit { display: inline-flex; align-items: center; gap: .8rem; padding: .7rem 1rem; border: 1px solid rgb(var(--c-gold)); border-radius: .55rem; color: rgb(var(--c-gold-dark)); font-weight: 600; transition: background .2s; }
.profile-edit:hover { background: rgb(var(--c-gold) / .12); }
.profile-details, .profile-form { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: .8rem; }
.profile-field, .profile-input { min-width: 0; padding: 1rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .65rem; background: rgb(var(--c-parchment-light)); box-shadow: 0 10px 28px #00000009; }
.profile-field.is-wide, .profile-input.is-wide, .profile-actions { grid-column: 1 / -1; }
.profile-field dt, .profile-input span { display: block; margin-bottom: .65rem; color: rgb(var(--c-gold-dark)); font-size: .72rem; }
.profile-field dd { overflow-wrap: anywhere; color: rgb(var(--c-ink)); font-size: .95rem; }
.profile-input input, .profile-input textarea { display: block; width: 100%; padding: .55rem .7rem; border: 1px solid rgb(var(--c-parchment-deep)); border-radius: .35rem; background: transparent; color: rgb(var(--c-ink)); outline: none; }
.profile-input input:focus, .profile-input textarea:focus { border-color: rgb(var(--c-gold-dark)); }
.profile-actions { display: flex; gap: .6rem; margin-top: .4rem; }
.profile-actions button { padding: .8rem 1.25rem; border-radius: .5rem; border: 1px solid rgb(var(--c-parchment-deep)); }
.profile-actions button:first-child { background: rgb(var(--c-ink)); color: rgb(var(--c-parchment-light)); }
.profile-message { margin: 1rem 0; color: #247254; font-size: .85rem; }.profile-message.is-error { color: #a3424a; }
@media (max-width: 640px) { .profile-details, .profile-form { grid-template-columns: 1fr; } }
</style>
