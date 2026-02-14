import { pickLocalized } from '@/i18n/runtime'

export function getApiErrorMessage(error, fallbackMessage = pickLocalized('Произошла ошибка', 'Something went wrong')) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim().length > 0) {
    return detail.trim()
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (typeof first?.msg === 'string' && first.msg.trim().length > 0) {
      return first.msg.trim()
    }
  }
  return fallbackMessage
}
