<template>
  <section v-if="plan" class="plan-view">
    <div class="meta-grid">
      <StatCell label="Goal" :value="formatTitle(input?.goal ?? 'Plan')" />
      <StatCell label="Level" :value="formatTitle(input?.experience ?? 'Any')" />
      <StatCell label="Days/wk" :value="String(input?.days_per_week ?? (activeDays.length || 0))" mono />
      <StatCell label="Session" :value="`${input?.session_minutes ?? '-'}m`" mono />
      <StatCell label="Equipment" :value="formatTitle(input?.equipment ?? 'Any')" />
      <StatCell label="Version" :value="`v${version ?? '-'}`" mono />
    </div>

    <div v-if="diff" class="diff-strip">
      <div class="diff-left">
        <div class="eyebrow">What changed</div>
        <DiffCount kind="added" :count="diffCount('added_exercises')" />
        <DiffCount kind="replaced" :count="diffCount('replaced_exercises')" />
        <DiffCount kind="removed" :count="diffCount('removed_exercises')" />
      </div>
      <div v-if="diff.restored_from" class="mono diff-note">restored from v{{ diff.restored_from }}</div>
      <div v-else class="mono diff-note">{{ diffNote }}</div>
    </div>

    <div class="day-tabs" role="tablist" aria-label="Workout week">
      <button
        v-for="(day, i) in weekDays"
        :key="`tab-${i}`"
        type="button"
        :class="['day-tab', { selected: selectedDay === i, rest: day.rest }]"
        role="tab"
        :aria-selected="selectedDay === i"
        @click="$emit('update:selectedDay', i)"
      >
        <span class="mono">{{ String(i + 1).padStart(2, "0") }}·{{ day.day.toUpperCase() }}</span>
        <strong>{{ day.rest ? "Rest" : shortFocus(day.focus) }}</strong>
      </button>
    </div>

    <article v-if="currentDay?.rest" class="rest-state">
      <div class="eyebrow">{{ currentDay.day }} · Rest day</div>
      <p>No lifting today. Optional: light walking + mobility.</p>
    </article>

    <article v-else-if="currentDay" class="day-table">
      <div class="table-head table-grid">
        <div class="eyebrow">#</div>
        <div class="eyebrow">Exercise</div>
        <div class="eyebrow">Sets</div>
        <div class="eyebrow">Reps</div>
        <div class="eyebrow">Rest</div>
        <div class="eyebrow"></div>
      </div>

      <div
        v-for="(lift, i) in currentLifts"
        :key="`${currentDay.sourceIndex}-${lift.block}-${lift.slot}-${lift.name}`"
        :class="['lift-row', 'table-grid', lift.changeKind ? `is-${lift.changeKind}` : '']"
      >
        <div class="change-gutter"></div>
        <div class="mono row-num">{{ String(i + 1).padStart(2, "0") }}</div>
        <div class="exercise-cell">
          <span>{{ lift.name }}</span>
          <span v-if="lift.block === 'main'" class="pill">COMPOUND</span>
          <span v-if="lift.changeKind === 'replaced' && lift.from" class="mono from-name">
            &larr; {{ lift.from }}
          </span>
          <span v-if="lift.notes" class="lift-notes">{{ lift.notes }}</span>
        </div>
        <div class="mono metric">{{ lift.sets ?? "" }}</div>
        <div class="mono metric">{{ lift.reps ?? "" }}</div>
        <div class="mono metric muted">{{ lift.rest_seconds != null ? `${lift.rest_seconds}s` : "" }}</div>
        <div class="row-more">...</div>
      </div>
    </article>

    <section class="about-card">
      <div class="eyebrow">About this plan</div>
      <div class="rule-grid">
        <div v-for="(rule, i) in aboutRules" :key="`rule-${i}`" class="rule-item">
          <CheckIcon />
          <span>{{ rule }}</span>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from "vue";
import type { PropType } from "vue";

type RawLift = {
  name?: string;
  sets?: number;
  reps?: string;
  rest_seconds?: number | null;
  notes?: string;
};

type Day = {
  day: string;
  focus: string;
  rest?: boolean;
  warmup?: any[];
  main?: any[];
  accessories?: any[];
  sourceIndex?: number;
};

type PlanOutput = {
  title: string;
  summary: string;
  weekly_split: Day[];
  progression_notes?: string[];
  safety_notes?: string[];
  estimated_minutes_total?: number;
  estimated_minutes_note?: string;
};

type Lift = {
  name: string;
  sets?: number;
  reps?: string;
  rest_seconds?: number | null;
  notes?: string;
  block: "main" | "accessories";
  slot: number;
  changeKind?: "added" | "replaced" | "removed";
  from?: string;
};

const props = defineProps({
  plan: { type: Object as PropType<PlanOutput | null>, default: null },
  input: { type: Object as PropType<Record<string, any> | null>, default: null },
  diff: { type: Object as PropType<Record<string, any> | null>, default: null },
  version: { type: Number as PropType<number | null>, default: null },
  selectedDay: { type: Number, default: 0 },
});

defineEmits<{
  "update:selectedDay": [value: number];
}>();

const activeDays = computed(() => props.plan?.weekly_split ?? []);

const weekDays = computed<Day[]>(() => {
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const sourceDays = activeDays.value.map((day, index) => ({
    ...day,
    day: normalizeDayLabel(day.day, labels[index] ?? `Day ${index + 1}`),
    rest: isRestDay(day),
    sourceIndex: index,
  }));

  return labels.map((label, index) => {
    const day = sourceDays[index];
    if (day) return day;
    return {
      day: label,
      focus: "Rest",
      rest: true,
      main: [],
      accessories: [],
      sourceIndex: index,
    };
  });
});

const currentDay = computed(() => weekDays.value[props.selectedDay] ?? weekDays.value[0]);

const currentLifts = computed<Lift[]>(() => {
  const day = currentDay.value;
  if (!day || day.rest) return [];
  return [
    ...normalizeToLifts(day.main, "main"),
    ...normalizeToLifts(day.accessories, "accessories"),
  ].map((lift) => withChangeState(lift, day.sourceIndex ?? props.selectedDay));
});

const diffNote = computed(() => {
  const first =
    props.diff?.added_exercises?.[0]?.reason ||
    props.diff?.replaced_exercises?.[0]?.reason ||
    props.diff?.removed_exercises?.[0]?.reason;
  return first ? formatTitle(first) : "latest changes";
});

const aboutRules = computed(() => {
  const rules = new Set<string>();
  const input = props.input ?? {};
  const plan = props.plan;

  if (plan?.summary) rules.add(plan.summary);
  if (input.equipment) rules.add(`Built for ${formatTitle(input.equipment)} equipment`);
  if (input.session_minutes) rules.add(`Designed for ${input.session_minutes} minute sessions`);
  if (input.days_per_week) rules.add(`${input.days_per_week} training days per week`);
  for (const note of plan?.progression_notes ?? []) rules.add(String(note));
  for (const note of plan?.safety_notes ?? []) rules.add(String(note));

  const constraints = [
    ...(Array.isArray(input.constraints_tokens) ? input.constraints_tokens : []),
    ...(Array.isArray(input.preferences_tokens) ? input.preferences_tokens : []),
    ...(Array.isArray(input.avoid) ? input.avoid.map((x: any) => `avoid ${x}`) : []),
  ].filter(Boolean);

  if (constraints.length) rules.add(`Honors: ${constraints.map(formatTitle).join(", ")}`);

  return Array.from(rules).slice(0, 8);
});

function normalizeToLifts(items: any[] | undefined, block: "main" | "accessories"): Lift[] {
  if (!items?.length) return [];
  return items.map((item, slot) => {
    const lift: RawLift = typeof item === "string" ? { name: item } : item ?? {};
    return {
      name: String(lift.name ?? ""),
      sets: lift.sets,
      reps: lift.reps,
      rest_seconds: lift.rest_seconds ?? null,
      notes: lift.notes ?? "",
      block,
      slot,
    };
  }).filter((lift) => lift.name.trim().length);
}

function withChangeState(lift: Lift, dayIndex: number): Lift {
  const changed = findDiff("added_exercises", lift, dayIndex);
  if (changed) return { ...lift, changeKind: "added" };

  const replaced = findDiff("replaced_exercises", lift, dayIndex);
  if (replaced) return { ...lift, changeKind: "replaced", from: String(replaced.from ?? "") };

  const removed = findDiff("removed_exercises", lift, dayIndex);
  if (removed) return { ...lift, changeKind: "removed" };

  return lift;
}

function findDiff(key: string, lift: Lift, dayIndex: number) {
  const entries = props.diff?.[key];
  if (!Array.isArray(entries)) return null;
  return entries.find((entry: any) => {
    const sameDay = Number(entry.day ?? -1) === dayIndex;
    const sameBlock = String(entry.block ?? "") === lift.block;
    const sameSlot = Number(entry.slot ?? -1) === lift.slot;
    const targetName = key === "replaced_exercises" ? entry.to : entry.name;
    const sameName = normalizeName(targetName) === normalizeName(lift.name);
    return sameDay && sameBlock && (sameSlot || sameName);
  }) ?? null;
}

function diffCount(key: string) {
  const entries = props.diff?.[key];
  return Array.isArray(entries) ? entries.length : 0;
}

function isRestDay(day: Day) {
  const focus = String(day.focus ?? "").toLowerCase();
  const label = String(day.day ?? "").toLowerCase();
  if (day.rest || focus.includes("rest") || label.includes("rest")) return true;
  return !hasAny(day.warmup) && !hasAny(day.main) && !hasAny(day.accessories);
}

function hasAny(arr: any[] | undefined) {
  return Array.isArray(arr) && arr.some((item) => {
    if (!item) return false;
    if (typeof item === "string") return item.trim().length > 0;
    if (typeof item === "object") return String(item.name ?? JSON.stringify(item)).trim().length > 0;
    return true;
  });
}

function normalizeDayLabel(label: string | undefined, fallback: string) {
  const raw = String(label ?? "").trim();
  const lower = raw.toLowerCase();
  if (!raw || lower.startsWith("day ")) return fallback;
  return raw.slice(0, 3);
}

function shortFocus(focus: string | undefined) {
  const raw = String(focus ?? "Training").trim();
  return raw.split(" · ").at(-1) || raw;
}

function formatTitle(value: any) {
  return String(value ?? "")
    .replace(/_/g, " ")
    .trim()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function normalizeName(name: any) {
  return String(name ?? "").trim().replace(/\s+/g, " ").toLowerCase();
}

const StatCell = defineComponent({
  props: {
    label: { type: String, required: true },
    value: { type: String, required: true },
    mono: { type: Boolean, default: false },
  },
  setup(cellProps) {
    return () => h("div", { class: "stat-cell" }, [
      h("div", { class: "eyebrow" }, cellProps.label),
      h("div", { class: ["stat-value", { mono: cellProps.mono }] }, cellProps.value),
    ]);
  },
});

const DiffCount = defineComponent({
  props: {
    kind: { type: String as PropType<"added" | "replaced" | "removed">, required: true },
    count: { type: Number, required: true },
  },
  setup(countProps) {
    const labels = {
      added: ["+", "added"],
      replaced: ["~", "replaced"],
      removed: ["-", "removed"],
    };
    return () => h("div", { class: ["diff-count", countProps.kind] }, [
      h("span", { class: "mono diff-number" }, `${labels[countProps.kind][0]}${countProps.count}`),
      h("span", { class: "mono diff-label" }, labels[countProps.kind][1]),
    ]);
  },
});

const CheckIcon = defineComponent({
  setup() {
    return () => h(
      "svg",
      { width: "11", height: "11", viewBox: "0 0 12 12", fill: "none", "aria-hidden": "true" },
      [
        h("path", {
          d: "M2.5 6.5L4.8 8.5L9.5 3.8",
          stroke: "var(--ll-ok)",
          "stroke-width": "1.4",
          "stroke-linecap": "round",
          "stroke-linejoin": "round",
        }),
      ],
    );
  },
});
</script>

<style scoped>
.plan-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
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

.meta-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0;
  border: 0.5px solid var(--ll-border);
  border-radius: 6px;
  background: var(--ll-surface);
  padding: 14px 18px;
}

.stat-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.stat-value {
  color: var(--ll-ink);
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stat-value.mono,
.metric,
.row-num {
  font-variant-numeric: tabular-nums;
  letter-spacing: 0;
}

.diff-strip {
  align-items: center;
  background: var(--ll-surface);
  border: 0.5px solid var(--ll-border);
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
}

.diff-left,
.diff-count {
  align-items: center;
  display: flex;
}

.diff-left {
  gap: 16px;
}

.diff-count {
  gap: 6px;
}

.diff-number {
  font-size: 12px;
  font-weight: 500;
}

.diff-count.added .diff-number {
  color: var(--ll-ok);
}

.diff-count.replaced .diff-number {
  color: var(--ll-accent);
}

.diff-count.removed .diff-number {
  color: var(--ll-bad);
}

.diff-label,
.diff-note {
  color: var(--ll-muted);
  font-size: 11px;
}

.day-tabs {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 4px;
}

.day-tab {
  background: var(--ll-surface);
  border: 0.5px solid var(--ll-border);
  border-radius: 5px;
  color: var(--ll-ink);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 58px;
  padding: 10px 8px;
  text-align: left;
  transition: background 120ms ease-out, color 120ms ease-out;
}

.day-tab .mono {
  font-size: 10px;
  opacity: 0.62;
}

.day-tab strong {
  font-family: var(--ll-sans);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.2;
}

.day-tab.rest:not(.selected) {
  color: var(--ll-muted);
}

.day-tab.selected {
  background: var(--ll-ink);
  border-color: var(--ll-ink);
  color: var(--ll-bg);
}

.day-table {
  background: var(--ll-surface);
  border: 0.5px solid var(--ll-border);
  border-radius: 6px;
  overflow: hidden;
}

.table-grid {
  display: grid;
  grid-template-columns: 32px minmax(180px, 1fr) 80px 90px 70px 30px;
}

.table-head {
  background: var(--ll-tint);
  border-bottom: 0.5px solid var(--ll-border);
  padding: 10px 16px;
}

.table-head .eyebrow {
  font-size: 9.5px;
}

.lift-row {
  align-items: center;
  border-bottom: 0.5px solid var(--ll-border);
  min-height: 58px;
  padding: 12px 16px;
  position: relative;
}

.lift-row:last-child {
  border-bottom: 0;
}

.change-gutter {
  background: transparent;
  bottom: 0;
  left: 0;
  position: absolute;
  top: 0;
  width: 2px;
}

.lift-row.is-added {
  background: var(--ll-ok-tint);
}

.lift-row.is-replaced {
  background: var(--ll-accent-tint);
}

.lift-row.is-removed {
  background: var(--ll-bad-tint);
}

.lift-row.is-added .change-gutter {
  background: var(--ll-ok);
}

.lift-row.is-replaced .change-gutter {
  background: var(--ll-accent);
}

.lift-row.is-removed .change-gutter {
  background: var(--ll-bad);
}

.row-num {
  color: var(--ll-faint);
  font-size: 11px;
}

.exercise-cell {
  align-items: center;
  color: var(--ll-ink);
  display: flex;
  flex-wrap: wrap;
  gap: 6px 8px;
  min-width: 0;
}

.exercise-cell > span:first-child {
  font-size: 13px;
}

.pill {
  align-items: center;
  background: var(--ll-tint);
  border: 0.5px solid var(--ll-border);
  border-radius: 4px;
  color: var(--ll-ink);
  display: inline-flex;
  font-family: var(--ll-mono);
  font-size: 9.5px;
  height: 16px;
  letter-spacing: 0.04em;
  padding: 0 5px;
}

.from-name {
  color: var(--ll-muted);
  font-size: 10.5px;
}

.lift-notes {
  color: var(--ll-muted);
  flex-basis: 100%;
  font-size: 11.5px;
  line-height: 1.4;
}

.metric {
  color: var(--ll-ink);
  font-size: 12.5px;
}

.metric.muted,
.row-more {
  color: var(--ll-muted);
}

.row-more {
  font-size: 13px;
  text-align: right;
}

.rest-state,
.about-card {
  background: var(--ll-surface);
  border: 0.5px solid var(--ll-border);
  border-radius: 6px;
}

.rest-state {
  border-style: dashed;
  color: var(--ll-muted);
  padding: 40px 18px;
  text-align: center;
}

.rest-state p {
  font-size: 13px;
  margin: 6px 0 0;
}

.about-card {
  padding: 16px 18px;
}

.rule-grid {
  display: grid;
  gap: 8px 24px;
  grid-template-columns: 1fr 1fr;
  margin-top: 10px;
}

.rule-item {
  align-items: center;
  color: var(--ll-ink);
  display: flex;
  font-size: 12.5px;
  gap: 8px;
  min-width: 0;
}

.rule-item svg {
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .meta-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    row-gap: 14px;
  }

  .day-tabs {
    display: flex;
    overflow-x: auto;
    padding-bottom: 2px;
  }

  .day-tab {
    flex: 0 0 112px;
  }

  .day-table {
    overflow-x: auto;
  }

  .table-grid {
    min-width: 680px;
  }

  .rule-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .meta-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .diff-strip,
  .diff-left {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
