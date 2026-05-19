<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const router = useRouter();
const route = useRoute();
const { resetPassword } = useAuth();

const token = ref("");
const password = ref("");
const confirmPassword = ref("");
const loading = ref(false);
const error = ref<string | null>(null);
const invalidLink = ref(false);

onMounted(() => {
  const t = route.query.token as string | undefined;
  if (!t) {
    invalidLink.value = true;
  } else {
    token.value = t;
  }
});

async function handleSubmit() {
  error.value = null;
  if (!password.value) {
    error.value = "Password is required";
    return;
  }
  if (password.value.length < 8) {
    error.value = "Password must be at least 8 characters";
    return;
  }
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }
  loading.value = true;
  try {
    await resetPassword(token.value, password.value);
    router.push("/login?reset=1");
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Something went wrong. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <div class="card">
      <div class="brand">
        <h1 class="wordmark">Lyft<span class="accent">Logic</span></h1>
        <p class="sub">Choose a new password</p>
      </div>

      <template v-if="invalidLink">
        <div class="state-box invalid-box">
          <div class="state-icon">⚠</div>
          <p class="state-title">Link expired</p>
          <p class="state-text">This reset link is invalid or has expired.</p>
          <NuxtLink to="/forgot-password" class="link-btn">Request a new reset link</NuxtLink>
        </div>
      </template>

      <template v-else>
        <div class="field">
          <label class="label">New password</label>
          <input
            v-model="password"
            type="password"
            class="input"
            placeholder="Min. 8 characters"
            autocomplete="new-password"
          />
        </div>
        <div class="field">
          <label class="label">Confirm password</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="input"
            placeholder="••••••••"
            autocomplete="new-password"
            @keydown.enter="handleSubmit"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handleSubmit">
          <span class="btn-text">{{ loading ? "Resetting…" : "Reset password" }}</span>
          <span v-if="loading" class="btn-spinner"></span>
        </button>

        <div v-if="error?.includes('invalid or has expired')" class="links-row">
          <NuxtLink to="/forgot-password" class="link-btn">Request a new reset link</NuxtLink>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: #0a0a0a;
  font-family: 'DM Sans', sans-serif;
  color: #ffffff;
}

.card {
  width: 100%;
  max-width: 420px;
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 36px 32px;
}

.brand {
  margin-bottom: 28px;
}

.wordmark {
  font-family: 'DM Sans', sans-serif;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
  color: #ffffff;
  line-height: 1;
}

.accent {
  color: #ffffff;
}

.sub {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
  letter-spacing: 0.02em;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-bottom: 14px;
}

.label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.35);
}

.input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 11px 14px;
  color: #ffffff;
  font-size: 15px;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.input:focus {
  border-color: rgba(255, 255, 255, 0.3);
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.btn-primary {
  width: 100%;
  padding: 11px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 6px;
  color: #ffffff;
  font-size: 12px;
  font-weight: 500;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  cursor: pointer;
  margin-top: 4px;
  transition: background 0.15s, border-color 0.15s, opacity 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.8);
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.99);
}

.btn-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 1.5px solid rgba(255,255,255,0.2);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: #f87171;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid #f87171;
  border-radius: 0 3px 3px 0;
}

.links-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 18px;
}

.link-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.45);
  font-size: 12px;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.03em;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  transition: color 0.15s;
}

.link-btn:hover {
  color: #ffffff;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.state-box {
  text-align: center;
  padding: 8px 0 4px;
}

.invalid-box .state-icon {
  color: #f87171;
  opacity: 0.8;
}

.state-icon {
  font-size: 28px;
  margin-bottom: 12px;
  display: block;
}

.state-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #ffffff;
}

.state-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  margin: 0 0 18px;
  line-height: 1.6;
}
</style>
