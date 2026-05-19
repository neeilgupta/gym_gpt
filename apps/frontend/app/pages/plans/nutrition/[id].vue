<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../../composables/usePlans";

const route = useRoute();
const { getNutritionPlan } = usePlans();

const plan = ref<any>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const input = computed(() => {
  try { return plan.value ? JSON.parse(plan.value.input_json) : null; } catch { return null; }
});

const output = computed(() => {
  try { return plan.value ? JSON.parse(plan.value.output_json) : null; } catch { return null; }
});

const SLOT_ORDER = ["breakfast", "snack 1", "snack", "lunch", "snack 2", "dinner"];

const mealsBySlot = computed(() => {
  const accepted: any[] = output.value?.accepted ?? [];
  const groups: Record<string, any[]> = {};
  for (const meal of accepted) {
    const slot = (meal.slot || meal.meal_type || "other").toLowerCase();
    if (!groups[slot]) groups[slot] = [];
    groups[slot].push(meal);
  }
  const ordered: { slot: string; meals: any[] }[] = [];
  const seen = new Set<string>();
  for (const s of SLOT_ORDER) {
    if (groups[s]) { ordered.push({ slot: s, meals: groups[s] }); seen.add(s); }
  }
  for (const [slot, meals] of Object.entries(groups)) {
    if (!seen.has(slot)) ordered.push({ slot, meals });
  }
  return ordered;
});

// Flatten meals in slot order: [{slot, meal}]
const flatMeals = computed(() => {
  const result: { slot: string; meal: any }[] = [];
  for (const group of mealsBySlot.value) {
    for (const meal of group.meals) {
      result.push({ slot: group.slot, meal });
    }
  }
  return result;
});

const totals = computed(() => {
  const accepted: any[] = output.value?.accepted ?? [];
  return accepted.reduce(
    (acc, meal) => {
      const m = meal.macros ?? meal;
      acc.calories += Number(m.calories ?? 0);
      acc.protein  += Number(m.protein ?? m.protein_g ?? 0);
      acc.carbs    += Number(m.carbs ?? m.carbs_g ?? 0);
      acc.fat      += Number(m.fat ?? m.fat_g ?? m.fats ?? 0);
      return acc;
    },
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );
});

const macroPercents = computed(() => {
  const cal = totals.value.calories;
  if (!cal) return { protein: 0, carbs: 0, fat: 0 };
  return {
    protein: Math.round((totals.value.protein * 4) / cal * 100),
    carbs: Math.round((totals.value.carbs * 4) / cal * 100),
    fat: Math.round((totals.value.fat * 9) / cal * 100),
  };
});

const allergies = computed<string[]>(() => input.value?.allergies ?? []);
const diet = computed<string | null>(() => input.value?.diet ?? null);

const statusText = computed(() => {
  const target = Number(input.value?.target_calories ?? 0);
  const actual = Math.round(totals.value.calories);
  if (!target || !actual) return null;
  const ratio = actual / target;
  if (ratio >= 0.95 && ratio <= 1.05) return "hits your targets";
  if (ratio < 0.95) return "slightly under target";
  return "over target";
});

const statusOk = computed(() => {
  const target = Number(input.value?.target_calories ?? 0);
  const actual = Math.round(totals.value.calories);
  if (!target || !actual) return true;
  const ratio = actual / target;
  return ratio >= 0.95 && ratio <= 1.05;
});

function slotLabel(slot: string): string {
  return slot.charAt(0).toUpperCase() + slot.slice(1);
}

function mealCalories(meal: any): number {
  return Math.round(Number(meal.macros?.calories ?? meal.calories ?? 0));
}

function mealMacros(meal: any): { p: number; c: number; f: number } {
  const m = meal.macros ?? meal;
  return {
    p: Math.round(Number(m.protein ?? m.protein_g ?? 0)),
    c: Math.round(Number(m.carbs ?? m.carbs_g ?? 0)),
    f: Math.round(Number(m.fat ?? m.fat_g ?? m.fats ?? 0)),
  };
}

onMounted(async () => {
  try {
    plan.value = await getNutritionPlan(route.params.id as string);
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Failed to load plan.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="page">
    <div v-if="loading" class="loading-card"><span class="spinner"></span>Loading nutrition plan…</div>
    <div v-else-if="error" class="error-card">{{ error }}</div>

    <template v-else-if="plan">
      <!-- Header -->
      <header class="page-header">
        <div>
          <p class="kicker">Meal Plan</p>
          <h1>{{ plan.title }}</h1>
        </div>
        <NuxtLink to="/nutrition" class="edit-btn">Edit</NuxtLink>
      </header>

      <!-- Macro grid -->
      <div class="macro-grid" v-if="output">
        <!-- Calories -->
        <div class="macro-cell">
          <div class="macro-label">Calories</div>
          <div class="macro-value-row">
            <span class="macro-value">{{ Math.round(totals.calories).toLocaleString() }}</span>
            <span class="macro-unit">kcal</span>
          </div>
        </div>
        <!-- Protein -->
        <div class="macro-cell">
          <div class="macro-label">Protein</div>
          <div class="macro-value-row">
            <span class="macro-value">{{ Math.round(totals.protein) }}</span>
            <span class="macro-unit">g</span>
          </div>
          <div class="macro-bar-track"><div class="macro-bar-fill" :style="{ width: `${macroPercents.protein}%` }"></div></div>
          <div class="macro-pct">{{ macroPercents.protein }}% kcal</div>
        </div>
        <!-- Carbs -->
        <div class="macro-cell">
          <div class="macro-label">Carbs</div>
          <div class="macro-value-row">
            <span class="macro-value">{{ Math.round(totals.carbs) }}</span>
            <span class="macro-unit">g</span>
          </div>
          <div class="macro-bar-track"><div class="macro-bar-fill" :style="{ width: `${macroPercents.carbs}%` }"></div></div>
          <div class="macro-pct">{{ macroPercents.carbs }}% kcal</div>
        </div>
        <!-- Fat -->
        <div class="macro-cell">
          <div class="macro-label">Fat</div>
          <div class="macro-value-row">
            <span class="macro-value">{{ Math.round(totals.fat) }}</span>
            <span class="macro-unit">g</span>
          </div>
          <div class="macro-bar-track"><div class="macro-bar-fill" :style="{ width: `${macroPercents.fat}%` }"></div></div>
          <div class="macro-pct">{{ macroPercents.fat }}% kcal</div>
        </div>
      </div>

      <!-- Body: meals + sidebar -->
      <div class="body-layout">
        <!-- Meals panel -->
        <div class="meals-panel">
          <div class="meals-head">
            <span>Meals</span>
            <span class="meals-count">{{ flatMeals.length }} slots</span>
          </div>

          <div v-if="flatMeals.length === 0" class="meals-empty">No meals in this plan.</div>

          <div
            v-for="({ slot, meal }, i) in flatMeals"
            :key="`${slot}-${i}`"
            class="meal-row"
          >
            <span class="meal-slot">{{ slotLabel(slot) }}</span>
            <span class="meal-name">{{ meal.name }}</span>
            <span class="meal-kcal">{{ mealCalories(meal) }}</span>
            <span class="meal-macros">
              P{{ mealMacros(meal).p }}&nbsp;C{{ mealMacros(meal).c }}&nbsp;F{{ mealMacros(meal).f }}
            </span>
          </div>

          <!-- Daily total -->
          <div class="daily-total-row">
            <span class="total-label">Daily total</span>
            <span class="total-value">
              {{ Math.round(totals.calories) }} kcal
              <template v-if="input?.target_calories">
                · target {{ input.target_calories }}
              </template>
            </span>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="sidebar">
          <!-- Allergies -->
          <div class="sidebar-section">
            <div class="sidebar-label">Allergies</div>
            <div v-if="allergies.length" class="allergy-pills">
              <span v-for="a in allergies" :key="a" class="allergy-pill">{{ a }}</span>
            </div>
            <div v-else class="sidebar-none">none</div>
            <div class="sidebar-dim" style="margin-top: 8px;">never included</div>
          </div>

          <!-- Diet -->
          <div class="sidebar-section">
            <div class="sidebar-label">Diet</div>
            <span v-if="diet && diet !== 'none'" class="diet-pill">{{ diet }}</span>
            <span v-else class="diet-pill">None</span>
          </div>

          <!-- Status -->
          <div class="sidebar-section" v-if="statusText">
            <div class="sidebar-label">Status</div>
            <div class="status-row">
              <span class="status-dot" :class="{ ok: statusOk, warn: !statusOk }"></span>
              <span class="status-text" :class="{ ok: statusOk, warn: !statusOk }">{{ statusText }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:global(html), :global(body) { background: #0a0a0a; margin: 0; }
:global(#__nuxt) { background: #0a0a0a; min-height: 100vh; }

.page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 36px 28px 80px;
  color: #ffffff;
  font-family: 'DM Sans', sans-serif;
  background: #0a0a0a;
  min-height: 100vh;
}

/* Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.kicker {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin: 0 0 6px;
}

h1 {
  font-size: clamp(24px, 4vw, 38px);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin: 0;
}

.edit-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.65);
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  font-weight: 500;
  padding: 7px 16px;
  text-decoration: none;
  white-space: nowrap;
  transition: border-color 0.15s, color 0.15s;
  flex-shrink: 0;
  margin-top: 4px;
}

.edit-btn:hover {
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
}

/* Macro grid */
.macro-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 14px;
}

.macro-cell {
  padding: 20px 18px;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.macro-cell:last-child {
  border-right: none;
}

.macro-label {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 10px;
}

.macro-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.macro-value {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1;
  color: #ffffff;
}

.macro-unit {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
}

.macro-bar-track {
  height: 2px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  margin: 10px 0 5px;
  overflow: hidden;
}

.macro-bar-fill {
  height: 100%;
  background: #60a5fa;
  border-radius: 999px;
  max-width: 100%;
}

.macro-pct {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.28);
}

/* Body layout */
.body-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 12px;
  align-items: start;
}

/* Meals panel */
.meals-panel {
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  overflow: hidden;
}

.meals-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
}

.meals-count {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.25);
}

.meals-empty {
  padding: 20px 16px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.35);
}

.meal-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.meal-row:last-of-type {
  border-bottom: none;
}

.meal-slot {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #60a5fa;
  min-width: 72px;
  flex-shrink: 0;
}

.meal-name {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meal-kcal {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  min-width: 36px;
  text-align: right;
  flex-shrink: 0;
}

.meal-macros {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  min-width: 110px;
  text-align: right;
  flex-shrink: 0;
}

.daily-total-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-family: 'DM Mono', monospace;
  font-size: 10px;
}

.total-label {
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.25);
}

.total-value {
  color: rgba(255, 255, 255, 0.5);
  font-size: 11px;
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-section {
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 14px 16px;
}

.sidebar-label {
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.28);
  margin-bottom: 10px;
}

.allergy-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.allergy-pill {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 3px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  padding: 2px 8px;
}

.diet-pill {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  padding: 2px 8px;
  display: inline-block;
}

.sidebar-none {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
}

.sidebar-dim {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.2);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 7px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  flex-shrink: 0;
}

.status-dot.ok { background: #4ade80; }
.status-dot.warn { background: #fbbf24; }

.status-text {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
}

.status-text.ok { color: #4ade80; }
.status-text.warn { color: #fbbf24; }

/* Loading / error */
.loading-card,
.error-card {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 16px;
  background: #111111;
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
}

.error-card { color: #fca5a5; }

.spinner {
  width: 13px;
  height: 13px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #ffffff;
  border-radius: 999px;
  animation: spin 0.75s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 760px) {
  .macro-grid { grid-template-columns: repeat(2, 1fr); }
  .macro-cell { border-bottom: 1px solid rgba(255,255,255,0.05); }
  .body-layout { grid-template-columns: 1fr; }
  .meal-macros { display: none; }
}

@media (max-width: 480px) {
  .page { padding: 24px 14px 64px; }
  h1 { font-size: 22px; }
}
</style>
