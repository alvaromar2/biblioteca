import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api'

export const useLoanStore = defineStore('loans', () => {
  const loans = ref([])
  const loading = ref(false)
  const error = ref(null)

  const stats = computed(() => {
    const list = loans.value
    return {
      total: list.length,
      pendientes: list.filter((p) => p.estado === 'Pendiente').length,
      aprobados: list.filter((p) => p.estado === 'Aprobado').length,
      devueltos: list.filter((p) => p.estado === 'Devuelto').length
    }
  })

  async function fetchLoans() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${API_BASE}/prestamos`)
      const data = await res.json()
      if (data.success) {
        loans.value = data.prestamos
      } else {
        error.value = data.error || 'No se pudieron cargar los préstamos.'
      }
    } catch {
      error.value = 'No se pudo conectar con el servidor Flask.'
    } finally {
      loading.value = false
    }
  }

  async function requestLoan(payload) {
    const res = await fetch(`${API_BASE}/prestamos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.success) {
      await fetchLoans()
    }
    return data
  }

  async function updateLoanStatus(id, estado) {
    const res = await fetch(`${API_BASE}/prestamos/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ estado })
    })
    const data = await res.json()
    if (data.success) {
      await fetchLoans()
    }
    return data
  }

  async function deleteLoan(id) {
    const res = await fetch(`${API_BASE}/prestamos/${id}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      loans.value = loans.value.filter((p) => p.id !== id)
    }
    return data
  }

  return {
    loans,
    loading,
    error,
    stats,
    fetchLoans,
    requestLoan,
    updateLoanStatus,
    deleteLoan
  }
})