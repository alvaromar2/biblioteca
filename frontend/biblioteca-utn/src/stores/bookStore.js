import { defineStore } from 'pinia'
import { ref } from 'vue'

const API_BASE = import.meta.env.DEV ? 'http://localhost:5000/api' : '/api'

export const useBookStore = defineStore('books', () => {
  const books = ref([])
  const deletedBooks = ref([])
  const favorites = ref(JSON.parse(localStorage.getItem('utn_fav_books') || '[]'))
  const loading = ref(false)
  const error = ref(null)

  async function fetchBooks() {
    loading.value = true
    error.value = null
    try {
      const resActivos = await fetch(`${API_BASE}/libros`)
      const dataActivos = await resActivos.json()
      if (!resActivos.ok) {
        throw new Error(dataActivos.error || 'Error al obtener los libros activos.')
      }
      books.value = Array.isArray(dataActivos) ? dataActivos : []

      const resBajas = await fetch(`${API_BASE}/libros/bajas`)
      if (resBajas.ok) {
        const dataBajas = await resBajas.json()
        deletedBooks.value = Array.isArray(dataBajas) ? dataBajas : []
      }
    } catch (err) {
      error.value = err.message || 'No se pudo conectar con el servidor Flask.'
    } finally {
      loading.value = false
    }
  }

  async function addBook(bookData) {
    const res = await fetch(`${API_BASE}/libros`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookData)
    })
    const nuevo = await res.json()
    if (res.ok) {
      books.value.unshift(nuevo)
    } else {
      alert(nuevo.error || 'Error al agregar libro.')
    }
  }

  async function updateBook(bookData) {
    const res = await fetch(`${API_BASE}/libros/${bookData.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(bookData)
    })
    const actualizado = await res.json()
    if (res.ok) {
      const idx = books.value.findIndex((b) => b.id === actualizado.id)
      if (idx !== -1) books.value[idx] = actualizado
    } else {
      alert(actualizado.error || 'Error al actualizar libro.')
    }
  }

  async function deleteBook(id, motivo) {
    const res = await fetch(`${API_BASE}/libros/${id}/baja`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motivo })
    })
    const dadoDeBaja = await res.json()
    if (res.ok) {
      books.value = books.value.filter((b) => b.id !== id)
      deletedBooks.value.unshift(dadoDeBaja)
    } else {
      alert(dadoDeBaja.error || 'Error al dar de baja el libro.')
    }
  }

  async function restoreBook(id) {
    const res = await fetch(`${API_BASE}/libros/${id}/restaurar`, {
      method: 'POST'
    })
    const restaurado = await res.json()
    if (res.ok) {
      deletedBooks.value = deletedBooks.value.filter((b) => b.id !== id)
      books.value.unshift(restaurado)
    } else {
      alert(restaurado.error || 'Error al restaurar el libro.')
    }
  }

  async function permanentDeleteBook(id) {
    const res = await fetch(`${API_BASE}/libros/${id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      deletedBooks.value = deletedBooks.value.filter((b) => b.id !== id)
    }
  }

  function toggleFavorite(bookId) {
    if (favorites.value.includes(bookId)) {
      favorites.value = favorites.value.filter((id) => id !== bookId)
    } else {
      favorites.value.push(bookId)
    }
    localStorage.setItem('utn_fav_books', JSON.stringify(favorites.value))
  }

  return {
    books,
    deletedBooks,
    favorites,
    loading,
    error,
    fetchBooks,
    addBook,
    updateBook,
    deleteBook,
    restoreBook,
    permanentDeleteBook,
    toggleFavorite
  }
})