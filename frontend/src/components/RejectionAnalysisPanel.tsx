/**
 * KI-Analyse einer Absage im Kontext des generierten Anschreibens.
 * Absage-Text wird nicht gespeichert, nur pro Analyse eingegeben.
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { Search, ThumbsUp, ThumbsDown, Lightbulb } from 'lucide-react'

interface AnalysisResult {
  strengths: string[]
  weaknesses: string[]
  improvement_suggestions: string[]
  summary: string
}

interface Props {
  applicationId: number
}

export default function RejectionAnalysisPanel({ applicationId }: Props) {
  const { t } = useTranslation('rejectionAnalysisPanel')
  const [rejectionText, setRejectionText] = useState('')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = async () => {
    if (!rejectionText.trim()) return
    setLoading(true)
    setError(null)
    try {
      const { data } = await axios.post(`/api/applications/${applicationId}/analyze-rejection`, {
        rejection_text: rejectionText,
      })
      if (!data.summary) {
        setError(t('genericError'))
      } else {
        setResult(data)
      }
    } catch {
      setError(t('genericError'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="p-4 bg-gray-50 dark:bg-gray-800">
        <p className="font-semibold text-sm flex items-center gap-1.5">
          <Search size={14} aria-hidden /> {t('title')}
        </p>
        <p className="text-xs text-gray-400 mb-2">{t('subtitle')}</p>
        <textarea
          value={rejectionText}
          onChange={e => setRejectionText(e.target.value)}
          placeholder={t('placeholder')}
          rows={3}
          className="w-full text-sm px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          aria-label={t('textareaAriaLabel')}
        />
        <button
          onClick={run}
          disabled={loading || !rejectionText.trim()}
          className="mt-2 px-4 py-1.5 rounded-xl text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
        >
          {loading ? t('analyzing') : t('analyze')}
        </button>
      </div>

      {error && <p className="p-4 text-sm text-red-500">{error}</p>}

      {result && (
        <div className="p-4 space-y-3">
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
          {result.weaknesses?.length > 0 && (
            <div className="text-xs space-y-1">
              {result.weaknesses.map((s, i) => (
                <p key={i} className="text-red-500 dark:text-red-400 flex items-start gap-1">
                  <ThumbsDown size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
                </p>
              ))}
            </div>
          )}
          {result.improvement_suggestions?.length > 0 && (
            <div className="text-xs space-y-1">
              {result.improvement_suggestions.map((s, i) => (
                <p key={i} className="text-blue-600 dark:text-blue-400 flex items-start gap-1">
                  <Lightbulb size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
