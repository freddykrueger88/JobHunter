/**
 * Aktivitaets-Heatmap im GitHub-Contribution-Graph-Stil (#79, G.3.7).
 * Ein Kaestchen pro Tag, Wochen als Spalten (Montag-Start, wie der
 * restliche Statistik-Bereich dieses Projekts ISO-Wochen nutzt),
 * Farbintensitaet nach Anzahl Bewerbungen an diesem Tag.
 */
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { formatDate } from '../lib/formatDate'

interface HeatmapEntry {
  datum: string
  anzahl: number
}

const DAYS = 182 // ca. 26 Wochen - passt gut in eine Dashboard-Kachel

function colorForCount(count: number): string {
  if (count === 0) return 'bg-gray-100 dark:bg-gray-800'
  if (count === 1) return 'bg-blue-200 dark:bg-blue-900'
  if (count <= 3) return 'bg-blue-400 dark:bg-blue-700'
  return 'bg-blue-600 dark:bg-blue-500'
}

export default function ActivityHeatmap() {
  const { t, i18n } = useTranslation(['activityHeatmap', 'common'])
  const { data: entries = [] } = useQuery<HeatmapEntry[]>({
    queryKey: ['activity-heatmap'],
    queryFn: () => axios.get('/api/stats/activity-heatmap', { params: { days: DAYS } }).then(r => r.data),
  })

  if (entries.length === 0) return null

  // In Wochen-Spalten gruppieren (Montag = erster Tag). Der allererste
  // Eintrag ist nicht zwingend ein Montag - vorne mit leeren Zellen
  // auffuellen, damit das Raster sauber ausgerichtet ist.
  const firstDate = new Date(entries[0].datum + 'T00:00:00')
  const firstWeekday = (firstDate.getDay() + 6) % 7 // 0 = Montag
  const padded: (HeatmapEntry | null)[] = [
    ...Array(firstWeekday).fill(null),
    ...entries,
  ]
  const weeks: (HeatmapEntry | null)[][] = []
  for (let i = 0; i < padded.length; i += 7) {
    weeks.push(padded.slice(i, i + 7))
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm">
      <p className="text-sm font-medium mb-3">{t('title')}</p>
      <div className="flex gap-1 overflow-x-auto pb-1">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((entry, di) => (
              <div
                key={di}
                className={`w-3 h-3 rounded-sm ${entry ? colorForCount(entry.anzahl) : 'bg-transparent'}`}
                title={entry ? `${formatDate(entry.datum, i18n.language)}: ${t('count', { count: entry.anzahl })}` : undefined}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-1.5 mt-3 text-xs text-gray-400">
        <span>{t('less')}</span>
        <div className="w-3 h-3 rounded-sm bg-gray-100 dark:bg-gray-800" />
        <div className="w-3 h-3 rounded-sm bg-blue-200 dark:bg-blue-900" />
        <div className="w-3 h-3 rounded-sm bg-blue-400 dark:bg-blue-700" />
        <div className="w-3 h-3 rounded-sm bg-blue-600 dark:bg-blue-500" />
        <span>{t('more')}</span>
      </div>
    </div>
  )
}
