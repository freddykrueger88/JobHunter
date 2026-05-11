import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Briefcase, XCircle, CheckCircle, MessageSquare, Star } from 'lucide-react'

const fetchStats = () => axios.get('/api/dashboard/stats').then(r => r.data)

const statConfig = [
  { key: 'beworben',    icon: Briefcase,     color: 'bg-blue-500',   tKey: 'applied' },
  { key: 'absage',      icon: XCircle,       color: 'bg-red-500',    tKey: 'rejected' },
  { key: 'angenommen',  icon: CheckCircle,   color: 'bg-green-500',  tKey: 'accepted' },
  { key: 'interview',   icon: MessageSquare, color: 'bg-yellow-500', tKey: 'interview' },
  { key: 'interessant', icon: Star,          color: 'bg-purple-500', tKey: 'open' },
]

export default function Dashboard() {
  const { t } = useTranslation()
  const { data, isLoading } = useQuery({ queryKey: ['stats'], queryFn: fetchStats })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{t('dashboard.title')}</h1>

      {/* Counter-Kacheln */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {statConfig.map(({ key, icon: Icon, color, tKey }) => (
          <div
            key={key}
            className="rounded-xl p-4 bg-gray-100 dark:bg-gray-800 flex flex-col items-center gap-2 shadow"
          >
            <div className={`${color} rounded-full p-2`}>
              <Icon size={20} className="text-white" aria-hidden="true" />
            </div>
            <span className="text-2xl font-bold">
              {isLoading ? '–' : (data?.counts?.[key] ?? 0)}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400">{t(`dashboard.${tKey}`)}</span>
          </div>
        ))}
      </div>

      {/* Letzte Aktivitäten */}
      <h2 className="text-lg font-semibold mb-3">Letzte Aktivitäten</h2>
      <ul className="space-y-2">
        {isLoading && <li className="text-gray-400">{t('common.loading')}</li>}
        {data?.recent_activity?.map((entry: any, i: number) => (
          <li key={i} className="flex items-start gap-3 bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2 text-sm">
            <span className="text-gray-400 text-xs whitespace-nowrap mt-0.5">
              {new Date(entry.at).toLocaleString()}
            </span>
            <span>{entry.description}</span>
          </li>
        ))}
        {!isLoading && !data?.recent_activity?.length && (
          <li className="text-gray-400 text-sm">Noch keine Aktivitäten vorhanden.</li>
        )}
      </ul>
    </div>
  )
}
