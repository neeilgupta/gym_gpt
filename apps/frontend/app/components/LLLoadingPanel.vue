<template>
  <section class="ll-loading" aria-live="polite" aria-busy="true">
    <div class="ll-loading__top">
      <div>
        <div class="ll-loading__title">{{ title }}</div>
        <div v-if="subtitle" class="ll-loading__subtitle">{{ subtitle }}</div>
      </div>

      <div class="ll-loading__meta">
        <span class="ll-loading__time">{{ prettyElapsed }}</span>
      </div>
    </div>

    <div class="ll-loading__bar" />

    <div class="ll-loading__grid">
      <div class="ll-skel skel--line" />
      <div class="ll-skel skel--line" />
      <div class="ll-skel skel--line" />
      <div class="ll-skel skel--line" />
    </div>

    <ul v-if="steps?.length" class="ll-loading__steps">
      <li
        v-for="(s, i) in steps"
        :key="`${i}-${s}`"
        :class="['ll-step', i === activeStep ? 'is-active' : '', i < activeStep ? 'is-done' : '']"
      >
        <span class="ll-step__dot" />
        <span class="ll-step__text">{{ s }}</span>
      </li>
    </ul>

    <div v-if="hint" class="ll-loading__hint">{{ hint }}</div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  title: string;
  subtitle?: string;
  /** seconds */
  elapsed?: number;
  /** ordered list of human-readable steps */
  steps?: string[];
  /** optional guidance / reassurance */
  hint?: string;
  /** how quickly the active step advances (seconds) */
  stepSeconds?: number;
}>();

const stepSeconds = computed(() => Math.max(1, props.stepSeconds ?? 3));

const activeStep = computed(() => {
  const s = props.steps?.length ?? 0;
  if (!s) return 0;
  const e = Math.max(0, props.elapsed ?? 0);
  return Math.min(s - 1, Math.floor(e / stepSeconds.value));
});

const prettyElapsed = computed(() => {
  const e = Math.max(0, Math.floor(props.elapsed ?? 0));
  if (e < 60) return `${e}s`;
  const m = Math.floor(e / 60);
  const r = e % 60;
  return `${m}m ${String(r).padStart(2, "0")}s`;
});
</script>

<style scoped>
.ll-loading {
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: #111111;
  border-radius: 6px;
  padding: 16px;
  margin-top: 14px;
}

.ll-loading__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.ll-loading__title {
  font-weight: 600;
  font-size: 14px;
  letter-spacing: -0.01em;
  color: #ffffff;
}

.ll-loading__subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 3px;
}

.ll-loading__time {
  font-family: 'DM Mono', ui-monospace, monospace;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: transparent;
  color: rgba(255, 255, 255, 0.45);
}

.ll-loading__bar {
  height: 2px;
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.08),
    rgba(255, 255, 255, 0.3),
    rgba(255, 255, 255, 0.08)
  );
  background-size: 200% 100%;
  animation: ll-shimmer 1.2s ease-in-out infinite;
  margin-bottom: 14px;
}

.ll-loading__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}

.ll-skel {
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.03),
    rgba(255, 255, 255, 0.07),
    rgba(255, 255, 255, 0.03)
  );
  background-size: 200% 100%;
  animation: ll-shimmer 1.2s ease-in-out infinite;
}

.skel--line {
  height: 36px;
}

.ll-loading__steps {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.ll-step {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
}

.ll-step__dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  flex-shrink: 0;
}

.ll-step.is-active {
  color: #ffffff;
}

.ll-step.is-active .ll-step__dot {
  border-color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.2);
}

.ll-step.is-done {
  color: rgba(255, 255, 255, 0.5);
}

.ll-step.is-done .ll-step__dot {
  border-color: rgba(74, 222, 128, 0.5);
  background: rgba(74, 222, 128, 0.15);
}

.ll-loading__hint {
  margin-top: 12px;
  font-family: 'DM Mono', ui-monospace, monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  line-height: 1.5;
}

@keyframes ll-shimmer {
  0% { background-position: 0% 0; }
  100% { background-position: 200% 0; }
}

@media (max-width: 900px) {
  .ll-loading__grid { grid-template-columns: 1fr; }
}
</style>
