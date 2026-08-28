/**
 * Branchen-Radar (#76, G.3.9): regionale Jobmarkt-Trends aus den
 * integrierten Portalen aggregiert. Siehe
 * backend/services/market_trends.py fuer die Branchen-Klassifikation
 * (einfache mehrsprachige Stichwort-Zuordnung, keine amtliche
 * Klassifikation) und die Trend-Definition (Vergleich zweier
 * aufeinanderfolgender Zeitfenster).
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Radar, TrendingUp, TrendingDown, Sparkles } from 'lucide-react'

interface BrancheEntry {
  branche: string
  aktuell: number
  vorher: number
  veraenderung_prozent: number | null
  trend: 'wachsend' | 'schrumpfend' | 'stabil' | 'neu'
}

interface MarketTrends {
  zeitraum_tage: number
  branchen: BrancheEntry[]
  top_wachsend: BrancheEntry[]
  top_schrumpfend: BrancheEntry[]
}

const TREND_COLORS: Record<BrancheEntry['trend'], string> = {
  wachsend: 'text-green-500',
  neu: 'text-blue-500',
  schrumpfend: 'text-red-500',
  stabil: 'text-gray-400',
}

function ChangeLabel({ entry, t }: { entry: BrancheEntry; t: (key: string) => string }) {
  if (entry.veraenderung_prozent === null) {
    return <span className={TREND_COLORS[entry.trend]}>{t('new')}</span>
  }
  const sign = entry.veraenderung_prozent > 0 ? '+' : ''
  return <span className={TREND_COLORS[entry.trend]}>{sign}{entry.veraenderung_prozent}%</span>
}

export default function BranchenRadar() {
  const { t } = useTranslation('branchenRadar')
  const [city, setCity] = useState('')
  const [postalCode, setPostalCode] = useState('')

  const { data, isLoading } = useQuery<MarketTrends>({
    queryKey: ['market-trends', city, postalCode],
    queryFn: () => axios.get('/api/stats/market-trends', {
      params: { city: city || undefined, postal_code: postalCode || undefined },
    }).then(r => r.data),
  })

  return (
    <div className="max-w-3xl mx-auto py-8">
      <div className="flex items-center gap-3 mb-2">
        <Radar size={28} className="text-blue-500" aria-hidden />
        <div>
          <h1 className="text-2xl font-bold">{t('title')}</h1>
          <p className="text-sm text-gray-400">{t('subtitle')}</p>
        </div>
      </div>

      <div className="flex gap-2 my-6">
        <input
          type="text"
          value={city}
          onChange={e => setCity(e.target.value)}
          placeholder={t('cityPlaceholder')}
          className="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          aria-label={t('cityPlaceholder')}
        />
        <input
          type="text"
          value={postalCode}
          onChange={e => setPostalCode(e.target.value)}
          placeholder={t('postalCodePlaceholder')}
          className="w-40 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          aria-label={t('postalCodePlaceholder')}
        />
      </div>

      {isLoading && <div className="animate-pulse h-40 bg-gray-100 dark:bg-gray-800 rounded-xl" />}

      {!isLoading && data && data.branchen.length === 0 && (
        <p className="text-sm text-gray-400">{t('noData')}</p>
      )}

      {!isLoading && data && data.branchen.length > 0 && (
        <div className="space-y-6">
          {(data.top_wachsend.length > 0 || data.top_schrumpfend.length > 0) && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {data.top_wachsend.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm">
                  <p className="text-sm font-medium mb-3 flex items-center gap-2">
                    <TrendingUp size={16} className="text-green-500" aria-hidden />
                    {t('topGrowing')}
                  </p>
                  <ul className="space-y-2">
                    {data.top_wachsend.map(e => (
                      <li key={e.branche} className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-1.5">
                          {e.trend === 'neu' && <Sparkles size={12} className="text-blue-500" aria-hidden />}
                          {e.branche}
                        </span>
                        <ChangeLabel entry={e} t={t} />
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {data.top_schrumpfend.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm">
                  <p className="text-sm font-medium mb-3 flex items-center gap-2">
                    <TrendingDown size={16} className="text-red-500" aria-hidden />
                    {t('topShrinking')}
                  </p>
                  <ul className="space-y-2">
                    {data.top_schrumpfend.map(e => (
                      <li key={e.branche} className="flex items-center justify-between text-sm">
                        <span>{e.branche}</span>
                        <ChangeLabel entry={e} t={t} />
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm">
            <p className="text-sm font-medium mb-3">{t('allBranches', { days: data.zeitraum_tage })}</p>
            <ul className="space-y-2.5">
              {data.branchen.map(e => (
                <li key={e.branche} className="flex items-center gap-3 text-sm">
                  <span className="w-48 shrink-0 truncate text-gray-600 dark:text-gray-300">{e.branche}</span>
                  <span className="w-16 shrink-0 text-gray-400">{e.aktuell}</span>
                  <ChangeLabel entry={e} t={t} />
                </li>
              ))}
            </ul>
          </div>

          <p className="text-xs text-gray-300 dark:text-gray-500">{t('methodHint')}</p>
        </div>
      )}
    </div>
  )
}
