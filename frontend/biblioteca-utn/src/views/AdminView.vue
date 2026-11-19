<template>
  <div class="admin-page">
    <div class="admin-header">
      <div>
        <h2>Panel de Administración</h2>
        <p class="subtitle">Gestión integral de ejemplares, préstamos, soporte y usuarios</p>
      </div>
      <button v-if="activeTab === 'active'" @click="abrirModalNuevo" class="btn-new">
        + Agregar Libro
      </button>
    </div>

    <!-- Pestañas de navegación -->
    <div class="admin-tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'active' }]"
        @click="activeTab = 'active'"
      >
        Catálogo Activo
        <span class="tab-count">{{ store.books.length }}</span>
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'history' }]"
        @click="activeTab = 'history'"
      >
        Historial de Bajas
        <span class="tab-count count-muted">{{ store.deletedBooks.length }}</span>
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'loans' }]"
        @click="activeTab = 'loans'"
      >
        Préstamos
        <span :class="['tab-count', { 'count-alert': loanStore.stats.pendientes > 0 }]">
          {{ loanStore.loans.length }}
        </span>
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'tickets' }]"
        @click="activeTab = 'tickets'"
      >
        Tickets de Soporte
        <span :class="['tab-count', { 'count-alert': ticketStore.stats.pendientes > 0 }]">
          {{ ticketStore.tickets.length }}
        </span>
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'users' }]"
        @click="activeTab = 'users'"
      >
        Usuarios
      </button>
    </div>

    <!-- Barra de Filtros Dependientes (solo para pestañas de libros) -->
    <div v-if="activeTab === 'active' || activeTab === 'history'" class="admin-filters">
      <div class="filter-item search-item">
        <label>Buscar ejemplar</label>
        <input
          v-model="busqueda"
          type="text"
          placeholder="Título, autor o N° inventario..."
          class="input-control"
        />
      </div>

      <div class="filter-item">
        <label>Universidad</label>
        <select
          v-model="filtroUniversidad"
          @change="onUniversidadFilterChange"
          class="input-control"
        >
          <option value="">Todas las universidades</option>
          <option value="UTN">UTN</option>
          <option value="UCES">UCES</option>
          <option value="UFLO">UFLO</option>
        </select>
      </div>

      <div v-if="filtroUniversidad" class="filter-item career-item">
        <label>Carrera ({{ filtroUniversidad }})</label>
        <select v-model="filtroCarrera" class="input-control">
          <option value="">Todas las carreras de {{ filtroUniversidad }}</option>
          <optgroup
            v-for="grupo in carrerasFiltroDisponibles"
            :key="grupo.grupo"
            :label="grupo.grupo"
          >
            <option v-for="carrera in grupo.opciones" :key="carrera" :value="carrera">
              {{ carrera }}
            </option>
          </optgroup>
        </select>
      </div>

      <button
        v-if="busqueda || filtroUniversidad || filtroCarrera"
        @click="limpiarFiltros"
        class="btn-clear"
      >
        Limpiar filtros
      </button>
    </div>

    <!-- TABLA 1: CATÁLOGO ACTIVO -->
    <div v-if="activeTab === 'active'" class="table-wrapper">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Inventario</th>
            <th>Título / Autor</th>
            <th>Universidad</th>
            <th>Carrera</th>
            <th>Estado</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="librosFiltrados.length === 0">
            <td colspan="6" class="empty-row">
              No se encontraron libros activos para los filtros seleccionados.
            </td>
          </tr>
          <tr v-for="book in librosFiltrados" :key="book.id">
            <td><code>{{ book.inventoryNumber }}</code></td>
            <td>
              <div class="book-cell-title">{{ book.title }}</div>
              <div class="book-cell-author">{{ book.author }} ({{ book.year }})</div>
            </td>
            <td>
              <span :class="['uni-badge', 'badge-' + book.library.toLowerCase()]">
                {{ book.library }}
              </span>
            </td>
            <td class="career-cell">
              {{ book.career || 'Sin asignar' }}
            </td>
            <td>
              <span :class="['status-pill', book.available ? 'ok' : 'off']">
                {{ book.available ? 'Disponible' : 'Prestado' }}
              </span>
            </td>
            <td class="actions-cell">
              <button @click="abrirModalEditar(book)" class="btn-edit">Editar</button>
              <button @click="abrirModalBaja(book)" class="btn-delete">Dar de baja</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- TABLA 2: HISTORIAL DE BAJAS -->
    <div v-else-if="activeTab === 'history'" class="table-wrapper">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Inventario</th>
            <th>Título / Autor</th>
            <th>Universidad / Carrera</th>
            <th>Fecha de baja</th>
            <th>Motivo</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="librosFiltrados.length === 0">
            <td colspan="6" class="empty-row">
              No hay ejemplares registrados en el historial de bajas.
            </td>
          </tr>
          <tr v-for="book in librosFiltrados" :key="book.id" class="row-deleted">
            <td><code>{{ book.inventoryNumber }}</code></td>
            <td>
              <div class="book-cell-title">{{ book.title }}</div>
              <div class="book-cell-author">{{ book.author }} ({{ book.year }})</div>
            </td>
            <td>
              <span :class="['uni-badge', 'badge-' + book.library.toLowerCase()]">
                {{ book.library }}
              </span>
              <div class="career-subtext">{{ book.career || 'Sin asignar' }}</div>
            </td>
            <td class="date-cell">{{ book.deletedAt }}</td>
            <td class="reason-cell">{{ book.deleteReason }}</td>
            <td class="actions-cell">
              <button @click="restaurarEjemplar(book)" class="btn-restore">
                Restaurar
              </button>
              <button @click="eliminarDefinitivo(book)" class="btn-delete" title="Borrar permanentemente">
                Borrar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PESTAÑA 3: PRÉSTAMOS -->
    <LoansAdminTab v-else-if="activeTab === 'loans'" />

    <!-- PESTAÑA 4: TICKETS DE SOPORTE -->
    <TicketsAdminTab v-else-if="activeTab === 'tickets'" />

    <!-- PESTAÑA 5: USUARIOS -->
    <UsersAdminTab v-else />

    <!-- Modal Crear / Editar Libro -->
    <div v-if="mostrarModal" class="modal-backdrop" @click.self="cerrarModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3>{{ modoEdicion ? 'Editar Ejemplar' : 'Nuevo Ejemplar' }}</h3>
          <button @click="cerrarModal" class="btn-close">&times;</button>
        </div>

        <form @submit.prevent="guardarLibro" class="modal-form">
          <div class="form-grid">
            <div class="form-group full">
              <label>Título del libro *</label>
              <input v-model="form.title" type="text" required class="input-control" />
            </div>

            <div class="form-group">
              <label>Autor *</label>
              <input v-model="form.author" type="text" required class="input-control" />
            </div>

            <div class="form-group">
              <label>N° Inventario *</label>
              <input v-model="form.inventoryNumber" type="text" required class="input-control" />
            </div>

            <div class="form-group">
              <label>Editorial *</label>
              <input v-model="form.publisher" type="text" required class="input-control" />
            </div>

            <div class="form-group">
              <label>Año *</label>
              <input v-model.number="form.year" type="number" required class="input-control" />
            </div>

            <div class="form-group">
              <label>Universidad *</label>
              <select
                v-model="form.library"
                @change="form.career = ''"
                required
                class="input-control"
              >
                <option value="" disabled>Seleccioná universidad</option>
                <option value="UTN">UTN</option>
                <option value="UCES">UCES</option>
                <option value="UFLO">UFLO</option>
              </select>
            </div>

            <div class="form-group" v-if="form.library">
              <label>Carrera ({{ form.library }}) *</label>
              <select v-model="form.career" required class="input-control">
                <option value="" disabled>Seleccioná una carrera</option>
                <optgroup
                  v-for="grupo in carrerasFormDisponibles"
                  :key="grupo.grupo"
                  :label="grupo.grupo"
                >
                  <option v-for="carrera in grupo.opciones" :key="carrera" :value="carrera">
                    {{ carrera }}
                  </option>
                </optgroup>
              </select>
            </div>

            <div class="form-group full checkbox-row">
              <label>
                <input type="checkbox" v-model="form.available" />
                Ejemplar disponible en sala / préstamo
              </label>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" @click="cerrarModal" class="btn-cancel">Cancelar</button>
            <button type="submit" class="btn-save">
              {{ modoEdicion ? 'Guardar Cambios' : 'Registrar Libro' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Confirmar Baja con Motivo -->
    <div v-if="mostrarModalBaja" class="modal-backdrop" @click.self="cerrarModalBaja">
      <div class="modal-card modal-sm">
        <div class="modal-header header-danger">
          <h3>Dar de baja ejemplar</h3>
          <button @click="cerrarModalBaja" class="btn-close">&times;</button>
        </div>

        <form @submit.prevent="confirmarBaja" class="modal-form">
          <p class="baja-texto">
            Vas a mover <strong>"{{ libroAEliminar?.title }}"</strong> ({{ libroAEliminar?.inventoryNumber }}) al historial de bajas. Podrás restaurarlo más adelante si lo necesitás.
          </p>

          <div class="form-group">
            <label>Motivo de baja (opcional)</label>
            <input
              v-model="motivoBaja"
              type="text"
              list="motivos-sugeridos"
              placeholder="Ej: Deterioro físico, extravío, error de carga..."
              class="input-control"
            />
            <datalist id="motivos-sugeridos">
              <option value="Deterioro físico" />
              <option value="Extravío en préstamo" />
              <option value="Bibliografía desactualizada" />
              <option value="Error de carga" />
              <option value="Transferencia de sede" />
            </datalist>
          </div>

          <div class="modal-footer">
            <button type="button" @click="cerrarModalBaja" class="btn-cancel">Cancelar</button>
            <button type="submit" class="btn-confirm-delete">Confirmar Baja</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useBookStore } from '../stores/bookStore'
import { useTicketStore } from '../stores/ticketStore'
import { useLoanStore } from '../stores/loanStore'
import { CARRERAS_POR_UNIVERSIDAD } from '../data/carreras'
import TicketsAdminTab from '../components/TicketsAdminTab.vue'
import LoansAdminTab from '../components/LoansAdminTab.vue'
import UsersAdminTab from '../components/UsersAdminTab.vue'

const store = useBookStore()
const ticketStore = useTicketStore()
const loanStore = useLoanStore()

onMounted(() => {
  ticketStore.fetchTickets()
  loanStore.fetchLoans()
})

const activeTab = ref('active')

const busqueda = ref('')
const filtroUniversidad = ref('')
const filtroCarrera = ref('')

const carrerasFiltroDisponibles = computed(() => {
  if (!filtroUniversidad.value) return []
  return CARRERAS_POR_UNIVERSIDAD[filtroUniversidad.value] || []
})

function onUniversidadFilterChange() {
  filtroCarrera.value = ''
}

function limpiarFiltros() {
  busqueda.value = ''
  filtroUniversidad.value = ''
  filtroCarrera.value = ''
}

const librosFiltrados = computed(() => {
  const fuente = activeTab.value === 'active' ? store.books : store.deletedBooks

  return fuente.filter((book) => {
    if (filtroUniversidad.value && book.library !== filtroUniversidad.value) {
      return false
    }
    if (filtroCarrera.value && book.career !== filtroCarrera.value) {
      return false
    }
    if (busqueda.value.trim()) {
      const q = busqueda.value.toLowerCase().trim()
      const coincideTitulo = book.title.toLowerCase().includes(q)
      const coincideAutor = book.author.toLowerCase().includes(q)
      const coincideInv = book.inventoryNumber.toLowerCase().includes(q)
      return coincideTitulo || coincideAutor || coincideInv
    }
    return true
  })
})

const mostrarModal = ref(false)
const modoEdicion = ref(false)

const form = reactive({
  id: null,
  title: '',
  subtitle: '',
  author: '',
  publisher: '',
  year: new Date().getFullYear(),
  library: '',
  career: '',
  inventoryNumber: '',
  available: true
})

const carrerasFormDisponibles = computed(() => {
  if (!form.library) return []
  return CARRERAS_POR_UNIVERSIDAD[form.library] || []
})

function abrirModalNuevo() {
  modoEdicion.value = false
  Object.assign(form, {
    id: null,
    title: '',
    subtitle: '',
    author: '',
    publisher: '',
    year: new Date().getFullYear(),
    library: filtroUniversidad.value || '',
    career: filtroCarrera.value || '',
    inventoryNumber: '',
    available: true
  })
  mostrarModal.value = true
}

function abrirModalEditar(book) {
  modoEdicion.value = true
  Object.assign(form, { ...book })
  mostrarModal.value = true
}

function cerrarModal() {
  mostrarModal.value = false
}

function guardarLibro() {
  if (modoEdicion.value) {
    store.updateBook({ ...form })
  } else {
    store.addBook({ ...form })
  }
  cerrarModal()
}

const mostrarModalBaja = ref(false)
const libroAEliminar = ref(null)
const motivoBaja = ref('')

function abrirModalBaja(book) {
  libroAEliminar.value = book
  motivoBaja.value = ''
  mostrarModalBaja.value = true
}

function cerrarModalBaja() {
  mostrarModalBaja.value = false
  libroAEliminar.value = null
  motivoBaja.value = ''
}

function confirmarBaja() {
  if (libroAEliminar.value) {
    store.deleteBook(libroAEliminar.value.id, motivoBaja.value)
  }
  cerrarModalBaja()
}

function restaurarEjemplar(book) {
  store.restoreBook(book.id)
}

function eliminarDefinitivo(book) {
  if (confirm(`¿Eliminar definitivamente "${book.title}"? Esta acción no se puede deshacer.`)) {
    store.permanentDeleteBook(book.id)
  }
}
</script>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.admin-header h2 {
  font-size: 1.6rem;
  color: var(--utn-text);
}

.subtitle {
  font-size: 0.9rem;
  color: var(--utn-text-muted);
}

.btn-new {
  background: var(--utn-blue);
  color: white;
  border: none;
  padding: 0.65rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
}

.admin-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid var(--utn-border);
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.tab-btn {
  background: transparent;
  border: none;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--utn-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.tab-btn.active {
  color: var(--utn-blue);
  border-bottom-color: var(--utn-blue);
}

.tab-count {
  background: #e2e8f0;
  color: var(--utn-blue);
  font-size: 0.75rem;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
}

.count-muted {
  background: #f1f5f9;
  color: var(--utn-text-muted);
}

.count-alert {
  background: #fef3c7;
  color: #92400e;
}

.admin-filters {
  background: var(--utn-card-bg);
  border: 1px solid var(--utn-border);
  border-radius: var(--radius-md);
  padding: 1.15rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 190px;
}

.search-item { flex: 1; min-width: 240px; }
.career-item { flex: 1.2; min-width: 270px; }

.filter-item label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--utn-text-muted);
}

.input-control {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--utn-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  background: #fdfdfd;
  color: var(--utn-text);
  width: 100%;
}

.btn-clear {
  background: transparent;
  border: 1px solid var(--utn-border);
  color: var(--utn-text-muted);
  padding: 0.55rem 0.9rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
}

.table-wrapper {
  background: var(--utn-card-bg);
  border: 1px solid var(--utn-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow-x: auto;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.admin-table th {
  background: #f8fafc;
  text-align: left;
  padding: 0.85rem 1rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  color: var(--utn-text-muted);
  border-bottom: 1px solid var(--utn-border);
}

.admin-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f0f4f8;
  vertical-align: middle;
}

.book-cell-title { font-weight: 600; color: var(--utn-blue); }
.book-cell-author { font-size: 0.8rem; color: var(--utn-text-muted); }
.career-cell { font-size: 0.85rem; color: var(--utn-text); max-width: 240px; }
.career-subtext { font-size: 0.78rem; color: var(--utn-text-muted); margin-top: 0.25rem; }
.date-cell { font-size: 0.82rem; color: var(--utn-text-muted); white-space: nowrap; }
.reason-cell { font-size: 0.85rem; color: var(--utn-text); font-style: italic; }

.uni-badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  color: white;
}

.badge-utn { background-color: #003366; }
.badge-uflo { background-color: #008080; }
.badge-uces { background-color: #6b21a8; }

.status-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
}

.status-pill.ok { background: #e6f4ea; color: #137333; }
.status-pill.off { background: #fce8e6; color: #c5221f; }

.actions-cell {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn-edit, .btn-delete, .btn-restore {
  padding: 0.35rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  cursor: pointer;
  border: 1px solid var(--utn-border);
  font-weight: 500;
}

.btn-edit { background: white; color: var(--utn-blue); }
.btn-restore { background: #e6f4ea; color: #137333; border-color: #ceead6; }
.btn-delete { background: #fff5f5; color: #c5221f; border-color: #f8d7da; }

.empty-row {
  text-align: center;
  padding: 2.5rem;
  color: var(--utn-text-muted);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(16, 45, 80, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  z-index: 200;
}

.modal-card {
  background: white;
  border-radius: var(--radius-md);
  width: 100%;
  max-width: 600px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  overflow: hidden;
}

.modal-sm { max-width: 460px; }

.modal-header {
  background: var(--utn-blue);
  color: white;
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-danger { background: #991b1b; }

.btn-close {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.modal-form { padding: 1.25rem; }
.baja-texto { font-size: 0.9rem; color: var(--utn-text); margin-bottom: 1rem; line-height: 1.5; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 0.82rem; font-weight: 600; color: var(--utn-text); }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f4f8;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--utn-border);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.btn-save {
  background: var(--utn-blue-light);
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
}

.btn-confirm-delete {
  background: #c5221f;
  color: white;
  border: none;
  padding: 0.5rem 1.2rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
}
</style>