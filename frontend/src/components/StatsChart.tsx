/**
 * Erweiterte Dashboard-Statistiken mit Recharts.
 * Zeigt Funnel, wochentliche Bewerbungsrate und Status-Verteilung.
 */
import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, FunnelChart, Funnel, LabelList,
} from 'recharts'
import axios from 'axios'

const STATUS_COLORS: Record<string, string> = {
  beworben:    '#3b82f6',
  eingeladen:  '#8b5cf6',
  gespraech:   '#f59e0b',
  zusage:      '#10b981',
  absage:      '#ef4444',
  zurueckgezogen: '#6b7280',
}

export default function StatsChart() {
  const [stats, setStats] = useState<any>(null)
  const [weekly, setWeekly] = useState<any[]>([])

  useEffect(() => {
    axios.get('/api/stats/').then(r => setStats(r.data))
    axios.get('/api/stats/weekly').then(r => setWeekly(r.data))
  }, [])

  if (!stats) return <div className="animate-pulse h-40 bg-gray-100 dark:bg-gray-800 rounded-xl" />

  const statusData = Object.entries(stats.nach_status || {}).map(([name, value]) => ({ name, value }))
  const funnelData = [
    { name: 'Beworben',    value: stats.gesamt },
    { name: 'Eingeladen',  value: (stats.nach_status?.eingeladen || 0) + (stats.nach_status?.gespraech || 0) },
    { name: 'Gespraech',   value: stats.nach_status?.gespraech || 0 },
    { name: 'Zusage',      value: stats.nach_status?.zusage || 0 },
  ].filter(d => d.value > 0)

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Status-Verteilung */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
        <h3 className="font-semibold mb-4 text-sm text-gray-500">Status-Verteilung</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={statusData} dataKey="value" nameKey="name"
              cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
              {statusData.map((entry, i) => (
                <Cell key={i} fill={STATUS_COLORS[entry.name] ?? '#94a3b8'} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Wochentliche Rate */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm">
        <h3 className="font-semibold mb-4 text-sm text-gray-500">Bewerbungen pro Woche</h3>
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
          <h3 className="font-semibold mb-4 text-sm text-gray-500">Bewerbungs-Funnel</h3>
          <ResponsiveContainer width="100%" height={180}>
            <FunnelChart>
              <Funnel dataKey="value" data={funnelData} isAnimationActive>
                {funnelData.map((entry, i) => (
                  <Cell key={i} fill={['#3b82f6','#8b5cf6','#f59e0b','#10b981'][i] ?? '#94a3b8'} />
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
