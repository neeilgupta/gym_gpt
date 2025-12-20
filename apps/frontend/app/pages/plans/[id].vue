<template>
  <div style="padding: 20px; font-family: system-ui;">
    <h1>Plan {{ id }}</h1>

    <p v-if="pending">Loading...</p>
    <p v-else-if="errorMsg" style="color: red;">{{ errorMsg }}</p>

    <pre v-else style="white-space: pre-wrap;">{{ plan }}</pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../composables/usePlans";

const route = useRoute();
const id = computed(() => route.params.id as string);

const { getPlan } = usePlans();

const { data: plan, pending, error } = await useAsyncData(
  `plan-${id.value}`,
  () => getPlan(id.value)
);

const errorMsg = computed(() => {
  const e: any = error.value;
  return e?.data?.detail ?? e?.message ?? (e ? String(e) : null);
});
</script>
