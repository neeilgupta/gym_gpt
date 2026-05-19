<script setup lang="ts">
import { useAuth } from "../../composables/useAuth"

const { me, logout } = useAuth()
const user = useState<{ id: number; email: string } | null>('user', () => null)

onMounted(async () => {
  try {
    user.value = await me()
  } catch {
    user.value = null
  }
})

async function handleLogout() {
  await logout()
  user.value = null
  navigateTo('/login')
}

function userInitial(email: string) {
  return email[0].toUpperCase()
}
</script>

<template>
  <header class="nav">
    <div class="nav-inner">
      <NuxtLink to="/" class="wordmark">
        <svg class="logo-icon" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 2L14 13H2L8 2Z" fill="currentColor" fill-opacity="0.9"/>
        </svg>
        lyft<span class="dot">·</span>logic
      </NuxtLink>

      <nav class="nav-links">
        <NuxtLink to="/plans" class="nav-link">Plans</NuxtLink>
        <NuxtLink to="/generate" class="nav-link">Generate</NuxtLink>
        <NuxtLink to="/nutrition" class="nav-link">Nutrition</NuxtLink>
        <NuxtLink to="/settings" class="nav-link">Settings</NuxtLink>

        <template v-if="user">
          <button class="avatar-btn" @click="handleLogout" :title="`Sign out (${user.email})`">
            {{ userInitial(user.email) }}
          </button>
        </template>
        <NuxtLink v-else to="/login" class="nav-signin">Sign in</NuxtLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

.nav {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(10, 10, 10, 0.95);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
  height: 54px;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.wordmark {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
  text-decoration: none;
  color: #ffffff;
  flex-shrink: 0;
}

.logo-icon {
  color: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
}

.dot {
  color: rgba(255, 255, 255, 0.3);
  font-weight: 400;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-left: auto;
}

.nav-link {
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.45);
  text-decoration: none;
  transition: color 0.15s;
  white-space: nowrap;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #ffffff;
}

.nav-signin {
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
  transition: color 0.15s;
}

.nav-signin:hover {
  color: #ffffff;
}

.avatar-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
  font-family: 'DM Sans', sans-serif;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  flex-shrink: 0;
}

.avatar-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .nav-inner {
    padding: 0 18px;
  }

  .nav-links {
    gap: 14px;
  }
}

@media (max-width: 520px) {
  .nav-link:not(:first-child):not(:last-child) {
    display: none;
  }
}
</style>
