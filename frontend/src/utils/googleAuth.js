const GOOGLE_SCRIPT_ID = 'google-gsi-script'
const GOOGLE_BASE_URL = 'https://accounts.google.com/gsi/client'

let scriptPromise = null
let loadedLocale = null

function normalizeLocale(locale) {
  return locale === 'en' ? 'en' : 'ru'
}

function removeExistingScript() {
  const known = document.getElementById(GOOGLE_SCRIPT_ID)
  if (known) {
    known.remove()
  }
  document.querySelectorAll('script[src*="accounts.google.com/gsi/client"]').forEach((script) => {
    script.remove()
  })
}

export function ensureGoogleScript(locale = 'ru') {
  const normalizedLocale = normalizeLocale(locale)
  if (window.google?.accounts?.id && loadedLocale === normalizedLocale) {
    return Promise.resolve(window.google)
  }

  if (loadedLocale !== normalizedLocale) {
    scriptPromise = null
    removeExistingScript()
    loadedLocale = null
  }

  if (scriptPromise) {
    return scriptPromise
  }

  scriptPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.id = GOOGLE_SCRIPT_ID
    script.src = `${GOOGLE_BASE_URL}?hl=${normalizedLocale}`
    script.async = true
    script.defer = true
    script.onload = () => {
      loadedLocale = normalizedLocale
      resolve(window.google)
    }
    script.onerror = () => {
      scriptPromise = null
      loadedLocale = null
      reject(new Error('Google script failed to load'))
    }
    document.head.appendChild(script)
  })

  return scriptPromise
}
