<template>
  <div class="soporte-container">
    <div class="contenedor-formulario">
      <div class="encabezado">
        <h2>Centro de Soporte</h2>
        <p class="subtitulo">Plataforma de Biblioteca - UTN</p>
      </div>

      <div class="contenido">
        <div v-if="mensajeExito" class="alerta-exito">
          <strong>¡Tu reporte #{{ ticketCreadoId }} ha sido enviado con éxito!</strong>
          <p style="margin-top: 0.4rem;">
            Nuestro equipo técnico lo revisará a la brevedad.
          </p>
          <button @click="resetForm" class="btn-reiniciar">Enviar otro reporte</button>
        </div>

        <template v-else>
          <p class="texto-inicial">
            Completá el siguiente formulario para que nuestro equipo técnico pueda ayudarte.
            Los campos marcados con * son obligatorios.
          </p>

          <div v-if="errorEnvio" class="alerta-error">
            {{ errorEnvio }}
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="grupo-input">
              <label for="nombre">Nombre completo *</label>
              <input
                id="nombre"
                v-model="form.nombre"
                type="text"
                placeholder="Ingresá tu nombre y apellido"
                required
              />
            </div>

            <div class="grupo-input">
              <label for="legajo">Legajo o DNI *</label>
              <input
                id="legajo"
                v-model="form.legajo"
                type="text"
                placeholder="Ej: 49500"
                required
              />
            </div>

            <div class="grupo-input">
              <label for="email">Correo electrónico *</label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                placeholder="Ej: correo@gmail.com"
                required
              />
            </div>

            <hr class="separador" />

            <div class="grupo-input">
              <label for="prioridad">Gravedad del problema *</label>
              <select id="prioridad" v-model="form.prioridad" required>
                <option value="" disabled>Seleccioná una prioridad</option>
                <option value="baja">Baja</option>
                <option value="media">Media</option>
                <option value="alta">Alta</option>
              </select>
            </div>

            <div class="grupo-input">
              <label for="categoria">Tipo de problema *</label>
              <select id="categoria" v-model="form.categoria" required>
                <option value="" disabled>Seleccioná el problema</option>
                <option value="No puedo buscar un libro por título o autor">
                  No puedo buscar un libro por título o autor
                </option>
                <option value="No me deja seleccionar las bibliotecas">
                  No me deja seleccionar las bibliotecas
                </option>
                <option value="Problema al ver los detalles de los libros">
                  Problema al ver los detalles de los libros
                </option>
                <option value="Otro">Otro problema</option>
              </select>
            </div>

            <div class="grupo-input">
              <label for="descripcion">Descripción del problema *</label>
              <textarea
                id="descripcion"
                v-model="form.descripcion"
                rows="5"
                placeholder="Contanos qué sucedió"
                required
              ></textarea>
            </div>

            <div class="grupo-input">
              <label for="adjunto">Adjuntar captura o imagen (opcional)</label>
              <input
                id="adjunto"
                ref="fileInput"
                type="file"
                accept="image/*"
                @change="handleFileUpload"
              />
              <span class="ayuda">
                La captura se enviará directamente al panel del administrador.
              </span>

              <div v-if="form.imagenBase64" class="preview-box">
                <img :src="form.imagenBase64" alt="Vista previa" class="preview-img" />
                <button type="button" class="btn-remove-img" @click="quitarImagen">
                  ✕ Quitar imagen
                </button>
              </div>
            </div>

            <button type="submit" class="btn-enviar" :disabled="enviando">
              {{ enviando ? 'Enviando...' : 'Enviar reporte →' }}
            </button>
          </form>
        </template>
      </div>

      <div class="pie">
        UTN · Centro de asistencia técnica
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useTicketStore } from '../stores/ticketStore'
import { useAuthStore } from '../stores/authStore'

const ticketStore = useTicketStore()
const authStore = useAuthStore()
const fileInput = ref(null)

const form = reactive({
  nombre: authStore.user?.nombre || '',
  legajo: authStore.user?.legajo || '',
  email: authStore.user?.email || '',
  prioridad: '',
  categoria: '',
  descripcion: '',
  imagenBase64: null
})

const enviando = ref(false)
const mensajeExito = ref(false)
const errorEnvio = ref('')
const ticketCreadoId = ref(null)

function comprimirImagen(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const MAX_DIM = 1024
        let { width, height } = img
        if (width > MAX_DIM || height > MAX_DIM) {
          if (width > height) {
            height = Math.round((height * MAX_DIM) / width)
            width = MAX_DIM
          } else {
            width = Math.round((width * MAX_DIM) / height)
            height = MAX_DIM
          }
        }
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        resolve(canvas.toDataURL('image/jpeg', 0.75))
      }
      img.onerror = reject
      img.src = e.target.result
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  try {
    form.imagenBase64 = await comprimirImagen(file)
  } catch {
    errorEnvio.value = 'No se pudo procesar la imagen seleccionada.'
  }
}

function quitarImagen() {
  form.imagenBase64 = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function handleSubmit() {
  enviando.value = true
  errorEnvio.value = ''

  try {
    const rolEtiqueta = authStore.user?.rol
      ? ` (${authStore.user.rol.toUpperCase()})`
      : ''

    const res = await ticketStore.createTicket({
      nombre: `${form.nombre}${rolEtiqueta}`,
      legajo: form.legajo,
      email: form.email,
      prioridad: form.prioridad,
      categoria: form.categoria,
      descripcion: form.descripcion,
      imagen_base64: form.imagenBase64
    })

    if (res && res.success) {
      ticketCreadoId.value = res.id
      mensajeExito.value = true
    } else {
      errorEnvio.value = res?.error || 'No se pudo registrar el ticket en el servidor.'
    }
  } catch {
    errorEnvio.value = 'Error de conexión con el servidor Flask.'
  } finally {
    enviando.value = false
  }
}

function resetForm() {
  form.nombre = authStore.user?.nombre || ''
  form.legajo = authStore.user?.legajo || ''
  form.email = authStore.user?.email || ''
  form.prioridad = ''
  form.categoria = ''
  form.descripcion = ''
  quitarImagen()
  errorEnvio.value = ''
  ticketCreadoId.value = null
  mensajeExito.value = false
}
</script>

<style scoped>
.soporte-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 10px;
}

.contenedor-formulario {
  width: 100%;
  max-width: 650px;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 35px rgba(20, 45, 80, 0.10);
  border: 1px solid #dce4ee;
}

.encabezado {
  background: linear-gradient(135deg, #102d50, #1765a5);
  padding: 35px 30px;
  text-align: center;
  color: white;
}

h2 {
  font-size: 27px;
  margin-bottom: 10px;
  font-weight: 650;
}

.subtitulo {
  font-size: 14px;
  color: #dceaff;
  line-height: 1.5;
}

.contenido {
  padding: 35px;
}

.texto-inicial {
  margin-bottom: 25px;
  font-size: 14px;
  color: #68788d;
  line-height: 1.6;
}

.grupo-input {
  margin-bottom: 21px;
  display: flex;
  flex-direction: column;
}

label {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 9px;
  color: #263c57;
}

input[type="text"],
input[type="email"],
input[type="file"],
select,
textarea {
  width: 100%;
  padding: 13px 14px;
  background: #f8fafc;
  border: 1px solid #dce4ee;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  color: #26354a;
  outline: none;
  transition: 0.3s;
  box-sizing: border-box;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #287ac0;
  background: white;
  box-shadow: 0 0 0 3px rgba(40, 122, 192, 0.10);
}

textarea {
  resize: vertical;
  min-height: 120px;
}

.ayuda {
  font-size: 12px;
  color: #8492a4;
  margin-top: 7px;
}

.preview-box {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8fafc;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #dce4ee;
}

.preview-img {
  max-height: 90px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
}

.btn-remove-img {
  background: #fee2e2;
  color: #991b1b;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.separador {
  border: none;
  border-top: 1px solid #e9eef4;
  margin: 27px 0;
}

.btn-enviar {
  width: 100%;
  padding: 15px;
  background: #1765a5;
  color: white;
  border: none;
  border-radius: 9px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}

.btn-enviar:hover:not(:disabled) {
  background: #104b80;
}

.btn-enviar:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.alerta-exito {
  background: #e6f4ea;
  border: 1px solid #137333;
  color: #137333;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  font-size: 0.95rem;
}

.alerta-error {
  background: #fee2e2;
  border: 1px solid #dc2626;
  color: #991b1b;
  padding: 0.9rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
}

.btn-reiniciar {
  display: block;
  margin: 1rem auto 0 auto;
  padding: 0.5rem 1rem;
  background: #137333;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.pie {
  text-align: center;
  padding: 17px;
  background: #f8fafc;
  border-top: 1px solid #edf1f5;
  font-size: 12px;
  color: #8492a4;
}
</style>