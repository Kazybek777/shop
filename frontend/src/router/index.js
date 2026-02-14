import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import ProductDetailPage from '@/views/ProductDetailPage.vue'
import CartPage from '@/views/CartPage.vue'
import CheckoutPage from '@/views/CheckoutPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'
import AdminPage from '@/views/AdminPage.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: {
        title: 'Shop - Home',
      },
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: ProductDetailPage,
      meta: {
        title: 'Product Details',
      },
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartPage,
      meta: {
        title: 'Shopping Cart',
      },
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: CheckoutPage,
      meta: {
        title: 'Checkout',
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: {
        title: 'Login',
        guestOnly: true,
      },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
      meta: {
        title: 'Register',
        guestOnly: true,
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminPage,
      meta: {
        title: 'Admin Panel',
        requiresAuth: true,
        requiresAdmin: true,
      },
    },
  ],
  scrollBehavior(_, __, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  await authStore.initAuth()

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.isAdmin) {
      return { name: 'admin' }
    }
    return { name: 'home' }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'home', query: { auth: 'login', redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return { name: 'home' }
  }
})

export default router
