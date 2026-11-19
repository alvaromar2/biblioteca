<template>
  <div v-if="book" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Ficha Técnica del Ejemplar</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <div class="doc-badge">{{ book.docType || 'Documento' }}</div>
        <h4>{{ book.title }}</h4>
        <p v-if="book.subtitle" class="subtitle"><em>{{ book.subtitle }}</em></p>

        <div class="detail-grid">
          <p><strong>Signatura Topográfica (Ubicación):</strong> <span class="signatura-tag">{{ book.signatura || 'S/N' }}</span></p>
          <p><strong>Autor:</strong> {{ book.author }}</p>
          <p><strong>Materia / Tema:</strong> {{ book.subject || 'General' }}</p>
          <p><strong>Editorial / Edición:</strong> {{ book.publisher }} ({{ book.year }}) - {{ book.edition }}</p>
          <p><strong>Biblioteca:</strong> {{ book.library }}</p>
          <p><strong>Nº Inventario General:</strong> {{ book.inventoryNumber }}</p>
        </div>

        <!-- Listado de Ejemplares Físicos -->
        <div class="copies-section">
          <h5>Ejemplares en Biblioteca:</h5>
          <table class="copies-table">
            <thead>
              <tr>
                <th>Código Ejemplar</th>
                <th>Estado / Condición</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="copy in book.copies" :key="copy.id">
                <td>{{ copy.number }}</td>
                <td>{{ copy.status }}</td>
              </tr>
              <tr v-if="!book.copies?.length">
                <td colspan="2">No se detallan copias adicionales.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-fav" @click="store.toggleFavorite(book.id)">
          {{ store.favorites.includes(book.id) ? '★ Quitar de favoritos' : '☆ Agregar a favoritos' }}
        </button>
        <button class="btn-secondary" @click="$emit('close')">Cerrar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useBookStore } from '../../stores/bookStore'

defineProps({
  book: { type: Object, default: null }
})

defineEmits(['close'])

const store = useBookStore()
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border: 1px solid #999;
  width: 90%;
  max-width: 550px;
  padding: 1.5rem;
  border-radius: 4px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 0.75rem;
}

.doc-badge {
  display: inline-block;
  font-size: 0.75rem;
  background: #003366;
  color: white;
  padding: 0.15rem 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 2px;
}

.signatura-tag {
  background: #eef2f7;
  border: 1px solid #003366;
  padding: 0.1rem 0.4rem;
  font-weight: bold;
  font-family: monospace;
}

.detail-grid p {
  margin: 0.35rem 0;
  font-size: 0.9rem;
}

.copies-section {
  margin-top: 1rem;
  border-top: 1px solid #eee;
  padding-top: 0.5rem;
}

.copies-section h5 {
  margin: 0 0 0.5rem 0;
}

.copies-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.copies-table th, .copies-table td {
  border: 1px solid #ddd;
  padding: 0.4rem;
  text-align: left;
}

.copies-table th {
  background: #f4f4f4;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 1.25rem;
  padding-top: 0.75rem;
  border-top: 1px solid #eee;
}

.btn-fav, .btn-secondary {
  padding: 0.4rem 0.8rem;
  border: 1px solid #999;
  background: white;
  cursor: pointer;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}
</style>