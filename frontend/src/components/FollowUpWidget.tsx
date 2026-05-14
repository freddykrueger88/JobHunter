import { useEffect, useState } from 'react'
import axios from 'axios'
import { Bell, CheckCircle, AlertCircle, Clock, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

interface FollowUpItem {
  applicationId: number
  jobTitle: string
  company: string
  followupAt: Date
  status: string
}

type Urgency = 'today' | 'tomorrow' | 'soon'

function getUrgency(date: Date): Urgency {
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = diffMs / (1000 * 60 * 60 * 24)
  if (diffDays <= 0) return 'today'
  if (diffDays <= 1) return 'tomorrow'
  return 'soon'
}

const URGENCY_CONFIG: Record<Urgency, { icon: typeof AlertCircle; color: string; label: string }> = {
  today: { icon: AlertCircle, color: 'text-red-500', label: 'Heute fällig' },
  tomorrow: { icon: Clock, color: 'text-yellow-500', label: 'Morgen fällig' },
  soon: { icon: CheckCircle, color: 'text-green-500', label: '' },
}

export default function FollowUpWidget() {
  const [items, setItems] = useState<FollowUpItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await axios.get('/api/applications/')
        const followups: FollowUpItem[] = []
        for (const app of data) {
          try {
            const notes = JSON.parse(app.notes || '{}')
            if (notes.followup_at) {
              const date = new Date(notes.followup_at)
              if (!isNaN(date.getTime()) && date > new Date(Date.now() - 86400000 * 7)) {
                followups.push({
                  applicationId: app.id,
                  jobTitle: app.job?.title || 'Unbekannte Stelle',
                  company: app.job?.company || 'Unbekannte Firma',
                  followupAt: date,
                  status: app.status,
                })
              }
            }
          } catch {
            // notes ist kein JSON – ignorieren
          }
        }
        // Sortiert: älteste zuerst
        followups.sort((a, b) => a.followupAt.getTime() - b.followupAt.getTime())
        setItems(followups)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2].map(i => (
          <div key={i} className="h-12 rounded-lg bg-gray-100 dark:bg-gray-700 animate-pulse" />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center py-6 text-gray-400">
        <Bell size={28} className="mb-2" aria-hidden />
        <p className="text-sm">Keine Wiedervorlagen fällig</p>
      </div>
    )
  }

  return (
    <ul className="space-y-2" role="list">
      {items.map(item => {
        const urgency = getUrgency(item.followupAt)
        const { icon: Icon, color, label } = URGENCY_CONFIG[urgency]
        return (
          <li key={item.applicationId}>
            <Link
              to={`/applications/${item.applicationId}`}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors group"
            >
              <Icon size={18} className={`flex-shrink-0 ${color}`} aria-hidden />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">
                  {item.jobTitle}
                </p>
                <p className="text-xs text-gray-400 truncate">
                  {item.company}
                  {label && <span className={`ml-2 font-semibold ${color}`}>{label}</span>}
                  {!label && (
                    <span className="ml-2">
                      Nachfassen: {item.followupAt.toLocaleDateString('de-DE')}
                    </span>
                  )}
                </p>
              </div>
              <ChevronRight size={14} className="text-gray-300 group-hover:text-gray-500 flex-shrink-0" aria-hidden />
            </Link>
          </li>
        )
      })}
    </ul>
  )
}
