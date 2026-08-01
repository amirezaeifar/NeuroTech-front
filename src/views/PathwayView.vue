<script setup>
/**
 * PathwayView — demo host for <NeuralProgressTree>.
 *
 * Recreates the "Browse the Library" section on the charcoal (#323A45) stage so
 * the frosted-glass sidebar has something to blur against, and lays out a tall,
 * scrollable course list on the right. The whole section carries
 * [data-progress-track], which the tree measures to drive its scroll fill.
 */
import NeuralProgressTree from '../components/NeuralProgressTree.vue'
import { userProgress } from '../data/userProgress.js'

const statusLabel = { completed: 'Completed', 'in-progress': 'In progress', locked: 'Locked' }
</script>

<template>
  <div class="stage">
    <!-- ambient depth wash so the frosted glass reads -->
    <div class="stage__ambient" aria-hidden="true"></div>

    <div class="wrap" data-progress-track>
      <header class="lib-head">
        <p class="lib-head__eyebrow">Neuro·Tech Academy</p>
        <h1 class="lib-head__title">Browse the Library</h1>
      </header>

      <div class="grid">
        <!-- ── Left sidebar: the Neural Pathway Progress Tree (self-sticky) ── -->
        <div class="rail">
          <NeuralProgressTree :data="userProgress" :sticky-top="28" />
        </div>

        <!-- ── Right: the scrollable course list that drives the fill ── -->
        <div class="content">
          <article
            v-for="course in userProgress.courses"
            :key="course.id"
            class="course"
          >
            <div class="course__bar">
              <span class="course__code">{{ course.code }}</span>
              <span class="course__status" :data-s="course.status">{{ statusLabel[course.status] }}</span>
            </div>
            <h2 class="course__title">{{ course.title }}</h2>
            <p class="course__lede">
              A structured pathway through {{ course.modules.length }} modules. Scroll on — the
              neural tree to the left fills with gold as you descend, and pulses at the module
              you're currently working through.
            </p>
            <ul class="mods">
              <li v-for="m in course.modules" :key="m.id" class="mod" :data-s="m.status">
                <span class="mod__dot"></span>
                <span class="mod__title">{{ m.title }}</span>
                <span class="mod__status">{{ statusLabel[m.status] }}</span>
              </li>
            </ul>
          </article>

          <div class="tail">End of library · the pathway is fully charted ✦</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stage {
  position: relative;
  min-height: 100vh;
  background: #323A45;
  color: #E9ECF1;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}
.stage__ambient {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(50% 40% at 18% 22%, rgba(244, 215, 145, 0.10), transparent 70%),
    radial-gradient(45% 45% at 85% 75%, rgba(90, 120, 160, 0.16), transparent 70%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: auto, auto, 26px 26px;
}

.wrap {
  position: relative;
  max-width: 1180px;
  margin: 0 auto;
  padding: 88px 28px 160px;
}

.lib-head { margin-bottom: 44px; }
.lib-head__eyebrow {
  margin: 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.34em;
  color: #EDC071;
  font-weight: 300;
}
.lib-head__title {
  margin: 12px 0 0;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 300;
  font-size: clamp(2.4rem, 5vw, 3.6rem);
  letter-spacing: 0.01em;
  color: #F6F3EC;
}

.grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 56px;
  align-items: start;
}
@media (max-width: 820px) {
  .grid { grid-template-columns: 1fr; }
  .rail :deep(.npt) { position: static; }
}

.rail { min-width: 0; }

/* ── Right column ──────────────────────────────────────────────────────────── */
.content { display: flex; flex-direction: column; gap: 40px; }

.course {
  border-radius: 18px;
  padding: 28px 30px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.015));
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}
.course__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.course__code {
  font-size: 11px;
  letter-spacing: 0.22em;
  color: #EDC071;
  font-variant-numeric: tabular-nums;
}
.course__status {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(233, 236, 241, 0.7);
}
.course__status[data-s='completed'] { color: #F4D791; border-color: rgba(244, 215, 145, 0.5); }
.course__status[data-s='in-progress'] { color: #9Fd0ff; border-color: rgba(159, 208, 255, 0.45); }

.course__title {
  margin: 16px 0 0;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 400;
  font-size: 28px;
  color: #F6F3EC;
}
.course__lede {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: rgba(233, 236, 241, 0.66);
  font-weight: 300;
  max-width: 52ch;
}

.mods { list-style: none; margin: 22px 0 0; padding: 0; display: flex; flex-direction: column; }
.mod {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  font-size: 13.5px;
}
.mod__dot {
  width: 8px; height: 8px; border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.04);
  flex: none;
}
.mod[data-s='completed'] .mod__dot { background: #F4D791; box-shadow: 0 0 10px rgba(244, 215, 145, 0.7); }
.mod[data-s='in-progress'] .mod__dot { background: #9FD0FF; box-shadow: 0 0 10px rgba(159, 208, 255, 0.7); }
.mod__title { color: #E9ECF1; flex: 1; }
.mod[data-s='locked'] .mod__title { color: rgba(233, 236, 241, 0.45); }
.mod__status {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: rgba(233, 236, 241, 0.4);
}

.tail {
  margin-top: 8px;
  text-align: center;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 18px;
  letter-spacing: 0.04em;
  color: rgba(244, 215, 145, 0.5);
  padding: 40px 0;
}
</style>
