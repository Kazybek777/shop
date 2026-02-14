import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { cartAPI } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { pickLocalized } from '@/i18n/runtime'

const CART_STORAGE_KEY = 'shopping_cart'

export const useCartStore = defineStore('cart', () => {
  const cartItems = ref({})
  const cartDetails = ref({ items: [], total: 0, items_count: 0 })
  const loading = ref(false)
  const error = ref('')

  const itemsCount = computed(() => Object.values(cartItems.value).reduce((sum, qty) => sum + Number(qty || 0), 0))
  const totalPrice = computed(() => cartDetails.value?.total || 0)
  const hasItems = computed(() => Object.keys(cartItems.value).length > 0)

  function normalizeCart(rawCart) {
    const normalized = {}
    Object.entries(rawCart || {}).forEach(([productId, quantity]) => {
      const parsedProductId = Number(productId)
      const parsedQuantity = Number(quantity)
      if (Number.isInteger(parsedProductId) && parsedProductId > 0 && Number.isInteger(parsedQuantity) && parsedQuantity > 0) {
        normalized[parsedProductId] = parsedQuantity
      }
    })
    return normalized
  }

  function initCart() {
    const savedCart = localStorage.getItem(CART_STORAGE_KEY)
    if (!savedCart) {
      return
    }
    try {
      cartItems.value = normalizeCart(JSON.parse(savedCart))
    } catch {
      cartItems.value = {}
      localStorage.removeItem(CART_STORAGE_KEY)
    }
  }

  function saveCart() {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems.value))
  }

  async function addToCart(productId, quantity = 1) {
    error.value = ''
    try {
      const response = await cartAPI.addItem({ product_id: productId, quantity }, cartItems.value)
      cartItems.value = normalizeCart(response.data.cart)
      saveCart()
      await fetchCartDetails()
      return true
    } catch (err) {
      error.value = getApiErrorMessage(err, pickLocalized('Не удалось добавить товар в корзину', 'Failed to add product to cart'))
      return false
    }
  }

  async function fetchCartDetails() {
    if (!hasItems.value) {
      cartDetails.value = { items: [], total: 0, items_count: 0 }
      return
    }

    loading.value = true
    error.value = ''
    try {
      const response = await cartAPI.getCart(cartItems.value)
      cartDetails.value = response.data
    } catch (err) {
      error.value = getApiErrorMessage(err, pickLocalized('Не удалось загрузить корзину', 'Failed to load cart'))
    } finally {
      loading.value = false
    }
  }

  async function updateQuantity(productId, quantity) {
    if (quantity <= 0) {
      return removeFromCart(productId)
    }

    error.value = ''
    try {
      const response = await cartAPI.updateItem({ product_id: productId, quantity }, cartItems.value)
      cartItems.value = normalizeCart(response.data.cart)
      saveCart()
      await fetchCartDetails()
      return true
    } catch (err) {
      error.value = getApiErrorMessage(err, pickLocalized('Не удалось обновить корзину', 'Failed to update cart'))
      return false
    }
  }

  async function removeFromCart(productId) {
    error.value = ''
    try {
      const response = await cartAPI.removeItem(productId, cartItems.value)
      cartItems.value = normalizeCart(response.data.cart)
      saveCart()
      await fetchCartDetails()
      return true
    } catch (err) {
      error.value = getApiErrorMessage(err, pickLocalized('Не удалось удалить товар из корзины', 'Failed to remove product from cart'))
      return false
    }
  }

  function clearCart() {
    cartItems.value = {}
    cartDetails.value = { items: [], total: 0, items_count: 0 }
    error.value = ''
    localStorage.removeItem(CART_STORAGE_KEY)
  }

  return {
    cartItems,
    cartDetails,
    loading,
    error,
    itemsCount,
    totalPrice,
    hasItems,
    initCart,
    addToCart,
    fetchCartDetails,
    updateQuantity,
    removeFromCart,
    clearCart,
  }
})
