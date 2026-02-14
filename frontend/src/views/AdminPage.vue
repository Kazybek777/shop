<template>
  <main class="page-wrap">
    <div class="hero-panel mb-8 fade-up">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 class="page-title mb-2">{{ t('admin.title') }}</h1>
          <p class="page-subtitle">{{ t('admin.subtitle') }}</p>
        </div>
        <button class="btn-secondary" :disabled="loading || busy" @click="loadData()">
          {{ loading ? t('common.refreshing') : t('common.refresh') }}
        </button>
      </div>
    </div>

    <p v-if="errorMessage" class="ui-card-soft mb-6 px-4 py-3 text-red-700 border border-red-200">
      {{ errorMessage }}
    </p>
    <p v-if="successMessage" class="ui-card-soft mb-6 px-4 py-3 text-[color:var(--accent-strong)] border border-[color:var(--accent-soft)]">
      {{ successMessage }}
    </p>

    <div v-if="loading" class="ui-card p-16 text-center">
      <div class="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-[color:var(--accent)]"></div>
      <p class="text-[color:var(--ink-500)] mt-4">{{ t('admin.loadingAdminData') }}</p>
    </div>

    <template v-else>
      <section class="ui-card p-5 mb-7 fade-up" style="animation-delay: 0.08s">
        <h2 class="text-2xl font-bold mb-4" style="font-family: var(--font-display)">{{ t('admin.users') }}</h2>
        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead>
              <tr class="border-b border-[color:var(--line)] text-left text-sm text-[color:var(--ink-500)]">
                <th class="py-2 pr-3 font-semibold">{{ t('common.name') }}</th>
                <th class="py-2 pr-3 font-semibold">{{ t('common.email') }}</th>
                <th class="py-2 pr-3 font-semibold">{{ t('common.provider') }}</th>
                <th class="py-2 pr-3 font-semibold">{{ t('common.role') }}</th>
                <th class="py-2 font-semibold">{{ t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in sortedUsers" :key="user.id" class="border-b border-[color:var(--line)]/70">
                <td class="py-3 pr-3">{{ user.full_name }}</td>
                <td class="py-3 pr-3">{{ user.email }}</td>
                <td class="py-3 pr-3 capitalize">{{ user.provider }}</td>
                <td class="py-3 pr-3">
                  <select class="field-select max-w-[140px]" :value="user.role" :disabled="busy" @change="updateRole(user, $event.target.value)">
                    <option value="user">{{ t('admin.roleUser') }}</option>
                    <option value="admin">{{ t('admin.roleAdmin') }}</option>
                  </select>
                </td>
                <td class="py-3">
                  <button
                    class="btn-ghost text-red-700 text-sm"
                    :disabled="busy || user.id === authStore.user?.id"
                    @click="deleteUser(user)"
                  >
                    {{ t('common.delete') }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="ui-card p-5 mb-7 fade-up" style="animation-delay: 0.12s">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <h2 class="text-2xl font-bold" style="font-family: var(--font-display)">{{ t('admin.categories') }}</h2>
          <button class="btn-secondary" :disabled="busy" @click="resetCategoryForm">{{ t('admin.newCategory') }}</button>
        </div>

        <form class="grid md:grid-cols-3 gap-3 mb-5" @submit.prevent="saveCategory">
          <input v-model.trim="categoryForm.name" required minlength="3" class="field" :placeholder="t('admin.categoryName')" />
          <input v-model.trim="categoryForm.slug" required minlength="3" class="field" :placeholder="t('admin.categorySlug')" />
          <button type="submit" :disabled="busy" class="btn-primary">
            {{ categoryForm.id ? t('admin.updateCategoryAction') : t('admin.createCategoryAction') }}
          </button>
        </form>

        <ul class="space-y-2">
          <li
            v-for="category in categories"
            :key="category.id"
            class="ui-card-soft px-3 py-2 flex items-center justify-between"
          >
            <div>
              <p class="font-semibold">{{ localizedCategoryName(category) }}</p>
              <p class="text-xs text-[color:var(--ink-500)]">{{ category.slug }}</p>
            </div>
            <div class="flex items-center gap-3">
              <button class="btn-ghost text-sm" :disabled="busy" @click="editCategory(category)">{{ t('common.edit') }}</button>
              <button class="btn-ghost text-sm text-red-700" :disabled="busy" @click="deleteCategory(category)">{{ t('common.delete') }}</button>
            </div>
          </li>
        </ul>
      </section>

      <section class="ui-card p-5 fade-up" style="animation-delay: 0.16s">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <h2 class="text-2xl font-bold" style="font-family: var(--font-display)">{{ t('admin.products') }}</h2>
          <button class="btn-secondary" :disabled="busy" @click="resetProductForm">{{ t('admin.newProduct') }}</button>
        </div>

        <form class="grid md:grid-cols-2 gap-3 mb-5" @submit.prevent="saveProduct">
          <input v-model.trim="productForm.name" required minlength="3" class="field" :placeholder="t('admin.productName')" />
          <input
            v-model.number="productForm.price"
            type="number"
            min="0.01"
            step="0.01"
            required
            class="field"
            :placeholder="t('common.price')"
          />
          <select v-model.number="productForm.category_id" required class="field-select">
            <option :value="null" disabled>{{ t('admin.selectCategory') }}</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">{{ localizedCategoryName(category) }}</option>
          </select>
          <label class="ui-card-soft px-3 py-2 flex flex-col gap-2">
            <span class="text-sm font-semibold text-[color:var(--ink-700)]">{{ t('admin.productImages') }}</span>
            <input ref="imageInputRef" type="file" accept="image/*" multiple class="field" @change="handleProductImageChange" />
            <span class="text-xs text-[color:var(--ink-500)]">{{ t('admin.productImagesHelp') }}</span>
            <span class="text-xs text-[color:var(--ink-500)]">
              {{ productImagesHint }}
            </span>
          </label>
          <textarea
            v-model.trim="productForm.description"
            rows="3"
            class="field-textarea md:col-span-2"
            :placeholder="t('admin.description')"
          ></textarea>
          <div v-if="productForm.image_urls.length || productImagePreviews.length" class="md:col-span-2">
            <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-[color:var(--ink-500)]">{{ t('admin.preview') }}</p>
            <div v-if="productForm.image_urls.length" class="mb-3">
              <p class="mb-1 text-xs text-[color:var(--ink-500)]">{{ t('admin.currentPhotos') }}</p>
              <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
                <div v-for="(image, index) in productForm.image_urls" :key="`existing-${index}`" class="relative">
                  <img :src="resolveImageUrl(image)" alt="Existing product preview" class="h-20 w-full rounded-xl object-cover border border-[color:var(--line)] bg-white/80" />
                  <button
                    type="button"
                    class="image-remove-btn"
                    :aria-label="t('common.delete')"
                    @click="removeExistingImage(index)"
                  >
                    x
                  </button>
                </div>
              </div>
            </div>
            <div v-if="productImagePreviews.length">
              <p class="mb-1 text-xs text-[color:var(--ink-500)]">{{ t('admin.newPhotos') }}</p>
              <div class="grid grid-cols-3 sm:grid-cols-5 gap-2">
                <div v-for="(image, index) in productImagePreviews" :key="`preview-${index}`" class="relative">
                  <img :src="image" alt="Product preview" class="h-20 w-full rounded-xl object-cover border border-[color:var(--line)] bg-white/80" />
                  <button
                    type="button"
                    class="image-remove-btn"
                    :aria-label="t('common.delete')"
                    @click="removeNewImage(index)"
                  >
                    x
                  </button>
                </div>
              </div>
            </div>
          </div>
          <button type="submit" :disabled="busy" class="btn-primary md:col-span-2">
            {{ productForm.id ? t('admin.updateProductAction') : t('admin.createProductAction') }}
          </button>
        </form>

        <div class="overflow-x-auto">
          <table class="w-full border-collapse">
            <thead>
              <tr class="border-b border-[color:var(--line)] text-left text-sm text-[color:var(--ink-500)]">
                <th class="py-2 pr-3 font-semibold">{{ t('common.image') }}</th>
                <th class="py-2 pr-3 font-semibold">{{ t('common.name') }}</th>
                <th class="py-2 pr-3 font-semibold">{{ t('common.category') }}</th>
                <th class="py-2 pr-3 font-semibold">{{ t('common.price') }}</th>
                <th class="py-2 font-semibold">{{ t('common.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in products" :key="product.id" class="border-b border-[color:var(--line)]/70">
                <td class="py-3 pr-3">
                  <img
                    :src="primaryImage(product)"
                    alt="Product image"
                    class="h-10 w-10 rounded-lg object-cover border border-[color:var(--line)]"
                    @error="onTableImageError"
                  />
                </td>
                <td class="py-3 pr-3">{{ localizedProductName(product) }}</td>
                <td class="py-3 pr-3">{{ localizedCategoryName(product.category) || '-' }}</td>
                <td class="py-3 pr-3">{{ formatCurrency(product.price) }}</td>
                <td class="py-3">
                  <div class="flex items-center gap-3">
                    <span class="text-xs text-[color:var(--ink-500)]">{{ t('admin.photos', { count: productImagesCount(product) }) }}</span>
                    <button class="btn-ghost text-sm" :disabled="busy" @click="editProduct(product)">{{ t('common.edit') }}</button>
                    <button class="btn-ghost text-sm text-red-700" :disabled="busy" @click="deleteProduct(product)">
                      {{ t('common.delete') }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { adminAPI } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { getPrimaryProductImage, getRawProductImages, resolveImageUrl } from '@/utils/media'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const MAX_PRODUCT_FILES = 5
const { t, formatCurrency, localizedCategoryName, localizedProductDescription, localizedProductName } = useI18n()

const users = ref([])
const categories = ref([])
const products = ref([])
const loading = ref(false)
const busy = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const messageTimer = ref(null)

const categoryForm = ref({
  id: null,
  name: '',
  slug: '',
})
const imageInputRef = ref(null)

function buildEmptyProductForm() {
  return {
    id: null,
    name: '',
    description: '',
    price: '',
    category_id: null,
    image_urls: [],
    image_files: [],
  }
}

const productForm = ref(buildEmptyProductForm())
const productImagePreviews = ref([])

const sortedUsers = computed(() =>
  [...users.value].sort((a, b) => {
    if (a.role === b.role) {
      return a.email.localeCompare(b.email)
    }
    return a.role === 'admin' ? -1 : 1
  }),
)

const productImagesHint = computed(() => {
  const selectedCount = productForm.value.image_files.length
  const existingCount = productForm.value.image_urls.length

  if (selectedCount > 0 && existingCount > 0) {
    return `${t('admin.imagesKept', { count: existingCount })}. ${t('admin.imagesSelected', { count: selectedCount })}`
  }

  if (selectedCount > 0) {
    return t('admin.imagesSelected', { count: selectedCount })
  }

  if (existingCount > 0) {
    return t('admin.imagesKept', { count: existingCount })
  }

  return t('admin.noImagesSelected')
})

function clearProductPreviewUrls() {
  productImagePreviews.value.forEach((url) => {
    if (typeof url === 'string' && url.startsWith('blob:')) {
      URL.revokeObjectURL(url)
    }
  })
  productImagePreviews.value = []
}

function clearMessageTimer() {
  if (messageTimer.value) {
    clearTimeout(messageTimer.value)
    messageTimer.value = null
  }
}

function showError(error, fallback) {
  clearMessageTimer()
  successMessage.value = ''
  errorMessage.value = getApiErrorMessage(error, fallback)
}

function showSuccess(message) {
  clearMessageTimer()
  errorMessage.value = ''
  successMessage.value = message
  messageTimer.value = setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

async function loadData() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [usersRes, categoriesRes, productsRes] = await Promise.all([
      adminAPI.getUsers(),
      adminAPI.getCategories(),
      adminAPI.getProducts(),
    ])
    users.value = usersRes.data
    categories.value = categoriesRes.data
    products.value = productsRes.data.products
  } catch (error) {
    showError(error, t('admin.failedLoad'))
  } finally {
    loading.value = false
  }
}

async function runAction(action, successText, fallbackErrorText) {
  if (busy.value) {
    return
  }
  busy.value = true
  try {
    await action()
    if (successText) {
      showSuccess(successText)
    }
  } catch (error) {
    showError(error, fallbackErrorText)
  } finally {
    busy.value = false
  }
}

async function updateRole(user, role) {
  if (user.role === role) {
    return
  }

  await runAction(
    async () => {
      const { data } = await adminAPI.updateUserRole(user.id, role)
      const index = users.value.findIndex((entry) => entry.id === user.id)
      if (index !== -1) {
        users.value[index] = data
      }
    },
    t('admin.userRoleUpdated'),
    t('admin.failedRoleUpdate'),
  )
}

async function deleteUser(user) {
  if (!confirm(t('admin.deleteUserConfirm', { email: user.email }))) {
    return
  }

  await runAction(
    async () => {
      await adminAPI.deleteUser(user.id)
      users.value = users.value.filter((entry) => entry.id !== user.id)
    },
    t('admin.userDeleted'),
    t('admin.failedUserDelete'),
  )
}

function resetCategoryForm() {
  categoryForm.value = { id: null, name: '', slug: '' }
}

function editCategory(category) {
  categoryForm.value = { ...category }
}

async function saveCategory() {
  const payload = {
    name: categoryForm.value.name.trim(),
    slug: categoryForm.value.slug.trim().toLowerCase(),
  }

  await runAction(
    async () => {
      if (categoryForm.value.id) {
        await adminAPI.updateCategory(categoryForm.value.id, payload)
      } else {
        await adminAPI.createCategory(payload)
      }
      resetCategoryForm()
      await loadData()
    },
    categoryForm.value.id ? t('admin.categoryUpdated') : t('admin.categoryCreated'),
    t('admin.failedCategorySave'),
  )
}

async function deleteCategory(category) {
  if (!confirm(t('admin.deleteCategoryConfirm', { name: localizedCategoryName(category) }))) {
    return
  }

  await runAction(
    async () => {
      await adminAPI.deleteCategory(category.id)
      await loadData()
    },
    t('admin.categoryDeleted'),
    t('admin.failedCategoryDelete'),
  )
}

function resetProductForm() {
  clearProductPreviewUrls()
  productForm.value = buildEmptyProductForm()
  if (imageInputRef.value) {
    imageInputRef.value.value = ''
  }
}

function editProduct(product) {
  clearProductPreviewUrls()
  productForm.value = {
    id: product.id,
    name: localizedProductName(product),
    description: localizedProductDescription(product) || '',
    price: Number(product.price),
    category_id: product.category_id,
    image_urls: getRawProductImages(product),
    image_files: [],
  }
  if (imageInputRef.value) {
    imageInputRef.value.value = ''
  }
}

function handleProductImageChange(event) {
  const selectedFiles = Array.from(event.target.files || [])
  if (selectedFiles.length === 0) {
    return
  }

  const existingCount = productForm.value.image_urls.length
  const alreadySelected = productForm.value.image_files.length
  const availableSlots = MAX_PRODUCT_FILES - existingCount - alreadySelected
  if (availableSlots <= 0) {
    showError(null, t('admin.uploadMax', { count: MAX_PRODUCT_FILES }))
    if (event?.target) {
      event.target.value = ''
    }
    return
  }

  if (selectedFiles.length > availableSlots) {
    showError(null, t('admin.uploadMax', { count: MAX_PRODUCT_FILES }))
  }

  const files = selectedFiles.slice(0, availableSlots)
  if (files.length === 0) {
    if (event?.target) {
      event.target.value = ''
    }
    return
  }

  productForm.value.image_files = [...productForm.value.image_files, ...files]
  productImagePreviews.value = [
    ...productImagePreviews.value,
    ...files.map((file) => URL.createObjectURL(file)),
  ]

  if (event?.target) {
    event.target.value = ''
  }
}

function removeExistingImage(index) {
  productForm.value.image_urls.splice(index, 1)
}

function removeNewImage(index) {
  const preview = productImagePreviews.value[index]
  if (typeof preview === 'string' && preview.startsWith('blob:')) {
    URL.revokeObjectURL(preview)
  }
  productImagePreviews.value.splice(index, 1)
  productForm.value.image_files.splice(index, 1)
}

async function saveProduct() {
  const payload = {
    name: productForm.value.name.trim(),
    description: productForm.value.description?.trim() || null,
    price: Number(productForm.value.price),
    category_id: productForm.value.category_id,
  }

  if (!payload.category_id || !payload.price || payload.price <= 0) {
    showError(null, t('admin.invalidProductData'))
    return
  }

  const keptImagesCount = productForm.value.image_urls.length
  const newImagesCount = productForm.value.image_files.length
  const totalImagesCount = keptImagesCount + newImagesCount

  if (!productForm.value.id && totalImagesCount === 0) {
    showError(null, t('admin.selectImageForNew'))
    return
  }

  if (productForm.value.id && totalImagesCount === 0) {
    showError(null, t('admin.productNeedAtLeastOneImage'))
    return
  }

  if (totalImagesCount > MAX_PRODUCT_FILES) {
    showError(null, t('admin.uploadMax', { count: MAX_PRODUCT_FILES }))
    return
  }

  const formData = new FormData()
  formData.append('name', payload.name)
  formData.append('description', payload.description || '')
  formData.append('price', String(payload.price))
  formData.append('category_id', String(payload.category_id))
  productForm.value.image_files.forEach((file) => formData.append('image_files', file))
  if (productForm.value.id) {
    formData.append('existing_image_urls', JSON.stringify(productForm.value.image_urls))
  }

  await runAction(
    async () => {
      if (productForm.value.id) {
        await adminAPI.updateProduct(productForm.value.id, formData)
      } else {
        await adminAPI.createProduct(formData)
      }
      resetProductForm()
      await loadData()
    },
    productForm.value.id ? t('admin.productUpdated') : t('admin.productCreated'),
    t('admin.failedProductSave'),
  )
}

async function deleteProduct(product) {
  if (!confirm(t('admin.deleteProductConfirm', { name: localizedProductName(product) }))) {
    return
  }

  await runAction(
    async () => {
      await adminAPI.deleteProduct(product.id)
      await loadData()
    },
    t('admin.productDeleted'),
    t('admin.failedProductDelete'),
  )
}

onMounted(() => {
  loadData()
})

onBeforeUnmount(() => {
  clearMessageTimer()
  clearProductPreviewUrls()
})

function onTableImageError(event) {
  event.target.src = 'https://via.placeholder.com/80x80?text=No+Image'
}

function primaryImage(product) {
  return getPrimaryProductImage(product) || 'https://via.placeholder.com/80x80?text=No+Image'
}

function productImagesCount(product) {
  return getRawProductImages(product).length
}
</script>

<style scoped>
.image-remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.78);
  color: #fff;
  font-size: 12px;
  line-height: 1;
  display: grid;
  place-items: center;
}

.image-remove-btn:hover {
  background: rgba(185, 28, 28, 0.95);
}
</style>
