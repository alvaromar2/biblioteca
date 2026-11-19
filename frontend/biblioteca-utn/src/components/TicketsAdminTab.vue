<script setup>
import { ref, onMounted } from 'vue'
import { useTicketStore } from '../stores/ticketStore'

const ticketStore = useTicketStore()
const imagenAmpliada = ref(null)

const typeIcons = {
  'Computadora de préstamo': '💻',
  'Impresora o escáner': '🖨️',
  'Conexión Wi-Fi': '📶',
  'Acceso a la cuenta o portal': '🔑',
  'Sugerencia bibliográfica (Cátedra)': '📚',
  Otro: '📌'
}

onMounted(() => {
  ticketStore.fetchTickets()
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

function getStatusClass(estado) {
  if (estado === 'Pendiente') return 'pendiente'
  if (estado === 'En proceso') return 'proceso'
  return 'solucionado'
}

function getPriorityClass(prioridad) {
  const p = String(prioridad || 'media').toLowerCase()
  if (p === 'alta') return 'prio-alta'
  if (p === 'baja') return 'prio-baja'
  return 'prio-media'
}

function confirmDelete(id) {
  if (confirm(`¿Seguro que deseas eliminar el ticket #${id}?`)) {
    ticketStore.deleteTicket(id)
  }
}
</script>

<template>
  <div class="tickets-admin-wrapper">
    <div class="tickets-topbar">
      <p class="tickets-subtitle">
        Monitoreo de solicitudes técnicas y sugerencias bibliográficas de cátedra
      </p>
      <div class="tickets-top-actions">
        <button
          type="button"
          class="btn btn-outline"
          :disabled="ticketStore.loading"
          @click="ticketStore.fetchTickets()"
        >
          <span>🔄</span> Actualizar
        </button>
        <button
          type="button"
          class="btn btn-outline"
          @click="ticketStore.exportToCSV()"
        >
          <span>📥</span> Exportar CSV
        </button>
      </div>
    </div>

    <!-- Grilla de Métricas -->
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ ticketStore.stats.total }}</div>
        <div class="stat-label">Total Tickets</div>
      </div>
      <div class="stat-card pending">
        <div class="stat-number">{{ ticketStore.stats.pendientes }}</div>
        <div class="stat-label">Pendientes</div>
      </div>
      <div class="stat-card in-process">
        <div class="stat-number">{{ ticketStore.stats.enProceso }}</div>
        <div class="stat-label">En Proceso</div>
      </div>
      <div class="stat-card solved">
        <div class="stat-number">{{ ticketStore.stats.solucionados }}</div>
        <div class="stat-label">Solucionados</div>
      </div>
    </section>

    <!-- Barra de controles -->
    <section class="controls-bar">
      <div class="filter-buttons">
        <button
          type="button"
          :class="['filter-btn', { active: ticketStore.statusFilter === 'all' }]"
          @click="ticketStore.statusFilter = 'all'"
        >
          Todos ({{ ticketStore.stats.total }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: ticketStore.statusFilter === 'Pendiente' }]"
          @click="ticketStore.statusFilter = 'Pendiente'"
        >
          🟡 Pendientes ({{ ticketStore.stats.pendientes }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: ticketStore.statusFilter === 'En proceso' }]"
          @click="ticketStore.statusFilter = 'En proceso'"
        >
          🔵 En proceso ({{ ticketStore.stats.enProceso }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: ticketStore.statusFilter === 'Solucionado' }]"
          @click="ticketStore.statusFilter = 'Solucionado'"
        >
          🟢 Solucionados ({{ ticketStore.stats.solucionados }})
        </button>
      </div>

      <div class="search-controls">
        <div class="search-box">
          <input
            v-model="ticketStore.searchQuery"
            type="search"
            placeholder="Buscar por ID, nombre, legajo o texto..."
          />
        </div>
        <select v-model="ticketStore.priorityFilter" class="select-priority">
          <option value="all">Todas las prioridades</option>
          <option value="alta">🔴 Alta</option>
          <option value="media">🟡 Media</option>
          <option value="baja">🟢 Baja</option>
        </select>
      </div>
    </section>

    <!-- Estados -->
    <div v-if="ticketStore.loading" class="empty-state">
      <p>Cargando tickets desde la base de datos...</p>
    </div>

    <div v-else-if="ticketStore.error" class="empty-state">
      <p>{{ ticketStore.error }}</p>
    </div>

    <div v-else-if="ticketStore.filteredTickets.length === 0" class="empty-state">
      <div class="empty-state-icon">📋</div>
      <p>No hay tickets para mostrar con los filtros actuales.</p>
    </div>

    <!-- Lista de tickets -->
    <section v-else class="tickets-list">
      <article
        v-for="ticket in ticketStore.filteredTickets"
        :key="ticket.id"
        :class="['ticket-card', `status-${getStatusClass(ticket.estado)}`]"
      >
        <div class="ticket-header">
          <div class="ticket-folio">
            <span>Ticket #{{ ticket.id }}</span>
            <span class="badge badge-tipo">
              {{ typeIcons[ticket.categoria] || '📌' }} {{ ticket.categoria }}
            </span>
            <span :class="['badge', `badge-${getPriorityClass(ticket.prioridad)}`]">
              Prioridad: {{ (ticket.prioridad || 'media').toUpperCase() }}
            </span>
          </div>

          <div>
            <span :class="['badge', `badge-${getStatusClass(ticket.estado)}`]">
              {{
                ticket.estado === 'Pendiente'
                  ? '🟡 Pendiente'
                  : ticket.estado === 'En proceso'
                  ? '🔵 En proceso'
                  : '🟢 Solucionado'
              }}
            </span>
          </div>
        </div>

        <div class="ticket-user-info">
          <span>👤 <strong>{{ ticket.nombre || 'Anónimo' }}</strong></span>
          <span>🎓 Legajo: <strong>{{ ticket.legajo || 'S/D' }}</strong></span>
          <span>
            ✉️ <a :href="`mailto:${ticket.email}`">{{ ticket.email }}</a>
          </span>
          <span>📅 {{ formatDate(ticket.fecha_creacion) }}</span>
        </div>

        <div class="ticket-body">
          <p style="margin: 0; white-space: pre-line;">{{ ticket.descripcion }}</p>

          <!-- Vista previa de imagen adjunta -->
          <div v-if="ticket.imagen_base64" class="attachment-box">
            <img
              :src="ticket.imagen_base64"
              alt="Captura adjunta"
              class="attachment-thumb"
              @click="imagenAmpliada = ticket.imagen_base64"
            />
            <button
              type="button"
              class="btn-view-img"
              @click="imagenAmpliada = ticket.imagen_base64"
            >
              🔍 Ver captura en pantalla completa
            </button>
          </div>
        </div>

        <div class="ticket-actions">
          <button
            v-if="ticket.estado !== 'Solucionado'"
            type="button"
            class="btn btn-success"
            @click="ticketStore.updateTicketStatus(ticket.id, 'Solucionado')"
          >
            <span>✓</span> Marcar como solucionado
          </button>

          <button
            v-if="ticket.estado !== 'En proceso'"
            type="button"
            class="btn btn-secondary"
            @click="ticketStore.updateTicketStatus(ticket.id, 'En proceso')"
          >
            <span>⚙️</span> En proceso
          </button>

          <button
            v-if="ticket.estado !== 'Pendiente'"
            type="button"
            class="btn btn-outline"
            @click="ticketStore.updateTicketStatus(ticket.id, 'Pendiente')"
          >
            <span>↺</span> Reabrir (Pendiente)
          </button>

          <button
            type="button"
            class="btn btn-danger-outline"
            title="Eliminar ticket permanentemente"
            @click="confirmDelete(ticket.id)"
          >
            <span>🗑️</span>
          </button>
        </div>
      </article>
    </section>

    <!-- Lightbox de imagen -->
    <div v-if="imagenAmpliada" class="lightbox-backdrop" @click.self="imagenAmpliada = null">
      <div class="lightbox-content">
        <button type="button" class="lightbox-close" @click="imagenAmpliada = null">
          Cerrar ✕
        </button>
        <img :src="imagenAmpliada" alt="Captura ampliada" class="lightbox-img" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.tickets-admin-wrapper {
  --primary: #004b87;
  --on-primary: #ffffff;
  --surface: #ffffff;
  --surface-2: #f8fafc;
  --surface-accent: #e2e8f0;
  --text: #0f172a;
  --text-muted: #64748b;
  --border: 1px solid #cbd5e1;
  --danger: #dc2626;
  --danger-light: #fee2e2;
  --success: #16a34a;
  --success-light: #dcfce7;
  --warning: #d97706;
  --warning-light: #fef3c7;
  --info-light: #e0f2fe;
  --process: #2563eb;
  --process-light: #dbeafe;
  --radius: 8px;
  --radius-full: 9999px;
  margin-top: 1.25rem;
}

.tickets-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.tickets-subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0;
}

.tickets-top-actions {
  display: flex;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--surface);
  border: var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  text-align: center;
}

.stat-number {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--primary);
  line-height: 1.1;
}

.stat-card.pending .stat-number { color: var(--warning); }
.stat-card.in-process .stat-number { color: var(--process); }
.stat-card.solved .stat-number { color: var(--success); }

.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
  margin-top: 0.35rem;
}

.controls-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  background: var(--surface);
  padding: 0.85rem;
  border-radius: var(--radius);
  border: var(--border);
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  background: var(--surface-2);
  border: var(--border);
  color: var(--text);
  padding: 0.45rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
}

.filter-btn.active {
  background: var(--primary);
  color: var(--on-primary);
  border-color: var(--primary);
}

.search-controls {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  min-width: 260px;
}

.search-box {
  flex: 1;
}

.search-box input,
.select-priority {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: var(--border);
  border-radius: var(--radius);
  font-size: 0.875rem;
  background: var(--surface);
  color: var(--text);
  box-sizing: border-box;
}

.select-priority {
  width: auto;
}

.tickets-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ticket-card {
  background: var(--surface);
  border: var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.ticket-card.status-pendiente { border-left: 5px solid var(--warning); }
.ticket-card.status-proceso { border-left: 5px solid var(--process); }
.ticket-card.status-solucionado { border-left: 5px solid var(--success); opacity: 0.92; }

.ticket-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.ticket-folio {
  font-weight: 700;
  font-size: 1rem;
  color: var(--primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ticket-user-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
  background: var(--surface-2);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
}

.ticket-user-info a {
  color: var(--primary);
  text-decoration: none;
}

.ticket-body {
  font-size: 0.9rem;
  color: var(--text);
  line-height: 1.55;
  background: var(--surface-2);
  padding: 0.75rem;
  border-radius: var(--radius);
  border-left: 3px solid var(--surface-accent);
}

.attachment-box {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px dashed #cbd5e1;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.attachment-thumb {
  width: 72px;
  height: 54px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  cursor: pointer;
}

.btn-view-img {
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.ticket-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--surface-accent);
  flex-wrap: wrap;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.65rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-pendiente { background: var(--warning-light); color: #92400e; border: 1px solid #fcd34d; }
.badge-proceso { background: var(--process-light); color: #1e40af; border: 1px solid #93c5fd; }
.badge-solucionado { background: var(--success-light); color: #166534; border: 1px solid #86efac; }
.badge-tipo { background: var(--info-light); color: #075985; }
.badge-prio-alta { background: var(--danger-light); color: #991b1b; border: 1px solid #fca5a5; }
.badge-prio-media { background: var(--warning-light); color: #854d0e; border: 1px solid #fde047; }
.badge-prio-baja { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
}

.btn-success { background: var(--success); color: #ffffff; }
.btn-secondary { background: var(--surface-accent); color: var(--text); }
.btn-outline { background: var(--surface); border: var(--border); color: var(--text); }
.btn-danger-outline { background: transparent; color: var(--danger); border: 1px solid var(--danger-light); }

.empty-state {
  background: var(--surface);
  border: 1px dashed #cbd5e1;
  border-radius: var(--radius);
  text-align: center;
  padding: 2.5rem 1rem;
  color: var(--text-muted);
}

.empty-state-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.lightbox-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.82);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
  z-index: 300;
}

.lightbox-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.lightbox-close {
  background: #ffffff;
  color: #0f172a;
  border: none;
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
}

.lightbox-img {
  max-width: 100%;
  max-height: 82vh;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}
</style>