import { computed } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import { messages } from '@/i18n/messages'

function getNestedValue(source, path) {
  return path.split('.').reduce((current, segment) => {
    if (current && typeof current === 'object' && segment in current) {
      return current[segment]
    }
    return undefined
  }, source)
}

function interpolate(template, params) {
  return String(template).replace(/\{(\w+)\}/g, (_, key) => String(params?.[key] ?? `{${key}}`))
}

function getPluralForm(locale, rawCount) {
  const count = Math.abs(Number(rawCount) || 0)
  if (locale !== 'ru') {
    return count === 1 ? 'one' : 'other'
  }

  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) {
    return 'one'
  }
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
    return 'few'
  }
  return 'many'
}

export function useI18n() {
  const i18nStore = useI18nStore()
  const locale = computed(() => i18nStore.locale)

  function rawMessage(key) {
    return getNestedValue(messages[locale.value], key) ?? getNestedValue(messages.en, key)
  }

  function t(key, params = {}) {
    const value = rawMessage(key)
    if (typeof value === 'string') {
      return interpolate(value, params)
    }
    return key
  }

  function tPlural(key, count, params = {}) {
    const forms = rawMessage(key)
    if (!forms || typeof forms !== 'object') {
      return t(key, { ...params, count })
    }

    const form = getPluralForm(locale.value, count)
    const template = forms[form] ?? forms.other ?? forms.one ?? ''
    return interpolate(template, { ...params, count })
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat(locale.value === 'ru' ? 'ru-KG' : 'en-US', {
      style: 'currency',
      currency: 'KGS',
      maximumFractionDigits: 2,
    }).format(Number(value || 0))
  }

  function formatDate(value) {
    return new Intl.DateTimeFormat(locale.value === 'ru' ? 'ru-RU' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date(value))
  }

  function localizedCategoryName(category) {
    if (!category) {
      return ''
    }
    if (locale.value === 'ru') {
      return category.name_ru || category.name || category.name_en || ''
    }
    return category.name_en || category.name || category.name_ru || ''
  }

  function localizedProductName(product) {
    if (!product) {
      return ''
    }
    if (locale.value === 'ru') {
      return product.name_ru || product.name || product.name_en || ''
    }
    return product.name_en || product.name || product.name_ru || ''
  }

  function localizedProductDescription(product) {
    if (!product) {
      return ''
    }
    if (locale.value === 'ru') {
      return product.description_ru || product.description || product.description_en || ''
    }
    return product.description_en || product.description || product.description_ru || ''
  }

  return {
    locale,
    setLocale: (nextLocale) => i18nStore.setLocale(nextLocale),
    t,
    tPlural,
    formatCurrency,
    formatDate,
    localizedCategoryName,
    localizedProductName,
    localizedProductDescription,
  }
}
