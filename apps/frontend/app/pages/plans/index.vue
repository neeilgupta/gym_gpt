<template>
  <div class="page">
    <header class="page-header">
      <h1>Your plans</h1>
      <NuxtLink to="/generate" class="btn-new">+ New plan</NuxtLink>
    </header>

    <!-- Not logged in -->
    <div v-if="!user && !authLoading" class="empty-card">
      <p class="empty-title">Sign in to view your plans</p>
      <p class="empty-copy">Your saved workout and nutrition plans will appear here.</p>
      <NuxtLink to="/login" class="btn-outline">Sign in</NuxtLink>
    </div>

    <template v-else-if="user">
      <!-- Filter row -->
      <div class="filter-row">
        <div class="filter-tabs">
          <button
            v-for="tab in filterTabs"
            :key="tab.key"
            class="filter-tab"
            :class="{ active: filterTab === tab.key }"
            @click="filterTab = tab.key"
          >
            {{ tab.label }} {{ tab.count }}
          </button>
        </div>
        <span class="sort-label">sort updated ↓</span>
      </div>

      <!-- Plans table -->
      <div class="plans-table">
        <!-- Table header -->
        <div class="table-head">
          <div class="col-kind">Kind</div>
          <div class="col-title">Title</div>
          <div class="col-versions">Versions</div>
          <div class="col-size">Size</div>
          <div class="col-updated">Updated</div>
          <div class="col-arrow"></div>
        </div>

        <!-- Loading -->
        <div v-if="plansLoading" class="table-msg">
          <span class="spinner"></span> Loading…
        </div>

        <!-- Empty -->
        <div v-else-if="filteredPlans.length === 0" class="table-msg muted">
          No {{ filterTab === 'all' ? '' : filterTab }} plans yet.
        </div>

        <!-- Rows -->
        <template v-else>
          <div v-for="p in filteredPlans" :key="`${p.kind}-${p.uid}`" class="plan-row-wrap">
            <!-- Normal row -->
            <NuxtLink
              v-if="editingId !== `${p.kind[0]}-${p.uid}`"
              class="plan-row"
              :to="planHref(p)"
            >
              <div class="col-kind">
                <div class="kind-badge" :class="p.kind">{{ p.kind === 'training' ? 'T' : 'N' }}</div>
              </div>
              <div class="col-title">
                <span class="plan-title">{{ p.title || "Untitled" }}</span>
                <span class="plan-id">#{{ p.uid }}</span>
              </div>
              <div class="col-versions col-mono">{{ planVersions(p) }}</div>
              <div class="col-size col-mono">{{ planSize(p) }}</div>
              <div class="col-updated col-mono">{{ timeAgo(p.created_at) }}</div>
              <div class="col-arrow">→</div>
            </NuxtLink>

            <!-- Rename row -->
            <div v-else class="plan-row editing">
              <div class="col-kind">
                <div class="kind-badge" :class="p.kind">{{ p.kind === 'training' ? 'T' : 'N' }}</div>
              </div>
              <div class="col-title rename-cell">
                <input
                  v-model="editingTitle"
                  class="rename-input"
                  @keydown.enter="submitRename(p)"
                  @keydown.escape="cancelRename"
                  autofocus
                />
                <div class="rename-actions">
                  <button class="rename-save" @click="submitRename(p)">Save</button>
                  <button class="rename-cancel" @click="cancelRename">Cancel</button>
                </div>
              </div>
              <div class="col-versions"></div>
              <div class="col-size"></div>
              <div class="col-updated"></div>
              <div class="col-arrow"></div>
            </div>

            <!-- Rename trigger -->
            <button
              class="rename-btn"
              title="Rename"
              @click.prevent.stop="startRename(`${p.kind[0]}-${p.uid}`, p.title || '')"
            >✎</button>
          </div>
        </template>
      </div>

      <p v-if="renameError" class="error-msg">{{ renameError }}</p>
      <p v-if="plansError || nutritionError" class="error-msg">{{ plansError || nutritionError }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { usePlans } from "../../../composables/usePlans";
import { useAuth } from "../../../composables/useAuth";

type User = { id: number; email: string };

const { listMyPlans, listMyNutritionPlans, renamePlan, renameNutritionPlan } = usePlans();
const { logout, me } = useAuth();

const user = ref<User | null>(null);
const authLoading = ref(false);
const authError = ref<string | null>(null);

const plans = ref<any[]>([]);
const nutritionPlans = ref<any[]>([]);
const plansLoading = ref(false);
const plansError = ref<string | null>(null);
const nutritionError = ref<string | null>(null);

const editingId = ref<string | null>(null);
const editingTitle = ref("");
const renameError = ref<string | null>(null);

const filterTab = ref<"all" | "training" | "nutrition">("all");

// Unified sorted list with kind tags
const combinedPlans = computed(() => {
  const workout = plans.value.map(p => ({
    ...p,
    kind: "training" as const,
    uid: p.plan_id,
  }));
  const nutrition = nutritionPlans.value.map(p => ({
    ...p,
    kind: "nutrition" as const,
    uid: p.id,
  }));
  return [...workout, ...nutrition].sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
});

const filteredPlans = computed(() => {
  if (filterTab.value === "all") return combinedPlans.value;
  return combinedPlans.value.filter(p => p.kind === filterTab.value);
});

const filterTabs = computed(() => [
  { key: "all" as const, label: "All", count: combinedPlans.value.length },
  { key: "training" as const, label: "Training", count: plans.value.length },
  { key: "nutrition" as const, label: "Nutrition", count: nutritionPlans.value.length },
]);

function timeAgo(iso?: string): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 7) return `${days}d ago`;
  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks}w ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

function planSize(p: any): string {
  try {
    const input = typeof p.input_json === "string" ? JSON.parse(p.input_json) : p.input_json;
    if (p.kind === "training") {
      const d = input?.days_per_week;
      return d != null ? `${d}d` : "—";
    } else {
      const output = typeof p.output_json === "string" ? JSON.parse(p.output_json) : p.output_json;
      const n = output?.accepted?.length ?? output?.meals?.length;
      return n != null ? `${n}m` : "—";
    }
  } catch {
    return "—";
  }
}

function planVersions(p: any): string {
  if (p.kind === "training") return `v${p.version ?? 1}`;
  return "v1";
}

function planHref(p: any): string {
  return p.kind === "training" ? `/plans/${p.uid}` : `/plans/nutrition/${p.uid}`;
}

async function loadMine() {
  if (!user.value) return;
  plansLoading.value = true;
  plansError.value = null;
  nutritionError.value = null;
  try {
    const [workoutRes, nutritionRes]: any[] = await Promise.all([
      listMyPlans(),
      listMyNutritionPlans(),
    ]);
    plans.value = workoutRes?.items ?? [];
    nutritionPlans.value = nutritionRes?.items ?? [];
  } catch (e: any) {
    plansError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    plansLoading.value = false;
  }
}

async function onLogout() {
  authLoading.value = true;
  authError.value = null;
  try {
    await logout();
    user.value = null;
    plans.value = [];
    nutritionPlans.value = [];
  } catch (e: any) {
    authError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    authLoading.value = false;
  }
}

function startRename(key: string, currentTitle: string) {
  editingId.value = key;
  editingTitle.value = currentTitle;
  renameError.value = null;
}

function cancelRename() {
  editingId.value = null;
  editingTitle.value = "";
}

async function submitRename(p: any) {
  const title = editingTitle.value.trim();
  if (!title) return;
  renameError.value = null;
  try {
    if (p.kind === "training") {
      await renamePlan(p.uid, title);
    } else {
      await renameNutritionPlan(p.uid, title);
    }
    p.title = title;
    editingId.value = null;
  } catch (err: any) {
    renameError.value = err?.data?.detail ?? "Rename failed";
  }
}

onMounted(async () => {
  authLoading.value = true;
  try {
    user.value = await me();
    if (user.value) await loadMine();
  } catch (e: any) {
    authError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    authLoading.value = false;
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:global(html), :global(body) { background: #0a0a0a; margin: 0; }
:global(#__nuxt) { background: #0a0a0a; min-height: 100vh; }

.page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 44px 32px 80px;
  color: #ffffff;
  font-family: 'DM Sans', sans-serif;
  background: #0a0a0a;
  min-height: 100vh;
}

/* Header */
.page-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
}

h1 {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1;
}

/* Solid white "New plan" button */
.btn-new {
  background: #ffffff;
  color: #111111;
  border: none;
  border-radius: 6px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 600;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  transition: background 0.15s;
}

.btn-new:hover {
  background: #e8e8e8;
}

/* Filter row */
.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.filter-tabs {
  display: flex;
  gap: 4px;
}

.filter-tab {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 20px;
  padding: 5px 13px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.filter-tab.active {
  background: #ffffff;
  color: #111111;
  border-color: #ffffff;
}

.filter-tab:not(.active):hover {
  color: rgba(255, 255, 255, 0.7);
  border-color: rgba(255, 255, 255, 0.12);
}

.sort-label {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.28);
  white-space: nowrap;
}

/* Plans table */
.plans-table {
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  overflow: hidden;
}

/* Column widths */
.col-kind    { width: 44px; flex-shrink: 0; }
.col-title   { flex: 1; min-width: 0; display: flex; align-items: center; gap: 0; }
.col-versions{ width: 80px; flex-shrink: 0; }
.col-size    { width: 64px; flex-shrink: 0; }
.col-updated { width: 96px; flex-shrink: 0; }
.col-arrow   { width: 28px; flex-shrink: 0; text-align: right; }

.table-head {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
  gap: 12px;
  font-family: 'DM Mono', monospace;
  font-size: 9px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.28);
}

.plan-row-wrap {
  position: relative;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.plan-row-wrap:last-child {
  border-bottom: none;
}

.plan-row {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  color: inherit;
  text-decoration: none;
  transition: background 0.12s;
}

.plan-row:hover {
  background: rgba(255, 255, 255, 0.025);
}

.plan-row.editing {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
}

/* Kind badge */
.kind-badge {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  display: inline-grid;
  place-items: center;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.kind-badge.training {
  background: rgba(99, 102, 241, 0.18);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.kind-badge.nutrition {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

/* Title + id */
.plan-title {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plan-id {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.28);
  margin-left: 7px;
  flex-shrink: 0;
}

.col-mono {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.col-arrow {
  color: rgba(255, 255, 255, 0.22);
  font-size: 14px;
}

/* Table messages */
.table-msg {
  padding: 24px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
}

.muted {
  color: rgba(255, 255, 255, 0.3);
}

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

/* Rename */
.rename-cell {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rename-input {
  flex: 1;
  min-width: 120px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: #ffffff;
  padding: 6px 10px;
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.15s;
}

.rename-input:focus { border-color: rgba(255, 255, 255, 0.4); }

.rename-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.rename-save,
.rename-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.65);
  font-size: 11px;
  font-family: 'DM Mono', monospace;
  padding: 4px 10px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.rename-save:hover, .rename-cancel:hover {
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
}

.rename-btn {
  flex-shrink: 0;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.2);
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.15s;
  margin-right: 6px;
}

.rename-btn:hover { color: rgba(255, 255, 255, 0.6); }

/* Empty state */
.empty-card {
  border: 1px dashed rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  padding: 40px 24px;
  text-align: center;
}

.empty-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
}

.empty-copy {
  margin: 0 0 20px;
  color: rgba(255, 255, 255, 0.45);
  font-size: 14px;
  line-height: 1.5;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  padding: 9px 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: transparent;
  color: #ffffff;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: border-color 0.15s, background 0.15s;
}

.btn-outline:hover {
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.04);
}

.error-msg {
  color: #fca5a5;
  margin-top: 12px;
  font-size: 13px;
  font-family: 'DM Mono', monospace;
}

@media (max-width: 720px) {
  .page { padding: 28px 16px 64px; }
  h1 { font-size: 26px; }
  .col-versions, .col-size { display: none; }
  .col-updated { width: 72px; font-size: 11px; }
  .table-head .col-versions,
  .table-head .col-size { display: none; }
}

@media (max-width: 480px) {
  .col-updated { display: none; }
  .table-head .col-updated { display: none; }
  .filter-tab { padding: 4px 10px; font-size: 10px; }
}
</style>
