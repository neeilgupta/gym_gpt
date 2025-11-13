// https://nuxt.com/docs/api/configuration/nuxt-config
// allow access to process.env in this config without adding node types
declare const process: any;

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  // Public runtime config so the frontend knows where to call the backend API.
  runtimeConfig: {
    public: {
      // Set API_BASE in your environment to override (e.g. http://localhost:8002)
      apiBase: process.env.API_BASE || 'http://127.0.0.1:8002'
    }
  }
})
