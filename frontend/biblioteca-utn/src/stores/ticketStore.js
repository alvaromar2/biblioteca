import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api'

export const useTicketStore = defineStore('tickets', () => {
  const tickets = ref([])
  const loading = ref(false)
  const error = ref(null)

  const statusFilter = ref('all')
  const priorityFilter = ref('all')
  const searchQuery = ref('')

  const stats = computed(() => {
    const list = tickets.value
    return {
      total: list.length,
      pendientes: list.filter((t) => t.estado === 'Pendiente').length,
      enProceso: list.filter((t) => t.estado === 'En proceso').length,
      solucionados: list.filter((t) => t.estado === 'Solucionado').length
    }
  })

  const filteredTickets = computed(() => {
    return tickets.value.filter((t) => {
      if (statusFilter.value !== 'all' && t.estado !== statusFilter.value) {
        return false
      }
      if (
        priorityFilter.value !== 'all' &&
        String(t.prioridad || '').toLowerCase() !== priorityFilter.value
      ) {
        return false
      }
      if (searchQuery.value.trim()) {
        const q = searchQuery.value.toLowerCase().trim()
        return (
          String(t.id).includes(q) ||
          (t.nombre || '').toLowerCase().includes(q) ||
          (t.legajo || '').toLowerCase().includes(q) ||
          (t.email || '').toLowerCase().includes(q) ||
          (t.categoria || '').toLowerCase().includes(q) ||
          (t.descripcion || '').toLowerCase().includes(q)
        )
      }
      return true
    })
  })

  async function fetchTickets() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch(`${API_BASE}/tickets`)
      const data = await res.json()
      if (data.success) {
        tickets.value = data.tickets
      } else {
        error.value = data.error || 'No se pudieron cargar los tickets.'
      }
    } catch {
      error.value = 'No se pudo conectar con el servidor Flask.'
    } finally {
      loading.value = false
    }
  }

  async function createTicket(payload) {
    const res = await fetch(`${API_BASE}/tickets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    if (data.success) {
      await fetchTickets()
    }
    return data
  }

  async function updateTicketStatus(id, estado) {
    try {
      const res = await fetch(`${API_BASE}/tickets/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado })
      })
      const data = await res.json()
      if (data.success) {
        const item = tickets.value.find((t) => t.id === id)
        if (item) item.estado = estado
      } else {
        alert('Error al actualizar estado: ' + data.error)
      }
    } catch {
      alert('Error de conexión al actualizar el ticket.')
    }
  }

  async function deleteTicket(id) {
    try {
      const res = await fetch(`${API_BASE}/tickets/${id}`, {
        method: 'DELETE'
      })
      const data = await res.json()
      if (data.success) {
        tickets.value = tickets.value.filter((t) => t.id !== id)
      } else {
        alert('Error al eliminar ticket: ' + data.error)
      }
    } catch {
      alert('Error de conexión al eliminar el ticket.')
    }
  }

  function exportToCSV() {
    if (!tickets.value.length) {
      alert('No hay tickets para exportar.')
      return
    }
    let csv = 'ID,Nombre,Legajo,Email,Prioridad,Categoria,Estado,Adjunto,Fecha_Creacion,Descripcion\r\n'
    tickets.value.forEach((t) => {
      const desc = `"${(t.descripcion || '').replace(/"/g, '""').replace(/\r?\n/g, ' ')}"`
      const tieneAdjunto = t.imagen_base64 ? 'Sí' : 'No'
      csv += `${t.id},"${t.nombre || ''}","${t.legajo || ''}","${t.email || ''}",${t.prioridad || 'media'},"${t.categoria || ''}",${t.estado},${tieneAdjunto},"${t.fecha_creacion || ''}",${desc}\r\n`
    })

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `reporte_tickets_utn_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return {
    tickets,
    loading,
    error,
    statusFilter,
    priorityFilter,
    searchQuery,
    stats,
    filteredTickets,
    fetchTickets,
    createTicket,
    updateTicketStatus,
    deleteTicket,
    exportToCSV
  }
})