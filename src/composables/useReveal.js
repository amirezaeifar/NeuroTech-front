import { onMounted, onBeforeUnmount } from 'vue'

// Adds the 'is-visible' class to elements with the 'reveal' class
// when they enter the viewport. Stagger via inline style transition-delay.
export function useReveal() {
  let observer
  let mutations

  onMounted(() => {
    if (typeof window === 'undefined' || !('IntersectionObserver' in window)) return
    observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add('is-visible')
            observer.unobserve(e.target)
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    )
    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el))
    // API-backed pages insert their cards after mount.
    mutations = new MutationObserver(records => {
      for (const record of records) for (const node of record.addedNodes) {
        if (!(node instanceof Element)) continue
        if (node.matches('.reveal:not(.is-visible)')) observer.observe(node)
        node.querySelectorAll('.reveal:not(.is-visible)').forEach(el => observer.observe(el))
      }
    })
    mutations.observe(document.body, { childList: true, subtree: true })
  })

  onBeforeUnmount(() => { observer?.disconnect(); mutations?.disconnect() })
}
