/**
 * ATS-Score-Panel: Zeigt Keyword-Match, Ampel und Verbesserungsvorschlaege.
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import clsx from 'clsx'
import { ShieldCheck, AlertTriangle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'

interface Suggestion { keyword: string; hinweis: string }
interface FormatWarning { typ: string; meldung: string }
interface AtsResult {
  score: number
  ampel: 'gruen' | 'gelb' | 'rot'
  matched_keywords: string[]
  missing_keywords: string[]
  suggestions: Suggestion[]
  format_warnings: FormatWarning[]
  ki_vorschlaege?: string[]
}

interface Props {
  applicationId: number
  cvText: string
  jobDescription: string
}

export default function AtsScorePanel({ applicationId, cvText, jobDescription }: Props) {
  const { t } = useTranslation('atsScorePanel')
  const [result, setResult] = useState<AtsResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const { data } = await axios.post(`/api/applications/${applicationId}/ats-check`, {
        cv_text: cvText,
        job_description: jobDescription,
      })
      setResult(data)
      setExpanded(true)
    } finally {
      setLoading(false)
    }
  }

  const ampelConfig = {
    gruen: { color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-900/20', Icon: ShieldCheck, label: t('ampel.gruen') },
    gelb:  { color: 'text-yellow-600', bg: 'bg-yellow-50 dark:bg-yellow-900/20', Icon: AlertTriangle, label: t('ampel.gelb') },
    rot:   { color: 'text-red-600', bg: 'bg-red-50 dark:bg-red-900/20', Icon: XCircle, label: t('ampel.rot') },
  }

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800">
        <div>
          <p className="font-semibold text-sm">{t('title')}</p>
          <p className="text-xs text-gray-400">{t('subtitle')}</p>
        </div>
        <button
          onClick={run}
          disabled={loading}
          className="px-4 py-1.5 rounded-xl text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          {loading ? t('analyzing') : t('analyze')}
        </button>
      </div>

      {result && (
        <div className={clsx('p-4 space-y-4', ampelConfig[result.ampel].bg)}>
          {/* Score */}
          <div className="flex items-center gap-3">
            {(() => { const { Icon, color, label } = ampelConfig[result.ampel]; return (
              <>
                <Icon size={28} className={color} aria-hidden />
                <div>
                  <p className={clsx('text-2xl font-bold', color)}>{result.score}<span className="text-base font-normal">/100</span></p>
                  <p className="text-xs text-gray-500">{t('keywordScore', { label, matched: result.matched_keywords.length, total: result.matched_keywords.length + result.missing_keywords.length })}
                  </p>
                </div>
              </>
            )})()}
          </div>

          {/* Verbesserungsvorschlaege */}
          {result.suggestions.length > 0 && (
            <div>
              <button
                onClick={() => setExpanded(e => !e)}
                className="flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-700"
                aria-expanded={expanded}
              >
                {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                {t('missingKeywords', { count: result.suggestions.length })}
              </button>
              {expanded && (
                <ul className="mt-2 space-y-1">
                  {result.suggestions.map((s, i) => (
                    <li key={i} className="text-xs text-gray-600 dark:text-gray-300">
                      <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">{s.keyword}</span>
                      {' '}→ {s.hinweis}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* KI-Vorschlaege */}
          {result.ki_vorschlaege && (
            <div className="text-xs space-y-1">
              <p className="font-medium text-gray-500">{t('aiImprovements')}</p>
              {result.ki_vorschlaege.map((v, i) => (
                <p key={i} className="text-gray-600 dark:text-gray-300">• {v}</p>
              ))}
            </div>
          )}

          {/* Format-Warnungen */}
          {result.format_warnings.length > 0 && (
            <div className="text-xs">
              <p className="font-medium text-red-500 mb-1">{t('formatWarnings')}</p>
              {result.format_warnings.map((w, i) => (
                <p key={i} className="text-red-400">⚠️ {w.meldung}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
