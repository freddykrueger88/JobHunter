/**
 * Bewerbungs-Qualitaetsscore: Gewichteter Score aus allen KI-Tools.
 * Zeigt Fortschrittsring, Checkliste und naechsten Schritt.
 */
import { useEffect, useState } from 'react'
import axios from 'axios'
import clsx from 'clsx'
import { CheckCircle2, Circle, ArrowRight } from 'lucide-react'

interface CheckItem {
  key: string
  label: string
  erledigt: boolean
  score: number
  link: string | null
}

interface QualityResult {
  gesamt_score: number
  ampel: 'gruen' | 'gelb' | 'rot'
  checklist: CheckItem[]
  naechster_schritt: CheckItem | null
  vollstaendig: boolean
}

interface Props { applicationId: number }

const AMPEL_COLORS = {
  gruen: '#10b981',
  gelb:  '#f59e0b',
  rot:   '#ef4444',
}

export default function QualityScoreCard({ applicationId }: Props) {
  const [data, setData] = useState<QualityResult | null>(null)

  useEffect(() => {
    axios.get(`/api/applications/${applicationId}/quality-score`).then(r => setData(r.data))
  }, [applicationId])

  if (!data) return <div className="animate-pulse h-32 bg-gray-100 dark:bg-gray-800 rounded-2xl" />

  const r = 36
  const circ = 2 * Math.PI * r
  const dash = (data.gesamt_score / 100) * circ

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center gap-4">
        {/* Fortschrittsring */}
        <svg width="90" height="90" aria-hidden>
          <circle cx="45" cy="45" r={r} fill="none" stroke="#e5e7eb" strokeWidth="8" />
          <circle
            cx="45" cy="45" r={r} fill="none"
            stroke={AMPEL_COLORS[data.ampel]}
            strokeWidth="8"
            strokeDasharray={`${dash} ${circ}`}
            strokeLinecap="round"
            transform="rotate(-90 45 45)"
            style={{ transition: 'stroke-dasharray 0.6s ease' }}
          />
          <text x="45" y="50" textAnchor="middle" fontSize="16" fontWeight="bold"
            fill={AMPEL_COLORS[data.ampel]}>{data.gesamt_score}</text>
        </svg>
        <div>
          <p className="font-semibold">Bewerbungsqualität</p>
          <p className="text-xs text-gray-400">
            {data.vollstaendig ? '✅ Vollständig' : `${data.checklist.filter(c => c.erledigt).length}/${data.checklist.length} Schritte erledigt`}
          </p>
        </div>
      </div>

      {/* Checkliste */}
      <ul className="space-y-1.5" role="list">
        {data.checklist.map(item => (
          <li key={item.key} className="flex items-center gap-2 text-sm">
            {item.erledigt
              ? <CheckCircle2 size={16} className="text-green-500 shrink-0" aria-hidden />
              : <Circle       size={16} className="text-gray-300 shrink-0" aria-hidden />}
            <span className={clsx(item.erledigt ? 'text-gray-700 dark:text-gray-200' : 'text-gray-400')}>
              {item.label}
            </span>
            {!item.erledigt && item.link && (
              <a href={item.link} className="ml-auto text-xs text-blue-500 hover:underline flex items-center gap-0.5">
                Jetzt <ArrowRight size={11} />
              </a>
            )}
          </li>
        ))}
      </ul>

      {/* Naechster Schritt */}
      {data.naechster_schritt && (
        <div className="text-xs bg-blue-50 dark:bg-blue-900/20 rounded-xl p-3">
          <span className="font-medium text-blue-600">Nächster Schritt: </span>
          <span className="text-gray-600 dark:text-gray-300">{data.naechster_schritt.label}</span>
          {data.naechster_schritt.link && (
            <a href={data.naechster_schritt.link} className="ml-2 text-blue-500 hover:underline">Starten →</a>
          )}
        </div>
      )}
    </div>
  )
}
