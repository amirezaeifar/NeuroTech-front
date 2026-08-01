<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppNavbar from './components/AppNavbar.vue'
import AppFooter from './components/AppFooter.vue'
import ScrollToTop from './components/ScrollToTop.vue'
import { useLocale } from './composables/useLocale.js'

useLocale()

const route = useRoute()
// Routes can opt out of the global navbar/footer (e.g. the standalone Auth page)
// via `meta: { hideChrome: true }` in the router config.
const showChrome = computed(() => !route.meta.hideChrome)
</script>

<template>
  <div class="min-h-screen flex flex-col bg-parchment-light text-ink overflow-x-clip">
    <AppNavbar v-if="showChrome" />
    <main class="flex-1">
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <AppFooter v-if="showChrome" />
    <ScrollToTop v-if="showChrome" />
  </div>
</template>
