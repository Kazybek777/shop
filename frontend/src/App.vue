<template>
  <div id="app" class="app-shell">
    <div class="ambient-dot ambient-dot--left"></div>
    <div class="ambient-dot ambient-dot--right"></div>

    <Header />
    <RouterView />

    <footer class="site-footer">
      <div class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid gap-5 md:grid-cols-2 md:items-end">
          <div>
            <p class="font-semibold text-[color:var(--ink-700)]">{{ t('footer.title') }}</p>
            <p class="text-sm text-[color:var(--ink-500)] mt-2 max-w-2xl">{{ t('footer.subtitle') }}</p>
          </div>

          <div class="md:text-right">
            <p class="text-sm font-semibold text-[color:var(--ink-700)] mb-2">{{ t('footer.follow') }}</p>
            <div class="inline-flex flex-wrap gap-2 md:justify-end">
              <a class="social-link" href="https://t.me/tashtemir" target="_blank" rel="noopener noreferrer">
                {{ t('footer.telegram') }}
              </a>
              <a class="social-link" href="https://wa.me/996000000000" target="_blank" rel="noopener noreferrer">
                {{ t('footer.whatsapp') }}
              </a>
              <a class="social-link" href="https://www.youtube.com/@tashtemir" target="_blank" rel="noopener noreferrer">
                {{ t('footer.youtube') }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import Header from '@/components/Header.vue'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const { locale, t } = useI18n()

const titleByRoute = {
  home: 'meta.home',
  'product-detail': 'meta.product',
  cart: 'meta.cart',
  checkout: 'meta.checkout',
  login: 'meta.login',
  register: 'meta.register',
  admin: 'meta.admin',
}

watch(
  [() => route.name, locale],
  () => {
    const key = titleByRoute[String(route.name)] || 'meta.home'
    document.title = t(key)
  },
  { immediate: true },
)
</script>

<style scoped>
.social-link {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.76);
  padding: 0.34rem 0.78rem;
  font-size: 0.84rem;
  font-weight: 700;
  color: var(--ink-700);
}

.social-link:hover {
  border-color: var(--line-strong);
  color: var(--ink-900);
  background: #fff;
}
</style>
