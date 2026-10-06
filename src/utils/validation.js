let currentLocale = () => document.documentElement.lang || 'en'
let sequence = 0
const feedback = new WeakMap()
const fa = () => currentLocale() === 'fa'
const controls = 'input, textarea, select'

function fieldName(field) {
  const label = field.labels?.[0]
  return field.dataset.fieldLabel || field.getAttribute('aria-label') ||
    (label?.querySelector('.admin-label') || label)?.textContent.trim() ||
    field.parentElement.querySelector('.admin-label')?.textContent.trim() ||
    field.placeholder?.trim() || field.name || (fa() ? 'این فیلد' : 'This field')
}

export function validationMessage(field) {
  const name = fieldName(field)
  const value = field.value.trim()
  if (field.required && !value) return fa() ? `«${name}» را وارد کنید.` : `Enter ${name}.`
  if (!value && !field.validity.badInput) return ''
  if (field.validity.typeMismatch || field.validity.badInput) {
    const format = field.type === 'email' ? (fa() ? 'ایمیل' : 'email address') : field.type === 'url' ? (fa() ? 'نشانی اینترنتی' : 'URL') : (fa() ? 'عدد' : 'number')
    return fa() ? `برای «${name}» یک ${format} معتبر وارد کنید.` : `Enter a valid ${format} for ${name}.`
  }
  if (field.type === 'tel' && !/^\+?[\d\s()-]{7,24}$/.test(value.replace(/[۰-۹]/g, c => '۰۱۲۳۴۵۶۷۸۹'.indexOf(c)))) return fa() ? `برای «${name}» شماره تماس معتبر وارد کنید؛ مانند 09121234567.` : `Enter a valid phone number for ${name}, e.g. +989121234567.`
  if (field.minLength > 0 && value.length < field.minLength) return fa() ? `«${name}» باید حداقل ${field.minLength} نویسه داشته باشد.` : `${name} must contain at least ${field.minLength} characters.`
  if (field.maxLength > 0 && value.length > field.maxLength) return fa() ? `«${name}» باید حداکثر ${field.maxLength} نویسه داشته باشد.` : `${name} must contain at most ${field.maxLength} characters.`
  if (field.validity.rangeUnderflow || field.validity.rangeOverflow) return fa() ? `«${name}» باید ${field.min ? `حداقل ${field.min}` : ''}${field.min && field.max ? ' و ' : ''}${field.max ? `حداکثر ${field.max}` : ''} باشد.` : `${name} must be ${field.min ? `at least ${field.min}` : ''}${field.min && field.max ? ' and ' : ''}${field.max ? `at most ${field.max}` : ''}.`
  if (!field.validity.valid) return fa() ? `مقدار «${name}» معتبر نیست؛ قالب خواسته‌شده را بررسی کنید.` : `Check the format of ${name}.`
  return ''
}

function display(field, message) {
  let item = feedback.get(field)
  if (!message) {
    if (item) {
      item.node.remove()
      const ids = (field.getAttribute('aria-describedby') || '').split(' ').filter(id => id !== item.node.id)
      if (ids.length) field.setAttribute('aria-describedby', ids.join(' ')); else field.removeAttribute('aria-describedby')
      field.removeAttribute('aria-invalid')
      feedback.delete(field)
    }
    return
  }
  if (!item) {
    const node = document.createElement('span')
    node.id = `field-error-${++sequence}`
    node.className = 'field-error'
    node.setAttribute('role', 'alert')
    // Keep floating-label input/label adjacency intact.
    const anchor = field.nextElementSibling?.tagName === 'LABEL' ? field.nextElementSibling : field
    anchor.after(node)
    item = { node }
    feedback.set(field, item)
    field.setAttribute('aria-describedby', [field.getAttribute('aria-describedby'), node.id].filter(Boolean).join(' '))
  }
  item.node.textContent = message
  field.setAttribute('aria-invalid', 'true')
}

export function validateSection(root) {
  if (!root) return false
  let first
  for (const field of root.querySelectorAll(controls)) {
    if (!field.willValidate) continue
    const message = validationMessage(field)
    display(field, message)
    if (message && !first) first = field
  }
  if (first) {
    for (let parent = first.parentElement; parent && parent !== root; parent = parent.parentElement) if (parent.tagName === 'DETAILS') parent.open = true
    first.focus({ preventScroll: true })
    first.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' })
  }
  return !first
}

export function installValidation(getLocale) {
  currentLocale = getLocale
  document.addEventListener('invalid', event => {
    event.preventDefault()
    display(event.target, validationMessage(event.target))
    const root = event.target.form
    if (root && root.querySelector('[aria-invalid="true"]') === event.target) event.target.focus()
  }, true)
  document.addEventListener('submit', event => {
    if (!validateSection(event.target)) { event.preventDefault(); event.stopImmediatePropagation() }
  }, true)
  for (const type of ['input', 'change', 'focusout']) document.addEventListener(type, event => {
    const field = event.target
    if (field.matches?.(controls) && field.willValidate && (feedback.has(field) || type === 'focusout' && field.value)) display(field, validationMessage(field))
  }, true)
}

export function formatValidationProblem(problem) {
  const fields = problem?.errors || problem?.invalid_params
  const messages = []
  const names = { name:'نام', title:'عنوان', email:'ایمیل', phone:'شماره تماس', password:'رمز عبور', subject:'موضوع', message:'متن درخواست', reply:'پاسخ', slug:'شناسه نشانی', sku:'کد محصول', translations:'ترجمه‌ها', description:'توضیحات', short_description:'توضیح کوتاه', instructor_name:'نام مدرس', duration_label:'مدت', quantity:'تعداد', amount_minor:'مبلغ', stock_quantity:'موجودی', starts_at:'زمان شروع', ends_at:'زمان پایان', code:'کد تأیید', display_name:'نام', url:'لینک', user_id:'شناسه کاربر', details:'جزئیات', position:'ترتیب', prices:'قیمت‌ها', title_fa:'عنوان فارسی' }
  const readable = key => fa() ? names[key] || key : key.replaceAll('_',' ')
  function describe(item, path) {
    if (!fa()) return `Check ${path}: ${item}`
    if (/missing|required|blank|empty/i.test(item)) return `«${path}» را وارد کنید.`
    if (/email/i.test(item)) return `برای «${path}» ایمیل معتبر وارد کنید.`
    const minimum = item.match(/(?:shorter than|at least|greater than or equal to) (\d+)/i)
    const maximum = item.match(/(?:longer than|at most|less than or equal to) (\d+)/i)
    if (minimum || maximum) return `مقدار «${path}» باید ${minimum ? `حداقل ${minimum[1]}` : ''}${minimum && maximum ? ' و ' : ''}${maximum ? `حداکثر ${maximum[1]}` : ''} باشد.`
    return `مقدار «${path}» معتبر نیست؛ قالب خواسته‌شده را بررسی کنید.`
  }
  function walk(value, path = '') {
    if (Array.isArray(value)) value.forEach(item => typeof item === 'string' ? messages.push(describe(item, path)) : walk(item, path))
    else if (value && typeof value === 'object') Object.entries(value).forEach(([key, item]) => walk(item, ['json', 'body', 'query'].includes(key) ? path : [path, readable(key)].filter(Boolean).join(' / ')))
  }
  walk(fields)
  return messages.length ? [...new Set(messages)].join('\n') : null
}
