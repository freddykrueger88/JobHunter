/**
 * Lebenslauf-Optimierung: KI-Verbesserungsvorschlaege fuer den zuletzt
 * hochgeladenen CV, im Kontext der Stellenbeschreibung dieser Bewerbung.
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import clsx from 'clsx'
import { GraduationCap, ThumbsUp, ThumbsDown, Lightbulb } from 'lucide-react'

interface Suggestion { section: string; suggestion: string }
interface CvOptimizeResult {
  score: number
  strengths: string[]
  weaknesses: string[]
  suggestions: Suggestion[]
}

interface Props {
  applicationId: number
}

export default function CvOptimizerPanel({ applicationId }: Props) {
  const { t } = useTranslation('cvOptimizerPanel')
  const [result, setResult] = useState<CvOptimizeResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.post(`/api/applications/${applicationId}/cv-optimize`)
      setResult(data)
    } catch (e) {
      if (axios.isAxiosError(e) && e.response?.status === 400) {
        setError(e.response.data?.detail ?? t('noCv'))
      } else {
        setError(t('genericError'))
      }
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = result
    ? result.score >= 70 ? 'text-green-600' : result.score >= 45 ? 'text-yellow-600' : 'text-red-600'
    : ''

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800">
        <div>
          <p className="font-semibold text-sm flex items-center gap-1.5">
            <GraduationCap size={14} aria-hidden /> {t('title')}
          </p>
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

      {error && <p className="p-4 text-sm text-red-500">{error}</p>}

      {result && (
        <div className="p-4 space-y-3">
          <div className="flex items-center gap-3">
            <p className={clsx('text-2xl font-bold', scoreColor)}>
              {result.score}<span className="text-base font-normal">/100</span>
            </p>
          </div>

          {result.strengths?.length > 0 && (
            <div className="text-xs space-y-1">
              {result.strengths.map((s, i) => (
                <p key={i} className="text-green-600 dark:text-green-400 flex items-start gap-1">
                  <ThumbsUp size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
                </p>
              ))}
            </div>
          )}

          {result.weaknesses?.length > 0 && (
            <div className="text-xs space-y-1">
              {result.weaknesses.map((w, i) => (
                <p key={i} className="text-yellow-600 dark:text-yellow-400 flex items-start gap-1">
                  <ThumbsDown size={12} className="shrink-0 mt-0.5" aria-hidden /> {w}
                </p>
              ))}
            </div>
          )}

          {result.suggestions?.length > 0 && (
            <div className="text-xs space-y-1">
              <p className="font-medium text-gray-500 flex items-center gap-1">
                <Lightbulb size={12} aria-hidden /> {t('suggestions')}
              </p>
              {result.suggestions.map((s, i) => (
                <p key={i} className="text-gray-600 dark:text-gray-300">
                  <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">{s.section}</span>
                  {' '}→ {s.suggestion}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
