import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { categoriesAPI, productsAPI } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { pickLocalized } from '@/i18n/runtime'

export const useProductsStore = defineStore('products', () => {
  const products = ref([])
  const categories = ref([])
  const selectedCategory = ref(null)
  const searchQuery = ref('')
  const loading = ref(false)
  const error = ref('')

  const filteredProducts = computed(() => {
    if (!selectedCategory.value) {
      return products.value
    }
    return products.value.filter((product) => product.category_id === selectedCategory.value)
  })

  const productsCount = computed(() => filteredProducts.value.length)

  async function fetchProducts(query = '') {
    loading.value = true
    error.value = ''
    try {
      const response = await productsAPI.getAll(query)
      products.value = response.data.products
      searchQuery.value = query
    } catch (err) {
      error.value = getApiErrorMessage(err, pickLocalized('Не удалось загрузить товары', 'Failed to load products'))
    } finally {
      loading.value = false
    }
  }

  async function fetchProductById(id) {
    loading.value = true
    error.value = ''
    try {
      const response = await productsAPI.getById(id)
      return response.data
    } catch (err) {
      error.value = getApiErrorMessage(err, pickLocalized('Не удалось загрузить товар', 'Failed to load product'))
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const response = await categoriesAPI.getAll()
      categories.value = response.data
    } catch {
      if (!error.value) {
        error.value = pickLocalized('Не удалось загрузить категории', 'Failed to load categories')
      }
    }
  }

  function setCategory(categoryId) {
    selectedCategory.value = categoryId
  }

  function clearCategoryFilter() {
    selectedCategory.value = null
  }

  return {
    products,
    categories,
    selectedCategory,
    searchQuery,
    loading,
    error,
    filteredProducts,
    productsCount,
    fetchProducts,
    fetchProductById,
    fetchCategories,
    setCategory,
    clearCategoryFilter,
  }
})
