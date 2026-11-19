import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const routes = [
  {
    path: '/',
    name: 'Catalog',
    component: () => import('../views/CatalogView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAdmin: true }
  },
  {
    path: '/soporte',
    name: 'Support',
    component: () => import('../views/SupportView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next(authStore.isAuthenticated ? { name: 'Catalog' } : { name: 'Login' })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next(authStore.isAdmin ? { name: 'Admin' } : { name: 'Catalog' })
  } else {
    next()
  }
})

export default router