/**
 * Burnout-Fruehwarner (#81, G.3.5): warnt auf dem Dashboard, wenn in
 * kurzer Zeit viele Bewerbungen ohne Erfolg abgeschickt wurden
 * (Schwellenwert in den Einstellungen konfigurierbar).
 */
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { HeartPulse } from 'lucide-react'

interface BurnoutCheck {
  warnung: boolean
  anzahl: number
  schwellenwert: number
  tage: number
}

export default function BurnoutWarning() {
  const { t } = useTranslation('burnoutWarning')
  const { data } = useQuery<BurnoutCheck>({
    queryKey: ['burnout-check'],
    queryFn: () => axios.get('/api/stats/burnout-check').then(r => r.data),
  })

  if (!data || !data.warnung) return null

  return (
    <div className="flex items-start gap-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-300 dark:border-orange-700 rounded-xl px-4 py-3 mb-6">
      <HeartPulse size={18} className="text-orange-500 shrink-0 mt-0.5" aria-hidden />
      <div>
        <p className="text-sm font-medium text-orange-800 dark:text-orange-200">
          {t('title')}
        </p>
        <p className="text-sm text-orange-700 dark:text-orange-300 mt-0.5">
          {t('message', { count: data.anzahl, days: data.tage })}
        </p>
      </div>
    </div>
  )
}
