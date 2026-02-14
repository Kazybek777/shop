import { defineStore } from 'pinia'
import { authAPI, TOKEN_KEY } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { pickLocalized } from '@/i18n/runtime'

const USER_KEY = 'auth_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
    loading: false,
    error: '',
    initialized: false,
    initPromise: null,
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
    isAdmin: (state) => state.user?.role === 'admin',
  },

  actions: {
    async initAuth(force = false) {
      if (this.initialized && !force) {
        return this.user
      }
      if (this.initPromise) {
        return this.initPromise
      }

      this.initPromise = (async () => {
        if (!this.token) {
          this.user = null
          this.initialized = true
          return null
        }

        try {
          return await this.fetchMe()
        } catch {
          this.logout()
          return null
        } finally {
          this.initialized = true
          this.initPromise = null
        }
      })()

      return this.initPromise
    },

    clearError() {
      this.error = ''
    },

    async register(payload) {
      this.loading = true
      this.error = ''
      try {
        const { data } = await authAPI.register(payload)
        this.setSession(data)
        this.initialized = true
        return data.user
      } catch (err) {
        this.error = getApiErrorMessage(err, pickLocalized('Не удалось зарегистрироваться', 'Registration failed'))
        throw err
      } finally {
        this.loading = false
      }
    },

    async login(payload) {
      this.loading = true
      this.error = ''
      try {
        const { data } = await authAPI.login(payload)
        this.setSession(data)
        this.initialized = true
        return data.user
      } catch (err) {
        this.error = getApiErrorMessage(err, pickLocalized('Не удалось войти', 'Login failed'))
        throw err
      } finally {
        this.loading = false
      }
    },

    async loginWithGoogle(idToken) {
      this.loading = true
      this.error = ''
      try {
        const { data } = await authAPI.google(idToken)
        this.setSession(data)
        this.initialized = true
        return data.user
      } catch (err) {
        this.error = getApiErrorMessage(err, pickLocalized('Не удалось войти через Google', 'Google login failed'))
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      const { data } = await authAPI.me()
      this.user = data
      localStorage.setItem(USER_KEY, JSON.stringify(data))
      return data
    },

    logout() {
      this.token = ''
      this.user = null
      this.error = ''
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      this.initialized = true
      this.initPromise = null
    },

    setSession(data) {
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem(TOKEN_KEY, data.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    },
  },
})
