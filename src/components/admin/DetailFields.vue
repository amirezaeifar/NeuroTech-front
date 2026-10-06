<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const props = defineProps({ modelValue: { required: true }, schema: { default: () => ({}) }, field: { default: '' }, language: { default: '' }, schemaOnly: { type: Boolean, default: false }, fieldLabels: { default: () => ({}) } })
const emit = defineEmits(['update:modelValue'])
const { locale } = useI18n()
const activeLanguage = computed(() => props.language || locale.value)
const tr = (en,fa) => activeLanguage.value === 'fa' ? fa : en
const names = { councilNumber:'شماره نظام پزشکی',venue:'نشریه / محل انتشار',lessons:'تعداد درس‌ها', collaborations:'زمینه‌های همکاری',experience:'سوابق کاری',education:'تحصیلات',publications:'مقالات',expertise:'تخصص‌ها',methodology:'روش آموزش',impact:'دستاوردها',courses:'دوره',playlists:'دوره',platform:'لینکدین',status:'وضعیت',demo:'پروفایل نمونه',role:'سمت',org:'سازمان',period:'بازه زمانی',degree:'مدرک',school:'دانشگاه',title:'عنوان',name:'نام',url:'لینک',year:'سال',journal:'نشریه',desc:'توضیحات',text:'متن',label:'عنوان',value:'مقدار',note:'توضیح',mark:'نشان',stat:'آمار',author:'نویسنده',rating:'امتیاز',type:'نوع',size:'حجم',slug:'شناسه نشانی',index:'شماره',badges:'نشان‌ها',keyFeatures:'ویژگی‌ها',specs:'مشخصات فنی',docs:'اسناد',reviews:'نظرات',certs:'گواهی‌ها',trials:'شواهد بالینی',ecosystem:'نرم‌افزارهای مرتبط',availability:'موجودی',leadTime:'زمان تحویل',priceNote:'توضیح قیمت',overviewLead:'معرفی کوتاه',overviewBody:'معرفی کامل',blueprintLead:'معرفی فنی',validationLead:'معرفی اعتبارسنجی',ecosystemLead:'معرفی نرم‌افزار',ecosystemNote:'توضیح نرم‌افزار',brochureUrl:'لینک بروشور' }
const englishNames = { impact: 'Achievements', playlists: 'Course', platform: 'LinkedIn' }
const label = (key) => props.fieldLabels[key] || (activeLanguage.value === 'fa' ? names[key] || key : englishNames[key] || key.replace(/([A-Z])/g,' $1').replace(/^./,c=>c.toUpperCase()))
const blank = (value) => Array.isArray(value) ? [] : value && typeof value==='object' ? Object.fromEntries(Object.entries(value).map(([k,v])=>[k,blank(v)])) : typeof value === 'number' ? 0 : typeof value === 'boolean' ? false : ''
const set = (key, value) => emit('update:modelValue', Array.isArray(props.modelValue) ? props.modelValue.map((v,i)=>i===key?value:v) : {...props.modelValue,[key]:value})
const keys = () => props.schemaOnly ? Object.keys(props.schema || {}) : [...new Set([...Object.keys(props.schema || {}),...Object.keys(props.modelValue || {})])]
const move = (i, step) => {const list=[...props.modelValue]; [list[i],list[i+step]]=[list[i+step],list[i]];emit('update:modelValue',list)}
</script>
<template>
  <div v-if="Array.isArray(modelValue)" class="space-y-3">
    <div v-for="(item,i) in modelValue" :key="i" class="admin-panel p-4 space-y-3">
      <DetailFields :model-value="item" :schema="schema?.[0] || item" :field="field" :language="language" :schema-only="schemaOnly" :field-labels="fieldLabels" @update:model-value="set(i,$event)" />
      <div class="flex gap-2"><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="i===0" @click="move(i,-1)">↑</button><button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" :disabled="i===modelValue.length-1" @click="move(i,1)">↓</button><button type="button" class="admin-btn admin-btn-danger admin-btn-sm" @click="emit('update:modelValue',modelValue.filter((_,j)=>i!==j))">{{ tr('Remove','حذف') }}</button></div>
    </div>
    <button type="button" class="admin-btn admin-btn-ghost admin-btn-sm" @click="emit('update:modelValue',[...modelValue,blank(schema?.[0] ?? modelValue[0] ?? '')])">+ {{ tr('Add item','افزودن مورد') }}</button>
  </div>
  <div v-else-if="modelValue && typeof modelValue==='object'" class="space-y-5">
    <div v-for="key in keys()" :key="key">
      <details v-if="Array.isArray(schema[key] ?? modelValue[key])" class="admin-panel p-4"><summary class="admin-label cursor-pointer">{{ label(key) }} · {{ modelValue[key]?.length || 0 }}</summary><DetailFields class="mt-4" :model-value="modelValue[key] ?? []" :schema="schema[key] ?? modelValue[key]" :field="key" :language="language" :schema-only="schemaOnly" :field-labels="fieldLabels" @update:model-value="set(key,$event)" /></details>
      <label v-else class="block"><span class="admin-label">{{ label(key) }}</span><DetailFields :model-value="modelValue[key] ?? blank(schema[key])" :schema="schema[key] ?? modelValue[key]" :field="key" :language="language" :schema-only="schemaOnly" :field-labels="fieldLabels" @update:model-value="set(key,$event)" /></label>
    </div>
  </div>
  <input v-else-if="typeof modelValue==='boolean'" type="checkbox" :checked="modelValue" @change="emit('update:modelValue',$event.target.checked)">
  <input v-else-if="typeof modelValue==='number'" type="number" class="admin-input" :value="modelValue" @input="emit('update:modelValue',Number($event.target.value))">
  <textarea v-else class="admin-textarea" rows="2" :value="modelValue" @input="emit('update:modelValue',$event.target.value)"></textarea>
</template>
