import { resolveApiUrl } from '../api/client.js'
export const courseImage = (course, dark, kind = 'cover') => {
 const images=course?.images || []
 const image=images.find(i=>i.kind===`${kind}_${dark?'dark':'light'}`) || images.find(i=>i.kind===`${kind}_light`) || images.find(i=>i.kind===`${kind}_dark`)
 return image?.url ? resolveApiUrl(image.url) : ''
}
