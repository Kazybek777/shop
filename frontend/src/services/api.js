import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const TOKEN_KEY = 'access_token'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem('auth_user')
    }
    return Promise.reject(error)
  },
)

export const productsAPI = {
  getAll(query = '') {
    const params = {}
    if (query?.trim()) {
      params.q = query.trim()
    }
    return apiClient.get('/products', { params })
  },

  getById(id) {
    return apiClient.get(`/products/${id}`)
  },

  getByCategory(categoryId) {
    return apiClient.get(`/products/category/${categoryId}`)
  },
}

export const categoriesAPI = {
  getAll() {
    return apiClient.get('/categories')
  },

  getById(id) {
    return apiClient.get(`/categories/${id}`)
  },
}

export const cartAPI = {
  addItem(item, cartData) {
    return apiClient.post('/cart/add', {
      product_id: item.product_id,
      quantity: item.quantity,
      cart: cartData,
    })
  },

  getCart(cartData) {
    return apiClient.post('/cart', cartData)
  },

  updateItem(item, cartData) {
    return apiClient.put('/cart/update', {
      product_id: item.product_id,
      quantity: item.quantity,
      cart: cartData,
    })
  },

  removeItem(productId, cartData) {
    return apiClient.delete(`/cart/remove/${productId}`, {
      data: {
        cart: cartData,
      },
    })
  },
}

export const authAPI = {
  register(payload) {
    return apiClient.post('/auth/register', payload)
  },

  login(payload) {
    return apiClient.post('/auth/login', payload)
  },

  google(idToken) {
    return apiClient.post('/auth/google', { id_token: idToken })
  },

  me() {
    return apiClient.get('/auth/me')
  },
}

export const adminAPI = {
  getUsers() {
    return apiClient.get('/admin/users')
  },

  updateUserRole(userId, role) {
    return apiClient.patch(`/admin/users/${userId}/role`, { role })
  },

  deleteUser(userId) {
    return apiClient.delete(`/admin/users/${userId}`)
  },

  getCategories() {
    return apiClient.get('/admin/categories')
  },

  createCategory(payload) {
    return apiClient.post('/admin/categories', payload)
  },

  updateCategory(id, payload) {
    return apiClient.put(`/admin/categories/${id}`, payload)
  },

  deleteCategory(id) {
    return apiClient.delete(`/admin/categories/${id}`)
  },

  getProducts() {
    return apiClient.get('/admin/products')
  },

  createProduct(formData) {
    return apiClient.post('/admin/products', formData)
  },

  updateProduct(id, formData) {
    return apiClient.put(`/admin/products/${id}`, formData)
  },

  deleteProduct(id) {
    return apiClient.delete(`/admin/products/${id}`)
  },
}

export { TOKEN_KEY }
export default apiClient
