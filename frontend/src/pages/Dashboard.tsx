import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import { formatDateTime } from '../lib/formatDate'
import { Briefcase, XCircle, CheckCircle, MessageSquare, Star, Bell, BellOff } from 'lucide-react'
import BadgesPanel from '../components/BadgesPanel'
import StatsChart from '../components/StatsChart'
import WeeklyGoalWidget from '../components/WeeklyGoalWidget'

interface DueReminder {
  id: number
  message: string | null
  remind_at: string
  application_id: number | null
}

interface HistoryEntry {
  id: number
  type: string
  description: string
  meta: unknown
  at: string
}

interface DashboardStats {
  counts: Record<string, number>
  total: number
  recent_activity: HistoryEntry[]
  due_reminders: DueReminder[]
}

const fetchStats = (): Promise<DashboardStats> => api.get('/dashboard/stats').then(r => r.data)

const statConfig = [
  { key: 'beworben',    icon: Briefcase,     color: 'bg-blue-500',   tKey: 'applied' },
  { key: 'absage',      icon: XCircle,       color: 'bg-red-500',    tKey: 'rejected' },
  { key: 'angenommen',  icon: CheckCircle,   color: 'bg-green-500',  tKey: 'accepted' },
  { key: 'interview',   icon: MessageSquare, color: 'bg-yellow-500', tKey: 'interview' },
  { key: 'interessant', icon: Star,          color: 'bg-purple-500', tKey: 'open' },
]

export default function Dashboard() {
  const { t, i18n } = useTranslation(['dashboard', 'common'])
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    refetchInterval: 30000, // alle 30s aktualisieren
  })

  const dismissReminder = useMutation({
    mutationFn: (id: number) => api.patch(`/reminders/${id}/done`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['stats'] }),
  })

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{t('title')}</h1>

      {/* Fällige Erinnerungen */}
      {(data?.due_reminders?.length ?? 0) > 0 && (
        <div className="mb-6 space-y-2">
          {data?.due_reminders.map((r) => (
            <div key={r.id} className="flex items-center gap-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded-xl px-4 py-3">
              <Bell size={16} className="text-yellow-500 shrink-0" aria-hidden />
              <span className="flex-1 text-sm">{r.message ?? t('reminderDefaultMessage')}</span>
              <button
                onClick={() => dismissReminder.mutate(r.id)}
                className="text-gray-400 hover:text-gray-600"
                aria-label={t('dismissReminderAriaLabel')}
              >
                <BellOff size={15} aria-hidden />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Counter-Kacheln */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        {statConfig.map(({ key, icon: Icon, color, tKey }) => (
          <div
            key={key}
            className="rounded-xl p-4 bg-gray-100 dark:bg-gray-800 flex flex-col items-center gap-2 shadow"
          >
            <div className={`${color} rounded-full p-2`}>
              <Icon size={20} className="text-white" aria-hidden />
            </div>
            <span className="text-2xl font-bold">
              {isLoading ? '–' : (data?.counts?.[key] ?? 0)}
            </span>
            <span className="text-xs text-gray-500 dark:text-gray-400 text-center">{t(tKey)}</span>
          </div>
        ))}
      </div>

      {/* Gesamt */}
      {!isLoading && (
        <p className="text-sm text-gray-500 mb-6">
          {t('totalBefore')} <strong>{data?.total ?? 0}</strong> {t('totalAfter')}
        </p>
      )}

      {/* Wochenziel */}
      <div className="mb-8">
        <WeeklyGoalWidget />
      </div>

      {/* Abzeichen */}
      <div className="mb-8">
        <BadgesPanel />
      </div>

      {/* Erweiterte Statistiken */}
      <div className="mb-8">
        <StatsChart />
      </div>

      {/* Letzte Aktivitäten */}
      <h2 className="text-lg font-semibold mb-3">{t('recentActivityHeading')}</h2>
      <ul className="space-y-2">
        {isLoading && <li className="text-gray-400">{t('common:loading')}</li>}
        {data?.recent_activity?.map((entry) => (
          <li key={entry.id} className="flex items-start gap-3 bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2 text-sm">
            <span className="text-gray-400 text-xs whitespace-nowrap mt-0.5">
              {formatDateTime(entry.at, i18n.language)}
            </span>
            <span>{entry.description}</span>
          </li>
        ))}
        {!isLoading && !data?.recent_activity?.length && (
          <li className="text-gray-400 text-sm">{t('noActivity')}</li>
        )}
      </ul>
    </div>
  )
}
