'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  PlusCircle, 
  LogOut, 
  Wifi,
  BarChart3
} from 'lucide-react'
import toast from 'react-hot-toast'

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { usuario, isAdmin, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    toast.success('Sesión cerrada correctamente')
    router.push('/')
  }

  const menuItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      adminOnly: false,
    },
    {
      name: 'Nuevo Análisis',
      href: '/analisis/nuevo',
      icon: PlusCircle,
      adminOnly: false,
    },
    {
      name: 'Mis Análisis',
      href: '/analisis',
      icon: FileText,
      adminOnly: false,
    },
    {
      name: 'Usuarios',
      href: '/usuarios',
      icon: Users,
      adminOnly: true,
    },
    {
      name: 'Estadísticas',
      href: '/estadisticas',
      icon: BarChart3,
      adminOnly: true,
    },
  ]

  const visibleItems = menuItems.filter(item => !item.adminOnly || isAdmin)

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Wifi className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900">WiFi Analyzer</h1>
            <p className="text-xs text-slate-500">Claro Chile</p>
          </div>
        </div>
      </div>

      {/* Usuario Info */}
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-700 font-semibold text-sm">
              {usuario?.nombre?.charAt(0) || usuario?.email?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm text-slate-900 truncate">
              {usuario?.nombre || 'Usuario'}
            </p>
            <p className="text-xs text-slate-500 truncate">
              {usuario?.email}
            </p>
            {isAdmin && (
              <span className="inline-block mt-1 px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded">
                Admin
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Menú */}
      <nav className="flex-1 p-4 space-y-1">
        {visibleItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                ${isActive 
                  ? 'bg-primary-50 text-primary-700 font-medium' 
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }
              `}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-slate-200">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>
  )
}
