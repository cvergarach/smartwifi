// ============================================
// STORE.TS - Estado global con Zustand
// ============================================

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// ============================================
// TIPOS
// ============================================

export interface Usuario {
  id: string
  email: string
  nombre?: string
  rol: 'admin' | 'user'
  activo: boolean
  created_at: string
}

export interface AuthState {
  token: string | null
  usuario: Usuario | null
  isAuthenticated: boolean
  isAdmin: boolean
  login: (token: string, usuario: Usuario) => void
  logout: () => void
}

// ============================================
// STORE DE AUTENTICACIÓN
// ============================================

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      usuario: null,
      isAuthenticated: false,
      isAdmin: false,
      
      login: (token, usuario) => {
        set({
          token,
          usuario,
          isAuthenticated: true,
          isAdmin: usuario.rol === 'admin',
        })
      },
      
      logout: () => {
        set({
          token: null,
          usuario: null,
          isAuthenticated: false,
          isAdmin: false,
        })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
