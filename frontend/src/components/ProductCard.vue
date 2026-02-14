<template>
  <article class="ui-card overflow-hidden">
    <router-link :to="`/product/${product.id}`" class="block group">
      <div class="aspect-square overflow-hidden relative">
        <img
          :src="imageSrc(product)"
          :alt="localizedProductName(product)"
          class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          @error="handleImageError"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent"></div>
      </div>
    </router-link>

    <div class="p-4">
      <div class="flex items-center justify-between mb-2">
        <span class="badge">{{ localizedCategoryName(product.category) }}</span>
        <span class="text-xs text-[color:var(--ink-500)]">{{ t('common.id') }} {{ product.id }}</span>
      </div>

      <router-link :to="`/product/${product.id}`">
        <h3 class="text-lg font-bold leading-tight text-[color:var(--ink-900)] hover:text-[color:var(--accent-strong)] transition-colors">
          {{ localizedProductName(product) }}
        </h3>
      </router-link>

      <div class="mt-3 mb-4 flex items-end justify-between">
        <p class="text-2xl font-extrabold text-[color:var(--ink-900)]" style="font-family: var(--font-display)">
          {{ formatCurrency(product.price) }}
        </p>
      </div>

      <button :disabled="adding" class="btn-primary w-full" @click="handleAddToCart">
        {{ adding ? t('productCard.adding') : t('productCard.addToCart') }}
      </button>

      <transition name="fade">
        <p v-if="showNotification" class="text-center text-sm mt-2 text-[color:var(--accent-strong)] font-semibold">
          {{ t('productCard.addedToCart') }}
        </p>
      </transition>
    </div>
  </article>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { getPrimaryProductImage } from '@/utils/media'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const cartStore = useCartStore()
const adding = ref(false)
const showNotification = ref(false)
const { t, formatCurrency, localizedCategoryName, localizedProductName } = useI18n()

async function handleAddToCart() {
  if (adding.value) {
    return
  }
  adding.value = true
  const success = await cartStore.addToCart(props.product.id, 1)
  if (success) {
    showNotification.value = true
    setTimeout(() => {
      showNotification.value = false
    }, 1800)
  }
  adding.value = false
}

function handleImageError(event) {
  event.target.src = 'https://via.placeholder.com/400x400?text=No+Image'
}

function imageSrc(product) {
  return getPrimaryProductImage(product) || 'https://via.placeholder.com/400x400?text=No+Image'
}
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
