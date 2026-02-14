<template>
  <article class="ui-card p-4 sm:p-5">
    <div class="flex flex-col sm:flex-row sm:items-center gap-4">
      <div class="w-24 h-24 rounded-xl overflow-hidden bg-white/60 flex-shrink-0">
        <img :src="imageSrc(item.image_url)" :alt="localizedItemName(item) || t('cart.unnamedProduct')" class="w-full h-full object-cover" @error="handleImageError" />
      </div>

      <div class="flex-grow">
        <h3 class="font-bold text-lg text-[color:var(--ink-900)]">{{ localizedItemName(item) || t('cart.unnamedProduct') }}</h3>
        <p class="text-sm text-[color:var(--ink-500)]">{{ formatCurrency(item.price || 0) }} {{ t('common.each') }}</p>

        <div class="mt-3 flex items-center gap-3">
          <div class="inline-flex items-center border border-[color:var(--line)] rounded-xl overflow-hidden bg-white/80">
            <button :disabled="updating" class="qty-btn" @click="decreaseQuantity">-</button>
            <span class="px-4 py-1.5 min-w-[42px] text-center font-semibold">{{ item.quantity }}</span>
            <button :disabled="updating" class="qty-btn" @click="increaseQuantity">+</button>
          </div>

          <button :disabled="updating" class="btn-ghost text-red-700 text-sm px-2 py-1" @click="handleRemove">
            {{ t('cart.remove') }}
          </button>
        </div>
      </div>

      <p class="text-xl font-extrabold text-[color:var(--ink-900)]" style="font-family: var(--font-display)">
        {{ formatCurrency(item.subtotal || Number(item.price || 0) * Number(item.quantity || 0)) }}
      </p>
    </div>
  </article>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { resolveImageUrl } from '@/utils/media'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

const cartStore = useCartStore()
const updating = ref(false)
const { t, formatCurrency, locale } = useI18n()

function localizedItemName(item) {
  if (!item) {
    return ''
  }
  if (locale.value === 'ru') {
    return item.name_ru || item.name || item.name_en || ''
  }
  return item.name_en || item.name || item.name_ru || ''
}

async function increaseQuantity() {
  updating.value = true
  await cartStore.updateQuantity(props.item.product_id, props.item.quantity + 1)
  updating.value = false
}

async function decreaseQuantity() {
  updating.value = true
  if (props.item.quantity > 1) {
    await cartStore.updateQuantity(props.item.product_id, props.item.quantity - 1)
  } else {
    await cartStore.removeFromCart(props.item.product_id)
  }
  updating.value = false
}

async function handleRemove() {
  updating.value = true
  await cartStore.removeFromCart(props.item.product_id)
  updating.value = false
}

function handleImageError(event) {
  event.target.src = 'https://via.placeholder.com/100x100?text=No+Image'
}

function imageSrc(imageUrl) {
  return resolveImageUrl(imageUrl) || 'https://via.placeholder.com/100x100?text=No+Image'
}
</script>

<style scoped>
.qty-btn {
  width: 30px;
  height: 30px;
  border: 0;
  font-weight: 800;
  color: var(--ink-700);
  background: transparent;
}

.qty-btn:hover {
  background: rgba(255, 255, 255, 0.95);
}

.qty-btn:disabled {
  opacity: 0.45;
}
</style>
