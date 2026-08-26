import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { Mic, ThumbsUp, AlertCircle, ChevronRight, RotateCcw, CheckSquare, Search, BookOpen } from 'lucide-react'
import clsx from 'clsx'

interface Question {
  question: string
  category: 'fachlich' | 'soft_skill' | 'situativ' | 'allgemein' | 'fehler'
}

interface Evaluation {
  score: number
  feedback: string
  tip: string
}

interface PrepQA {
  question: string
  sample_answer: string
}

interface PrepData {
  technical: PrepQA[]
  personal: PrepQA[]
  salary: PrepQA[]
}

const CATEGORY_COLORS: Record<string, string> = {
  fachlich: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  soft_skill: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  situativ: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  allgemein: 'bg-gray-100 text-gray-600',
  fehler: 'bg-red-100 text-red-600',
}

export default function InterviewSimulator() {
  const { t } = useTranslation('interviewSimulator')
  const [jobId, setJobId] = useState('')
  const [questions, setQuestions] = useState<Question[]>([])
  const [jobTitle, setJobTitle] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [evaluations, setEvaluations] = useState<Record<number, Evaluation>>({})
  const [loading, setLoading] = useState(false)
  const [evalLoading, setEvalLoading] = useState(false)
  const [phase, setPhase] = useState<'setup' | 'quiz' | 'results' | 'prep'>('setup')
  const [mode, setMode] = useState<'practice' | 'prep'>('practice')
  const [prepData, setPrepData] = useState<PrepData | null>(null)

  const loadQuestions = async () => {
    if (!jobId) return
    setLoading(true)
    try {
      if (mode === 'prep') {
        const { data } = await axios.post(`/api/interview/prep/${jobId}`)
        setPrepData(data)
        setPhase('prep')
      } else {
        const { data } = await axios.get(`/api/interview/questions/${jobId}`)
        setQuestions(data.questions)
        setJobTitle(data.job_title)
        setCurrentIndex(0)
        setAnswers({})
        setEvaluations({})
        setPhase('quiz')
      }
    } catch {
      alert(t('errorNotFound'))
    } finally {
      setLoading(false)
    }
  }

  const evaluateCurrent = async () => {
    const answer = answers[currentIndex] || ''
    if (!answer.trim()) return
    setEvalLoading(true)
    try {
      const { data } = await axios.post('/api/interview/evaluate', {
        job_id: parseInt(jobId),
        question: questions[currentIndex].question,
        answer,
      })
      setEvaluations(prev => ({ ...prev, [currentIndex]: data }))
    } catch {
      setEvaluations(prev => ({ ...prev, [currentIndex]: { score: 0, feedback: t('aiUnreachable'), tip: '' } }))
    } finally {
      setEvalLoading(false)
    }
  }

  const avgScore = () => {
    const vals = Object.values(evaluations).map(e => e.score)
    if (!vals.length) return 0
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
  }

  if (phase === 'setup') {
    return (
      <div className="max-w-lg mx-auto py-12">
        <div className="text-center mb-8">
          <Mic size={40} className="mx-auto text-blue-500 mb-3" aria-hidden />
          <h1 className="text-2xl font-bold mb-2">{t('title')}</h1>
          <p className="text-gray-500 dark:text-gray-400">{t('subtitle')}</p>
        </div>
        <div className="flex gap-2 mb-4 justify-center">
          <button
            onClick={() => setMode('practice')}
            className={clsx('px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              mode === 'practice' ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300')}
            aria-pressed={mode === 'practice'}
          >
            <Mic size={14} className="inline mr-1" aria-hidden /> {t('modePractice')}
          </button>
          <button
            onClick={() => setMode('prep')}
            className={clsx('px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              mode === 'prep' ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300')}
            aria-pressed={mode === 'prep'}
          >
            <BookOpen size={14} className="inline mr-1" aria-hidden /> {t('modePrep')}
          </button>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-md">
          <label className="block text-sm font-medium mb-2" htmlFor="job-id-input">{t('jobIdLabel')}</label>
          <div className="flex gap-2">
            <input
              id="job-id-input"
              type="number"
              value={jobId}
              onChange={e => setJobId(e.target.value)}
              placeholder={t('jobIdPlaceholder')}
              className="flex-1 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm"
              onKeyDown={e => e.key === 'Enter' && loadQuestions()}
            />
            <button
              onClick={loadQuestions}
              disabled={!jobId || loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
            >
              {loading ? <span className="animate-spin">&#9696;</span> : <Search size={16} aria-hidden />}
              {t('start')}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-3">{t('jobIdHint')}</p>
        </div>
      </div>
    )
  }

  if (phase === 'results') {
    return (
      <div className="max-w-2xl mx-auto py-8">
        <div className="text-center mb-6">
          <CheckSquare size={36} className="mx-auto text-green-500 mb-2" aria-hidden />
          <h2 className="text-xl font-bold">{t('completed')}</h2>
          <p className="text-gray-400">{jobTitle}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-md mb-6">
          <div className="text-center">
            <div className="text-5xl font-bold text-blue-600 mb-1">{avgScore()}<span className="text-2xl text-gray-400">/10</span></div>
            <p className="text-gray-500">{t('averageScore')}</p>
          </div>
        </div>
        <div className="space-y-4">
          {questions.map((q, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
              <div className="flex items-start gap-3">
                <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 mt-0.5', CATEGORY_COLORS[q.category])}>
                  {t(`categories.${q.category}`, q.category)}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium mb-1">{q.question}</p>
                  <p className="text-xs text-gray-400 mb-2 italic">{`"${answers[i] || t('noAnswer')}"`}</p>
                  {evaluations[i] && (
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <ThumbsUp size={14} className="text-blue-500" aria-hidden />
                        <span className="text-sm font-semibold text-blue-600">{evaluations[i].score}/10</span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-300 mb-1">{evaluations[i].feedback}</p>
                      {evaluations[i].tip && (
                        <p className="text-xs text-orange-600 dark:text-orange-400">💡 {evaluations[i].tip}</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="flex justify-center mt-6">
          <button
            onClick={() => { setPhase('setup'); setQuestions([]); setJobId('') }}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium transition-colors"
          >
            <RotateCcw size={16} aria-hidden />
            {t('newInterview')}
          </button>
        </div>
      </div>
    )
  }

  if (phase === 'prep' && prepData) {
    const sections: { key: keyof PrepData; label: string }[] = [
      { key: 'technical', label: t('prepSections.technical') },
      { key: 'personal', label: t('prepSections.personal') },
      { key: 'salary', label: t('prepSections.salary') },
    ]
    return (
      <div className="max-w-2xl mx-auto py-8 space-y-6">
        <div className="text-center mb-2">
          <BookOpen size={36} className="mx-auto text-blue-500 mb-2" aria-hidden />
          <h2 className="text-xl font-bold">{t('prepTitle')}</h2>
        </div>
        {sections.map(({ key, label }) => (
          (prepData[key]?.length ?? 0) > 0 && (
            <div key={key}>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">{label}</h3>
              <div className="space-y-3">
                {prepData[key].map((qa, i) => (
                  <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm">
                    <p className="text-sm font-medium mb-1.5">{qa.question}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{qa.sample_answer}</p>
                  </div>
                ))}
              </div>
            </div>
          )
        ))}
        <div className="flex justify-center pt-2">
          <button
            onClick={() => { setPhase('setup'); setPrepData(null); setJobId('') }}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium transition-colors"
          >
            <RotateCcw size={16} aria-hidden />
            {t('newInterview')}
          </button>
        </div>
      </div>
    )
  }

  const q = questions[currentIndex]
  const isLast = currentIndex === questions.length - 1
  const eval_ = evaluations[currentIndex]

  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="font-bold text-lg">{jobTitle}</h2>
          <p className="text-sm text-gray-400">{t('questionProgress', { current: currentIndex + 1, total: questions.length })}</p>
        </div>
        <div className="flex gap-1">
          {questions.map((_, i) => (
            <div
              key={i}
              className={clsx('h-1.5 w-6 rounded-full transition-colors', {
                'bg-blue-600': i === currentIndex,
                'bg-green-500': i < currentIndex,
                'bg-gray-200 dark:bg-gray-700': i > currentIndex,
              })}
            />
          ))}
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-md mb-4">
        <div className="flex items-start gap-3 mb-4">
          <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0', CATEGORY_COLORS[q.category])}>
            {t(`categories.${q.category}`, q.category)}
          </span>
        </div>
        <p className="text-base font-medium mb-5">{q.question}</p>
        <textarea
          value={answers[currentIndex] || ''}
          onChange={e => setAnswers(prev => ({ ...prev, [currentIndex]: e.target.value }))}
          placeholder={t('answerPlaceholder')}
          rows={4}
          className="w-full px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:outline-none"
        />
        <div className="flex gap-3 mt-3">
          <button
            onClick={evaluateCurrent}
            disabled={!answers[currentIndex]?.trim() || evalLoading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-sm font-medium disabled:opacity-50 transition-colors"
          >
            {evalLoading ? <span className="animate-spin text-xs">&#9696;</span> : <ThumbsUp size={14} aria-hidden />}
            {t('aiFeedback')}
          </button>
          <button
            onClick={() => {
              if (isLast) setPhase('results')
              else setCurrentIndex(i => i + 1)
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors ml-auto"
          >
            {isLast ? t('finish') : t('nextQuestion')}
            <ChevronRight size={14} aria-hidden />
          </button>
        </div>
      </div>

      {eval_ && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-100 dark:border-blue-800">
          <div className="flex items-center gap-2 mb-2">
            <ThumbsUp size={16} className="text-blue-600" aria-hidden />
            <span className="font-semibold text-blue-600">{eval_.score}/10</span>
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-200 mb-2">{eval_.feedback}</p>
          {eval_.tip && (
            <p className="text-xs text-orange-600 dark:text-orange-400 flex items-start gap-1">
              <AlertCircle size={12} className="flex-shrink-0 mt-0.5" aria-hidden />
              {eval_.tip}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
