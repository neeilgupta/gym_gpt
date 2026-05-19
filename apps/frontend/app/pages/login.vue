<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const router = useRouter();
const route = useRoute();
const { requestCode, verifyCode, register, passwordLogin, me, resendVerification } = useAuth();
const user = useState<{ id: number; email: string } | null>('user', () => null);

// "password" | "register" | "otp"
const mode = ref<"password" | "register" | "otp">("password");

// Shared
const email = ref("");
const error = ref<string | null>(null);
const loading = ref(false);

// Password / Register fields
const password = ref("");
const confirmPassword = ref("");

// Post-register state
const registered = ref(false);
const resendLoading = ref(false);
const resendSent = ref(false);

// OTP fields
const codeSent = ref(false);
const code = ref("");

// Banner for successful password reset redirect
const resetSuccess = route.query.reset === "1";

function resetState() {
  error.value = null;
  password.value = "";
  confirmPassword.value = "";
  codeSent.value = false;
  code.value = "";
  registered.value = false;
  resendSent.value = false;
}

function switchMode(m: "password" | "register" | "otp") {
  mode.value = m;
  resetState();
}

async function handlePasswordLogin() {
  error.value = null;
  if (!email.value || !password.value) {
    error.value = "Email and password are required";
    return;
  }
  loading.value = true;
  try {
    await passwordLogin(email.value.trim().toLowerCase(), password.value);
    user.value = await me();
    router.push("/plans");
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Login failed";
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  error.value = null;
  if (!email.value || !password.value) {
    error.value = "Email and password are required";
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
    await register(email.value.trim().toLowerCase(), password.value);
    registered.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Registration failed";
  } finally {
    loading.value = false;
  }
}

async function handleResendVerification() {
  resendSent.value = false;
  resendLoading.value = true;
  try {
    await resendVerification(email.value.trim().toLowerCase());
    resendSent.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Failed to resend link";
  } finally {
    resendLoading.value = false;
  }
}

async function handleRequestCode() {
  error.value = null;
  if (!email.value) {
    error.value = "Email is required";
    return;
  }
  loading.value = true;
  try {
    await requestCode(email.value.trim().toLowerCase());
    codeSent.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Failed to send code";
  } finally {
    loading.value = false;
  }
}

async function handleVerifyCode() {
  error.value = null;
  if (!code.value) {
    error.value = "Enter the 6-digit code";
    return;
  }
  loading.value = true;
  try {
    await verifyCode(email.value.trim().toLowerCase(), code.value.trim());
    user.value = await me();
    router.push("/plans");
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Invalid or expired code";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <div class="card">
      <!-- Logo -->
      <div class="card-logo">
        <svg width="18" height="18" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M8 2L14 13H2L8 2Z" fill="currentColor" fill-opacity="0.85"/>
        </svg>
        lyft<span class="logo-dot">·</span>logic
      </div>
      <hr class="divider" />

      <!-- Password login -->
      <template v-if="mode === 'password'">
        <p class="section-label">Sign in</p>
        <h1 class="card-heading">Welcome back</h1>

        <div v-if="resetSuccess" class="banner success-banner">
          Password reset — sign in with your new password.
        </div>

        <div class="field">
          <label class="label">Email</label>
          <input
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            autocomplete="email"
            @keydown.enter="handlePasswordLogin"
          />
        </div>
        <div class="field">
          <label class="label">Password</label>
          <input
            v-model="password"
            type="password"
            class="input"
            placeholder="••••••••"
            autocomplete="current-password"
            @keydown.enter="handlePasswordLogin"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handlePasswordLogin">
          <span>{{ loading ? "Signing in…" : "Sign in" }}</span>
          <span v-if="loading" class="btn-spinner"></span>
        </button>

        <div class="or-row"><hr /><span>or</span><hr /></div>

        <button class="btn-secondary" @click="switchMode('otp')">
          Use a magic link
        </button>

        <div class="footer-row">
          <span>no account</span>
          <span class="footer-sep"> · </span>
          <button class="accent-link" @click="switchMode('register')">create one</button>
        </div>

        <div class="forgot-row">
          <NuxtLink to="/forgot-password" class="link-sm">Forgot password?</NuxtLink>
        </div>
      </template>

      <!-- Register -->
      <template v-else-if="mode === 'register'">
        <template v-if="registered">
          <p class="section-label">Sign up</p>
          <h1 class="card-heading">Check your inbox</h1>
          <p class="sub-text">We sent a verification link to <strong>{{ email }}</strong>. Click it to activate your account.</p>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <p class="sub-text">
            Didn't get it?
            <button class="accent-link" :disabled="resendLoading" @click="handleResendVerification">
              {{ resendLoading ? "Sending…" : resendSent ? "Sent!" : "Resend link" }}
            </button>
          </p>
          <div class="footer-row" style="margin-top: 24px;">
            <button class="accent-link" @click="switchMode('password')">← Back to sign in</button>
          </div>
        </template>
        <template v-else>
          <p class="section-label">Sign up</p>
          <h1 class="card-heading">Create your account</h1>

          <div class="field">
            <label class="label">Email</label>
            <input
              v-model="email"
              type="email"
              class="input"
              placeholder="you@example.com"
              autocomplete="email"
            />
          </div>
          <div class="field">
            <label class="label">Password</label>
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
              @keydown.enter="handleRegister"
            />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button class="btn-primary" :disabled="loading" @click="handleRegister">
            <span>{{ loading ? "Creating account…" : "Create account" }}</span>
            <span v-if="loading" class="btn-spinner"></span>
          </button>

          <div class="or-row"><hr /><span>or</span><hr /></div>

          <button class="btn-secondary" @click="switchMode('otp')">
            Use a magic link
          </button>

          <div class="footer-row">
            <span>have an account</span>
            <span class="footer-sep"> · </span>
            <button class="accent-link" @click="switchMode('password')">sign in</button>
          </div>
        </template>
      </template>

      <!-- OTP -->
      <template v-else-if="mode === 'otp'">
        <template v-if="!codeSent">
          <p class="section-label">Magic link</p>
          <h1 class="card-heading">Sign in without a password</h1>

          <div class="field">
            <label class="label">Email</label>
            <input
              v-model="email"
              type="email"
              class="input"
              placeholder="you@example.com"
              autocomplete="email"
              @keydown.enter="handleRequestCode"
            />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button class="btn-primary" :disabled="loading" @click="handleRequestCode">
            <span>{{ loading ? "Sending…" : "Send magic link" }}</span>
            <span v-if="loading" class="btn-spinner"></span>
          </button>

          <div class="footer-row" style="margin-top: 20px;">
            <button class="accent-link" @click="switchMode('password')">← Sign in with password</button>
          </div>
        </template>
        <template v-else>
          <p class="section-label">Magic link</p>
          <h1 class="card-heading">Check your email</h1>
          <p class="sub-text">Code sent to {{ email }}</p>

          <div class="field">
            <label class="label">6-digit code</label>
            <input
              v-model="code"
              type="text"
              class="input input-code"
              placeholder="123456"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              @keydown.enter="handleVerifyCode"
            />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button class="btn-primary" :disabled="loading" @click="handleVerifyCode">
            <span>{{ loading ? "Verifying…" : "Verify code" }}</span>
            <span v-if="loading" class="btn-spinner"></span>
          </button>

          <div class="footer-row" style="margin-top: 20px;">
            <button class="accent-link" @click="codeSent = false; error = null">← Different email</button>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');

:global(html), :global(body) { background: #0a0a0a; margin: 0; }
:global(#__nuxt) { background: #0a0a0a; min-height: 100vh; }

.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  background: #0a0a0a;
  font-family: 'DM Sans', sans-serif;
  color: #ffffff;
}

.card {
  width: min(520px, 100%);
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 36px 36px 32px;
  box-sizing: border-box;
}

/* Logo */
.card-logo {
  display: flex;
  align-items: center;
  gap: 9px;
  font-family: 'DM Mono', monospace;
  font-size: 15px;
  font-weight: 400;
  color: #ffffff;
  letter-spacing: -0.01em;
}

.card-logo svg {
  color: rgba(255, 255, 255, 0.85);
  flex-shrink: 0;
}

.logo-dot {
  color: rgba(255, 255, 255, 0.3);
}

.divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  margin: 22px 0 24px;
}

/* Section label + heading */
.section-label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin: 0 0 8px;
}

.card-heading {
  font-family: 'DM Sans', sans-serif;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
  color: #ffffff;
  margin: 0 0 24px;
}

/* Fields */
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
  min-height: 46px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
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
  color: rgba(255, 255, 255, 0.22);
}

.input-code {
  font-family: 'DM Mono', monospace;
  font-size: 22px;
  letter-spacing: 0.3em;
  text-align: center;
}

/* Primary button — solid filled */
.btn-primary {
  width: 100%;
  padding: 13px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  color: #111111;
  font-size: 15px;
  font-weight: 500;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  margin-top: 6px;
  transition: background 0.15s, opacity 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Secondary button — outlined */
.btn-secondary {
  width: 100%;
  padding: 13px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 400;
  font-family: 'DM Sans', sans-serif;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.btn-secondary:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.04);
}

/* Spinner */
.btn-spinner {
  width: 14px;
  height: 14px;
  border: 1.5px solid rgba(0, 0, 0, 0.2);
  border-top-color: #111111;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Or divider */
.or-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.or-row hr {
  flex: 1;
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.or-row span {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
  letter-spacing: 0.06em;
}

/* Footer links */
.footer-row {
  text-align: center;
  margin-top: 18px;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

.footer-sep {
  margin: 0 2px;
}

.accent-link {
  background: none;
  border: none;
  color: #60a5fa;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  transition: color 0.15s;
}

.accent-link:hover {
  color: #93c5fd;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.accent-link:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.forgot-row {
  text-align: center;
  margin-top: 10px;
}

.link-sm {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.3);
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  transition: color 0.15s;
}

.link-sm:hover {
  color: rgba(255, 255, 255, 0.6);
}

/* Messages */
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

.sub-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  margin: 0 0 14px;
  line-height: 1.55;
}

.banner {
  padding: 10px 14px;
  border-radius: 4px;
  margin-bottom: 18px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.02em;
}

.success-banner {
  background: rgba(74, 222, 128, 0.07);
  border-left: 2px solid #4ade80;
  color: #86efac;
}

@media (max-width: 520px) {
  .page {
    align-items: flex-start;
    padding-top: 20px;
  }

  .card {
    padding: 28px 20px 24px;
  }

  .card-heading {
    font-size: 24px;
  }
}
</style>
