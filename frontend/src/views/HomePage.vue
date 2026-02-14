<template>
  <div class="page-wrap">
    <section class="hero-panel fade-up mb-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="page-title mb-2">{{ t('home.title') }}</h1>
          <p class="page-subtitle max-w-2xl">
            {{ t('home.subtitle') }}
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <span class="stat-chip">{{ tPlural('common.products', productsStore.products.length) }}</span>
          <span class="stat-chip">{{ tPlural('common.categories', productsStore.categories.length) }}</span>
          <span class="stat-chip">{{ t('home.updatedToday') }}</span>
        </div>
      </div>
    </section>

    <div class="flex flex-col lg:flex-row gap-8">
      <aside class="w-full lg:w-72 lg:flex-shrink-0 fade-up" style="animation-delay: 0.08s">
        <CategoryFilter />
      </aside>

      <main class="flex-grow">
        <div class="mb-5 flex flex-wrap items-center justify-between gap-3 fade-up" style="animation-delay: 0.13s">
          <p class="text-[color:var(--ink-700)]">
            <strong class="text-[color:var(--ink-900)]">{{ t('home.shown', { count: productsStore.productsCount }) }}</strong>
          </p>
          <div class="flex items-center gap-2">
            <button v-if="productsStore.searchQuery" class="btn-ghost text-sm" @click="clearSearch">{{ t('home.clearSearch') }}</button>
            <button v-if="productsStore.selectedCategory" class="btn-ghost text-sm" @click="productsStore.clearCategoryFilter">
              {{ t('home.clearFilter') }}
            </button>
          </div>
        </div>

        <div v-if="productsStore.loading" class="ui-card p-12 text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--accent)]"></div>
          <p class="mt-4 text-[color:var(--ink-500)]">{{ t('home.loadingProducts') }}</p>
        </div>

        <div v-else-if="productsStore.error" class="ui-card p-8 text-center">
          <p class="text-red-600 font-semibold">{{ productsStore.error }}</p>
        </div>

        <div v-else-if="productsStore.filteredProducts.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 stagger">
          <ProductCard v-for="product in productsStore.filteredProducts" :key="product.id" :product="product" />
        </div>

        <div v-else class="ui-card p-10 text-center">
          <p class="text-lg font-semibold text-[color:var(--ink-700)]">{{ t('home.noProducts') }}</p>
          <button class="btn-secondary mt-4" @click="productsStore.clearCategoryFilter">{{ t('home.showAllProducts') }}</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import ProductCard from '@/components/ProductCard.vue'
import CategoryFilter from '@/components/CategoryFilter.vue'
import { useI18n } from '@/composables/useI18n'

const productsStore = useProductsStore()
const route = useRoute()
const router = useRouter()
const { t, tPlural } = useI18n()

function clearSearch() {
  const nextQuery = { ...route.query }
  delete nextQuery.q
  router.replace({ query: nextQuery })
}

function getSearchFromRoute() {
  return typeof route.query.q === 'string' ? route.query.q : ''
}

onMounted(async () => {
  await Promise.all([productsStore.fetchProducts(getSearchFromRoute()), productsStore.fetchCategories()])
})

watch(() => route.query.q, () => productsStore.fetchProducts(getSearchFromRoute()))
</script>
