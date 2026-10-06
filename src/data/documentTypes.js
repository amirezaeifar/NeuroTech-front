export const documentTypes = ['PDF', 'DOC', 'DOCX', 'XLS', 'XLSX', 'PPT', 'PPTX', 'CSV', 'TXT', 'RTF', 'ZIP']

const labels = {
  PDF: ['PDF document', 'سند پی‌دی‌اف'],
  DOC: ['Word document (DOC)', 'سند ورد (DOC)'],
  DOCX: ['Word document (DOCX)', 'سند ورد (DOCX)'],
  XLS: ['Excel spreadsheet (XLS)', 'صفحه‌گسترده اکسل (XLS)'],
  XLSX: ['Excel spreadsheet (XLSX)', 'صفحه‌گسترده اکسل (XLSX)'],
  PPT: ['PowerPoint presentation (PPT)', 'ارائه پاورپوینت (PPT)'],
  PPTX: ['PowerPoint presentation (PPTX)', 'ارائه پاورپوینت (PPTX)'],
  CSV: ['CSV table', 'داده جدولی سی‌اس‌وی'],
  TXT: ['Plain text', 'متن ساده'],
  RTF: ['Rich text (RTF)', 'متن آر‌تی‌اف'],
  ZIP: ['ZIP archive', 'فایل فشرده زیپ'],
}

export const documentTypeLabel = (type, locale = 'en') => labels[type]?.[locale === 'fa' ? 1 : 0] || type
