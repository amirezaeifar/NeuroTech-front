import { resolveApiUrl } from '../api/client.js'

export function eventMedia(value) {
  if (!value) return null
  if (/^\/api\/v1\/files\/[0-9a-f-]{36}$/i.test(value)) return { type: 'video', src: resolveApiUrl(value) }
  try {
    const url = new URL(value)
    if (url.protocol !== 'https:' || url.username || url.password) return null
    const host = url.hostname.replace(/^www\./, '')
    let id
    if (host === 'youtube.com' || host === 'youtube-nocookie.com' || host === 'youtu.be') {
      id = host === 'youtu.be' ? url.pathname.slice(1) : url.searchParams.get('v') || url.pathname.match(/^\/(?:embed|live)\/([^/]+)$/)?.[1]
      return /^[\w-]{11}$/.test(id || '') ? { type: 'iframe', src: `https://www.youtube-nocookie.com/embed/${id}` } : null
    }
    if (host === 'vimeo.com' || host === 'player.vimeo.com') {
      id = url.pathname.match(/(?:\/video)?\/(\d+)$/)?.[1]
      return id ? { type: 'iframe', src: `https://player.vimeo.com/video/${id}${url.searchParams.has('h') ? `?h=${encodeURIComponent(url.searchParams.get('h'))}` : ''}` } : null
    }
    if (host === 'aparat.com') {
      id = url.pathname.match(/^\/v\/([A-Za-z0-9]+)$/)?.[1] || url.pathname.match(/\/videohash\/([A-Za-z0-9]+)/)?.[1]
      return id ? { type: 'iframe', src: `https://www.aparat.com/video/video/embed/videohash/${id}/vt/frame` } : null
    }
    return { type: 'video', src: url.href }
  } catch { return null }
}
