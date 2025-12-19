// ============================================
// API.TS - Cliente API con Axios
// ============================================

import axios, { AxiosInstance, AxiosError } from 'axios'
import { useAuthStore } from './store'
import toast from 'react-hot-toast'

// ============================================
// CONFIGURACIÓN BASE
// ============================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ============================================
// INSTANCIA DE AXIOS
// ============================================

const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================
// INTERCEPTORES
// ============================================

// Request interceptor - Agregar token automáticamente
apiClient.interceptors.request.use(
  (config) => {
    const { token } = useAuthStore.getState()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<any>) => {
    const { logout } = useAuthStore.getState()
    
    // Si el token expiró o es inválido, hacer logout
    if (error.response?.status === 401) {
      logout()
      if (typeof window !== 'undefined') {
        toast.error('Sesión expirada. Por favor inicia sesión nuevamente.')
        window.location.href = '/login'
      }
    }
    
    // Otros errores
    if (error.response?.status === 403) {
      toast.error('No tienes permisos para realizar esta acción')
    }
    
    if (error.response?.status === 500) {
      toast.error('Error del servidor. Intenta más tarde.')
    }
    
    return Promise.reject(error)
  }
)

// ============================================
// FUNCIONES DE API - AUTH
// ============================================

export const auth = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post('/api/auth/login', { email, password })
    return response.data
  },
  
  me: async () => {
    const response = await apiClient.get('/api/auth/me')
    return response.data
  },
  
  logout: async () => {
    const response = await apiClient.post('/api/auth/logout')
    return response.data
  },
}

// ============================================
// FUNCIONES DE API - USUARIOS
// ============================================

export const usuarios = {
  listar: async () => {
    const response = await apiClient.get('/api/usuarios')
    return response.data
  },
  
  crear: async (data: {
    email: string
    password: string
    nombre?: string
    rol?: 'admin' | 'user'
    activo?: boolean
  }) => {
    const response = await apiClient.post('/api/usuarios', data)
    return response.data
  },
  
  actualizar: async (id: string, data: {
    nombre?: string
    rol?: 'admin' | 'user'
    activo?: boolean
    password?: string
  }) => {
    const response = await apiClient.put(`/api/usuarios/${id}`, data)
    return response.data
  },
  
  eliminar: async (id: string) => {
    const response = await apiClient.delete(`/api/usuarios/${id}`)
    return response.data
  },
}

// ============================================
// FUNCIONES DE API - ANÁLISIS
// ============================================

export const analisis = {
  crear: async (data: {
    mac_address: string
    incluir_eventos?: boolean
  }) => {
    const response = await apiClient.post('/api/analisis', data)
    return response.data
  },
  
  listar: async (params?: {
    limit?: number
    offset?: number
  }) => {
    const response = await apiClient.get('/api/analisis', { params })
    return response.data
  },
  
  obtener: async (id: string) => {
    const response = await apiClient.get(`/api/analisis/${id}`)
    return response.data
  },
  
  eliminar: async (id: string) => {
    const response = await apiClient.delete(`/api/analisis/${id}`)
    return response.data
  },
}

// ============================================
// FUNCIONES DE API - CHAT
// ============================================

export const chat = {
  enviar: async (data: {
    analisis_id: string
    pregunta: string
  }) => {
    const response = await apiClient.post('/api/chat', data)
    return response.data
  },
  
  historial: async (analisis_id: string) => {
    const response = await apiClient.get(`/api/chat/${analisis_id}`)
    return response.data
  },
}

// ============================================
// FUNCIONES DE API - ESTADÍSTICAS
// ============================================

export const estadisticas = {
  global: async () => {
    const response = await apiClient.get('/api/estadisticas/global')
    return response.data
  },
}

// ============================================
// HEALTH CHECK
// ============================================

export const health = {
  check: async () => {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export default apiClient
