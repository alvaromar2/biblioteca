<template>
  <div class="pagination-container" v-if="totalItems > 0">
    <div class="items-per-page">
      <label>Mostrar por página:</label>
      <select 
        :value="itemsPerPage" 
        @change="$emit('update:itemsPerPage', Number($event.target.value))"
      >
        <option :value="2">2</option>
        <option :value="5">5</option>
        <option :value="10">10</option>
      </select>
    </div>

    <div class="nav-buttons">
      <button 
        :disabled="currentPage === 1" 
        @click="$emit('update:currentPage', currentPage - 1)"
      >
        &lt; Anterior
      </button>

      <span>Página {{ currentPage }} de {{ totalPages }}</span>

      <button 
        :disabled="currentPage === totalPages" 
        @click="$emit('update:currentPage', currentPage + 1)"
      >
        Siguiente &gt;
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalItems: { type: Number, required: true },
  itemsPerPage: { type: Number, required: true }
})

defineEmits(['update:currentPage', 'update:itemsPerPage'])

const totalPages = computed(() => Math.ceil(props.totalItems / props.itemsPerPage) || 1)
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #ddd;
}

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

button {
  padding: 0.3rem 0.7rem;
  border: 1px solid #999;
  background: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>