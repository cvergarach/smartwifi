'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { analisis as analisisApi } from '@/lib/api'
import toast from 'react-hot-toast'
import { Wifi, AlertCircle, CheckCircle } from 'lucide-react'

export default function NuevoAnalisisPage() {
  const router = useRouter()
  const [macAddress, setMacAddress] = useState('')
  const [incluirEventos, setIncluirEventos] = useState(true)

  const mutation = useMutation({
    mutationFn: (data: { mac_address: string; incluir_eventos: boolean }) =>
      analisisApi.crear(data),
    onSuccess: (data) => {
      toast.success('¡Análisis completado exitosamente!')
      router.push(`/analisis/${data.id}`)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Error al crear análisis')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!macAddress.trim()) {
      toast.error('Ingresa una dirección MAC')
      return
    }

    mutation.mutate({
      mac_address: macAddress.trim(),
      incluir_eventos: incluirEventos,
    })
  }

  const formatMAC = (value: string) => {
    // Eliminar caracteres no permitidos
    const cleaned = value.replace(/[^0-9A-Fa-f]/g, '')
    
    // Formatear con dos puntos cada 2 caracteres
    const formatted = cleaned.match(/.{1,2}/g)?.join(':') || cleaned
    
    return formatted.toUpperCase().slice(0, 17) // Máximo AA:BB:CC:DD:EE:FF
  }

  const handleMACChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatMAC(e.target.value)
    setMacAddress(formatted)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Nuevo Análisis de Gateway
        </h1>
        <p className="text-slate-600 mt-2">
          Analiza un gateway WiFi y obtén un informe detallado generado por IA
        </p>
      </div>

      {/* Formulario */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dirección MAC */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Dirección MAC del Gateway
            </label>
            <div className="relative">
              <Wifi className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={macAddress}
                onChange={handleMACChange}
                placeholder="AA:BB:CC:DD:EE:FF"
                className="input pl-10 font-mono"
                disabled={mutation.isPending}
                required
              />
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Formato: AA:BB:CC:DD:EE:FF (se formatea automáticamente)
            </p>
          </div>

          {/* Incluir Eventos */}
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              id="incluirEventos"
              checked={incluirEventos}
              onChange={(e) => setIncluirEventos(e.target.checked)}
              className="mt-1"
              disabled={mutation.isPending}
            />
            <div>
              <label 
                htmlFor="incluirEventos" 
                className="font-medium text-slate-900 cursor-pointer"
              >
                Incluir historial de eventos
              </label>
              <p className="text-sm text-slate-600 mt-1">
                Obtén información sobre reinicios, cambios de canal y otros eventos del gateway
              </p>
            </div>
          </div>

          {/* Info Box */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-900 mb-1">
                  ¿Qué incluye el análisis?
                </p>
                <ul className="text-blue-700 space-y-1 list-disc list-inside">
                  <li>Información básica del gateway</li>
                  <li>Dispositivos conectados y su calidad de señal</li>
                  <li>Configuración WiFi (2.4GHz y 5GHz)</li>
                  <li>Análisis de interferencia con redes vecinas</li>
                  <li>Estado de puertos LAN</li>
                  <li>Recomendaciones accionables generadas por IA</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Botón Submit */}
          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full btn btn-primary flex items-center justify-center gap-2"
          >
            {mutation.isPending ? (
              <>
                <div className="spinner w-5 h-5" />
                <span>Analizando gateway...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                <span>Iniciar Análisis</span>
              </>
            )}
          </button>
        </form>

        {/* Mensaje de progreso */}
        {mutation.isPending && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex gap-3">
              <div className="spinner w-5 h-5 text-yellow-600" />
              <div className="text-sm">
                <p className="font-medium text-yellow-900 mb-1">
                  Análisis en progreso...
                </p>
                <p className="text-yellow-700">
                  Estamos consultando la API del gateway y generando el informe con IA. 
                  Esto puede tardar hasta 30 segundos.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Ejemplos */}
      <div className="card">
        <h3 className="font-semibold text-slate-900 mb-4">
          Ejemplos de direcciones MAC válidas
        </h3>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
            <code className="font-mono text-primary-600">AA:BB:CC:DD:EE:FF</code>
            <span className="text-slate-600">Formato con dos puntos</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
            <code className="font-mono text-primary-600">AABBCCDDEEFF</code>
            <span className="text-slate-600">Sin separadores (se formatea automáticamente)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
