const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '')

export function toAbsoluteMediaUrl(imageUrl) {
  if (!imageUrl) {
    return ''
  }
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }
  if (imageUrl.startsWith('/')) {
    return `${API_ORIGIN}${imageUrl}`
  }
  return `${API_ORIGIN}/${imageUrl}`
}

export function resolveImageUrl(imageUrl) {
  return toAbsoluteMediaUrl(imageUrl)
}

export function getRawProductImages(product) {
  if (!product) {
    return []
  }

  const images = Array.isArray(product.images) ? product.images : []
  const normalized = images.map((url) => String(url || '').trim()).filter(Boolean)
  if (normalized.length > 0) {
    return normalized
  }

  const fallback = String(product.image_url || '').trim()
  return fallback ? [fallback] : []
}

export function getProductImages(product) {
  return getRawProductImages(product).map((url) => toAbsoluteMediaUrl(url)).filter(Boolean)
}

export function getPrimaryProductImage(product) {
  const images = getRawProductImages(product)
  return images[0] ? toAbsoluteMediaUrl(images[0]) : ''
}
