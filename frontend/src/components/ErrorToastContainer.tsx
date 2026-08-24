/**
 * Einheitliche Fehleranzeige fuer alle ueber lib/api.ts laufenden
 * API-Aufrufe (Rework-Plan Phase D.1, Audit-Befund REPOSITORY_AUDIT_DE.md
 * 1.2 "kein zentraler Frontend-API-Client" / "keine einheitliche
 * Fehleranzeige"). Baut visuell auf dem UndoToast-Muster auf, hoert aber
 * auf das globale API_ERROR_EVENT statt einen lokalen Hook-State zu
 * nutzen, da der Ausloeser (axios-Interceptor) ausserhalb des
 * React-Baums liegt.
 */
import { useEffect, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { AlertCircle, X } from 'lucide-react'
import { API_ERROR_EVENT } from '../lib/errorToast'

interface ToastItem {
  id: number
  message: string
}

let nextId = 0
const AUTO_DISMISS_MS = 6000

export default function ErrorToastContainer() {
  const { t } = useTranslation('errorToastContainer')
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const dismiss = useCallback((id: number) => {
    setToasts(prev => prev.filter(item => item.id !== id))
  }, [])

  useEffect(() => {
    const handler = (e: Event) => {
      const message = (e as CustomEvent<string>).detail
      const id = nextId++
      setToasts(prev => [...prev, { id, message }])
      setTimeout(() => dismiss(id), AUTO_DISMISS_MS)
    }
    window.addEventListener(API_ERROR_EVENT, handler)
    return () => window.removeEventListener(API_ERROR_EVENT, handler)
  }, [dismiss])

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-6 left-6 z-50 flex flex-col gap-2 max-w-sm" aria-live="assertive">
      {toasts.map(toast => (
        <div
          key={toast.id}
          role="alert"
          className="flex items-start gap-2 bg-red-600 text-white rounded-xl shadow-2xl px-4 py-3"
        >
          <AlertCircle size={18} className="shrink-0 mt-0.5" aria-hidden />
          <span className="text-sm font-medium flex-1">{toast.message}</span>
          <button
            onClick={() => dismiss(toast.id)}
            className="shrink-0 text-red-100 hover:text-white transition-colors"
            aria-label={t('dismissAriaLabel')}
          >
            <X size={16} aria-hidden />
          </button>
        </div>
      ))}
    </div>
  )
}
