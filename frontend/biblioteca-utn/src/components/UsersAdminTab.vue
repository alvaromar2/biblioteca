<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api'
const authStore = useAuthStore()

const usuarios = ref([])
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('all')

const stats = computed(() => {
  const list = usuarios.value
  return {
    total: list.length,
    alumnos: list.filter((u) => u.rol === 'alumno').length,
    profesores: list.filter((u) => u.rol === 'profesor').length,
    admins: list.filter((u) => u.rol === 'admin').length
  }
})

const filteredUsers = computed(() => {
  return usuarios.value.filter((u) => {
    if (roleFilter.value !== 'all' && u.rol !== roleFilter.value) {
      return false
    }
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase().trim()
      return (
        (u.nombre || '').toLowerCase().includes(q) ||
        (u.email || '').toLowerCase().includes(q) ||
        (u.legajo || '').toLowerCase().includes(q) ||
        (u.universidad || '').toLowerCase().includes(q)
      )
    }
    return true
  })
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/usuarios`)
    const data = await res.json()
    if (data.success) {
      usuarios.value = data.usuarios
    }
  } catch {
    alert('Error de conexión al cargar usuarios.')
  } finally {
    loading.value = false
  }
}

async function cambiarRol(usuario, event) {
  const nuevoRol = event.target.value
  if (nuevoRol === usuario.rol) return

  if (!confirm(`¿Cambiar el rol de ${usuario.nombre} a ${nuevoRol.toUpperCase()}?`)) {
    event.target.value = usuario.rol
    return
  }

  try {
    const res = await fetch(`${API_BASE}/usuarios/${usuario.id}/rol`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rol: nuevoRol })
    })
    const data = await res.json()
    if (data.success) {
      usuario.rol = nuevoRol
    } else {
      alert(data.error || 'No se pudo cambiar el rol.')
      event.target.value = usuario.rol
    }
  } catch {
    alert('Error de conexión al cambiar rol.')
    event.target.value = usuario.rol
  }
}

async function eliminarUsuario(usuario) {
  if (!confirm(`¿Eliminar permanentemente la cuenta de ${usuario.nombre} (${usuario.email})?`)) {
    return
  }

  try {
    const res = await fetch(`${API_BASE}/usuarios/${usuario.id}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.success) {
      usuarios.value = usuarios.value.filter((u) => u.id !== usuario.id)
    } else {
      alert(data.error || 'No se pudo eliminar el usuario.')
    }
  } catch {
    alert('Error de conexión al eliminar el usuario.')
  }
}

function formatDate(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  } catch {
    return iso
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="users-admin">
    <div class="topbar">
      <p class="subtitle">Administración de cuentas registradas (Alumnos, Profesores y Administradores)</p>
      <button type="button" class="btn-outline" @click="fetchUsers">🔄 Actualizar</button>
    </div>

    <!-- Métricas -->
    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-number">{{ stats.total }}</div>
        <div class="stat-label">Total Cuentas</div>
      </div>
      <div class="stat-card">
        <div class="stat-number text-blue">{{ stats.alumnos }}</div>
        <div class="stat-label">🎓 Alumnos</div>
      </div>
      <div class="stat-card">
        <div class="stat-number text-amber">{{ stats.profesores }}</div>
        <div class="stat-label">👨‍🏫 Profesores</div>
      </div>
      <div class="stat-card">
        <div class="stat-number text-green">{{ stats.admins }}</div>
        <div class="stat-label">🛡️ Admins</div>
      </div>
    </section>

    <!-- Filtros -->
    <section class="controls-bar">
      <div class="filter-buttons">
        <button
          type="button"
          :class="['filter-btn', { active: roleFilter === 'all' }]"
          @click="roleFilter = 'all'"
        >
          Todos ({{ stats.total }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: roleFilter === 'alumno' }]"
          @click="roleFilter = 'alumno'"
        >
          🎓 Alumnos ({{ stats.alumnos }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: roleFilter === 'profesor' }]"
          @click="roleFilter = 'profesor'"
        >
          👨‍🏫 Profesores ({{ stats.profesores }})
        </button>
        <button
          type="button"
          :class="['filter-btn', { active: roleFilter === 'admin' }]"
          @click="roleFilter = 'admin'"
        >
          🛡️ Admins ({{ stats.admins }})
        </button>
      </div>

      <div class="search-box">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Buscar por nombre, correo, legajo o universidad..."
        />
      </div>
    </section>

    <!-- Tabla -->
    <div class="table-wrapper">
      <table class="users-table">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Legajo / DNI</th>
            <th>Universidad</th>
            <th>Registro</th>
            <th>Rol asignado</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="empty-row">Cargando usuarios...</td>
          </tr>
          <tr v-else-if="filteredUsers.length === 0">
            <td colspan="6" class="empty-row">No se encontraron usuarios.</td>
          </tr>
          <tr v-for="u in filteredUsers" :key="u.id">
            <td>
              <div class="user-name">{{ u.nombre }}</div>
              <div class="user-email">{{ u.email }}</div>
            </td>
            <td><code>{{ u.legajo || 'S/D' }}</code></td>
            <td>
              <span class="badge-uni">{{ u.universidad || 'UTN' }}</span>
            </td>
            <td class="date-cell">{{ formatDate(u.fecha_registro) }}</td>
            <td>
              <select
                :value="u.rol"
                :disabled="u.email === 'admin@utn.edu.ar' || u.id === authStore.user?.id"
                class="role-select"
                @change="cambiarRol(u, $event)"
              >
                <option value="alumno">🎓 Alumno</option>
                <option value="profesor">👨‍🏫 Profesor</option>
                <option value="admin">🛡️ Admin</option>
              </select>
            </td>
            <td class="actions-cell">
              <button
                v-if="u.email !== 'admin@utn.edu.ar' && u.id !== authStore.user?.id"
                type="button"
                class="btn-delete"
                @click="eliminarUsuario(u)"
              >
                Eliminar
              </button>
              <span v-else class="protected-label">Protegido</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.users-admin {
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

.btn-outline {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
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

.text-blue { color: #2563eb; }
.text-amber { color: #d97706; }
.text-green { color: #16a34a; }

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

.table-wrapper {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.users-table th {
  background: #f8fafc;
  text-align: left;
  padding: 0.85rem 1rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  color: #64748b;
  border-bottom: 1px solid #cbd5e1;
}

.users-table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.user-name {
  font-weight: 600;
  color: #0f172a;
}

.user-email {
  font-size: 0.8rem;
  color: #64748b;
}

.badge-uni {
  background: #0f3d6e;
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.date-cell {
  font-size: 0.82rem;
  color: #64748b;
}

.role-select {
  padding: 0.4rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.84rem;
  background: #f8fafc;
}

.actions-cell {
  text-align: right;
}

.btn-delete {
  background: #fff5f5;
  color: #c5221f;
  border: 1px solid #f8d7da;
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
}

.protected-label {
  font-size: 0.78rem;
  color: #94a3b8;
  font-style: italic;
}

.empty-row {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}
</style>