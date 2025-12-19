'use client'

import { useQuery } from '@tanstack/react-query'
import { analisis } from '@/lib/api'
import Link from 'next/link'
import { FileText, Clock, Wifi } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'

export default function AnalisisListPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['analisis'],
    queryFn: () => analisis.listar({ limit: 50 }),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner w-8 h-8" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Mis Análisis</h1>
          <p className="text-slate-600 mt-2">Historial completo de análisis realizados</p>
        </div>
        <Link href="/analisis/nuevo" className="btn btn-primary">
          + Nuevo Análisis
        </Link>
      </div>

      {!data || data.length === 0 ? (
        <div className="card text-center py-12">
          <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-600 mb-4">No hay análisis realizados aún</p>
          <Link href="/analisis/nuevo" className="btn btn-primary inline-flex">
            Crear primer análisis
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {data.map((item: any) => (
            <Link
              key={item.id}
              href={`/analisis/${item.id}`}
              className="card hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <Wifi className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900">{item.mac_address}</p>
                    <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                      <Clock className="w-4 h-4" />
                      {formatDistanceToNow(new Date(item.created_at), {
                        addSuffix: true,
                        locale: es,
                      })}
                    </div>
                  </div>
                </div>
                <span className={`badge ${
                  item.estado === 'completado' ? 'badge-success' : 'badge-warning'
                }`}>
                  {item.estado}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
