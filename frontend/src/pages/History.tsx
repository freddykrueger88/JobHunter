import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Trash2, Filter } from 'lucide-react'
import { formatDateTime } from '../lib/formatDate'

interface HistoryEntry {
  id: number
  type: string
  description: string
  meta: Record<string, any> | null
  at: string
}

const EVENT_ICONS: Record<string, string> = {
  job_created: '💼',
  job_search: '🔍',
  application_created: '📤',
  status_changed: '🔄',
  cover_letter_generated: '✍️',
  cv_uploaded: '📄',
}

const EVENT_TYPES = Object.keys(EVENT_ICONS)

export default function History() {
  const { t, i18n } = useTranslation(['history', 'common'])
  const qc = useQueryClient()
  const [filter, setFilter] = useState('')
  const [limit, setLimit] = useState(50)

  const { data: entries = [], isLoading } = useQuery<HistoryEntry[]>({
    queryKey: ['history', filter, limit],
    queryFn: () => axios.get('/api/history/', {
      params: { event_type: filter || undefined, limit },
    }).then(r => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/history/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['history'] }),
  })

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-6">{t('title')}</h1>

      {/* Filter */}
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <Filter size={16} className="text-gray-400" aria-hidden />
        <select
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="rounded-lg px-3 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label={t('filterByType')}
        >
          <option value="">{t('allTypes')}</option>
          {EVENT_TYPES.map(evType => (
            <option key={evType} value={evType}>{EVENT_ICONS[evType]} {t(`eventTypes.${evType}`)}</option>
          ))}
        </select>
        <select
          value={limit}
          onChange={e => setLimit(Number(e.target.value))}
          className="rounded-lg px-3 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
          aria-label={t('limitAriaLabel')}
        >
          {[25, 50, 100, 200].map(l => <option key={l} value={l}>{t('count', { count: l })}</option>)}
        </select>
        <span className="text-xs text-gray-400 ml-auto">{t('count', { count: entries.length })}</span>
      </div>

      {/* Liste */}
      {isLoading && <p className="text-gray-400 text-sm">{t('common:loading')}</p>}
      <ul className="space-y-1">
        {entries.map(entry => (
          <li
            key={entry.id}
            className="flex items-start gap-3 bg-gray-50 dark:bg-gray-800/60 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg px-4 py-2.5 text-sm group transition-colors"
          >
            <span className="text-base mt-0.5 select-none" aria-hidden>{EVENT_ICONS[entry.type] ?? '🟡'}</span>
            <div className="flex-1 min-w-0">
              <p className="truncate">{entry.description}</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {formatDateTime(entry.at, i18n.language)}
                {entry.meta && Object.keys(entry.meta).length > 0 && (
                  <span className="ml-2 text-gray-300">
                    {Object.entries(entry.meta).map(([k, v]) => `${k}: ${v}`).join(' • ')}
                  </span>
                )}
              </p>
            </div>
            <button
              onClick={() => deleteMutation.mutate(entry.id)}
              className="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all p-1 rounded"
              aria-label={t('deleteEntry', { description: entry.description })}
            >
              <Trash2 size={14} aria-hidden />
            </button>
          </li>
        ))}
        {!isLoading && entries.length === 0 && (
          <li className="text-gray-400 text-sm text-center py-8">{t('empty')}</li>
        )}
      </ul>
    </div>
  )
}
