'use client'

import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/lib/store'
import { analisis, estadisticas } from '@/lib/api'
import { 
  FileText, 
  Users, 
  Activity, 
  TrendingUp,
  Wifi,
  Clock
} from 'lucide-react'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'

export default function DashboardPage() {
  const { usuario, isAdmin } = useAuthStore()

  // Obtener análisis recientes del usuario
  const { data: analisisRecientes, isLoading: loadingAnalisis } = useQuery({
    queryKey: ['analisis', 'recientes'],
    queryFn: () => analisis.listar({ limit: 5 }),
  })

  // Obtener estadísticas globales (solo admin)
  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['estadisticas', 'global'],
    queryFn: estadisticas.global,
    enabled: isAdmin,
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Dashboard
        </h1>
        <p className="text-slate-600 mt-2">
          Bienvenido, {usuario?.nombre || usuario?.email}
        </p>
      </div>

      {/* Stats Cards - Solo para Admin */}
      {isAdmin && stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Usuarios</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.total_usuarios}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  {stats.usuarios_activos} activos
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Análisis</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.total_analisis}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  {stats.analisis_hoy} hoy
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Esta Semana</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">
                  {stats.analisis_semana}
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  Análisis realizados
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Sistema</p>
                <p className="text-2xl font-bold text-slate-900 mt-1">
                  Activo
                </p>
                <p className="text-xs text-green-600 mt-1">
                  Todos los servicios OK
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Acciones Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link 
          href="/analisis/nuevo"
          className="card hover:shadow-lg transition-shadow cursor-pointer group"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
              <Wifi className="w-7 h-7 text-primary-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-900">
                Nuevo Análisis
              </h3>
              <p className="text-sm text-slate-600">
                Analizar un gateway WiFi
              </p>
            </div>
          </div>
        </Link>

        <Link 
          href="/analisis"
          className="card hover:shadow-lg transition-shadow cursor-pointer group"
        >
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
              <FileText className="w-7 h-7 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-900">
                Mis Análisis
              </h3>
              <p className="text-sm text-slate-600">
                Ver historial completo
              </p>
            </div>
          </div>
        </Link>
      </div>

      {/* Análisis Recientes */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">
            Análisis Recientes
          </h2>
          <Link 
            href="/analisis"
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Ver todos →
          </Link>
        </div>

        {loadingAnalisis ? (
          <div className="flex items-center justify-center py-12">
            <div className="spinner w-8 h-8" />
          </div>
        ) : !analisisRecientes || analisisRecientes.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">
              No hay análisis realizados aún
            </p>
            <Link 
              href="/analisis/nuevo"
              className="btn btn-primary inline-flex mt-4"
            >
              Crear primer análisis
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {analisisRecientes.map((item: any) => (
              <Link
                key={item.id}
                href={`/analisis/${item.id}`}
                className="block p-4 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                      <Wifi className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">
                        {item.mac_address}
                      </p>
                      <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                        <Clock className="w-4 h-4" />
                        <span>
                          {formatDistanceToNow(new Date(item.created_at), {
                            addSuffix: true,
                            locale: es,
                          })}
                        </span>
                      </div>
                    </div>
                  </div>
                  <span className={`badge ${
                    item.estado === 'completado' 
                      ? 'badge-success' 
                      : item.estado === 'error'
                      ? 'badge-danger'
                      : 'badge-warning'
                  }`}>
                    {item.estado}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
