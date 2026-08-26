/**
 * KI-Bewertung des zuletzt generierten Anschreibens einer Bewerbung.
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import clsx from 'clsx'
import { Star, ThumbsUp, ThumbsDown } from 'lucide-react'

interface EvaluationResult {
  overall_score: number
  relevance: number
  tone: number
  structure: number
  strengths: string[]
  improvements: string[]
  summary: string
}

interface Props {
  applicationId: number
}

export default function CoverLetterQualityPanel({ applicationId }: Props) {
  const { t } = useTranslation('coverLetterQualityPanel')
  const [result, setResult] = useState<EvaluationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.post(`/api/applications/${applicationId}/evaluate-cover-letter`)
      if (typeof data.overall_score !== 'number') {
        setError(t('genericError'))
      } else {
        setResult(data)
      }
    } catch (e) {
      if (axios.isAxiosError(e) && e.response?.status === 404) {
        setError(t('noCoverLetter'))
      } else {
        setError(t('genericError'))
      }
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = result
    ? result.overall_score >= 70 ? 'text-green-600' : result.overall_score >= 40 ? 'text-yellow-600' : 'text-red-600'
    : ''

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800">
        <div>
          <p className="font-semibold text-sm flex items-center gap-1.5">
            <Star size={14} aria-hidden /> {t('title')}
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
              {result.overall_score}
              <span className="text-base font-normal">/100</span>
            </p>
            <p className="text-xs text-gray-500">
              {t('subscores', { relevance: result.relevance, tone: result.tone, structure: result.structure })}
            </p>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300">{result.summary}</p>
          {result.strengths?.length > 0 && (
            <div className="text-xs space-y-1">
              {result.strengths.map((s, i) => (
                <p key={i} className="text-green-600 dark:text-green-400 flex items-start gap-1">
                  <ThumbsUp size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
                </p>
              ))}
            </div>
          )}
          {result.improvements?.length > 0 && (
            <div className="text-xs space-y-1">
              {result.improvements.map((s, i) => (
                <p key={i} className="text-yellow-600 dark:text-yellow-400 flex items-start gap-1">
                  <ThumbsDown size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
