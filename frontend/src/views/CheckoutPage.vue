<template>
  <main class="page-wrap">
    <div class="mb-8 fade-up">
      <h1 class="page-title mb-2">{{ t('checkout.title') }}</h1>
      <p class="page-subtitle">{{ t('checkout.subtitle') }}</p>
    </div>

    <section v-if="orderDone" class="ui-card p-8 sm:p-10 text-center fade-up">
      <h2 class="text-3xl font-bold mb-3" style="font-family: var(--font-display)">{{ t('checkout.successTitle') }}</h2>
      <p class="text-[color:var(--ink-600)] mb-6">{{ t('checkout.successText') }}</p>
      <div class="flex flex-wrap justify-center gap-3">
        <RouterLink to="/" class="btn-primary">{{ t('checkout.goCatalog') }}</RouterLink>
        <RouterLink to="/cart" class="btn-secondary">{{ t('checkout.backToCart') }}</RouterLink>
      </div>
    </section>

    <section v-else-if="cartStore.loading" class="ui-card p-14 text-center">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--accent)]"></div>
      <p class="mt-4 text-[color:var(--ink-500)]">{{ t('cart.loading') }}</p>
    </section>

    <section v-else-if="!hasItems" class="ui-card p-10 text-center fade-up">
      <h2 class="text-2xl font-bold mb-3">{{ t('checkout.emptyTitle') }}</h2>
      <p class="text-[color:var(--ink-500)] mb-6">{{ t('checkout.emptySubtitle') }}</p>
      <RouterLink to="/cart" class="btn-primary">{{ t('checkout.backToCart') }}</RouterLink>
    </section>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 fade-up">
      <form id="checkout-form" class="lg:col-span-2 ui-card p-5 sm:p-6 space-y-5" @submit.prevent="submitOrder">
        <section>
          <h2 class="text-xl font-bold mb-3" style="font-family: var(--font-display)">{{ t('checkout.contactInfo') }}</h2>
          <div class="grid sm:grid-cols-2 gap-3">
            <label class="block">
              <span class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('checkout.fullName') }}</span>
              <input v-model.trim="form.full_name" type="text" required minlength="2" class="field" />
            </label>
            <label class="block">
              <span class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('checkout.email') }}</span>
              <input v-model.trim="form.email" type="email" required class="field" />
            </label>
            <label class="block sm:col-span-2">
              <span class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('checkout.phone') }}</span>
              <input v-model.trim="form.phone" type="tel" required class="field" />
            </label>
          </div>
        </section>

        <section>
          <h2 class="text-xl font-bold mb-3" style="font-family: var(--font-display)">{{ t('checkout.deliveryInfo') }}</h2>
          <div class="grid sm:grid-cols-2 gap-3">
            <label class="block">
              <span class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('checkout.city') }}</span>
              <input v-model.trim="form.city" type="text" required class="field" />
            </label>
            <label class="block sm:col-span-2">
              <span class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('checkout.address') }}</span>
              <input v-model.trim="form.address" type="text" required class="field" />
            </label>
            <label class="block sm:col-span-2">
              <span class="block text-sm font-semibold text-[color:var(--ink-700)] mb-1.5">{{ t('checkout.comment') }}</span>
              <textarea v-model.trim="form.comment" rows="3" class="field-textarea"></textarea>
            </label>
          </div>
        </section>

        <section>
          <h2 class="text-xl font-bold mb-3" style="font-family: var(--font-display)">{{ t('checkout.paymentMethod') }}</h2>
          <div class="grid sm:grid-cols-3 gap-3">
            <label class="ui-card-soft px-3 py-2 flex items-center gap-2 cursor-pointer">
              <input v-model="form.payment_method" type="radio" value="cash" />
              <span>{{ t('checkout.paymentCash') }}</span>
            </label>
            <label class="ui-card-soft px-3 py-2 flex items-center gap-2 cursor-pointer">
              <input v-model="form.payment_method" type="radio" value="card" />
              <span>{{ t('checkout.paymentCard') }}</span>
            </label>
            <label class="ui-card-soft px-3 py-2 flex items-center gap-2 cursor-pointer">
              <input v-model="form.payment_method" type="radio" value="online" />
              <span>{{ t('checkout.paymentOnline') }}</span>
            </label>
          </div>
        </section>
      </form>

      <aside class="lg:col-span-1">
        <div class="ui-card p-5 sticky top-24">
          <h2 class="text-xl font-bold mb-4" style="font-family: var(--font-display)">{{ t('checkout.summary') }}</h2>

          <div class="space-y-3 max-h-[280px] overflow-auto pr-1 mb-4">
            <article
              v-for="item in cartStore.cartDetails?.items || []"
              :key="`checkout-item-${item.product_id}`"
              class="flex items-start gap-3 pb-3 border-b border-[color:var(--line)]/60"
            >
              <img
                :src="resolveImageUrl(item.image_url) || 'https://via.placeholder.com/64x64?text=No+Image'"
                :alt="localizedItemName(item)"
                class="w-14 h-14 rounded-lg object-cover border border-[color:var(--line)]"
              />
              <div class="flex-1 min-w-0">
                <p class="font-semibold text-sm truncate">{{ localizedItemName(item) }}</p>
                <p class="text-xs text-[color:var(--ink-500)]">x{{ item.quantity }}</p>
              </div>
              <p class="text-sm font-semibold">{{ formatCurrency(item.subtotal) }}</p>
            </article>
          </div>

          <div class="space-y-3 text-sm mb-4">
            <div class="flex justify-between">
              <span>{{ t('cart.items', { count: cartStore.cartDetails?.items_count || 0 }) }}</span>
              <span>{{ formatCurrency(cartStore.totalPrice) }}</span>
            </div>
            <div class="flex justify-between">
              <span>{{ t('cart.shipping') }}</span>
              <span>{{ t('common.free') }}</span>
            </div>
          </div>

          <div class="border-t border-[color:var(--line)] pt-4 mb-4 flex justify-between font-bold text-lg">
            <span>{{ t('cart.total') }}</span>
            <span>{{ formatCurrency(cartStore.totalPrice) }}</span>
          </div>

          <button type="submit" form="checkout-form" class="btn-primary w-full" :disabled="placingOrder">
            {{ placingOrder ? t('checkout.placingOrder') : t('checkout.placeOrder') }}
          </button>
        </div>
      </aside>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { resolveImageUrl } from '@/utils/media'
import { useI18n } from '@/composables/useI18n'

const cartStore = useCartStore()
const { t, formatCurrency, locale } = useI18n()

const placingOrder = ref(false)
const orderDone = ref(false)

const form = ref({
  full_name: '',
  email: '',
  phone: '',
  city: '',
  address: '',
  comment: '',
  payment_method: 'cash',
})

const hasItems = computed(() => (cartStore.cartDetails?.items?.length || 0) > 0)

function localizedItemName(item) {
  if (!item) {
    return ''
  }
  if (locale.value === 'ru') {
    return item.name_ru || item.name || item.name_en || t('cart.unnamedProduct')
  }
  return item.name_en || item.name || item.name_ru || t('cart.unnamedProduct')
}

async function submitOrder() {
  if (placingOrder.value || !hasItems.value) {
    return
  }
  placingOrder.value = true
  await new Promise((resolve) => setTimeout(resolve, 800))
  cartStore.clearCart()
  placingOrder.value = false
  orderDone.value = true
}

onMounted(async () => {
  await cartStore.fetchCartDetails()
})
</script>
