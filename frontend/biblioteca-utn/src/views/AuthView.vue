<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>Acceso a Biblioteca</h2>
        <p>Sistema integrado UTN · UCES · UFLO</p>
      </div>

      <!-- Pestañas Login / Registro -->
      <div class="auth-tabs">
        <button
          type="button"
          :class="['auth-tab', { active: modo === 'login' }]"
          @click="cambiarModo('login')"
        >
          Iniciar Sesión
        </button>
        <button
          type="button"
          :class="['auth-tab', { active: modo === 'register' }]"
          @click="cambiarModo('register')"
        >
          Registrarse
        </button>
      </div>

      <div class="auth-body">
        <div v-if="authStore.error" class="alerta-error">
          {{ authStore.error }}
        </div>

        <!-- FORMULARIO DE LOGIN -->
        <form v-if="modo === 'login'" @submit.prevent="handleLogin">
          <div class="grupo-input">
            <label for="login-email">Correo electrónico *</label>
            <input
              id="login-email"
              v-model="loginForm.email"
              type="text"
              placeholder="ejemplo@frsf.utn.edu.ar"
              required
            />
          </div>

          <div class="grupo-input">
            <label for="login-pass">Contraseña *</label>
            <input
              id="login-pass"
              v-model="loginForm.password"
              type="password"
              placeholder="Ingresá tu contraseña"
              required
            />
          </div>

          <button type="submit" class="btn-submit" :disabled="authStore.loading">
            {{ authStore.loading ? 'Ingresando...' : 'Ingresar →' }}
          </button>

          <p class="auth-hint">
            ¿Todavía no tenés cuenta?
            <a href="#" @click.prevent="cambiarModo('register')">Registrate como Alumno o Profesor</a>
          </p>
        </form>

        <!-- FORMULARIO DE REGISTRO -->
        <form v-else @submit.prevent="handleRegister">
          <div class="grupo-input">
            <label>Tipo de usuario *</label>
            <div class="role-selector">
              <button
                type="button"
                :class="['role-card', { selected: registerForm.rol === 'alumno' }]"
                @click="registerForm.rol = 'alumno'"
              >
                <span class="role-icon">🎓</span>
                <span class="role-title">Alumno</span>
                <span class="role-desc">Consulta y préstamos</span>
              </button>

              <button
                type="button"
                :class="['role-card', { selected: registerForm.rol === 'profesor' }]"
                @click="registerForm.rol = 'profesor'"
              >
                <span class="role-icon">👨‍🏫</span>
                <span class="role-title">Profesor</span>
                <span class="role-desc">Docente / Investigador</span>
              </button>
            </div>
          </div>

          <div class="grupo-input">
            <label for="reg-nombre">Nombre y apellido *</label>
            <input
              id="reg-nombre"
              v-model="registerForm.nombre"
              type="text"
              placeholder="Ej: María Laura Gómez"
              required
            />
          </div>

          <div class="form-row-2">
            <div class="grupo-input">
              <label for="reg-legajo">
                {{ registerForm.rol === 'alumno' ? 'Legajo estudiantil *' : 'Legajo docente / DNI *' }}
              </label>
              <input
                id="reg-legajo"
                v-model="registerForm.legajo"
                type="text"
                :placeholder="registerForm.rol === 'alumno' ? 'Ej: 49500' : 'Ej: 28450123'"
                required
              />
            </div>

            <div class="grupo-input">
              <label for="reg-uni">Universidad *</label>
              <select id="reg-uni" v-model="registerForm.universidad" required>
                <option value="UTN">UTN</option>
                <option value="UCES">UCES</option>
                <option value="UFLO">UFLO</option>
              </select>
            </div>
          </div>

          <div class="grupo-input">
            <label for="reg-email">Correo electrónico *</label>
            <input
              id="reg-email"
              v-model="registerForm.email"
              type="email"
              placeholder="correo@ejemplo.com"
              required
            />
          </div>

          <div class="form-row-2">
            <div class="grupo-input">
              <label for="reg-pass">Contraseña *</label>
              <input
                id="reg-pass"
                v-model="registerForm.password"
                type="password"
                placeholder="Mínimo 6 caracteres"
                minlength="6"
                required
              />
            </div>

            <div class="grupo-input">
              <label for="reg-pass2">Repetir contraseña *</label>
              <input
                id="reg-pass2"
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="Confirmá tu clave"
                minlength="6"
                required
              />
            </div>
          </div>

          <button type="submit" class="btn-submit" :disabled="authStore.loading">
            {{
              authStore.loading
                ? 'Creando cuenta...'
                : `Registrarme como ${registerForm.rol === 'alumno' ? 'Alumno' : 'Profesor'} →`
            }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const modo = ref('login')

const loginForm = reactive({
  email: '',
  password: ''
})

const registerForm = reactive({
  rol: 'alumno',
  nombre: '',
  legajo: '',
  universidad: 'UTN',
  email: '',
  password: '',
  confirmPassword: ''
})

function cambiarModo(nuevoModo) {
  modo.value = nuevoModo
  authStore.error = ''
}

function redirigirSegunRol() {
  if (authStore.isAdmin) {
    router.push('/admin')
  } else {
    router.push('/')
  }
}

async function handleLogin() {
  const ok = await authStore.login(loginForm.email, loginForm.password)
  if (ok) {
    redirigirSegunRol()
  }
}

async function handleRegister() {
  if (registerForm.password !== registerForm.confirmPassword) {
    authStore.error = 'Las contraseñas no coinciden.'
    return
  }

  const ok = await authStore.register({
    rol: registerForm.rol,
    nombre: registerForm.nombre,
    legajo: registerForm.legajo,
    universidad: registerForm.universidad,
    email: registerForm.email,
    password: registerForm.password
  })

  if (ok) {
    redirigirSegunRol()
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 1rem;
}

.auth-card {
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 35px rgba(20, 45, 80, 0.1);
  border: 1px solid #dce4ee;
}

.auth-header {
  background: linear-gradient(135deg, #102d50, #1765a5);
  padding: 2rem 1.5rem;
  text-align: center;
  color: #ffffff;
}

.auth-header h2 {
  font-size: 1.6rem;
  margin: 0 0 0.35rem;
}

.auth-header p {
  font-size: 0.9rem;
  color: #dceaff;
  margin: 0;
}

.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: #f1f5f9;
  border-bottom: 1px solid #dce4ee;
}

.auth-tab {
  padding: 0.9rem;
  border: none;
  background: transparent;
  font-size: 0.95rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.auth-tab.active {
  background: #ffffff;
  color: #102d50;
  border-bottom-color: #1765a5;
}

.auth-body {
  padding: 1.75rem;
}

.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.role-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.9rem 0.6rem;
  background: #f8fafc;
  border: 2px solid #dce4ee;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.role-card:hover {
  border-color: #93c5fd;
}

.role-card.selected {
  background: #eff6ff;
  border-color: #1765a5;
}

.role-icon {
  font-size: 1.5rem;
}

.role-title {
  font-weight: 700;
  font-size: 0.95rem;
  color: #1e293b;
}

.role-desc {
  font-size: 0.75rem;
  color: #64748b;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.grupo-input {
  margin-bottom: 1.15rem;
  display: flex;
  flex-direction: column;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: #263c57;
}

input,
select {
  width: 100%;
  padding: 0.7rem 0.85rem;
  background: #f8fafc;
  border: 1px solid #dce4ee;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #1e293b;
  box-sizing: border-box;
}

input:focus,
select:focus {
  outline: none;
  border-color: #1765a5;
  background: #ffffff;
}

.btn-submit {
  width: 100%;
  padding: 0.85rem;
  background: #1765a5;
  color: #ffffff;
  border: none;
  border-radius: 9px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.4rem;
}

.btn-submit:hover:not(:disabled) {
  background: #104b80;
}

.btn-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.alerta-error {
  background: #fee2e2;
  border: 1px solid #dc2626;
  color: #991b1b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.1rem;
  font-size: 0.88rem;
}

.auth-hint {
  text-align: center;
  margin-top: 1.1rem;
  font-size: 0.85rem;
  color: #64748b;
}

.auth-hint a {
  color: #1765a5;
  font-weight: 600;
  text-decoration: none;
}

@media (max-width: 520px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }
}
</style>