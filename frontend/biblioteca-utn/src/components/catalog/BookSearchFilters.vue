<template>
  <div class="filter-box">
    <!-- Búsqueda Principal -->
    <div class="search-row">
      <div class="input-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          v-model="store.filters.query" 
          type="text" 
          placeholder="Buscar por título o autor..."
          class="input-text"
          @keyup.enter="handleSearch"
        />
      </div>

      <select v-model="store.filters.searchType" class="input-select">
        <option value="all">Buscar por: Título y Autor</option>
        <option value="title">Solo Título</option>
        <option value="author">Solo Autor</option>
      </select>

      <button @click="handleSearch" class="btn-primary">Buscar</button>
    </div>

    <!-- Opciones Secundarias -->
    <div class="options-row">
      <label class="checkbox-label">
        <input type="checkbox" v-model="store.filters.exactMatch" />
        Coincidencia exacta
      </label>

      <div class="filter-group">
        <label class="label-inline">Biblioteca:</label>
        <select v-model="store.filters.library" class="input-select-sm">
          <option value="">Todas (UTN, UFLO, UCES)</option>
          <option value="UTN">UTN</option>
          <option value="UFLO">UFLO</option>
          <option value="UCES">UCES</option>
        </select>
      </div>

      <button @click="store.resetFilters" class="btn-secondary">Restablecer</button>
    </div>
  </div>
</template>

<script setup>
import { useBookStore } from '../../stores/bookStore'

const store = useBookStore()

function handleSearch() {
  store.currentPage = 1
}
</script>

<style scoped>
.filter-box {
  background: var(--utn-card-bg);
  border: 1px solid var(--utn-border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.5rem;
}

.search-row, .options-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-row {
  margin-bottom: 0.85rem;
}

.input-wrapper {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.85rem;
  opacity: 0.5;
}

.input-text {
  width: 100%;
  padding: 0.6rem 0.8rem 0.6rem 2.2rem;
  border: 1px solid var(--utn-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  background: #fdfdfd;
}

.input-select, .input-select-sm {
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--utn-border);
  border-radius: var(--radius-sm);
  background: white;
  font-size: 0.9rem;
  color: var(--utn-text);
  cursor: pointer;
}

.input-text:focus, .input-select:focus, .input-select-sm:focus {
  outline: none;
  border-color: var(--utn-blue-light);
  box-shadow: 0 0 0 3px rgba(23, 101, 165, 0.12);
}

.options-row {
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid #f0f4f8;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label-inline {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--utn-text-muted);
}

.checkbox-label {
  font-size: 0.85rem;
  color: var(--utn-text);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  cursor: pointer;
}

.btn-primary {
  background: var(--utn-blue-light);
  color: white;
  border: none;
  padding: 0.6rem 1.3rem;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:hover {
  background: #104b80;
}

.btn-secondary {
  background: transparent;
  color: var(--utn-text-muted);
  border: 1px solid var(--utn-border);
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f8fafc;
  color: var(--utn-text);
}
</style>