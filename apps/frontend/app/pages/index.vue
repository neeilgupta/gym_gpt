<script setup lang="ts">
useHead({
  title: "LyftLogic",
  meta: [
    {
      name: "description",
      content:
        "LyftLogic helps you build workout and nutrition plans that are simple, consistent, and easy to follow.",
    },
  ],
})
</script>

<template>
  <main class="home-page">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="line-white">Workout and meal plans,</span><br>
          <span class="line-dim">built for you.</span>
        </h1>

        <p class="hero-sub">
          Tell us your goal, your gear, and how much time you have. We'll build
          a weekly plan you can edit, save, and come back to.
        </p>

        <div class="cta-row">
          <NuxtLink to="/generate" class="btn btn-primary">Get started →</NuxtLink>
          <NuxtLink to="/login" class="btn btn-ghost">Sign in</NuxtLink>
        </div>
      </div>
    </section>

    <!-- FEATURE CARDS -->
    <section class="grid-2col">
      <article class="feature-card">
        <div class="feature-tag">Training</div>
        <div class="feature-title">Workout Plans</div>
        <div class="feature-sub">
          Build a weekly workout plan around your goal, schedule, and equipment.
        </div>
        <ul class="feature-list">
          <li>Choose days per week and session length</li>
          <li>Use full gym, dumbbells, or bodyweight</li>
          <li>Save and edit plans from your account</li>
        </ul>
        <NuxtLink to="/generate" class="btn btn-primary feature-btn">Start workout plan →</NuxtLink>
      </article>

      <article class="feature-card">
        <div class="feature-tag">Nutrition</div>
        <div class="feature-title">Nutrition Plans</div>
        <div class="feature-sub">
          Build a simple meal plan from your calories, diet, and allergies.
        </div>
        <ul class="feature-list">
          <li>Estimate calories and macros</li>
          <li>Set diet and allergy needs</li>
          <li>Save meal plans for later</li>
        </ul>
        <NuxtLink to="/nutrition" class="btn btn-secondary feature-btn">Start nutrition plan →</NuxtLink>
      </article>
    </section>

    <!-- ABOUT -->
    <section class="grid-about">
      <article class="about-card about-card-wide">
        <div class="about-label">What it does</div>
        <p class="about-p">
          LyftLogic helps you make a workout plan, a nutrition plan, or both.
          You choose the inputs. The app builds the plan.
        </p>
      </article>

      <article class="about-card">
        <div class="about-label">Why use it</div>
        <p class="about-p">
          It keeps the setup simple and gives you a plan you can actually use.
        </p>
      </article>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <div class="footer-rule"></div>
      <div class="footer-text">lyft·logic — workout and nutrition planning</div>
    </footer>
  </main>
</template>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:global(html),
:global(body) {
  background: #0a0a0a;
  margin: 0;
}

:global(#__nuxt) {
  background: #0a0a0a;
  min-height: 100vh;
}

.home-page {
  background: #0a0a0a;
  color: #ffffff;
  min-height: 100vh;
  padding: 0 48px 48px;
  font-family: 'DM Sans', sans-serif;
}

.home-page > * {
  max-width: 1080px;
  margin-left: auto;
  margin-right: auto;
}

/* HERO */
.hero {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: calc(100vh - 54px);
  padding: 80px 0;
}

.hero-content {
  max-width: 760px;
}

.hero-title {
  font-family: 'DM Sans', sans-serif;
  font-size: clamp(52px, 8vw, 100px);
  font-weight: 700;
  line-height: 1.06;
  letter-spacing: -0.02em;
  margin: 0 0 28px;
}

.line-white {
  color: #ffffff;
  white-space: nowrap;
}

.line-dim {
  color: rgba(255, 255, 255, 0.38);
}

.hero-sub {
  font-size: clamp(15px, 1.8vw, 18px);
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.45);
  max-width: 520px;
  margin: 0 0 36px;
}

/* CTA */
.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: 6px;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.btn-primary {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.55);
  color: #ffffff;
}

.btn-primary:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.8);
}

.btn-secondary {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.65);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
}

.btn-ghost {
  background: transparent;
  border-color: transparent;
  color: rgba(255, 255, 255, 0.45);
  padding-left: 0;
}

.btn-ghost:hover {
  color: #ffffff;
}

/* FEATURE CARDS */
.grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 0;
}

.feature-card {
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 24px 22px;
  display: flex;
  flex-direction: column;
}

.feature-tag {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 10px;
}

.feature-title {
  font-family: 'DM Sans', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}

.feature-sub {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.45);
  margin-bottom: 16px;
}

.feature-list {
  margin: 0 0 20px;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.feature-list li {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.55);
  padding-left: 14px;
  position: relative;
}

.feature-list li::before {
  content: '—';
  position: absolute;
  left: 0;
  color: rgba(255, 255, 255, 0.2);
  font-size: 11px;
}

.feature-btn {
  align-self: flex-start;
  margin-top: auto;
}

/* ABOUT */
.grid-about {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 12px;
  margin-top: 12px;
}

.about-card {
  background: #111111;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 6px;
  padding: 22px;
}

.about-label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.25);
  margin-bottom: 12px;
}

.about-p {
  font-size: 14px;
  line-height: 1.65;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

/* FOOTER */
.footer {
  margin-top: 28px;
  padding-bottom: 10px;
}

.footer-rule {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin-bottom: 14px;
}

.footer-text {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.2);
}

/* RESPONSIVE */
@media (max-width: 860px) {
  .home-page {
    padding: 0 24px 32px;
  }

  .hero {
    min-height: auto;
    padding: 60px 0 40px;
  }

  .grid-2col {
    grid-template-columns: 1fr;
  }

  .grid-about {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .home-page {
    padding: 0 16px 24px;
  }

  .hero-title {
    font-size: 44px;
  }
}
</style>
