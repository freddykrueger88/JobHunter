/**
 * Zeigt aehnliche/moeglicherweise doppelte Stellen zu einem Job
 * (Fuzzy-Matching, backend/services/duplicate_detection.py).
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { Copy, ChevronDown, ChevronUp } from 'lucide-react'

interface DuplicateJob {
  id: number
  title: string
  company: string
  city: string | null
  similarity_score: number
}

interface Props {
  jobId: number
}

export default function DuplicateJobsPanel({ jobId }: Props) {
  const { t } = useTranslation('duplicateJobsPanel')
  const [open, setOpen] = useState(false)

  const { data: duplicates = [], isLoading } = useQuery<DuplicateJob[]>({
    queryKey: ['job-duplicates', jobId],
    queryFn: () => axios.get(`/api/jobs/${jobId}/duplicates`).then(r => r.data),
    enabled: open,
  })

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between p-3 text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        aria-expanded={open}
      >
        <span className="flex items-center gap-1.5">
          <Copy size={14} aria-hidden /> {t('title')}
        </span>
        {open ? <ChevronUp size={14} aria-hidden /> : <ChevronDown size={14} aria-hidden />}
      </button>
      {open && (
        <div className="p-3 pt-0 space-y-2">
          {isLoading && <p className="text-xs text-gray-400">{t('loading')}</p>}
          {!isLoading && duplicates.length === 0 && (
            <p className="text-xs text-gray-400">{t('none')}</p>
          )}
          {duplicates.map(d => (
            <div key={d.id} className="text-xs bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
              <p className="font-medium">{d.title}</p>
              <p className="text-gray-500">{d.company}{d.city && ` · ${d.city}`}</p>
              <p className="text-gray-400 mt-0.5">{t('similarity', { percent: Math.round(d.similarity_score * 100) })}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
