<template>
  <main class="generate-page">
    <section class="generate-shell">
      <aside class="generate-rail">
        <p class="rail-kicker">Workout</p>
        <h1 class="page-title">
          Build your<br>
          workout plan
        </h1>
        <p class="page-sub">
          Choose your goal, equipment, schedule, and any muscles you want to focus on.
        </p>
        <div class="rail-list">
          <div class="rail-item"><span></span>Fits your equipment</div>
          <div class="rail-item"><span></span>Fits your session length</div>
          <div class="rail-item"><span></span>Saves when signed in</div>
        </div>
      </aside>

    <form @submit.prevent="onSubmit" class="generate-form glass-card">
      <div class="form-header">
        <div class="form-pill">Training</div>
        <h2>Workout plan</h2>
        <p>Fill out the basics and generate your plan.</p>
      </div>

      <section class="ll-card">
        <div class="card-heading">Plan details</div>

        <div class="form-grid">
          <label class="form-field">
            <span class="form-label">Goal</span>
            <select v-model="form.goal" class="form-input form-select" :disabled="loading">
              <option value="hypertrophy">Hypertrophy</option>
              <option value="strength">Strength</option>
              <option value="fat_loss">Fat loss</option>
            </select>
          </label>

          <label class="form-field">
            <span class="form-label">Experience</span>
            <select v-model="form.experience" class="form-input form-select" :disabled="loading">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </label>

          <label class="form-field">
            <span class="form-label">Days per week</span>
            <input v-model.number="form.days_per_week" type="number" min="1" max="6" class="form-input" :disabled="loading" />
          </label>

          <label class="form-field">
            <span class="form-label">Session minutes</span>
            <input v-model.number="form.session_minutes" type="number" min="20" max="120" class="form-input" :disabled="loading" />
          </label>

          <label class="form-field full-width">
            <span class="form-label">Equipment</span>
            <select v-model="form.equipment" class="form-input form-select" :disabled="loading">
              <option value="full_gym">Full gym</option>
              <option value="dumbbells">Dumbbells</option>
              <option value="bodyweight">Bodyweight</option>
            </select>
          </label>
        </div>
      </section>

      <section class="ll-card">
        <div class="card-heading">
          Focus Muscles
          <span class="card-heading-optional">(optional)</span>
        </div>
        <p class="focus-hint">Pick any muscles you want the plan to focus on.</p>
        <div class="muscle-chips">
          <button
            v-for="m in MUSCLE_OPTIONS"
            :key="m.value"
            type="button"
            :class="['muscle-chip', { 'muscle-chip--active': form.focus_muscles.includes(m.value) }]"
            :disabled="loading"
            @click="toggleMuscle(m.value)"
          >{{ m.label }}</button>
        </div>
      </section>

      <section class="ll-card">
        <label class="form-field">
          <span class="form-label">Notes</span>
          <textarea
            v-model="form.constraints"
            rows="6"
            class="form-input"
            :disabled="loading"
            placeholder="Examples:
- No dumbbells
- No barbells
- Prefer machines
- Extra glute focus
- Avoid shoulders (pain)"
          />
        </label>
      </section>

      <button :disabled="loading" type="submit" class="generate-button">
        <span>{{ loading ? "Generating…" : "Generate plan" }}</span>
        <span v-if="loading" class="btn-spinner"></span>
      </button>

      <LLLoadingPanel
        v-if="loading"
        title="Generating your training plan"
        subtitle="This usually takes a few seconds."
        :elapsed="elapsedSeconds"
        :steps="trainingSteps"
        hint="Cold starts can take a little longer."
      />

      <div v-if="error" class="error-message">{{ error }}</div>
      <PlanViewer v-if="result?.output" :plan="result.output" />
    </form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { usePlans } from "../../composables/usePlans";
import { useAuth } from "../../composables/useAuth";
import PlanViewer from "../../components/PlanViewer.vue";
import LLLoadingPanel from "../components/LLLoadingPanel.vue";

const router = useRouter();
const { generatePlan } = usePlans();
const { me } = useAuth();

const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<any>(null);

const form = ref({
  goal: "hypertrophy",
  experience: "intermediate",
  days_per_week: 4,
  session_minutes: 60,
  equipment: "full_gym",
  constraints: "",
  focus_muscles: [] as string[],
});

const MUSCLE_OPTIONS: { label: string; value: string }[] = [
  { label: "Chest",       value: "chest" },
  { label: "Back",        value: "back" },
  { label: "Lats",        value: "lats" },
  { label: "Shoulders",   value: "shoulders" },
  { label: "Front Delts", value: "front_delts" },
  { label: "Side Delts",  value: "side_delts" },
  { label: "Rear Delts",  value: "rear_delts" },
  { label: "Biceps",      value: "biceps" },
  { label: "Triceps",     value: "triceps" },
  { label: "Upper Back",  value: "upper_back" },
  { label: "Quads",       value: "quads" },
  { label: "Hamstrings",  value: "hamstrings" },
  { label: "Glutes",      value: "glutes" },
  { label: "Calves",      value: "calves" },
  { label: "Abs",         value: "abs" },
  { label: "Adductors",   value: "adductors" },
  { label: "Abductors",   value: "abductors" },
];

function toggleMuscle(value: string) {
  const idx = form.value.focus_muscles.indexOf(value);
  if (idx === -1) {
    form.value.focus_muscles.push(value);
  } else {
    form.value.focus_muscles.splice(idx, 1);
  }
}

// --- premium loading UX (status text + elapsed time)
const startedAtMs = ref<number | null>(null);
const elapsedSec = ref(0);
let timer: number | null = null;

const elapsedSeconds = computed(() => elapsedSec.value);

const trainingSteps = [
  "Reading your inputs",
  "Choosing exercises",
  "Building sets and reps",
  "Saving your plan",
];

watch(loading, (isLoading) => {
  if (isLoading) {
    startedAtMs.value = Date.now();
    elapsedSec.value = 0;

    if (timer != null) window.clearInterval(timer);
    timer = window.setInterval(() => {
      if (!startedAtMs.value) return;
      elapsedSec.value = Math.floor((Date.now() - startedAtMs.value) / 1000);
    }, 250);
  } else {
    if (timer != null) window.clearInterval(timer);
    timer = null;
  }
});

onBeforeUnmount(() => {
  if (timer != null) window.clearInterval(timer);
});

async function onSubmit() {
  loading.value = true;
  error.value = null;
  result.value = null;

  try {
    const res: any = await generatePlan(form.value);
    result.value = res;

    const user = await me();
    const planId = res?.plan_id;
    if (user && planId) {
      router.push(`/plans/${planId}`);
    }
  } catch (e: any) {
    error.value =
      e?.data?.detail ??
      e?.data?.message ??
      e?.message ??
      JSON.stringify(e, null, 2);
  } finally {
    loading.value = false;
  }
}
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');

:global(html),
:global(body) {
  background: #0a0a0a;
  margin: 0;
}

:global(#__nuxt) {
  background: #0a0a0a;
  min-height: 100vh;
}

.generate-page {
  background: #0a0a0a;
  color: #ffffff;
  padding: 38px 32px;
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
}

.generate-shell {
  width: min(1220px, 100%);
  margin-left: auto;
  margin-right: auto;
  display: grid;
  grid-template-columns: minmax(390px, 0.68fr) minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.generate-rail {
  position: sticky;
  top: 78px;
  min-height: 520px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 34px;
  background: #111111;
}

.rail-kicker,
.form-pill {
  width: fit-content;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background: transparent;
  color: rgba(255, 255, 255, 0.35);
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 4px 10px;
  margin: 0 0 14px;
}

.page-title {
  font-family: 'DM Sans', sans-serif;
  font-size: clamp(28px, 3.5vw, 44px);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin: 0 0 16px;
  color: #ffffff;
  max-width: 100%;
}

.page-sub {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
  max-width: 480px;
}

.rail-list {
  display: grid;
  gap: 11px;
  margin-top: 24px;
}

.rail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
}

.rail-item span {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

/* Form */
.generate-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  background: #111111;
  padding: 30px;
}

.form-header {
  text-align: center;
  margin-bottom: 10px;
}

.form-pill {
  margin: 0 auto 12px;
}

.form-header h2 {
  margin: 0 0 8px;
  font-size: clamp(20px, 2.5vw, 28px);
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #ffffff;
}

.form-header p {
  margin: 0;
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
}

.ll-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 20px;
}

.card-heading {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 16px;
}

/* Form grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field.full-width {
  grid-column: span 2;
}

.form-label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
}

.form-input {
  min-height: 42px;
  padding: 10px 14px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 14px;
  font-family: 'DM Sans', sans-serif;
  transition: border-color 0.15s;
  box-sizing: border-box;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.25);
  font-size: 13px;
}

.form-input:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.form-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='rgba(255,255,255,0.3)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 38px;
}

.form-select option {
  background: #111111;
  color: #ffffff;
}

textarea.form-input {
  resize: vertical;
  line-height: 1.55;
  min-height: 120px;
}

/* Generate button */
.generate-button {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 6px;
  color: #ffffff;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 11px 24px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, opacity 0.15s;
  width: fit-content;
  display: flex;
  align-items: center;
  gap: 10px;
}

.generate-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.8);
}

.generate-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.generate-form :deep(.ll-loading) {
  margin-top: 6px;
}

.error-message {
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid #f87171;
  border-radius: 0 3px 3px 0;
  color: #fca5a5;
  padding: 12px 16px;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.card-heading-optional {
  font-weight: 400;
  opacity: 0.45;
  text-transform: none;
  font-size: 10px;
  letter-spacing: 0.05em;
}

.focus-hint {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
  margin: 0 0 14px;
  line-height: 1.5;
}

.muscle-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.muscle-chip {
  padding: 5px 12px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: border-color 0.12s, color 0.12s, background 0.12s;
  user-select: none;
}

.muscle-chip:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.muscle-chip--active {
  border-color: rgba(255, 255, 255, 0.55);
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.muscle-chip:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .generate-page {
    padding: 24px 18px;
  }

  .generate-shell {
    grid-template-columns: 1fr;
  }

  .generate-rail {
    position: static;
    min-height: auto;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: span 1;
  }
}

@media (max-width: 560px) {
  .generate-page {
    padding: 18px 12px;
  }

  .generate-rail {
    display: none;
  }

  .glass-card {
    padding: 22px 16px;
  }

  .generate-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
