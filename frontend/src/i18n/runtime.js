export function getStoredLocale() {
  return localStorage.getItem('shop_locale') === 'en' ? 'en' : 'ru'
}

export function pickLocalized(ruMessage, enMessage) {
  return getStoredLocale() === 'ru' ? ruMessage : enMessage
}
