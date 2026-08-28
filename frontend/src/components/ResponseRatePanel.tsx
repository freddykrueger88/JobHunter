/**
 * Ruecklaufquoten-Tracker (#78, G.3.8): zeigt, welche Portale/
 * Wochentage/Anschreiben-Laengen zu Antworten fuehren, mit
 * automatisch abgeleiteten Empfehlungen sobald genug Daten vorliegen
 * (siehe backend/services/response_rate_analyzer.py fuer die
 * Mindeststichprobengroesse).
 */
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { TrendingUp, Lightbulb } from 'lucide-react'

interface RateEntry {
  key: string | number
  label?: string
  total: number
  beantwortet: number
  quote: number
}

interface ResponseRateData {
  by_portal: RateEntry[]
  by_weekday: RateEntry[]
  by_cover_letter_length: RateEntry[]
  by_hour: RateEntry[]
  by_days_until_applied: RateEntry[]
  empfehlungen: string[]
}

const fetchData = (): Promise<ResponseRateData> =>
  axios.get('/api/stats/response-rates').then(r => r.data)

function RateBar({ entry, label }: { entry: RateEntry; label: string }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-28 shrink-0 truncate text-gray-600 dark:text-gray-300">{label}</span>
      <div className="flex-1 h-2.5 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full"
          style={{ width: `${entry.quote}%` }}
        />
      </div>
      <span className="w-24 shrink-0 text-right text-xs text-gray-400">
        {entry.quote}% ({entry.beantwortet}/{entry.total})
      </span>
    </div>
  )
}

export default function ResponseRatePanel() {
  const { t } = useTranslation('responseRates')
  const { data } = useQuery({ queryKey: ['response-rates'], queryFn: fetchData })

  if (!data) return <div className="animate-pulse h-40 bg-gray-100 dark:bg-gray-800 rounded-xl" />

  const byPortal = data.by_portal.filter(e => e.total > 0)
  const byWeekday = data.by_weekday.filter(e => e.total > 0)
  const byLength = data.by_cover_letter_length.filter(e => e.total > 0)
  const byHour = data.by_hour.filter(e => e.total > 0)
  const byDaysUntil = data.by_days_until_applied.filter(e => e.total > 0)

  if (byPortal.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm">
        <p className="text-sm font-medium mb-1 flex items-center gap-2">
          <TrendingUp size={16} className="text-blue-500" aria-hidden />
          {t('title')}
        </p>
        <p className="text-xs text-gray-400">{t('notEnoughData')}</p>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm space-y-5">
      <p className="text-sm font-medium flex items-center gap-2">
        <TrendingUp size={16} className="text-blue-500" aria-hidden />
        {t('title')}
      </p>

      {byPortal.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{t('byPortal')}</p>
          {byPortal.map(e => <RateBar key={e.key} entry={e} label={String(e.key)} />)}
        </div>
      )}

      {byWeekday.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{t('byWeekday')}</p>
          {byWeekday.map(e => <RateBar key={e.key} entry={e} label={e.label ?? String(e.key)} />)}
        </div>
      )}

      {byLength.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{t('byLength')}</p>
          {byLength.map(e => <RateBar key={e.key} entry={e} label={e.label ?? String(e.key)} />)}
        </div>
      )}

      {byHour.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{t('byHour')}</p>
          {byHour.map(e => <RateBar key={e.key} entry={e} label={e.label ?? String(e.key)} />)}
        </div>
      )}

      {byDaysUntil.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{t('byDaysUntilApplied')}</p>
          {byDaysUntil.map(e => <RateBar key={e.key} entry={e} label={e.label ?? String(e.key)} />)}
        </div>
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
