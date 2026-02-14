<template>
  <div class="page-wrap">
    <div class="mb-8 fade-up">
      <h1 class="page-title mb-2">{{ t('cart.title') }}</h1>
      <p class="page-subtitle">{{ t('cart.subtitle') }}</p>
    </div>

    <div v-if="cartStore.loading" class="ui-card p-14 text-center">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--accent)]"></div>
      <p class="mt-4 text-[color:var(--ink-500)]">{{ t('cart.loading') }}</p>
    </div>

    <div v-else-if="cartStore.error" class="ui-card p-10 text-center">
      <p class="text-red-600 text-lg font-semibold mb-6">{{ cartStore.error }}</p>
      <router-link to="/" class="btn-secondary">{{ t('common.continueShopping') }}</router-link>
    </div>

    <div v-else-if="!cartStore.hasItems" class="ui-card p-12 text-center">
      <h2 class="text-2xl font-bold mb-3">{{ t('cart.emptyTitle') }}</h2>
      <p class="text-[color:var(--ink-500)] mb-7">{{ t('cart.emptySubtitle') }}</p>
      <router-link to="/" class="btn-primary">{{ t('cart.goCatalog') }}</router-link>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 fade-up">
      <section class="lg:col-span-2 space-y-4 stagger">
        <CartItem v-for="item in cartStore.cartDetails?.items" :key="item.product_id" :item="item" />
      </section>

      <aside class="lg:col-span-1">
        <div class="ui-card p-6 sticky top-24">
          <h2 class="text-2xl font-bold mb-6" style="font-family: var(--font-display)">{{ t('cart.orderSummary') }}</h2>

          <div class="space-y-4 mb-6 text-[color:var(--ink-700)]">
            <div class="flex justify-between">
              <span>{{ t('cart.items', { count: cartStore.cartDetails?.items_count || 0 }) }}</span>
              <span>{{ formatCurrency(cartStore.totalPrice) }}</span>
            </div>
            <div class="flex justify-between">
              <span>{{ t('cart.shipping') }}</span>
              <span class="text-[color:var(--accent-strong)] font-semibold">{{ t('common.free') }}</span>
            </div>
          </div>

          <div class="border-t border-[color:var(--line)] pt-4 mb-6 flex justify-between text-xl font-bold">
            <span>{{ t('cart.total') }}</span>
            <span>{{ formatCurrency(cartStore.totalPrice) }}</span>
          </div>

          <button class="btn-primary w-full mb-3" @click="handleCheckout">{{ t('cart.proceedCheckout') }}</button>
          <router-link to="/" class="btn-secondary w-full mb-2">{{ t('common.continueShopping') }}</router-link>
          <button class="btn-ghost w-full text-red-700" @click="handleClearCart">{{ t('cart.clearCart') }}</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/CartItem.vue'
import { useI18n } from '@/composables/useI18n'

const cartStore = useCartStore()
const router = useRouter()
const { t, formatCurrency } = useI18n()

function handleCheckout() {
  router.push('/checkout')
}

function handleClearCart() {
  if (confirm(t('cart.clearConfirm'))) {
    cartStore.clearCart()
  }
}

onMounted(async () => {
  await cartStore.fetchCartDetails()
})
</script>
