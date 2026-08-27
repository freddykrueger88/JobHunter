/**
 * Erweiterte Dashboard-Statistiken mit Recharts.
 * Zeigt Funnel, wochentliche Bewerbungsrate und Status-Verteilung.
 */
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, FunnelChart, Funnel, LabelList,
} from 'recharts'
import axios from 'axios'

const STATUS_COLORS: Record<string, string> = {
  interessant: '#a855f7',
  beworben:    '#3b82f6',
  interview:   '#f59e0b',
  angenommen:  '#10b981',
  absage:      '#ef4444',
}

interface Stats {
  gesamt: number
  nach_status?: Record<string, number>
}

interface WeeklyEntry {
  woche: string
  anzahl: number
}

export default function StatsChart() {
  const { t } = useTranslation('statsChart')
  const [stats, setStats] = useState<Stats | null>(null)
  const [weekly, setWeekly] = useState<WeeklyEntry[]>([])

  useEffect(() => {
    axios.get('/api/stats/').then(r => setStats(r.data))
    axios.get('/api/stats/weekly').then(r => setWeekly(r.data))
  }, [])

  if (!stats) return <div className="animate-pulse h-40 bg-gray-100 dark:bg-gray-800 rounded-xl" />

  const statusData = Object.entries(stats.nach_status || {}).map(([key, value]) => ({
    key,
    name: t(`statusLabels.${key}`, key),
    value,
  }))
  const funnelData = [
    { name: t('funnelLabels.applied'),   value: stats.gesamt },
    { name: t('funnelLabels.interview'), value: (stats.nach_status?.interview || 0) + (stats.nach_status?.angenommen || 0) },
    { name: t('funnelLabels.offer'),     value: stats.nach_status?.angenommen || 0 },
  ].filter(d => d.value > 0)

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Status-Verteilung */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
        <h3 className="font-semibold mb-4 text-sm text-gray-500">{t('statusDistribution')}</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={statusData} dataKey="value" nameKey="name"
              cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
              {statusData.map((entry, i) => (
                <Cell key={i} fill={STATUS_COLORS[entry.key] ?? '#94a3b8'} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Wochentliche Rate */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
        <h3 className="font-semibold mb-4 text-sm text-gray-500">{t('weeklyRate')}</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={weekly}>
            <XAxis dataKey="woche" tick={{ fontSize: 11 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="anzahl" fill="#3b82f6" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Funnel */}
      {funnelData.length > 1 && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm md:col-span-2">
          <h3 className="font-semibold mb-4 text-sm text-gray-500">{t('funnel')}</h3>
          <ResponsiveContainer width="100%" height={180}>
            <FunnelChart>
              <Funnel dataKey="value" data={funnelData} isAnimationActive>
                {funnelData.map((entry, i) => (
                  <Cell key={i} fill={['#3b82f6','#f59e0b','#10b981'][i] ?? '#94a3b8'} />
                ))}
                <LabelList position="center" fill="#fff" fontSize={12} />
              </Funnel>
              <Tooltip />
            </FunnelChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
