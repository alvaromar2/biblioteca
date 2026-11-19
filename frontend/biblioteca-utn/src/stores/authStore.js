import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api'
const STORAGE_KEY = 'utn_auth_user'

function loadUser() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref(loadUser())
  const loading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => Boolean(user.value))
  const isAlumno = computed(() => user.value?.rol === 'alumno')
  const isProfesor = computed(() => user.value?.rol === 'profesor')
  const isAdmin = computed(() => user.value?.rol === 'admin')

  function setUser(userData) {
    user.value = userData
    if (userData) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(userData))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  async function register(payload) {
    loading.value = true
    error.value = ''
    try {
      const res = await fetch(`${API_BASE}/auth/registro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (data.success) {
        setUser(data.user)
        return true
      } else {
        error.value = data.error || 'No se pudo completar el registro.'
        return false
      }
    } catch {
      error.value = 'No se pudo conectar con el servidor Flask.'
      return false
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = ''
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (data.success) {
        setUser(data.user)
        return true
      } else {
        error.value = data.error || 'Credenciales inválidas.'
        return false
      }
    } catch {
      error.value = 'No se pudo conectar con el servidor Flask.'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    setUser(null)
    error.value = ''
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isAlumno,
    isProfesor,
    isAdmin,
    register,
    login,
    logout
  }
})