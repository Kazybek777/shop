<template>
  <main class="page-wrap">
    <section class="max-w-md mx-auto ui-card p-6 sm:p-7 fade-up">
      <div class="mb-6">
        <p class="badge mb-3">{{ t('authPages.createAccount') }}</p>
        <h1 class="page-title !text-3xl mb-1">{{ t('authPages.register') }}</h1>
        <p class="page-subtitle">{{ t('authPages.registerSubtitle') }}</p>
      </div>

      <form class="space-y-4" @submit.prevent="handleRegister">
        <div>
          <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.fullName') }}</label>
          <input v-model.trim="form.full_name" type="text" required minlength="2" class="field" />
        </div>

        <div>
          <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.email') }}</label>
          <input v-model.trim="form.email" type="email" required class="field" />
        </div>

        <div>
          <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.password') }}</label>
          <div class="password-wrap">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              required
              minlength="8"
              class="field field--password"
            />
            <button
              type="button"
              class="password-toggle"
              :aria-label="showPassword ? t('header.hidePassword') : t('header.showPassword')"
              @click="showPassword = !showPassword"
            >
              <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18M10.58 10.58a2 2 0 002.83 2.83M16.68 16.67A9.72 9.72 0 0112 18C7 18 3.27 14.94 2 12a11.75 11.75 0 012.8-3.9M9.88 5.09A10.62 10.62 0 0112 6c5 0 8.73 3.06 10 6a11.8 11.8 0 01-1.67 2.75" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.46 12C3.73 8.94 7 6 12 6s8.27 2.94 9.54 6c-1.27 3.06-4.54 6-9.54 6S3.73 15.06 2.46 12z" />
              </svg>
            </button>
          </div>
        </div>
        <div>
          <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('authPages.confirmPassword') }}</label>
          <div class="password-wrap">
            <input
              v-model="form.confirm_password"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              minlength="8"
              class="field field--password"
            />
            <button
              type="button"
              class="password-toggle"
              :aria-label="showConfirmPassword ? t('header.hidePassword') : t('header.showPassword')"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <svg v-if="showConfirmPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18M10.58 10.58a2 2 0 002.83 2.83M16.68 16.67A9.72 9.72 0 0112 18C7 18 3.27 14.94 2 12a11.75 11.75 0 012.8-3.9M9.88 5.09A10.62 10.62 0 0112 6c5 0 8.73 3.06 10 6a11.8 11.8 0 01-1.67 2.75" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.46 12C3.73 8.94 7 6 12 6s8.27 2.94 9.54 6c-1.27 3.06-4.54 6-9.54 6S3.73 15.06 2.46 12z" />
              </svg>
            </button>
          </div>
        </div>

        <p v-if="validationError || authStore.error" class="text-red-600 text-sm font-medium">{{ validationError || authStore.error }}</p>

        <button type="submit" :disabled="authStore.loading" class="btn-primary w-full">
          {{ authStore.loading ? t('authPages.creating') : t('header.createAccount') }}
        </button>
      </form>

      <p class="text-sm mt-6 text-center text-[color:var(--ink-600)]">
        {{ t('authPages.alreadyHaveAccount') }}
        <RouterLink to="/login" class="font-semibold underline">{{ t('authPages.signInAction') }}</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const validationError = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = ref({
  full_name: '',
  email: '',
  password: '',
  confirm_password: '',
})

async function handleRegister() {
  validationError.value = ''
  if (form.value.password !== form.value.confirm_password) {
    validationError.value = t('authPages.passwordMismatch')
    return
  }
  try {
    await authStore.register({
      full_name: form.value.full_name,
      email: form.value.email,
      password: form.value.password,
    })
    await router.push(route.query.redirect || '/')
  } catch {
    // handled in store
  }
}

onMounted(() => {
  authStore.clearError()
})

watch(
  () => [form.value.password, form.value.confirm_password],
  () => {
    if (validationError.value && form.value.password === form.value.confirm_password) {
      validationError.value = ''
    }
  },
)

onBeforeUnmount(() => {
  authStore.clearError()
})
</script>

<style scoped>
.password-wrap {
  position: relative;
}

.field--password {
  padding-right: 2.5rem;
}

.password-toggle {
  position: absolute;
  right: 0.45rem;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--ink-600);
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
}

.password-toggle:hover {
  background: rgba(255, 255, 255, 0.82);
  color: var(--ink-900);
}
</style>
