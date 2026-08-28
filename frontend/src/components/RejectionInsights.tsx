/**
 * Absagen-Analyse (#73, G.3.12): zeigt, welche strukturellen Signale
 * (Skill-Gap-Score, ATS-Match, Senioritaets-Abgleich) mit einer
 * merklich hoeheren Absage-Quote korrelieren. Siehe
 * backend/services/rejection_pattern.py fuer die Definitionen und die
 * Mindeststichprobe.
 */
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { AlertOctagon, Lightbulb } from 'lucide-react'

interface GroupStats {
  total: number
  absagen: number
  absage_quote: number
}

interface Signal {
  signal: string
  label: string
  risiko_gruppe: GroupStats
  referenz_gruppe: GroupStats
  auffaellig: boolean
}

interface RejectionPatterns {
  gesamt_bewerbungen: number
  gesamt_absagen: number
  genug_daten: boolean
  signale: Signal[]
  empfehlungen: string[]
}

const fetchData = (): Promise<RejectionPatterns> =>
  axios.get('/api/stats/rejection-patterns').then(r => r.data)

export default function RejectionInsights() {
  const { t } = useTranslation('rejectionInsights')
  const { data } = useQuery({ queryKey: ['rejection-patterns'], queryFn: fetchData })

  if (!data) return <div className="animate-pulse h-32 bg-gray-100 dark:bg-gray-800 rounded-xl" />

  const auffaellige = data.signale.filter(s => s.auffaellig)

  if (!data.genug_daten) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm">
        <p className="text-sm font-medium mb-1 flex items-center gap-2">
          <AlertOctagon size={16} className="text-red-500" aria-hidden />
          {t('title')}
        </p>
        <p className="text-xs text-gray-400">
          {t('notEnoughData', { count: data.gesamt_absagen })}
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm space-y-3">
      <p className="text-sm font-medium flex items-center gap-2">
        <AlertOctagon size={16} className="text-red-500" aria-hidden />
        {t('title')}
      </p>

      {auffaellige.length === 0 && (
        <p className="text-xs text-gray-400">{t('noPatterns')}</p>
      )}

      {auffaellige.length > 0 && (
        <ul className="space-y-2">
          {auffaellige.map(s => (
            <li key={s.signal} className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-300">{s.label}</span>
              <span className="text-red-500 font-medium">
                {s.risiko_gruppe.absage_quote}% {t('vs')} {s.referenz_gruppe.absage_quote}%
              </span>
            </li>
          ))}
        </ul>
      )}

      {data.empfehlungen.length > 0 && (
        <div className="space-y-1.5 pt-1 border-t border-gray-100 dark:border-gray-700">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide flex items-center gap-1.5">
            <Lightbulb size={12} aria-hidden />
            {t('recommendations')}
          </p>
          <ul className="space-y-1">
            {data.empfehlungen.map((text, i) => (
              <li key={i} className="text-sm text-gray-600 dark:text-gray-300">{text}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
