/**
 * KI-Stellenanalyse (Gehalt/Arbeitsmodell/Tags) + Skill-Gap-Analyse
 * (CV vs. Stellenbeschreibung) fuer einen Job.
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import clsx from 'clsx'
import { Sparkles, GraduationCap, CheckCircle2, XCircle, Lightbulb } from 'lucide-react'

interface JobAnalysisResult {
  salary_min: number | null
  salary_max: number | null
  work_model: string | null
  tags: string[]
}

interface SkillGapResult {
  match_score: number
  existing_skills: string[]
  missing_skills: string[]
  learning_recommendations: string[]
}

interface Props {
  jobId: number
}

export default function JobAnalysisPanel({ jobId }: Props) {
  const { t } = useTranslation('jobAnalysisPanel')
  const [analysis, setAnalysis] = useState<JobAnalysisResult | null>(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  const [skillGap, setSkillGap] = useState<SkillGapResult | null>(null)
  const [skillGapLoading, setSkillGapLoading] = useState(false)
  const [skillGapError, setSkillGapError] = useState<string | null>(null)

  const runAnalysis = async () => {
    setAnalysisLoading(true)
    setAnalysisError(null)
    try {
      const { data } = await axios.post(`/api/jobs/${jobId}/analyze`)
      setAnalysis(data)
    } catch {
      setAnalysisError(t('analysisError'))
    } finally {
      setAnalysisLoading(false)
    }
  }

  const runSkillGap = async () => {
    setSkillGapLoading(true)
    setSkillGapError(null)
    try {
      const { data } = await axios.post(`/api/jobs/${jobId}/skill-gap`)
      if (typeof data.match_score !== 'number') {
        setSkillGapError(t('skillGapGenericError'))
      } else {
        setSkillGap(data)
      }
    } catch (e) {
      if (axios.isAxiosError(e) && e.response?.status === 400) {
        setSkillGapError(t('skillGapNoCv'))
      } else {
        setSkillGapError(t('skillGapGenericError'))
      }
    } finally {
      setSkillGapLoading(false)
    }
  }

  const matchColor = skillGap
    ? skillGap.match_score >= 70 ? 'text-green-600' : skillGap.match_score >= 40 ? 'text-yellow-600' : 'text-red-600'
    : ''

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 divide-y divide-gray-200 dark:divide-gray-700">
      {/* Stellenanalyse */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-300 flex items-center gap-1.5">
            <Sparkles size={13} aria-hidden /> {t('analysisTitle')}
          </p>
          <button
            onClick={runAnalysis}
            disabled={analysisLoading}
            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
          >
            {analysisLoading ? t('analyzing') : t('analyze')}
          </button>
        </div>
        {analysisError && <p className="text-xs text-red-500">{analysisError}</p>}
        {analysis && (
          <div className="space-y-1.5">
            {(analysis.salary_min || analysis.salary_max) && (
              <p className="text-xs text-gray-600 dark:text-gray-300">
                {t('salary', { min: analysis.salary_min ?? '?', max: analysis.salary_max ?? '?' })}
              </p>
            )}
            {analysis.work_model && (
              <p className="text-xs text-gray-600 dark:text-gray-300">{t('workModel', { model: t(`workModels.${analysis.work_model}`, { defaultValue: analysis.work_model }) })}</p>
            )}
            {analysis.tags?.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {analysis.tags.map((tag, i) => (
                  <span key={i} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded-full">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Skill-Gap */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-300 flex items-center gap-1.5">
            <GraduationCap size={13} aria-hidden /> {t('skillGapTitle')}
          </p>
          <button
            onClick={runSkillGap}
            disabled={skillGapLoading}
            className="px-2.5 py-1 rounded-lg text-xs font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
          >
            {skillGapLoading ? t('analyzing') : t('analyze')}
          </button>
        </div>
        {skillGapError && <p className="text-xs text-red-500">{skillGapError}</p>}
        {skillGap && (
          <div className="space-y-1.5">
            <p className={clsx('text-lg font-bold', matchColor)}>
              {skillGap.match_score}<span className="text-sm font-normal">/100 {t('matchScore')}</span>
            </p>
            {skillGap.existing_skills?.map((s, i) => (
              <p key={`e${i}`} className="text-xs text-green-600 dark:text-green-400 flex items-start gap-1">
                <CheckCircle2 size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
              </p>
            ))}
            {skillGap.missing_skills?.map((s, i) => (
              <p key={`m${i}`} className="text-xs text-red-500 dark:text-red-400 flex items-start gap-1">
                <XCircle size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
              </p>
            ))}
            {skillGap.learning_recommendations?.map((s, i) => (
              <p key={`l${i}`} className="text-xs text-blue-600 dark:text-blue-400 flex items-start gap-1">
                <Lightbulb size={12} className="shrink-0 mt-0.5" aria-hidden /> {s}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
