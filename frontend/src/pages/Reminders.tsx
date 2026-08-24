import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Bell, BellOff, Plus, Trash2 } from 'lucide-react'
import clsx from 'clsx'
import { formatDateTime } from '../lib/formatDate'

interface Reminder {
  id: number
  application_id: number | null
  remind_at: string
  message: string | null
  is_done: boolean
}

export default function Reminders() {
  const { t, i18n } = useTranslation(['reminders', 'common'])
  const qc = useQueryClient()
  const [showDone, setShowDone] = useState(false)
  const [newMsg, setNewMsg] = useState('')
  const [newDate, setNewDate] = useState('')

  const { data: reminders = [], isLoading } = useQuery<Reminder[]>({
    queryKey: ['reminders', showDone],
    queryFn: () => axios.get(`/api/reminders/?only_pending=${!showDone}`).then(r => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => axios.post('/api/reminders/', { remind_at: newDate, message: newMsg }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['reminders'] }); setNewMsg(''); setNewDate('') },
  })

  const doneMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/reminders/${id}/done`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/reminders/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }),
  })

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Bell size={22} aria-hidden /> {t('title')}
      </h1>

      {/* Neue Erinnerung */}
      <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 mb-6 space-y-3">
        <h2 className="text-sm font-semibold text-gray-500">{t('newReminder')}</h2>
        <div className="flex gap-2">
          <input
            type="datetime-local"
            value={newDate}
            onChange={e => setNewDate(e.target.value)}
            className="rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={t('dateAriaLabel')}
          />
          <input
            className="flex-1 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={t('messagePlaceholder')}
            value={newMsg}
            onChange={e => setNewMsg(e.target.value)}
            aria-label={t('messageAriaLabel')}
          />
          <button
            onClick={() => createMutation.mutate()}
            disabled={!newDate || createMutation.isPending}
            className="flex items-center gap-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            aria-label={t('addAriaLabel')}
          >
            <Plus size={15} aria-hidden /> {t('add')}
          </button>
        </div>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-2 mb-4">
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={showDone} onChange={e => setShowDone(e.target.checked)} className="rounded" />
          {t('showDone')}
        </label>
        <span className="text-xs text-gray-400 ml-auto">{t('count', { count: reminders.length })}</span>
      </div>

      {/* Liste */}
      {isLoading && <p className="text-gray-400 text-sm">{t('common:loading')}</p>}
      <ul className="space-y-2">
        {reminders.map(r => (
          <li
            key={r.id}
            className={clsx(
              'flex items-center gap-3 rounded-xl px-4 py-3 border',
              r.is_done
                ? 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-800 opacity-60'
                : 'bg-white dark:bg-gray-800 border-yellow-200 dark:border-yellow-800'
            )}
          >
            <Bell size={16} className={r.is_done ? 'text-gray-400' : 'text-yellow-500'} aria-hidden />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{r.message ?? t('fallbackMessage')}</p>
              <p className="text-xs text-gray-400">
                {formatDateTime(r.remind_at, i18n.language)}
              </p>
            </div>
            <div className="flex gap-1 shrink-0">
              {!r.is_done && (
                <button
                  onClick={() => doneMutation.mutate(r.id)}
                  className="text-green-500 hover:text-green-700 p-1 rounded transition-colors"
                  aria-label={t('markDone')}
                >
                  <BellOff size={15} aria-hidden />
                </button>
              )}
              <button
                onClick={() => deleteMutation.mutate(r.id)}
                className="text-red-400 hover:text-red-600 p-1 rounded transition-colors"
                aria-label={t('delete')}
              >
                <Trash2 size={15} aria-hidden />
              </button>
            </div>
          </li>
        ))}
        {!isLoading && reminders.length === 0 && (
          <li className="text-gray-400 text-sm text-center py-8">
            {showDone ? t('emptyDone') : t('emptyPending')}
          </li>
        )}
      </ul>
    </div>
  )
}
