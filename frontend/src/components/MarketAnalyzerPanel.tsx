/**
 * Marktlage-Analyse-Panel: KI bewertet Wettbewerb, optimalen Zeitpunkt
 * und empfiehlt eine Bewerbungsstrategie.
 */
import { useState } from 'react'
import axios from 'axios'
import clsx from 'clsx'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  Briefcase,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  AlertTriangle,
} from 'lucide-react'

interface Heuristik {
  dringlichkeit: boolean
  team_wachstum: boolean
  fluktuation: boolean
}

interface MarketResult {
  wettbewerb: 'niedrig' | 'mittel' | 'hoch'
  wettbewerb_begruendung: string
  optimaler_zeitpunkt: 'sofort' | '1 Woche' | '2 Wochen'
  zeitpunkt_begruendung: string
  unternehmenstyp: 'startup' | 'kmu' | 'konzern' | 'behoerde' | 'unbekannt'
  strategie: string
  strategie_begruendung: string
  chancen: string[]
  risiken: string[]
  heuristik: Heuristik
}

interface Props {
  applicationId: number
  jobTitle: string
  firma: string
  jobDescription: string
}

const wettbewerbConfig = {
  niedrig: {
    Icon: TrendingDown,
    color: 'text-green-600',
    bg: 'bg-green-50 dark:bg-green-900/20',
    label: 'Geringer Wettbewerb',
  },
  mittel: {
    Icon: Minus,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    label: 'Mittlerer Wettbewerb',
  },
  hoch: {
    Icon: TrendingUp,
    color: 'text-red-600',
    bg: 'bg-red-50 dark:bg-red-900/20',
    label: 'Hoher Wettbewerb',
  },
}

const unternehmensTypLabel: Record<string, string> = {
  startup: '🚀 Startup',
  kmu: '🏢 KMU',
  konzern: '🏭 Konzern',
  behoerde: '🏛️ Behörde',
  unbekannt: '❓ Unbekannt',
}

export default function MarketAnalyzerPanel({
  applicationId,
  jobTitle,
  firma,
  jobDescription,
}: Props) {
  const [result, setResult] = useState<MarketResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const { data } = await axios.post(
        `/api/applications/${applicationId}/market-analysis`,
        {
          job_title: jobTitle,
          firma,
          job_description: jobDescription,
        }
      )
      setResult(data)
      setExpanded(true)
    } finally {
      setLoading(false)
    }
  }

  const cfg = result ? wettbewerbConfig[result.wettbewerb] : null

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800">
        <div>
          <p className="font-semibold text-sm">Marktlage-Analyse</p>
          <p className="text-xs text-gray-400">Wettbewerb · Timing · Strategie</p>
        </div>
        <button
          onClick={run}
          disabled={loading}
          className="px-4 py-1.5 rounded-xl text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Analysiere…' : 'Analysieren'}
        </button>
      </div>

      {result && cfg && (
        <div className={clsx('p-4 space-y-4', cfg.bg)}>

          {/* Wettbewerb-Level */}
          <div className="flex items-center gap-3">
            <cfg.Icon size={28} className={cfg.color} aria-hidden />
            <div>
              <p className={clsx('text-lg font-bold', cfg.color)}>{cfg.label}</p>
              <p className="text-xs text-gray-500">{result.wettbewerb_begruendung}</p>
            </div>
          </div>

          {/* Unternehmenstyp + Timing */}
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl bg-white/60 dark:bg-gray-700/40 p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <Briefcase size={14} className="text-gray-400" aria-hidden />
                <p className="text-xs font-medium text-gray-500">Unternehmenstyp</p>
              </div>
              <p className="text-sm font-semibold">
                {unternehmensTypLabel[result.unternehmenstyp] ?? result.unternehmenstyp}
              </p>
            </div>
            <div className="rounded-xl bg-white/60 dark:bg-gray-700/40 p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <Clock size={14} className="text-gray-400" aria-hidden />
                <p className="text-xs font-medium text-gray-500">Optimaler Zeitpunkt</p>
              </div>
              <p className="text-sm font-semibold">{result.optimaler_zeitpunkt}</p>
              <p className="text-xs text-gray-400 mt-0.5">{result.zeitpunkt_begruendung}</p>
            </div>
          </div>

          {/* Heuristik-Badges */}
          <div className="flex flex-wrap gap-2">
            {result.heuristik.dringlichkeit && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300">
                ⚡ Dringend gesucht
              </span>
            )}
            {result.heuristik.team_wachstum && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                📈 Team wächst
              </span>
            )}
            {result.heuristik.fluktuation && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                🔄 Nachbesetzung
              </span>
            )}
          </div>

          {/* Strategie */}
          <div className="rounded-xl bg-white/60 dark:bg-gray-700/40 p-3">
            <p className="text-xs font-medium text-gray-500 mb-1">Empfohlene Strategie</p>
            <p className="text-sm font-semibold">{result.strategie}</p>
            <p className="text-xs text-gray-400 mt-0.5">{result.strategie_begruendung}</p>
          </div>

          {/* Chancen & Risiken */}
          <div>
            <button
              onClick={() => setExpanded(e => !e)}
              className="flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-700"
              aria-expanded={expanded}
            >
              {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              Chancen & Risiken
            </button>

            {expanded && (
              <div className="mt-2 grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs font-medium text-green-600 mb-1 flex items-center gap-1">
                    <Lightbulb size={12} aria-hidden /> Chancen
                  </p>
                  <ul className="space-y-1">
                    {result.chancen.map((c, i) => (
                      <li key={i} className="text-xs text-gray-600 dark:text-gray-300">• {c}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="text-xs font-medium text-red-500 mb-1 flex items-center gap-1">
                    <AlertTriangle size={12} aria-hidden /> Risiken
                  </p>
                  <ul className="space-y-1">
                    {result.risiken.map((r, i) => (
                      <li key={i} className="text-xs text-gray-600 dark:text-gray-300">• {r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
