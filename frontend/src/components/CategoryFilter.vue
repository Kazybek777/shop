<template>
  <div class="ui-card p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="font-bold text-lg" style="font-family: var(--font-display)">{{ t('filters.categories') }}</h2>
      <span class="badge">{{ productsStore.categories.length }}</span>
    </div>

    <ul class="space-y-2">
      <li>
        <button
          :class="[
            'filter-item',
            !productsStore.selectedCategory ? 'filter-item--active' : '',
          ]"
          @click="selectCategory(null)"
        >
          <span>{{ t('filters.allCategories') }}</span>
          <strong>{{ totalProductsCount }}</strong>
        </button>
      </li>

      <li v-for="category in productsStore.categories" :key="category.id">
        <button
          :class="[
            'filter-item',
            productsStore.selectedCategory === category.id ? 'filter-item--active' : '',
          ]"
          @click="selectCategory(category.id)"
        >
          <span>{{ localizedCategoryName(category) }}</span>
          <strong>{{ getCategoryCount(category.id) }}</strong>
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useProductsStore } from '@/stores/products'
import { useI18n } from '@/composables/useI18n'

const productsStore = useProductsStore()
const { t, localizedCategoryName } = useI18n()

const totalProductsCount = computed(() => productsStore.products.length)

function getCategoryCount(categoryId) {
  return productsStore.products.filter((product) => product.category_id === categoryId).length
}

function selectCategory(categoryId) {
  if (categoryId === null) {
    productsStore.clearCategoryFilter()
    return
  }
  productsStore.setCategory(categoryId)
}
</script>

<style scoped>
.filter-item {
  width: 100%;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.62rem 0.72rem;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.7);
  color: var(--ink-700);
  transition: all 0.2s ease;
}

.filter-item:hover {
  border-color: var(--line);
  background: #fff;
}

.filter-item strong {
  color: var(--ink-500);
  font-size: 0.82rem;
}

.filter-item--active {
  border-color: rgba(15, 118, 110, 0.2);
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.filter-item--active strong {
  color: var(--accent-strong);
}
</style>
