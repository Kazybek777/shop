<template>
  <header class="site-header">
    <div class="max-w-7xl mx-auto px-4">
      <div class="h-20 flex items-center gap-3">
        <router-link to="/" class="inline-flex items-center gap-3 px-3 py-2 rounded-2xl hover:bg-white/60 transition-colors">
          <span class="h-10 w-10 rounded-xl bg-[color:var(--accent-soft)] text-[color:var(--accent-strong)] grid place-items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
          </span>
          <div>
            <p class="font-semibold text-sm text-[color:var(--ink-500)]">{{ t('header.onlineStore') }}</p>
            <p class="font-bold text-lg leading-tight" style="font-family: var(--font-display)">TashTemir</p>
          </div>
        </router-link>

        <form class="hidden md:flex header-search" @submit.prevent="submitSearch">
          <input
            v-model="searchInput"
            type="search"
            class="search-input"
            :placeholder="t('header.searchPlaceholder')"
            @input="handleSearchInput"
          />
          <button type="submit" class="search-btn" :aria-label="t('header.searchAria')">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M10.8 18a7.2 7.2 0 100-14.4 7.2 7.2 0 000 14.4z" />
            </svg>
          </button>
        </form>

        <nav class="hidden md:flex items-center gap-2 ml-auto">
          <router-link to="/" class="nav-link" active-class="nav-link--active">{{ t('header.catalog') }}</router-link>
          <router-link to="/cart" class="nav-link nav-link-cart" active-class="nav-link--active">
            <span>{{ t('header.cart') }}</span>
            <span v-if="cartStore.itemsCount > 0" class="cart-count-pill">
              {{ cartStore.itemsCount > 99 ? '99+' : cartStore.itemsCount }}
            </span>
          </router-link>

          <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link" active-class="nav-link--active">
            {{ t('header.admin') }}
          </router-link>

          <div class="lang-switch" :aria-label="t('header.language')">
            <button type="button" :class="['lang-btn', locale === 'ru' ? 'lang-btn--active' : '']" @click="setLocale('ru')">RU</button>
            <button type="button" :class="['lang-btn', locale === 'en' ? 'lang-btn--active' : '']" @click="setLocale('en')">EN</button>
          </div>

          <div ref="profileWrapRef" class="relative">
            <button class="avatar-btn" type="button" :aria-label="t('header.account')" @click="handleUserButtonClick">
              <span v-if="authStore.isAuthenticated && userInitials" class="avatar-initial">{{ userInitials }}</span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[color:var(--ink-700)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 14a4 4 0 10-8 0m8 0a4 4 0 01-8 0m8 0v.8A2.2 2.2 0 0113.8 17h-3.6A2.2 2.2 0 018 14.8V14m8 0V9a4 4 0 00-8 0v5" />
              </svg>
            </button>

            <transition name="slide-fade">
              <div v-if="profileMenuOpen && authStore.isAuthenticated" class="profile-panel">
                <p class="text-sm font-semibold text-[color:var(--ink-900)]">{{ authStore.user?.full_name }}</p>
                <p class="text-xs text-[color:var(--ink-500)] mb-2">{{ authStore.user?.email }}</p>
                <button class="btn-ghost w-full text-sm" @click="handleLogout">{{ t('header.logout') }}</button>
              </div>
            </transition>
          </div>
        </nav>

        <button
          class="md:hidden h-11 w-11 rounded-xl bg-white/80 border border-[color:var(--line)] grid place-items-center"
          :aria-expanded="mobileOpen ? 'true' : 'false'"
          @click="mobileOpen = !mobileOpen"
        >
          <span class="sr-only">Toggle menu</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-[color:var(--ink-700)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="mobileOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'" />
          </svg>
        </button>
      </div>

      <transition name="slide-fade">
        <div v-if="mobileOpen" class="md:hidden pb-4">
          <nav class="ui-card-soft p-3 flex flex-col gap-2">
            <form class="mobile-search" @submit.prevent="submitSearchAndClose">
              <input
                v-model="searchInput"
                type="search"
                class="search-input"
                :placeholder="t('header.searchPlaceholder')"
                @input="handleSearchInput"
              />
            </form>

            <div class="lang-switch self-start" :aria-label="t('header.language')">
              <button type="button" :class="['lang-btn', locale === 'ru' ? 'lang-btn--active' : '']" @click="setLocale('ru')">RU</button>
              <button type="button" :class="['lang-btn', locale === 'en' ? 'lang-btn--active' : '']" @click="setLocale('en')">EN</button>
            </div>

            <router-link to="/" class="mobile-link" @click="mobileOpen = false">{{ t('header.catalog') }}</router-link>
            <router-link to="/cart" class="mobile-link mobile-link-cart" @click="mobileOpen = false">
              <span>{{ t('header.cart') }}</span>
              <span v-if="cartStore.itemsCount > 0" class="cart-count-pill cart-count-pill--mobile">
                {{ cartStore.itemsCount > 99 ? '99+' : cartStore.itemsCount }}
              </span>
            </router-link>

            <router-link v-if="authStore.isAdmin" to="/admin" class="mobile-link" @click="mobileOpen = false">{{ t('header.admin') }}</router-link>

            <template v-if="authStore.isAuthenticated">
              <p class="px-3 py-2 text-sm text-[color:var(--ink-600)]">{{ authStore.user?.full_name }}</p>
              <button class="mobile-link text-left" @click="handleLogout">{{ t('header.logout') }}</button>
            </template>
            <template v-else>
              <button class="mobile-link text-left font-semibold" @click="openAuthModal('login')">{{ t('header.account') }}</button>
            </template>
          </nav>
        </div>
      </transition>
    </div>
  </header>

  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="authModalOpen" class="auth-modal-backdrop" @click.self="closeAuthModal">
        <section class="auth-modal-card ui-card">
          <div class="flex items-center justify-between mb-4">
            <div class="inline-flex items-center rounded-xl bg-[color:var(--accent-soft)] p-1">
              <button
                type="button"
                class="auth-tab"
                :class="{ 'auth-tab--active': authMode === 'login' }"
                @click="authMode = 'login'"
              >
                {{ t('header.login') }}
              </button>
              <button
                type="button"
                class="auth-tab"
                :class="{ 'auth-tab--active': authMode === 'register' }"
                @click="authMode = 'register'"
              >
                {{ t('header.register') }}
              </button>
            </div>
            <button class="btn-ghost px-2 py-1" type="button" @click="closeAuthModal">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form v-if="authMode === 'login'" class="space-y-3" @submit.prevent="handleLoginSubmit">
            <div>
              <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.email') }}</label>
              <input v-model.trim="loginForm.email" type="email" required class="field" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.password') }}</label>
              <div class="password-wrap">
                <input v-model="loginForm.password" :type="showLoginPassword ? 'text' : 'password'" required minlength="8" class="field field--password" />
                <button
                  type="button"
                  class="password-toggle"
                  :aria-label="showLoginPassword ? t('header.hidePassword') : t('header.showPassword')"
                  @click="showLoginPassword = !showLoginPassword"
                >
                  <svg v-if="showLoginPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18M10.58 10.58a2 2 0 002.83 2.83M16.68 16.67A9.72 9.72 0 0112 18C7 18 3.27 14.94 2 12a11.75 11.75 0 012.8-3.9M9.88 5.09A10.62 10.62 0 0112 6c5 0 8.73 3.06 10 6a11.8 11.8 0 01-1.67 2.75" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.46 12C3.73 8.94 7 6 12 6s8.27 2.94 9.54 6c-1.27 3.06-4.54 6-9.54 6S3.73 15.06 2.46 12z" />
                  </svg>
                </button>
              </div>
            </div>

            <p v-if="authStore.error" class="text-red-600 text-sm font-medium">{{ authStore.error }}</p>
            <button type="submit" :disabled="authStore.loading" class="btn-primary w-full">
              {{ authStore.loading ? t('header.signingIn') : t('header.signIn') }}
            </button>
          </form>

          <form v-else class="space-y-3" @submit.prevent="handleRegisterSubmit">
            <div>
              <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.fullName') }}</label>
              <input v-model.trim="registerForm.full_name" type="text" required minlength="2" class="field" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.email') }}</label>
              <input v-model.trim="registerForm.email" type="email" required class="field" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.password') }}</label>
              <div class="password-wrap">
                <input
                  v-model="registerForm.password"
                  :type="showRegisterPassword ? 'text' : 'password'"
                  required
                  minlength="8"
                  class="field field--password"
                />
                <button
                  type="button"
                  class="password-toggle"
                  :aria-label="showRegisterPassword ? t('header.hidePassword') : t('header.showPassword')"
                  @click="showRegisterPassword = !showRegisterPassword"
                >
                  <svg v-if="showRegisterPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
              <label class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('header.confirmPassword') }}</label>
              <div class="password-wrap">
                <input
                  v-model="registerForm.confirm_password"
                  :type="showRegisterConfirmPassword ? 'text' : 'password'"
                  required
                  minlength="8"
                  class="field field--password"
                />
                <button
                  type="button"
                  class="password-toggle"
                  :aria-label="showRegisterConfirmPassword ? t('header.hidePassword') : t('header.showPassword')"
                  @click="showRegisterConfirmPassword = !showRegisterConfirmPassword"
                >
                  <svg v-if="showRegisterConfirmPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18M10.58 10.58a2 2 0 002.83 2.83M16.68 16.67A9.72 9.72 0 0112 18C7 18 3.27 14.94 2 12a11.75 11.75 0 012.8-3.9M9.88 5.09A10.62 10.62 0 0112 6c5 0 8.73 3.06 10 6a11.8 11.8 0 01-1.67 2.75" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.46 12C3.73 8.94 7 6 12 6s8.27 2.94 9.54 6c-1.27 3.06-4.54 6-9.54 6S3.73 15.06 2.46 12z" />
                  </svg>
                </button>
              </div>
            </div>

            <p v-if="registerErrorMessage" class="text-red-600 text-sm font-medium">{{ registerErrorMessage }}</p>
            <button type="submit" :disabled="authStore.loading" class="btn-primary w-full">
              {{ authStore.loading ? t('header.creatingAccount') : t('header.createAccount') }}
            </button>
          </form>

          <div v-if="authMode === 'login'" class="mt-4">
            <div class="text-center text-sm text-[color:var(--ink-500)] mb-3">{{ t('header.continueWithGoogle') }}</div>
            <div ref="googleButton" class="flex justify-center"></div>
            <p v-if="googleError" class="text-red-600 text-sm text-center mt-3">{{ googleError }}</p>
          </div>
        </section>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import { useProductsStore } from '@/stores/products'
import { useI18n } from '@/composables/useI18n'
import { ensureGoogleScript } from '@/utils/googleAuth'

defineOptions({
  name: 'AppHeader',
})

const cartStore = useCartStore()
const authStore = useAuthStore()
const productsStore = useProductsStore()
const router = useRouter()
const route = useRoute()
const { locale, setLocale, t } = useI18n()

const mobileOpen = ref(false)
const profileMenuOpen = ref(false)
const profileWrapRef = ref(null)
const searchInput = ref('')
let searchTimer = null

const authModalOpen = ref(false)
const authMode = ref('login')
const googleButton = ref(null)
const googleError = ref('')
const registerLocalError = ref('')
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)
const showRegisterConfirmPassword = ref(false)

const loginForm = ref({
  email: '',
  password: '',
})

const registerForm = ref({
  full_name: '',
  email: '',
  password: '',
  confirm_password: '',
})

const registerErrorMessage = computed(() => registerLocalError.value || authStore.error)

const userInitials = computed(() => {
  const fullName = authStore.user?.full_name || ''
  const parts = fullName
    .split(' ')
    .map((part) => part.trim())
    .filter(Boolean)
  if (parts.length === 0) {
    return ''
  }
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase()
  }
  return `${parts[0][0] || ''}${parts[1][0] || ''}`.toUpperCase()
})

watch(
  () => route.fullPath,
  () => {
    mobileOpen.value = false
    profileMenuOpen.value = false
    syncSearchFromRoute()
    maybeOpenAuthModalFromQuery()
  },
  { immediate: true },
)

watch([authModalOpen, authMode], async ([isOpen, mode]) => {
  registerLocalError.value = ''
  if (!isOpen || mode !== 'login') {
    return
  }
  await nextTick()
  await renderGoogleButton()
})

watch(locale, async () => {
  if (!authModalOpen.value || authMode.value !== 'login') {
    return
  }
  await nextTick()
  await renderGoogleButton()
})

watch(
  () => [registerForm.value.password, registerForm.value.confirm_password],
  () => {
    if (registerLocalError.value && registerForm.value.password === registerForm.value.confirm_password) {
      registerLocalError.value = ''
    }
  },
)

function getRouteSearch() {
  const queryValue = route.query.q
  if (typeof queryValue === 'string') {
    return queryValue
  }
  return productsStore.searchQuery || ''
}

function syncSearchFromRoute() {
  const nextValue = getRouteSearch()
  if (searchInput.value !== nextValue) {
    searchInput.value = nextValue
  }
}

function handleSearchInput() {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    applySearch(searchInput.value)
  }, 320)
}

async function submitSearch() {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
  await applySearch(searchInput.value)
}

async function submitSearchAndClose() {
  await submitSearch()
  mobileOpen.value = false
}

async function applySearch(rawValue) {
  const query = (rawValue || '').trim()
  const currentQuery = typeof route.query.q === 'string' ? route.query.q : ''
  if (route.name === 'home') {
    if (query === currentQuery) {
      return
    }
    const nextQuery = { ...route.query }
    if (query) {
      nextQuery.q = query
    } else {
      delete nextQuery.q
    }
    await router.replace({ name: 'home', query: nextQuery })
    return
  }

  await router.push({
    name: 'home',
    query: query ? { q: query } : {},
  })
}

function maybeOpenAuthModalFromQuery() {
  const authQuery = route.query.auth
  if (authQuery !== 'login' && authQuery !== 'register') {
    return
  }
  if (authStore.isAuthenticated) {
    return
  }
  openAuthModal(authQuery)
}

function openAuthModal(mode = 'login') {
  authMode.value = mode === 'register' ? 'register' : 'login'
  authStore.clearError()
  googleError.value = ''
  registerLocalError.value = ''
  showLoginPassword.value = false
  showRegisterPassword.value = false
  showRegisterConfirmPassword.value = false
  profileMenuOpen.value = false
  mobileOpen.value = false
  authModalOpen.value = true
}

function closeAuthModal() {
  authModalOpen.value = false
  authStore.clearError()
  googleError.value = ''
  registerLocalError.value = ''
  showLoginPassword.value = false
  showRegisterPassword.value = false
  showRegisterConfirmPassword.value = false

  const nextQuery = { ...route.query }
  if (nextQuery.auth || nextQuery.redirect) {
    delete nextQuery.auth
    delete nextQuery.redirect
    router.replace({ query: nextQuery })
  }
}

function handleUserButtonClick() {
  if (!authStore.isAuthenticated) {
    openAuthModal('login')
    return
  }
  profileMenuOpen.value = !profileMenuOpen.value
}

function handleDocumentPointerDown(event) {
  if (!profileMenuOpen.value) {
    return
  }
  const wrap = profileWrapRef.value
  if (wrap && !wrap.contains(event.target)) {
    profileMenuOpen.value = false
  }
}

function handleDocumentKeydown(event) {
  if (event.key === 'Escape' && profileMenuOpen.value) {
    profileMenuOpen.value = false
  }
}

async function handleLoginSubmit() {
  try {
    await authStore.login(loginForm.value)
    await completeAuthFlow()
  } catch {
    // handled in store
  }
}

async function handleRegisterSubmit() {
  registerLocalError.value = ''
  if (registerForm.value.password !== registerForm.value.confirm_password) {
    registerLocalError.value = t('header.passwordMismatch')
    return
  }
  try {
    await authStore.register({
      full_name: registerForm.value.full_name,
      email: registerForm.value.email,
      password: registerForm.value.password,
    })
    await completeAuthFlow()
  } catch {
    // handled in store
  }
}

async function completeAuthFlow() {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  const target = redirect || (authStore.isAdmin ? '/admin' : '/')

  authModalOpen.value = false
  authStore.clearError()
  googleError.value = ''
  registerLocalError.value = ''
  showLoginPassword.value = false
  showRegisterPassword.value = false
  showRegisterConfirmPassword.value = false
  loginForm.value = { email: '', password: '' }
  registerForm.value = { full_name: '', email: '', password: '', confirm_password: '' }

  await router.push(target)
}

async function handleGoogleCredential(response) {
  if (!response?.credential) {
    googleError.value = t('header.googleNoCredential')
    return
  }
  try {
    await authStore.loginWithGoogle(response.credential)
    await completeAuthFlow()
  } catch {
    // handled in store
  }
}

async function renderGoogleButton() {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (!clientId) {
    googleError.value = t('header.googleClientMissing')
    return false
  }

  try {
    await ensureGoogleScript(locale.value)
  } catch {
    googleError.value = t('header.googleScriptFailed')
    return false
  }

  if (!window.google?.accounts?.id || !googleButton.value) {
    googleError.value = t('header.googleScriptFailed')
    return false
  }

  googleError.value = ''
  googleButton.value.innerHTML = ''
  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: handleGoogleCredential,
  })
  window.google.accounts.id.renderButton(googleButton.value, {
    type: 'standard',
    shape: 'pill',
    theme: 'outline',
    text: 'signin_with',
    size: 'large',
    width: 320,
  })
  return true
}

function handleLogout() {
  authStore.logout()
  profileMenuOpen.value = false
  mobileOpen.value = false
  router.push('/')
}

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown)
  document.addEventListener('keydown', handleDocumentKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
  document.removeEventListener('keydown', handleDocumentKeydown)
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
})
</script>

<style scoped>
.header-search {
  position: relative;
  width: min(440px, 100%);
  margin-left: 0.5rem;
}

.search-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.62rem 2.6rem 0.62rem 0.82rem;
  color: var(--ink-900);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.12);
}

.search-btn {
  position: absolute;
  right: 0.45rem;
  top: 50%;
  transform: translateY(-50%);
  height: 32px;
  width: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--ink-600);
}

.search-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  color: var(--ink-900);
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 12px;
  padding: 0.55rem 0.85rem;
  font-weight: 700;
  font-size: 0.92rem;
  color: var(--ink-700);
  transition: all 0.2s ease;
}

.nav-link-cart {
  padding-right: 0.72rem;
}

.cart-count-pill {
  min-width: 1.35rem;
  height: 1.35rem;
  border-radius: 999px;
  background: var(--accent);
  color: #fff;
  font-size: 0.71rem;
  font-weight: 800;
  padding: 0 0.35rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 4px 10px rgba(15, 118, 110, 0.24);
}

.cart-count-pill--mobile {
  min-width: 1.25rem;
  height: 1.25rem;
  font-size: 0.68rem;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.82);
  color: var(--ink-900);
}

.nav-link--active {
  background: #fff;
  color: var(--ink-900);
  box-shadow: 0 6px 16px rgba(32, 39, 34, 0.1);
}

.lang-switch {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.85);
}

.lang-btn {
  border: none;
  background: transparent;
  padding: 0.35rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--ink-600);
}

.lang-btn--active {
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.avatar-btn {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.9);
}

.avatar-btn:hover {
  border-color: var(--line-strong);
}

.avatar-initial {
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--accent-strong);
}

.profile-panel {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 220px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(255, 250, 242, 0.98);
  padding: 0.75rem;
  box-shadow: 0 14px 26px rgba(36, 42, 36, 0.13);
}

.mobile-link {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 10px;
  padding: 0.6rem 0.7rem;
  color: var(--ink-700);
  font-size: 0.95rem;
}

.mobile-link:hover {
  background: rgba(255, 255, 255, 0.8);
  color: var(--ink-900);
}

.mobile-link-cart {
  gap: 0.5rem;
}

.mobile-search {
  margin-bottom: 0.2rem;
}

.auth-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 90;
  padding: 1rem;
  display: grid;
  place-items: center;
  background: rgba(20, 27, 23, 0.58);
  backdrop-filter: blur(6px);
}

.auth-modal-card {
  width: min(460px, 100%);
  padding: 1.1rem;
  border-radius: 18px;
  box-shadow: 0 18px 34px rgba(20, 25, 23, 0.34);
}

.auth-tab {
  border: none;
  background: transparent;
  color: var(--ink-700);
  padding: 0.46rem 0.86rem;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
}

.auth-tab--active {
  background: #fff;
  color: var(--ink-900);
  box-shadow: 0 6px 14px rgba(35, 45, 40, 0.11);
}

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

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
