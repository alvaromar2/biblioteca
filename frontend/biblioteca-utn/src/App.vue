<template>
  <div id="app-container">
    <header class="main-header">
      <div class="header-content">
        <router-link to="/" class="brand-link">
          <img :src="logoUrl" alt="Biblioteca UTN Logo" class="header-logo" />
        </router-link>

        <nav class="nav-links">
          <router-link to="/" class="nav-item">Catálogo</router-link>
          <router-link to="/soporte" class="nav-item">Soporte</router-link>

          <template v-if="authStore.isAuthenticated">
            <router-link v-if="authStore.isAdmin" to="/admin" class="nav-item">
              Panel Admin
            </router-link>

            <div class="user-pill" :title="`${authStore.user?.email} (${authStore.user?.universidad || 'UTN'})`">
              <span class="user-icon">
                {{ authStore.isProfesor ? '👨‍🏫' : authStore.isAlumno ? '🎓' : '🛡️' }}
              </span>
              <span class="user-name">{{ authStore.user?.nombre }}</span>
              <span :class="['role-tag', `role-${authStore.user?.rol}`]">
                {{ rolLegible }}
              </span>
            </div>

            <button @click="handleLogout" class="btn-logout">Cerrar Sesión</button>
          </template>

          <template v-else>
            <router-link to="/login" class="nav-item btn-login">
              Ingresar / Registrarse
            </router-link>
          </template>
        </nav>
      </div>
    </header>

    <main class="main-body">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/authStore'
import { useBookStore } from './stores/bookStore'
import logoUrl from './assets/logo.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const bookStore = useBookStore()

const rolLegible = computed(() => {
  const rol = authStore.user?.rol
  if (rol === 'profesor') return 'Profesor'
  if (rol === 'alumno') return 'Alumno'
  if (rol === 'admin') return 'Admin'
  return ''
})

function handleLogout() {
  authStore.logout()
  if (route.meta.requiresAdmin) {
    router.push({ name: 'Login' })
  } else {
    router.push({ name: 'Catalog' })
  }
}

onMounted(() => {
  bookStore.fetchBooks()
})
</script>

<style scoped>
.main-header {
  background-color: var(--utn-blue);
  padding: 0.6rem 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 51, 102, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.header-logo {
  height: 46px;
  width: auto;
  background-color: #ffffff;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  object-fit: contain;
}

.nav-links {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.7rem;
}

.nav-item {
  color: #dceaff;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-sm);
}

.nav-item:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.1);
}

.router-link-exact-active:not(.brand-link) {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.user-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: #ffffff;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.84rem;
}

.user-name {
  font-weight: 600;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  letter-spacing: 0.03em;
}

.role-alumno {
  background: #dbeafe;
  color: #1e40af;
}

.role-profesor {
  background: #fef3c7;
  color: #92400e;
}

.role-admin {
  background: #dcfce7;
  color: #166534;
}

.btn-login {
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.btn-logout {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-logout:hover {
  background: #bd2130;
}

.main-body {
  max-width: 1100px;
  margin: 1.8rem auto;
  padding: 0 1rem;
}
</style>