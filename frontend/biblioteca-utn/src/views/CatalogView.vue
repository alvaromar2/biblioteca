<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useBookStore } from '../stores/bookStore'
import { useAuthStore } from '../stores/authStore'
import { useLoanStore } from '../stores/loanStore'
import { useTicketStore } from '../stores/ticketStore'

const store = useBookStore()
const authStore = useAuthStore()
const loanStore = useLoanStore()
const ticketStore = useTicketStore()

// Filtros y ordenamiento locales sobre store.books
const query = ref('')
const searchType = ref('all')
const exactMatch = ref(false)
const selectedLibrary = ref('')
const showOnlyFavorites = ref(false)
const sortBy = ref('title')
const sortOrder = ref('asc')
const currentPage = ref(1)
const itemsPerPage = 10

// Respaldo local de favoritos por si bookStore no lo define
const localFavorites = ref(JSON.parse(localStorage.getItem('utn_fav_books') || '[]'))

const favoritesList = computed(() =>
  Array.isArray(store.favorites) ? store.favorites : localFavorites.value
)

function isFavorite(bookId) {
  return favoritesList.value.includes(bookId)
}

function handleToggleFavorite(bookId) {
  if (typeof store.toggleFavorite === 'function') {
    store.toggleFavorite(bookId)
  } else {
    if (localFavorites.value.includes(bookId)) {
      localFavorites.value = localFavorites.value.filter((id) => id !== bookId)
    } else {
      localFavorites.value.push(bookId)
    }
    localStorage.setItem('utn_fav_books', JSON.stringify(localFavorites.value))
  }
}

// Préstamos y modal de cátedra
const mostrarMisPrestamos = ref(false)
const solicitandoLibroId = ref(null)
const mostrarModalCatedra = ref(false)
const enviandoSugerencia = ref(false)

const sugerenciaForm = reactive({
  titulo: '',
  autor: '',
  editorial: '',
  catedra: '',
  universidad: authStore.user?.universidad || 'UTN',
  justificacion: ''
})

onMounted(async () => {
  if (!Array.isArray(store.books) || store.books.length === 0) {
    await store.fetchBooks()
  }
  if (authStore.isAuthenticated) {
    await loanStore.fetchLoans()
  }
})

const misPrestamos = computed(() => {
  if (!authStore.user) return []
  return loanStore.loans.filter((p) => p.usuario_id === authStore.user.id)
})

function estadoPrestamoUsuario(bookId) {
  const encontrado = misPrestamos.value.find(
    (p) => p.libro_id === bookId && (p.estado === 'Pendiente' || p.estado === 'Aprobado')
  )
  return encontrado ? encontrado.estado : null
}

async function solicitarPrestamo(book) {
  if (!authStore.isAuthenticated) return
  solicitandoLibroId.value = book.id
  try {
    const res = await loanStore.requestLoan({
      libro_id: book.id,
      usuario_id: authStore.user.id,
      usuario_nombre: authStore.user.nombre,
      usuario_rol: authStore.user.rol,
      usuario_legajo: authStore.user.legajo,
      usuario_email: authStore.user.email
    })
    if (res.success) {
      alert(
        `¡Solicitud registrada! Plazo asignado (${authStore.isProfesor ? 'Profesor: 15 días' : 'Alumno: 7 días'}). Podés seguir el estado en "Mis Préstamos".`
      )
    } else {
      alert(res.error || 'No se pudo solicitar el préstamo.')
    }
  } catch {
    alert('Error de conexión con el servidor Flask.')
  } finally {
    solicitandoLibroId.value = null
  }
}

async function enviarSugerenciaCatedra() {
  enviandoSugerencia.value = true
  try {
    const descripcion = [
      `SOLICITUD BIBLIOGRÁFICA DE CÁTEDRA`,
      `• Título: ${sugerenciaForm.titulo}`,
      `• Autor: ${sugerenciaForm.autor}`,
      `• Editorial / Edición: ${sugerenciaForm.editorial || 'Sin especificar'}`,
      `• Cátedra / Materia: ${sugerenciaForm.catedra}`,
      `• Universidad: ${sugerenciaForm.universidad}`,
      `• Observaciones: ${sugerenciaForm.justificacion || 'Requerido para cursado.'}`
    ].join('\n')

    const res = await ticketStore.createTicket({
      nombre: `${authStore.user.nombre} (PROFESOR)`,
      legajo: authStore.user.legajo || 'DOCENTE',
      email: authStore.user.email,
      prioridad: 'alta',
      categoria: 'Sugerencia bibliográfica (Cátedra)',
      descripcion
    })

    if (res && res.success) {
      alert(`¡Sugerencia #${res.id} enviada al equipo de biblioteca!`)
      Object.assign(sugerenciaForm, {
        titulo: '',
        autor: '',
        editorial: '',
        catedra: '',
        universidad: authStore.user?.universidad || 'UTN',
        justificacion: ''
      })
      mostrarModalCatedra.value = false
    } else {
      alert(res?.error || 'No se pudo enviar la sugerencia.')
    }
  } catch {
    alert('Error de conexión con el servidor Flask.')
  } finally {
    enviandoSugerencia.value = false
  }
}

const filteredDisplayBooks = computed(() => {
  const base = Array.isArray(store.books) ? store.books : []

  const filtrados = base.filter((book) => {
    const titulo = String(book.title || book.titulo || '')
    const autor = String(book.author || book.autor || '')
    const uni = String(book.library || book.universidad || '')

    if (selectedLibrary.value && uni !== selectedLibrary.value) {
      return false
    }

    if (showOnlyFavorites.value && !isFavorite(book.id)) {
      return false
    }

    if (query.value.trim()) {
      const q = query.value.toLowerCase().trim()
      const tLow = titulo.toLowerCase()
      const aLow = autor.toLowerCase()

      if (exactMatch.value) {
        if (searchType.value === 'title') return tLow === q
        if (searchType.value === 'author') return aLow === q
        return tLow === q || aLow === q
      } else {
        if (searchType.value === 'title') return tLow.includes(q)
        if (searchType.value === 'author') return aLow.includes(q)
        return tLow.includes(q) || aLow.includes(q)
      }
    }

    return true
  })

  return [...filtrados].sort((a, b) => {
    const valA = String(a[sortBy.value] || '').toLowerCase()
    const valB = String(b[sortBy.value] || '').toLowerCase()
    const comp = valA.localeCompare(valB, 'es')
    return sortOrder.value === 'asc' ? comp : -comp
  })
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredDisplayBooks.value.length / itemsPerPage))
)

const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredDisplayBooks.value.slice(start, start + itemsPerPage)
})

watch(
  [query, searchType, exactMatch, selectedLibrary, showOnlyFavorites],
  () => {
    currentPage.value = 1
  }
)

function resetAll() {
  query.value = ''
  searchType.value = 'all'
  exactMatch.value = false
  selectedLibrary.value = ''
  showOnlyFavorites.value = false
  currentPage.value = 1
}

function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

function isAvailable(book) {
  return book.available !== undefined ? Boolean(book.available) : Boolean(book.disponible)
}
</script>

<template>
  <div class="catalog-container">
    <header class="catalog-header">
      <div>
        <h1>Catálogo de Libros</h1>
        <p>Explorá los ejemplares de nuestras bibliotecas asociadas</p>
      </div>

      <div class="header-role-actions">
        <button
          v-if="authStore.isProfesor"
          type="button"
          class="btn-catedra"
          @click="mostrarModalCatedra = true"
        >
          📚 Sugerir bibliografía para cátedra
        </button>

        <button
          v-if="authStore.isAlumno || authStore.isProfesor"
          type="button"
          class="btn-my-loans"
          @click="mostrarMisPrestamos = !mostrarMisPrestamos"
        >
          📖 Mis Préstamos ({{ misPrestamos.length }})
        </button>
      </div>
    </header>

    <!-- Panel desplegable Mis Préstamos -->
    <section v-if="mostrarMisPrestamos && (authStore.isAlumno || authStore.isProfesor)" class="my-loans-box">
      <div class="my-loans-header">
        <strong>Mis Solicitudes de Préstamo</strong>
        <span class="role-benefit">
          Beneficio activo: {{ authStore.isProfesor ? 'Profesor (15 días)' : 'Alumno (7 días)' }}
        </span>
      </div>

      <div v-if="misPrestamos.length === 0" class="my-loans-empty">
        Todavía no realizaste ninguna solicitud de préstamo.
      </div>

      <div v-else class="my-loans-list">
        <div v-for="p in misPrestamos" :key="p.id" class="my-loan-row">
          <div>
            <strong>{{ p.libro_titulo }}</strong>
            <span class="loan-inv">({{ p.libro_inventario }})</span>
            <small class="loan-days"> · Plazo: {{ p.dias_prestamo }} días</small>
          </div>
          <span :class="['loan-pill', p.estado.toLowerCase()]">{{ p.estado }}</span>
        </div>
      </div>
    </section>

    <!-- Panel de búsqueda y filtros -->
    <section class="search-card">
      <form class="search-row" @submit.prevent>
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input
            v-model="query"
            type="text"
            placeholder="Buscar por título o autor..."
            class="search-input"
          />
        </div>

        <select v-model="searchType" class="select-control">
          <option value="all">Buscar por: Título y Autor</option>
          <option value="title">Buscar por: Título</option>
          <option value="author">Buscar por: Autor</option>
        </select>

        <button type="submit" class="btn-primary">Buscar</button>
      </form>

      <div class="filters-row">
        <label class="checkbox-label">
          <input v-model="exactMatch" type="checkbox" />
          <span>Coincidencia exacta</span>
        </label>

        <div class="library-filter">
          <label for="library-select">Biblioteca:</label>
          <select id="library-select" v-model="selectedLibrary" class="select-control">
            <option value="">Todas (UTN, UFLO, UCES)</option>
            <option value="UTN">UTN</option>
            <option value="UFLO">UFLO</option>
            <option value="UCES">UCES</option>
          </select>
        </div>

        <button type="button" @click="resetAll" class="btn-secondary">
          Restablecer
        </button>
      </div>
    </section>

    <!-- Barra de resultados y ordenamiento -->
    <div class="toolbar">
      <span class="results-count">
        Resultados: <strong>{{ filteredDisplayBooks.length }}</strong>
      </span>

      <div class="toolbar-actions">
        <button
          type="button"
          @click="showOnlyFavorites = !showOnlyFavorites"
          :class="['btn-fav-filter', { active: showOnlyFavorites }]"
        >
          ★ Favoritos ({{ favoritesList.length }})
        </button>

        <select v-model="sortBy" class="select-control compact">
          <option value="title">Título</option>
          <option value="author">Autor</option>
          <option value="library">Biblioteca</option>
        </select>

        <button type="button" @click="toggleSortOrder" class="btn-sort">
          {{ sortOrder === 'asc' ? '↑ Asc' : '↓ Desc' }}
        </button>
      </div>
    </div>

    <!-- Estados -->
    <div v-if="store.loading" class="no-results">
      <p>Cargando ejemplares desde la biblioteca...</p>
    </div>

    <div v-else-if="store.error" class="no-results">
      <p>{{ store.error }}</p>
      <button @click="store.fetchBooks()" class="btn-reset">Reintentar conexión</button>
    </div>

    <div v-else-if="filteredDisplayBooks.length === 0" class="no-results">
      <p v-if="showOnlyFavorites">No tenés libros guardados en tus favoritos.</p>
      <p v-else-if="!store.books || store.books.length === 0">
        No se recibieron libros desde el servidor. Verificá que Flask esté corriendo en el puerto 5000.
      </p>
      <p v-else>No se encontraron publicaciones con los filtros aplicados.</p>
      <button @click="store.books?.length ? resetAll() : store.fetchBooks()" class="btn-reset">
        {{ store.books?.length ? 'Restablecer búsqueda' : 'Reintentar carga' }}
      </button>
    </div>

    <!-- Listado de libros -->
    <div v-else class="books-list">
      <article v-for="book in paginatedBooks" :key="book.id" class="book-card">
        <div class="book-main">
          <div class="book-badges">
            <span class="badge-uni">{{ book.library || book.universidad }}</span>
            <span class="badge-inv">{{ book.inventoryNumber || book.nro_inventario }}</span>
            <span :class="['badge-status', isAvailable(book) ? 'available' : 'unavailable']">
              {{ isAvailable(book) ? 'Disponible' : 'Prestado' }}
            </span>
          </div>

          <h2 class="book-title">{{ book.title || book.titulo }}</h2>
          <p v-if="book.subtitle || book.subtitulo" class="book-subtitle">
            {{ book.subtitle || book.subtitulo }}
          </p>

          <p class="book-author">
            <strong>Autor:</strong> {{ book.author || book.autor }}
          </p>

          <div class="book-meta">
            <span><strong>Carrera:</strong> {{ book.career || book.carrera }}</span>
            <span v-if="book.publisher || book.editorial">
              • <strong>Editorial:</strong> {{ book.publisher || book.editorial }}
            </span>
            <span v-if="book.year || book.anio">
              ({{ book.year || book.anio }})
            </span>
          </div>
        </div>

        <div class="book-actions">
          <button
            type="button"
            @click="handleToggleFavorite(book.id)"
            :class="['btn-star', { saved: isFavorite(book.id) }]"
          >
            {{ isFavorite(book.id) ? '★ Guardado' : '☆ Favorito' }}
          </button>

          <template v-if="authStore.isAlumno || authStore.isProfesor">
            <span
              v-if="estadoPrestamoUsuario(book.id)"
              class="loan-requested-tag"
            >
              {{ estadoPrestamoUsuario(book.id) === 'Aprobado' ? '📖 En tu poder' : '⏳ Solicitud pendiente' }}
            </span>

            <button
              v-else-if="isAvailable(book)"
              type="button"
              class="btn-loan"
              :disabled="solicitandoLibroId === book.id"
              @click="solicitarPrestamo(book)"
            >
              {{ solicitandoLibroId === book.id ? 'Solicitando...' : 'Solicitar préstamo' }}
            </button>
          </template>

          <router-link
            v-else-if="!authStore.isAuthenticated && isAvailable(book)"
            to="/login"
            class="login-to-loan"
          >
            Ingresá para pedir préstamo
          </router-link>
        </div>
      </article>

      <!-- Paginación -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          type="button"
          class="btn-page"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          Anterior
        </button>

        <span class="page-info">
          Página {{ currentPage }} de {{ totalPages }}
        </span>

        <button
          type="button"
          class="btn-page"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          Siguiente
        </button>
      </div>
    </div>

    <!-- Modal Sugerencia de Cátedra (Solo Profesores) -->
    <div v-if="mostrarModalCatedra" class="modal-backdrop" @click.self="mostrarModalCatedra = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>📚 Sugerir Bibliografía para Cátedra</h3>
          <button type="button" class="btn-close" @click="mostrarModalCatedra = false">&times;</button>
        </div>

        <form @submit.prevent="enviarSugerenciaCatedra" class="modal-form">
          <div class="form-group">
            <label>Título del libro solicitado *</label>
            <input v-model="sugerenciaForm.titulo" type="text" required class="select-control" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Autor *</label>
              <input v-model="sugerenciaForm.autor" type="text" required class="select-control" />
            </div>

            <div class="form-group">
              <label>Editorial / Edición</label>
              <input v-model="sugerenciaForm.editorial" type="text" class="select-control" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Cátedra / Materia *</label>
              <input
                v-model="sugerenciaForm.catedra"
                type="text"
                placeholder="Ej: Análisis Matemático II"
                required
                class="select-control"
              />
            </div>

            <div class="form-group">
              <label>Universidad *</label>
              <select v-model="sugerenciaForm.universidad" class="select-control">
                <option value="UTN">UTN</option>
                <option value="UCES">UCES</option>
                <option value="UFLO">UFLO</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Cantidad de ejemplares sugeridos / Observaciones</label>
            <textarea
              v-model="sugerenciaForm.justificacion"
              rows="3"
              placeholder="Ej: Se necesitan 3 ejemplares para bibliografía obligatoria del 1er cuatrimestre"
              class="select-control"
            ></textarea>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="mostrarModalCatedra = false">
              Cancelar
            </button>
            <button type="submit" class="btn-primary" :disabled="enviandoSugerencia">
              {{ enviandoSugerencia ? 'Enviando...' : 'Enviar solicitud a Biblioteca' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.catalog-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1rem 1.25rem 3rem;
}

.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.catalog-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.35rem;
}

.catalog-header p {
  color: #64748b;
  font-size: 0.95rem;
  margin: 0;
}

.header-role-actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.btn-catedra {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #f59e0b;
  padding: 0.55rem 0.95rem;
  border-radius: 8px;
  font-size: 0.86rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-my-loans {
  background: #eff6ff;
  color: #1e40af;
  border: 1px solid #93c5fd;
  padding: 0.55rem 0.95rem;
  border-radius: 8px;
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
}

.my-loans-box {
  background: #ffffff;
  border: 1px solid #93c5fd;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
}

.my-loans-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #0f172a;
}

.role-benefit {
  font-size: 0.78rem;
  background: #dbeafe;
  color: #1e40af;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-weight: 600;
}

.my-loans-empty {
  font-size: 0.88rem;
  color: #64748b;
}

.my-loans-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.my-loan-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.88rem;
}

.loan-inv {
  font-family: monospace;
  color: #64748b;
  margin-left: 0.35rem;
}

.loan-days {
  color: #64748b;
}

.loan-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
}

.loan-pill.pendiente { background: #fef3c7; color: #92400e; }
.loan-pill.aprobado { background: #dbeafe; color: #1e40af; }
.loan-pill.devuelto { background: #dcfce7; color: #166534; }
.loan-pill.rechazado { background: #fee2e2; color: #991b1b; }

.search-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}

.search-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  min-width: 240px;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  opacity: 0.65;
}

.search-input {
  width: 100%;
  padding: 0.65rem 0.9rem 0.65rem 2.3rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #1e293b;
  box-sizing: border-box;
}

.select-control {
  padding: 0.65rem 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #ffffff;
  color: #1e293b;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
}

.search-row .select-control,
.library-filter .select-control {
  width: auto;
}

.select-control.compact {
  padding: 0.45rem 0.75rem;
  width: auto;
}

.btn-primary,
.btn-reset {
  background: #155da0;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.65rem 1.35rem;
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
}

.filters-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 0.9rem;
  border-top: 1px solid #f1f5f9;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.9rem;
  color: #334155;
  cursor: pointer;
}

.library-filter {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.9rem;
  color: #475569;
}

.btn-secondary {
  background: #f8fafc;
  color: #475569;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.88rem;
  cursor: pointer;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 1.35rem 0 1rem;
}

.results-count {
  font-size: 0.92rem;
  color: #475569;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-fav-filter,
.btn-sort {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-size: 0.88rem;
  color: #1e293b;
  cursor: pointer;
}

.btn-fav-filter.active {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
  font-weight: 600;
}

.no-results {
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 3rem 1.5rem;
  text-align: center;
  color: #64748b;
}

.books-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.book-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.2rem 1.4rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);
}

.book-badges {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.badge-uni {
  background: #0f3d6e;
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.badge-inv {
  background: #f1f5f9;
  color: #475569;
  font-size: 0.78rem;
  font-family: monospace;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.badge-status {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}

.badge-status.available { background: #dcfce7; color: #166534; }
.badge-status.unavailable { background: #fee2e2; color: #991b1b; }

.book-title {
  font-size: 1.12rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.2rem;
}

.book-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0 0 0.45rem;
}

.book-author {
  font-size: 0.92rem;
  color: #334155;
  margin: 0 0 0.35rem;
}

.book-meta {
  font-size: 0.85rem;
  color: #64748b;
}

.book-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.btn-star {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-size: 0.85rem;
  color: #334155;
  cursor: pointer;
  white-space: nowrap;
}

.btn-star.saved {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
  font-weight: 600;
}

.btn-loan {
  background: #155da0;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 0.85rem;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.loan-requested-tag {
  font-size: 0.78rem;
  font-weight: 600;
  background: #eff6ff;
  color: #1e40af;
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  white-space: nowrap;
}

.login-to-loan {
  font-size: 0.78rem;
  color: #155da0;
  text-decoration: none;
  white-space: nowrap;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.25rem;
}

.btn-page {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.45rem 0.95rem;
  font-size: 0.88rem;
  cursor: pointer;
}

.btn-page:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  z-index: 250;
}

.modal-card {
  background: #ffffff;
  border-radius: 12px;
  width: 100%;
  max-width: 540px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  background: #0f3d6e;
  color: #ffffff;
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.05rem;
}

.btn-close {
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 1.4rem;
  cursor: pointer;
}

.modal-form {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.5rem;
}
</style>