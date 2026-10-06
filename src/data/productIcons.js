export const productIcons = [
  { key: 'brain', en: 'Brain', fa: 'مغز', paths: ['M9.5 4.5A3 3 0 0 0 4 6v1.2A3.5 3.5 0 0 0 3 13v1a3.5 3.5 0 0 0 4 3.45V18a2.5 2.5 0 0 0 5 0V6.5a2 2 0 0 0-2.5-2z', 'M14.5 4.5A3 3 0 0 1 20 6v1.2a3.5 3.5 0 0 1 1 5.8v1a3.5 3.5 0 0 1-4 3.45V18a2.5 2.5 0 0 1-5 0V6.5a2 2 0 0 1 2.5-2z'] },
  { key: 'pulse', en: 'Neural pulse', fa: 'پالس عصبی', paths: ['M3 12h4l2.2-5 4.1 10 2.2-5H21'] },
  { key: 'shield', en: 'Clinical safety', fa: 'ایمنی بالینی', paths: ['M12 3l7 3v5c0 4.7-2.8 8-7 10-4.2-2-7-5.3-7-10V6l7-3z', 'M9 12l2 2 4-5'] },
  { key: 'certificate', en: 'Certification', fa: 'گواهی', paths: ['M7 3h10v12H7z', 'M9 7h6M9 10h6', 'M10 15l-1 6 3-2 3 2-1-6'] },
  { key: 'microscope', en: 'Laboratory', fa: 'آزمایشگاه', paths: ['M9 3h4v3H9z', 'M11 6v5a4 4 0 0 1-4 4H5', 'M14 9l3 3-2 2-3-3', 'M5 19h14M8 15a5 5 0 0 0 9 0'] },
  { key: 'sensor', en: 'Sensor', fa: 'حسگر', paths: ['M12 8a4 4 0 1 1 0 8 4 4 0 0 1 0-8z', 'M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4 1.4'] },
  { key: 'network', en: 'Connected system', fa: 'سامانه متصل', paths: ['M12 5a2 2 0 1 1 0-4 2 2 0 0 1 0 4zM5 14a2 2 0 1 1 0-4 2 2 0 0 1 0 4zM19 14a2 2 0 1 1 0-4 2 2 0 0 1 0 4zM12 23a2 2 0 1 1 0-4 2 2 0 0 1 0 4z', 'M12 5v4M7 11l4-2M17 11l-4-2M7 14l4 5M17 14l-4 5'] },
  { key: 'precision', en: 'Precision', fa: 'دقت', paths: ['M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z', 'M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z', 'M12 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2z'] },
  { key: 'clinical', en: 'Medical care', fa: 'مراقبت پزشکی', paths: ['M12 21s-8-4.8-8-11a4 4 0 0 1 7-2.6L12 9l1-1.6A4 4 0 0 1 20 10c0 6.2-8 11-8 11z', 'M9 13h6M12 10v6'] },
  { key: 'innovation', en: 'Innovation', fa: 'نوآوری', paths: ['M9 18h6M10 21h4', 'M8.5 15.5A7 7 0 1 1 15.5 15.5L14 17h-4z', 'M12 3v3M5.6 5.6l2.1 2.1M18.4 5.6l-2.1 2.1'] },
]

export const productIcon = (key) => productIcons.find((item) => item.key === key) || productIcons[3]
