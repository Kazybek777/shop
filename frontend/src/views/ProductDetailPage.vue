<template>
  <div class="page-wrap">
    <button class="btn-ghost mb-6" @click="router.push('/')">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      {{ t('productDetail.backToCatalog') }}
    </button>

    <div v-if="loading" class="ui-card p-14 text-center">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--accent)]"></div>
      <p class="mt-4 text-[color:var(--ink-500)]">{{ t('productDetail.loadingProduct') }}</p>
    </div>

    <div v-else-if="error" class="ui-card p-10 text-center">
      <p class="text-red-600 font-semibold text-lg">{{ error }}</p>
      <button class="btn-secondary mt-5" @click="router.push('/')">{{ t('productDetail.returnToCatalog') }}</button>
    </div>

    <article v-else-if="product" class="ui-card overflow-hidden fade-up">
      <div class="grid grid-cols-1 lg:grid-cols-2">
        <div class="relative overflow-hidden bg-white/60 p-4 sm:p-5">
          <div class="relative overflow-hidden rounded-2xl border border-[color:var(--line)] bg-white/80 aspect-square">
            <img
              :src="currentImageSrc()"
              :alt="localizedProductName(product)"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <div class="absolute left-3 top-3 badge">{{ localizedCategoryName(product.category) }}</div>
          </div>

          <div v-if="galleryImages.length > 1" class="mt-4 grid grid-cols-5 gap-2">
            <button
              v-for="(image, index) in galleryImages"
              :key="`${product.id}-image-${index}`"
              type="button"
              class="relative overflow-hidden rounded-xl border bg-white/80 transition"
              :class="selectedImage === image ? 'border-[color:var(--accent)] shadow-sm' : 'border-[color:var(--line)] hover:border-[color:var(--line-strong)]'"
              @click="selectedImage = image"
            >
              <img :src="image" :alt="`${localizedProductName(product)} ${index + 1}`" class="h-16 w-full object-cover" />
            </button>
          </div>
        </div>

        <div class="p-6 sm:p-8">
          <h1 class="page-title !text-3xl sm:!text-4xl mb-3">{{ localizedProductName(product) }}</h1>
          <p class="text-3xl font-extrabold mb-5 text-[color:var(--ink-900)]" style="font-family: var(--font-display)">
            {{ formatCurrency(product.price) }}
          </p>

          <div class="ui-card-soft p-4 mb-6">
            <p class="text-sm uppercase tracking-wide text-[color:var(--ink-500)] mb-2">{{ t('productDetail.description') }}</p>
            <p class="text-[color:var(--ink-700)] leading-relaxed">
              {{ localizedProductDescription(product) || t('common.noDescription') }}
            </p>
          </div>

          <button :disabled="adding" class="btn-primary w-full text-base py-3.5" @click="handleAddToCart">
            {{ adding ? t('productDetail.addingToCart') : t('productDetail.addToCart') }}
          </button>

          <transition name="fade">
            <p v-if="showNotification" class="mt-3 text-center font-semibold text-[color:var(--accent-strong)]">
              {{ t('productDetail.addedToCart') }}
            </p>
          </transition>

          <div class="mt-8 pt-4 border-t border-[color:var(--line)] text-sm text-[color:var(--ink-500)]">
            <p>{{ t('productDetail.productId') }}: {{ product.id }}</p>
            <p>{{ t('productDetail.addedDate') }}: {{ formatDate(product.created_at) }}</p>
          </div>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'
import { getPrimaryProductImage, getProductImages } from '@/utils/media'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()
const cartStore = useCartStore()

const product = ref(null)
const loading = ref(false)
const error = ref('')
const adding = ref(false)
const showNotification = ref(false)
const selectedImage = ref('')
const { t, formatCurrency, formatDate, localizedCategoryName, localizedProductDescription, localizedProductName } = useI18n()

const galleryImages = computed(() => getProductImages(product.value))

async function loadProduct() {
  loading.value = true
  error.value = ''

  try {
    const productId = Number(route.params.id)
    if (!Number.isInteger(productId) || productId <= 0) {
      throw new Error('Invalid product id')
    }
    product.value = await productsStore.fetchProductById(productId)
    selectedImage.value = getPrimaryProductImage(product.value) || ''
  } catch {
    error.value = t('productDetail.productNotFound')
    product.value = null
    selectedImage.value = ''
  } finally {
    loading.value = false
  }
}

async function handleAddToCart() {
  if (!product.value || adding.value) {
    return
  }

  adding.value = true
  const success = await cartStore.addToCart(product.value.id, 1)
  if (success) {
    showNotification.value = true
    setTimeout(() => {
      showNotification.value = false
    }, 2200)
  }
  adding.value = false
}

function handleImageError(event) {
  event.target.src = 'https://via.placeholder.com/700x700?text=No+Image'
}

function currentImageSrc() {
  return selectedImage.value || getPrimaryProductImage(product.value) || 'https://via.placeholder.com/700x700?text=No+Image'
}

onMounted(loadProduct)

watch(
  () => route.params.id,
  () => {
    loadProduct()
  },
)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
