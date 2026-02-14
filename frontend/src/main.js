import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { useI18nStore } from '@/stores/i18n'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

const cartStore = useCartStore(pinia)
cartStore.initCart()

const authStore = useAuthStore(pinia)
await authStore.initAuth()

const i18nStore = useI18nStore(pinia)
i18nStore.applyLocale()

app.use(router)

app.mount('#app')
