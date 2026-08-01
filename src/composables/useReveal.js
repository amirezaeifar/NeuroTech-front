import { onMounted, onBeforeUnmount } from 'vue'

// Adds the 'is-visible' class to elements with the 'reveal' class
// when they enter the viewport. Stagger via inline style transition-delay.
export function useReveal() {
  let observer

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
  })

  onBeforeUnmount(() => observer && observer.disconnect())
}
