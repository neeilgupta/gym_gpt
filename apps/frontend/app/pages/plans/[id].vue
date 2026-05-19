<template>
  <main class="plan-detail-page">
    <section v-if="pending" class="status-panel">Loading plan...</section>
    <section v-else-if="errorMsg" class="status-panel error">{{ errorMsg }}</section>

    <section v-else-if="selectedOutput" class="plan-workspace">
      <aside class="history-rail">
        <NuxtLink to="/plans" class="back-link">&larr; All plans</NuxtLink>

        <div>
          <div class="eyebrow">Plan</div>
          <div class="mono plan-id">p_{{ id }}</div>
        </div>

        <div class="history-block">
          <div class="eyebrow history-label">History</div>
          <div v-if="versionsPending" class="rail-note">Loading versions...</div>
          <div v-else-if="!versions.length" class="rail-note">No versions yet.</div>
          <button
            v-for="v in versions"
            v-else
            :key="v.version"
            type="button"
            :class="['version-row', { active: v.version === selectedVersionNumber }]"
            @click="selectedVersionNumber = v.version"
          >
            <span class="mono version-num">v{{ v.version }}</span>
            <span class="version-copy">
              <span>{{ versionNote(v) }}</span>
              <span class="mono version-time">{{ formatVersionTime(v.created_at) }}</span>
            </span>
            <span v-if="v.version === latestVersionNumber" class="pill accent">NOW</span>
          </button>
        </div>

        <p v-if="versionsError" class="rail-error">{{ versionsError }}</p>
      </aside>

      <section class="plan-main">
        <header class="plan-header">
          <div>
            <div class="eyebrow">Workout plan</div>
            <h1>{{ selectedOutput.title }}</h1>
          </div>

          <div class="header-actions">
            <button
              v-if="selectedVersionNumber != null && selectedVersionNumber !== latestVersionNumber"
              type="button"
              class="btn secondary"
              :disabled="restoring || versionsPending"
              @click="restoreSelected"
            >
              {{ restoring ? "Restoring..." : `Restore v${selectedVersionNumber}` }}
            </button>
            <button type="button" class="btn primary" @click="focusComposer">Edit plan</button>
          </div>
        </header>

        <PlanViewer
          :plan="selectedOutput"
          :input="selectedInput"
          :diff="displayDiff"
          :version="selectedVersionNumber"
          :selected-day="selectedDay"
          @update:selected-day="selectedDay = $event"
        />
      </section>

      <aside class="chat-rail">
        <header class="chat-head">
          <div class="eyebrow">Edit</div>
          <span class="pill">v{{ selectedVersionNumber ?? ((plan as any)?.version ?? "?") }}</span>
        </header>

        <div class="quick-edits">
          <button type="button" @click="insertQuickEdit('avoid shoulders')">Avoid shoulders</button>
          <button type="button" @click="insertQuickEdit('no barbells')">No barbells</button>
          <button type="button" @click="insertQuickEdit('prefer cables')">Prefer cables</button>
        </div>

        <div ref="chatScrollEl" class="chat-messages">
          <div v-if="!chatHistory.length" class="empty-chat">
            No edits yet. Send a message to start.
          </div>

          <article v-for="(m, i) in chatHistory" :key="`ch-${i}`" class="chat-msg">
            <div class="chat-meta">
              <span class="mono who">you</span>
              <span class="mono">{{ formatChatTime(m.created_at) }}</span>
            </div>
            <div class="chat-bubble">{{ m.message }}</div>
          </article>
        </div>

        <footer class="composer">
          <textarea
            ref="composerEl"
            v-model="editMessage"
            rows="3"
            placeholder="e.g. swap barbell rows for cables"
            class="chat-textarea"
            @keydown.meta.enter.prevent="sendEditAndApply()"
            @keydown.ctrl.enter.prevent="sendEditAndApply()"
          />
          <div class="composer-row">
            <span class="mono send-hint">Cmd+Enter to send</span>
            <button
              type="button"
              class="btn primary"
              :disabled="editPending || applyPending || !editMessage.trim()"
              @click="sendEditAndApply()"
            >
              {{ (editPending || applyPending) ? "Working..." : "Send" }}
            </button>
          </div>
          <div v-if="appliedOk || editError || applyError" class="composer-status">
            <span v-if="appliedOk" class="inline-success">Applied</span>
            <span v-if="editError" class="inline-error">{{ editError }}</span>
            <span v-if="applyError" class="inline-error">{{ applyError }}</span>
          </div>
        </footer>
      </aside>
    </section>

    <section v-else class="status-panel">No plan data found.</section>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ layout: "plan" });

import { computed, nextTick, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../composables/usePlans";
import { useRuntimeConfig } from "#imports";
import PlanViewer from "../../../components/PlanViewer.vue";

type PlanOutput = {
  title: string;
  summary: string;
  weekly_split: any[];
  progression_notes?: string[];
  safety_notes?: string[];
};

type PlanDetail = {
  plan_id: number;
  version: number;
  input?: any;
  output?: PlanOutput;
  diff?: any;
  is_restored?: boolean;
  restored_from?: number | null;
  created_at?: string;
  summary?: string;
  weekly_split?: any[];
  title?: string;
};

type VersionItem = {
  version: number;
  created_at?: string;
  input: any;
  output: any;
  diff?: any;
  is_restored?: boolean;
  restored_from?: number | null;
};

type EditPlanResponseT = {
  can_apply: boolean;
  proposed_patch: {
    constraints_add: string[];
    constraints_remove: string[];
    preferences_add: string[];
    preferences_remove: string[];
    emphasis: string | null;
    avoid: string[];
    set_style: "low" | "standard" | "high" | null;
    rep_style: "strength" | "hypertrophy" | "pump" | null;
  };
  change_summary: string[];
  errors: string[];
};

const route = useRoute();
const id = computed(() => String(route.params.id));
const { getPlan } = usePlans();

const { data: plan, pending, error, refresh } = await useAsyncData(
  () => `plan-${id.value}`,
  () => getPlan(id.value),
);

const selectedDay = ref(0);
const composerEl = ref<HTMLTextAreaElement | null>(null);
const chatScrollEl = ref<HTMLElement | null>(null);

const editMessage = ref("");
const editPending = ref(false);
const appliedOk = ref(false);
const editError = ref<string | null>(null);
const editResponse = ref<EditPlanResponseT | null>(null);
const applyPending = ref(false);
const applyError = ref<string | null>(null);
const applyResponse = ref<any>(null);
const lastDiff = ref<any | null>(null);

const versions = ref<VersionItem[]>([]);
const selectedVersionNumber = ref<number | null>(null);
const restoring = ref(false);
const versionsPending = ref(false);
const versionsError = ref<string | null>(null);
const versionsReqToken = ref(0);

const config = useRuntimeConfig();
const apiBase = (config.public as any)?.apiBase ?? "http://127.0.0.1:8000";

const errorMsg = computed(() => {
  const e: any = error.value;
  return e?.data?.detail ?? e?.message ?? (e ? String(e) : null);
});

const output = computed<PlanOutput | null>(() => {
  const p = plan.value as PlanDetail | null;
  if (!p) return null;
  if (p.output?.weekly_split) return p.output;
  if ((p as any).weekly_split) {
    return {
      title: (p as any).title ?? "Workout Plan",
      summary: (p as any).summary ?? "",
      weekly_split: (p as any).weekly_split ?? [],
      progression_notes: (p as any).progression_notes ?? [],
      safety_notes: (p as any).safety_notes ?? [],
    };
  }
  return null;
});

const input = computed<any>(() => {
  const p: any = plan.value;
  return p?.input ?? null;
});

const chatHistory = computed<any[]>(() => {
  const h = selectedInput.value?.chat_history ?? (plan.value as any)?.input?.chat_history;
  return Array.isArray(h) ? h : [];
});

const latestVersionNumber = computed(() => {
  if (!versions.value.length) return (plan.value as any)?.version ?? null;
  return Math.max(...versions.value.map((v) => v.version));
});

const selectedVersion = computed<VersionItem | null>(() => {
  if (selectedVersionNumber.value == null) return null;
  return versions.value.find((v) => v.version === selectedVersionNumber.value) ?? null;
});

const selectedOutput = computed<PlanOutput | null>(() => {
  const sv = selectedVersion.value;
  if (sv?.output?.weekly_split) return sv.output as PlanOutput;
  return output.value;
});

const selectedInput = computed<any>(() => {
  const sv = selectedVersion.value;
  if (sv?.input) return sv.input;
  return input.value;
});

const displayDiff = computed<any | null>(() => {
  const sv = selectedVersion.value;
  const selNum = selectedVersionNumber.value;

  if (selNum != null && sv) {
    if (sv.diff !== undefined) return sv.diff ?? null;
    return null;
  }

  return lastDiff.value;
});

const hasRealPatch = computed(() => {
  const p = editResponse.value?.proposed_patch;
  if (!p) return false;
  return (
    (p.constraints_add?.length ?? 0) > 0 ||
    (p.constraints_remove?.length ?? 0) > 0 ||
    (p.preferences_add?.length ?? 0) > 0 ||
    (p.preferences_remove?.length ?? 0) > 0 ||
    (p.avoid?.length ?? 0) > 0 ||
    !!p.emphasis ||
    !!p.set_style ||
    !!p.rep_style
  );
});

watch(
  () => id.value,
  () => {
    lastDiff.value = null;
    applyResponse.value = null;
    applyError.value = null;
    editResponse.value = null;
    editError.value = null;
    editMessage.value = "";
    selectedDay.value = 0;
    versions.value = [];
    selectedVersionNumber.value = null;
    fetchVersions();
  },
);

watch(chatHistory, async () => {
  await nextTick();
  scrollChatToBottom();
});

function authedPlanFetch<T = any>(path: string, options: any = {}) {
  return $fetch<T>(`${apiBase}${path}`, {
    ...options,
    credentials: "include",
  });
}

async function fetchVersions(opts?: { keepSelection?: boolean }) {
  const keepSelection = opts?.keepSelection ?? false;
  versionsPending.value = true;
  versionsError.value = null;
  const token = ++versionsReqToken.value;

  try {
    const res: any = await authedPlanFetch(`/plans/${id.value}/versions`);
    if (token !== versionsReqToken.value) return;

    const items: VersionItem[] = res.items ?? res ?? [];
    versions.value = [...items].sort((a, b) => b.version - a.version);

    const latest = versions.value[0]?.version ?? null;
    if (keepSelection && selectedVersionNumber.value != null) {
      const stillExists = versions.value.some((v) => v.version === selectedVersionNumber.value);
      if (!stillExists) selectedVersionNumber.value = latest;
    } else {
      selectedVersionNumber.value = latest;
    }
  } catch (e: any) {
    if (token !== versionsReqToken.value) return;
    versionsError.value = e?.data?.detail ?? e?.message ?? String(e);
    versions.value = [];
    selectedVersionNumber.value = null;
  } finally {
    if (token === versionsReqToken.value) versionsPending.value = false;
  }
}

await fetchVersions();

async function restoreSelected() {
  if (!selectedVersion.value) return;

  const v = selectedVersion.value.version;
  if (v === latestVersionNumber.value) return;

  restoring.value = true;
  try {
    await authedPlanFetch(`/plans/${id.value}/restore`, {
      method: "POST",
      body: { version: v },
    });
    await fetchVersions({ keepSelection: false });
    await refresh();
    lastDiff.value = null;
  } catch (e: any) {
    versionsError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    restoring.value = false;
  }
}

async function applyPatch() {
  applyError.value = null;
  applyResponse.value = null;

  const patch = editResponse.value?.proposed_patch;
  if (!patch) {
    applyError.value = "No proposed_patch to apply. Send an edit first.";
    return;
  }
  if (!hasRealPatch.value) {
    applyError.value = "No real changes to apply yet.";
    return;
  }

  applyPending.value = true;
  try {
    const res = await authedPlanFetch(`/plans/${id.value}/apply`, {
      method: "POST",
      body: patch,
    });
    applyResponse.value = res;
    lastDiff.value = (res as any)?.diff ?? null;
    await refresh();
    await fetchVersions({ keepSelection: false });
    lastDiff.value = null;
    appliedOk.value = true;
    setTimeout(() => (appliedOk.value = false), 1500);
    editMessage.value = "";
    editResponse.value = null;
    editError.value = null;
    applyError.value = null;
  } catch (e: any) {
    applyResponse.value = e?.data?.detail ?? e?.data ?? null;
    applyError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    applyPending.value = false;
  }
}

async function sendEdit() {
  editError.value = null;
  editResponse.value = null;
  applyResponse.value = null;
  applyError.value = null;

  const msg = editMessage.value.trim();
  if (!msg) return;

  editPending.value = true;
  try {
    editResponse.value = await authedPlanFetch<EditPlanResponseT>(`/plans/${id.value}/edit`, {
      method: "POST",
      body: { message: msg },
    });
  } catch (e: any) {
    editError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    editPending.value = false;
  }
}

async function sendEditAndApply() {
  editError.value = null;
  applyError.value = null;

  const msg = editMessage.value.trim();
  if (!msg) return;

  editPending.value = true;
  applyPending.value = true;

  try {
    const res = await authedPlanFetch<EditPlanResponseT>(`/plans/${id.value}/edit`, {
      method: "POST",
      body: { message: msg },
    });

    editResponse.value = res;

    if (!res?.can_apply) {
      editError.value = res?.errors?.[0] ?? "No actionable changes detected.";
      return;
    }

    const patch = res.proposed_patch;
    if (!patch) {
      editError.value = "No proposed_patch returned.";
      return;
    }

    const applyRes = await authedPlanFetch(`/plans/${id.value}/apply`, {
      method: "POST",
      body: patch,
    });

    applyResponse.value = applyRes;
    lastDiff.value = (applyRes as any)?.diff ?? null;
    await refresh();
    await fetchVersions({ keepSelection: false });
    lastDiff.value = null;

    appliedOk.value = true;
    setTimeout(() => (appliedOk.value = false), 1500);
    editMessage.value = "";
    editResponse.value = null;
  } catch (e: any) {
    const msg = e?.data?.detail ?? e?.message ?? String(e);
    if (!editResponse.value) editError.value = msg;
    else applyError.value = msg;
  } finally {
    editPending.value = false;
    applyPending.value = false;
  }
}

function focusComposer() {
  composerEl.value?.focus();
}

function insertQuickEdit(message: string) {
  editMessage.value = message;
  focusComposer();
}

function scrollChatToBottom() {
  const el = chatScrollEl.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

function formatChatTime(iso: any) {
  if (!iso) return "";
  try {
    return new Date(String(iso)).toLocaleString([], {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(iso);
  }
}

function formatVersionTime(iso: any) {
  if (!iso) return "";
  try {
    return new Date(String(iso)).toLocaleString([], {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return String(iso);
  }
}

function versionNote(v: VersionItem) {
  if (v.is_restored && v.restored_from) return `Restored from v${v.restored_from}`;
  const diff = v.diff;
  if (diff?.restored_from) return `Restored from v${diff.restored_from}`;
  const added = Array.isArray(diff?.added_exercises) ? diff.added_exercises.length : 0;
  const replaced = Array.isArray(diff?.replaced_exercises) ? diff.replaced_exercises.length : 0;
  const removed = Array.isArray(diff?.removed_exercises) ? diff.removed_exercises.length : 0;
  const total = added + replaced + removed;
  if (total > 0) return `${added} added · ${replaced} replaced · ${removed} removed`;
  return v.version === 1 ? "Generated" : "Updated plan";
}
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap");

:global(html),
:global(body) {
  background: #0a0a0a;
  margin: 0;
}

:global(#__nuxt) {
  background: #0a0a0a;
  min-height: 100vh;
}

.plan-detail-page {
  --ll-bg: #0a0a0a;
  --ll-surface: #111111;
  --ll-surface-2: #0f0f0f;
  --ll-tint: rgba(255, 255, 255, 0.04);
  --ll-ink: #ffffff;
  --ll-muted: rgba(255, 255, 255, 0.45);
  --ll-faint: rgba(255, 255, 255, 0.25);
  --ll-border: rgba(255, 255, 255, 0.08);
  --ll-accent: rgba(255, 255, 255, 0.7);
  --ll-accent-tint: rgba(255, 255, 255, 0.06);
  --ll-accent-line: rgba(255, 255, 255, 0.15);
  --ll-ok: #4ade80;
  --ll-ok-tint: rgba(74, 222, 128, 0.08);
  --ll-bad: #f87171;
  --ll-bad-tint: rgba(248, 113, 113, 0.08);
  --ll-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --ll-mono: 'DM Mono', ui-monospace, SFMono-Regular, Menlo, monospace;

  background: var(--ll-bg);
  color: var(--ll-ink);
  font-family: var(--ll-sans);
  font-size: 13px;
  line-height: 1.5;
  min-height: calc(100vh - 54px);
}

.plan-workspace {
  background: var(--ll-bg);
  display: grid;
  grid-template-columns: 200px minmax(0, 1fr) 320px;
  height: calc(100vh - 54px);
  min-height: 680px;
}

.history-rail,
.plan-main,
.chat-rail {
  min-height: 0;
  overflow: auto;
}

.history-rail {
  border-right: 0.5px solid var(--ll-border);
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 20px 16px;
}

.plan-main {
  padding: 24px 32px;
}

.chat-rail {
  background: var(--ll-surface-2);
  border-left: 0.5px solid var(--ll-border);
  display: flex;
  flex-direction: column;
}

.mono,
.eyebrow {
  font-family: var(--ll-mono);
}

.eyebrow {
  color: var(--ll-muted);
  font-size: 10.5px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.back-link {
  color: var(--ll-muted);
  font-family: var(--ll-mono);
  font-size: 11px;
  text-decoration: none;
}

.back-link:hover {
  color: var(--ll-accent);
}

.plan-id {
  color: var(--ll-ink);
  display: block;
  font-size: 13px;
  margin-top: 4px;
}

.history-label {
  margin-bottom: 10px;
}

.history-block {
  min-width: 0;
}

.rail-note,
.rail-error {
  color: var(--ll-muted);
  font-size: 12px;
  margin: 0;
}

.rail-error {
  color: var(--ll-bad);
}

.version-row {
  align-items: flex-start;
  background: transparent;
  border: 0;
  border-radius: 5px;
  color: var(--ll-muted);
  cursor: pointer;
  display: flex;
  font-family: inherit;
  gap: 10px;
  padding: 8px 9px;
  text-align: left;
  width: 100%;
}

.version-row:hover,
.version-row.active {
  background: var(--ll-tint);
}

.version-row.active .version-num {
  color: var(--ll-accent);
}

.version-row.active .version-copy > span:first-child {
  color: var(--ll-ink);
}

.version-num {
  flex: 0 0 24px;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  margin-top: 1px;
}

.version-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  font-size: 11.5px;
  gap: 2px;
  line-height: 1.4;
  min-width: 0;
}

.version-time {
  color: var(--ll-faint);
  font-size: 10px;
}

.pill {
  align-items: center;
  background: var(--ll-tint);
  border: 0.5px solid var(--ll-border);
  border-radius: 4px;
  color: var(--ll-ink);
  display: inline-flex;
  font-family: var(--ll-mono);
  font-size: 10.5px;
  height: 20px;
  letter-spacing: 0.04em;
  padding: 0 7px;
  white-space: nowrap;
}

.pill.accent {
  background: var(--ll-accent-tint);
  border-color: var(--ll-accent-line);
  color: var(--ll-accent);
  font-size: 9.5px;
  height: 16px;
  padding: 0 5px;
}

.plan-header {
  align-items: center;
  border-bottom: 0.5px solid var(--ll-border);
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
  padding-bottom: 18px;
}

.plan-header h1 {
  color: var(--ll-ink);
  font-size: 22px;
  font-weight: 500;
  letter-spacing: -0.015em;
  line-height: 1.15;
  margin: 6px 0 0;
}

.header-actions {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.btn {
  border-radius: 5px;
  cursor: pointer;
  font-family: var(--ll-mono);
  font-size: 11.5px;
  font-weight: 500;
  height: 28px;
  letter-spacing: 0.02em;
  padding: 0 12px;
  transition: background 120ms ease-out, border-color 120ms ease-out, opacity 120ms ease-out;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.btn.primary {
  background: var(--ll-ink);
  border: 0;
  color: var(--ll-bg);
}

.btn.secondary {
  background: transparent;
  border: 0.5px solid var(--ll-border);
  color: var(--ll-ink);
}

.chat-head {
  align-items: center;
  border-bottom: 0.5px solid var(--ll-border);
  display: flex;
  justify-content: space-between;
  padding: 14px 18px;
}

.quick-edits {
  border-bottom: 0.5px solid var(--ll-border);
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 12px 14px;
}

.quick-edits button {
  background: var(--ll-accent-tint);
  border: 0.5px solid var(--ll-accent-line);
  border-radius: 4px;
  color: var(--ll-accent);
  cursor: pointer;
  font-family: var(--ll-mono);
  font-size: 10.5px;
  height: 24px;
  padding: 0 7px;
}

.chat-messages {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 14px;
  overflow: auto;
  padding: 16px 18px;
}

.empty-chat {
  color: var(--ll-muted);
  font-size: 12.5px;
}

.chat-msg {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-meta {
  align-items: center;
  color: var(--ll-faint);
  display: flex;
  gap: 8px;
  font-size: 9.5px;
}

.chat-meta .who {
  color: var(--ll-accent);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chat-bubble {
  background: var(--ll-bg);
  border: 0.5px solid var(--ll-border);
  border-radius: 5px;
  color: var(--ll-ink);
  font-size: 12.5px;
  line-height: 1.5;
  padding: 8px 10px;
  white-space: pre-wrap;
  word-break: break-word;
}

.composer {
  border-top: 0.5px solid var(--ll-border);
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
}

.chat-textarea {
  background: var(--ll-bg);
  border: 0.5px solid var(--ll-border);
  border-radius: 5px;
  box-sizing: border-box;
  color: var(--ll-ink);
  font-family: var(--ll-sans);
  font-size: 12.5px;
  line-height: 1.5;
  outline: none;
  padding: 10px;
  resize: none;
  width: 100%;
}

.chat-textarea:focus {
  border-color: var(--ll-accent-line);
}

.chat-textarea::placeholder {
  color: var(--ll-faint);
}

.composer-row {
  align-items: center;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.send-hint {
  color: var(--ll-faint);
  font-size: 10px;
}

.composer-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.inline-error,
.inline-success {
  font-size: 12px;
}

.inline-error {
  color: var(--ll-bad);
}

.inline-success {
  color: var(--ll-ok);
}

.status-panel {
  align-items: center;
  color: var(--ll-muted, #6b6b73);
  display: flex;
  font-family: var(--ll-sans, system-ui);
  min-height: calc(100vh - 54px);
  justify-content: center;
}

.status-panel.error {
  color: #d93636;
}

@media (max-width: 1100px) {
  .plan-workspace {
    grid-template-columns: 1fr;
    height: auto;
    min-height: calc(100vh - 54px);
  }

  .plan-main {
    order: 1;
  }

  .history-rail {
    border-bottom: 0.5px solid var(--ll-border);
    border-right: 0;
    order: 2;
  }

  .chat-rail {
    border-left: 0;
    border-top: 0.5px solid var(--ll-border);
    min-height: 520px;
    order: 3;
  }
}

@media (max-width: 700px) {
  .plan-main {
    padding: 20px 14px;
  }

  .plan-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions,
  .header-actions .btn {
    width: 100%;
  }
}
</style>
