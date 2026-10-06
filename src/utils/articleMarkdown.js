import { resolveApiUrl } from '../api/client.js'

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char])
const safeUrl = (value) => {
  try {
    const url = new URL(value.startsWith('/api/') ? resolveApiUrl(value) : value, window.location.origin)
    return ['http:', 'https:'].includes(url.protocol) ? escapeHtml(url.href) : ''
  } catch { return '' }
}

const inline = (value) => {
  let html = escapeHtml(value)
  html = html.replace(/!\[([^\]]*)\]\(([^\s)]+)\)/g, (_, alt, url) => {
    const href = safeUrl(url)
    return href ? `<img src="${href}" alt="${alt}" loading="lazy">` : alt
  })
  html = html.replace(/\[([^\]]+)\]\(([^\s)]+)\)/g, (_, label, url) => {
    const href = safeUrl(url)
    return href ? `<a href="${href}" rel="noopener noreferrer" target="_blank">${label}</a>` : label
  })
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  html = html.replace(/~~([^~]+)~~/g, '<del>$1</del>')
  return html
}

export const renderArticle = (source) => {
  const lines = String(source || '').replace(/\r/g, '').split('\n')
  const out = []
  let list = ''
  const closeList = () => { if (list) { out.push(`</${list}>`); list = '' } }
  for (const raw of lines) {
    const line = raw.trim()
    if (!line) { closeList(); continue }
    if (/^---+$/.test(line)) { closeList(); out.push('<hr>'); continue }
    const heading = /^(#{1,3})\s+(.+)$/.exec(line)
    if (heading) { closeList(); out.push(`<h${heading[1].length}>${inline(heading[2])}</h${heading[1].length}>`); continue }
    const bullet = /^[-*+]\s+(.+)$/.exec(line)
    const numbered = /^\d+\.\s+(.+)$/.exec(line)
    if (bullet || numbered) { const type = numbered ? 'ol' : 'ul'; if (list !== type) { closeList(); out.push(`<${type}>`); list = type } out.push(`<li>${inline((bullet || numbered)[1])}</li>`); continue }
    closeList()
    const quote = /^>\s+(.+)$/.exec(line)
    if (quote) { out.push(`<blockquote>${inline(quote[1])}</blockquote>`); continue }
    out.push(`<p>${inline(line)}</p>`)
  }
  closeList()
  return out.join('')
}
