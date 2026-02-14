import { defineStore } from 'pinia'

const LOCALE_KEY = 'shop_locale'
const SUPPORTED_LOCALES = ['ru', 'en']

function normalizeLocale(value) {
  return SUPPORTED_LOCALES.includes(value) ? value : 'ru'
}

export const useI18nStore = defineStore('i18n', {
  state: () => ({
    locale: normalizeLocale(localStorage.getItem(LOCALE_KEY)),
  }),

  actions: {
    applyLocale() {
      document.documentElement.lang = this.locale
    },

    setLocale(nextLocale) {
      const locale = normalizeLocale(nextLocale)
      if (this.locale === locale) {
        return
      }
      this.locale = locale
      localStorage.setItem(LOCALE_KEY, locale)
      this.applyLocale()
    },
  },
})
