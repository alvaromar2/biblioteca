<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLoanStore } from '../stores/loanStore'
import { useBookStore } from '../stores/bookStore'

const loanStore = useLoanStore()
const bookStore = useBookStore()

const statusFilter = ref('all')
const searchQuery = ref('')

onMounted(() => {
  loanStore.fetchLoans()
})

const filteredLoans = computed(() => {
  return loanStore.loans.filter((p) => {
    if (statusFilter.value !== 'all' && p.estado !== statusFilter.value) {
      return false
    }
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim()
      return (
        String(p.id).includes(q) ||
        (p.libro_titulo || '').toLowerCase().includes(q) ||
        (p.libro_inventario || '').toLowerCase().includes(q) ||
        (p.usuario_nombre || '').toLowerCase().includes(q) ||
        (p.usuario_legajo || '').toLowerCase().includes(q)
      )
    }
    return true
  })
})

function formatDate(isoString) {
  if (!isoString) return ''
  try {
    const d = new Date(isoString)
    return d.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return isoString
  }
}

async function cambiarEstado(id, nuevoEstado) {
  const res = await loanStore.updateLoanStatus(id, nuevoEstado)
  if (res && res.success) {
    await bookStore.fetchBooks()
  } else {
    alert(res?.error || 'No se pudo actualizar el préstamo.')
  }
}

async function borrarPrestamo(id) {
  if (!confirm(`¿Eliminar el registro de préstamo #${id}?`)) return
  const res = await loanStore.deleteLoan(id)
  if (res && res.success) {
    await bookStore.fetchBooks()
  }
}
</script>

<template>
  <div class="loans-admin">
    <div class="topbar">
      <p class="subtitle">
        Aprobación de préstamos y control de devoluciones (Profesores: 15 días · Alumnos: 7 días)
      </p>
      <button type="button" class="btn btn-outline" @click="loanStore.fetchLoans()">
        🔄 Actualizar
      </button>
    </div>

    <!-- Métricas -->
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ loanStore.stats.total }}</div>
        <div class="stat-label">Total Solicitudes</div>
      </div>
      <div class="stat-card pending">
        <div class="stat-number">{{ loanStore.stats.pendientes }}</div>
        <div class="stat-label">Pendientes</div>
      </div>
      <div class="stat-card active">
        <div class="stat-number">{{ loanStore.stats.aprobados }}</div>
        <div class="stat-label">En Préstamo</div>
      </div>
      <div class="stat-card returned">
        <div class="stat-number">{{ loanStore.stats.devueltos }}</div>
        <div class="stat-label">Devueltos</div>
      </div>
    </section>

    <!-- Filtros -->
    <section class="controls-bar">
      <div class="filter-buttons">
        <button
          type="button"
          :class="['filter-btn', { active: statusFilter === 'all' }]"
          @click="statusFilter = 'all'"
        >
          Todos ({{ loanStore.stats.total }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: statusFilter === 'Pendiente' }]"
          @click="statusFilter = 'Pendiente'"
        >
          🟡 Pendientes ({{ loanStore.stats.pendientes }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: statusFilter === 'Aprobado' }]"
          @click="statusFilter = 'Aprobado'"
        >
          🔵 En Préstamo ({{ loanStore.stats.aprobados }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: statusFilter === 'Devuelto' }]"
          @click="statusFilter = 'Devuelto'"
        >
          🟢 Devueltos ({{ loanStore.stats.devueltos }})
        </button>
      </div>

      <div class="search-box">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Buscar por libro, inventario, alumno o legajo..."
        />
      </div>
    </section>

    <!-- Listado -->
    <div v-if="loanStore.loading" class="empty-state">
      Cargando solicitudes de préstamo...
    </div>

    <div v-else-if="filteredLoans.length === 0" class="empty-state">
      No hay solicitudes de préstamo para los filtros seleccionados.
    </div>

    <div v-else class="loans-list">
      <article
        v-for="item in filteredLoans"
        :key="item.id"
        :class="['loan-card', `state-${item.estado.toLowerCase()}`]"
      >
        <div class="loan-top">
          <div class="loan-title-group">
            <span class="loan-id">Préstamo #{{ item.id }}</span>
            <span class="badge-inv">{{ item.libro_inventario }}</span>
            <span class="badge-uni">{{ item.libro_universidad }}</span>
            <span :class="['badge-role', item.usuario_rol]">
              {{ item.usuario_rol === 'profesor' ? '👨‍🏫 Profesor (15 días)' : '🎓 Alumno (7 días)' }}
            </span>
          </div>

          <span :class="['badge-status', item.estado.toLowerCase()]">
            {{ item.estado }}
          </span>
        </div>

        <h3 class="book-name">{{ item.libro_titulo || 'Ejemplar #' + item.libro_id }}</h3>

        <div class="loan-meta">
          <span>👤 <strong>{{ item.usuario_nombre }}</strong></span>
          <span>🆔 Legajo: <strong>{{ item.usuario_legajo || 'S/D' }}</strong></span>
          <span>✉️ {{ item.usuario_email }}</span>
          <span>📅 Solicitado: {{ formatDate(item.fecha_solicitud) }}</span>
          <span v-if="item.fecha_devolucion">
            ✅ Devuelto: {{ formatDate(item.fecha_devolucion) }}
          </span>
        </div>

        <div class="loan-actions">
          <button
            v-if="item.estado === 'Pendiente'"
            type="button"
            class="btn btn-approve"
            @click="cambiarEstado(item.id, 'Aprobado')"
          >
            ✓ Aprobar entrega
          </button>

          <button
            v-if="item.estado === 'Pendiente'"
            type="button"
            class="btn btn-reject"
            @click="cambiarEstado(item.id, 'Rechazado')"
          >
            ✕ Rechazar
          </button>

          <button
            v-if="item.estado === 'Aprobado'"
            type="button"
            class="btn btn-return"
            @click="cambiarEstado(item.id, 'Devuelto')"
          >
            ↩ Registrar devolución
          </button>

          <button
            type="button"
            class="btn btn-danger-outline"
            title="Eliminar registro"
            @click="borrarPrestamo(item.id)"
          >
            🗑️
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.loans-admin {
  margin-top: 1.25rem;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.subtitle {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #004b87;
}

.stat-card.pending .stat-number { color: #d97706; }
.stat-card.active .stat-number { color: #2563eb; }
.stat-card.returned .stat-number { color: #16a34a; }

.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 600;
  margin-top: 0.25rem;
}

.controls-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.85rem;
  margin-bottom: 1.25rem;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.filter-btn {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  cursor: pointer;
}

.filter-btn.active {
  background: #004b87;
  color: #ffffff;
  border-color: #004b87;
}

.search-box {
  flex: 1;
  min-width: 240px;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.88rem;
  box-sizing: border-box;
}

.loans-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.loan-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.loan-card.state-pendiente { border-left: 5px solid #d97706; }
.loan-card.state-aprobado { border-left: 5px solid #2563eb; }
.loan-card.state-devuelto { border-left: 5px solid #16a34a; opacity: 0.9; }
.loan-card.state-rechazado { border-left: 5px solid #dc2626; opacity: 0.8; }

.loan-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.loan-title-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.loan-id {
  font-weight: 700;
  color: #004b87;
}

.badge-inv {
  background: #f1f5f9;
  font-family: monospace;
  font-size: 0.78rem;
  padding: 0.18rem 0.5rem;
  border-radius: 5px;
}

.badge-uni {
  background: #0f3d6e;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.18rem 0.5rem;
  border-radius: 5px;
}

.badge-role {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}

.badge-role.profesor { background: #fef3c7; color: #92400e; }
.badge-role.alumno { background: #dbeafe; color: #1e40af; }

.badge-status {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.22rem 0.65rem;
  border-radius: 999px;
}

.badge-status.pendiente { background: #fef3c7; color: #92400e; }
.badge-status.aprobado { background: #dbeafe; color: #1e40af; }
.badge-status.devuelto { background: #dcfce7; color: #166534; }
.badge-status.rechazado { background: #fee2e2; color: #991b1b; }

.book-name {
  margin: 0;
  font-size: 1.05rem;
  color: #0f172a;
}

.loan-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.82rem;
  color: #475569;
  background: #f8fafc;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
}

.loan-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.6rem;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 0.45rem 0.85rem;
  border-radius: 7px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-approve { background: #16a34a; color: #ffffff; }
.btn-return { background: #2563eb; color: #ffffff; }
.btn-reject { background: #f1f5f9; color: #991b1b; border: 1px solid #fecaca; }
.btn-outline { background: #ffffff; border: 1px solid #cbd5e1; color: #0f172a; }
.btn-danger-outline { background: transparent; border: 1px solid #fee2e2; color: #dc2626; }

.empty-state {
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 2.5rem;
  text-align: center;
  color: #64748b;
}
</style>