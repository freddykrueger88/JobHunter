import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { BookOpen, Trash2, Pencil, Search, Download, X, Check } from 'lucide-react'
import { formatDateTime } from '../lib/formatDate'

interface DiaryEntryData {
  id: number
  content: string
  created_at: string
  updated_at: string
}

export default function Diary() {
  const { t, i18n } = useTranslation(['diary', 'common'])
  const qc = useQueryClient()
  const [newContent, setNewContent] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => setSearch(searchInput), 400)
    return () => clearTimeout(timer)
  }, [searchInput])

  const { data: entries = [], isLoading } = useQuery<DiaryEntryData[]>({
    queryKey: ['diary', search],
    queryFn: () => axios.get('/api/diary/', { params: search ? { search } : {} }).then(r => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => axios.post('/api/diary/', { content: newContent }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['diary'] })
      setNewContent('')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      axios.patch(`/api/diary/${id}`, { content }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['diary'] })
      setEditingId(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/diary/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['diary'] }),
  })

  const startEdit = (entry: DiaryEntryData) => {
    setEditingId(entry.id)
    setEditContent(entry.content)
  }

  const exportPdfUrl = search
    ? `/api/diary/pdf?search=${encodeURIComponent(search)}`
    : '/api/diary/pdf'

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <BookOpen size={22} aria-hidden /> {t('title')}
      </h1>

      {/* Neuer Eintrag */}
      <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 mb-6 space-y-3">
        <textarea
          className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
          placeholder={t('newEntryPlaceholder')}
          value={newContent}
          onChange={e => setNewContent(e.target.value)}
          aria-label={t('newEntryAriaLabel')}
        />
        <button
          onClick={() => createMutation.mutate()}
          disabled={!newContent.trim() || createMutation.isPending}
          className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {t('save')}
        </button>
      </div>

      {/* Suche + Export */}
      <div className="flex items-center gap-2 mb-4">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" aria-hidden />
          <input
            className="w-full rounded-lg pl-9 pr-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={t('searchPlaceholder')}
            value={searchInput}
            onChange={e => setSearchInput(e.target.value)}
            aria-label={t('searchAriaLabel')}
          />
        </div>
        <a
          href={exportPdfUrl}
          className="flex items-center gap-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 px-3 py-2 rounded-lg transition-colors shrink-0"
        >
          <Download size={14} aria-hidden /> {t('exportPdf')}
        </a>
      </div>

      {/* Liste */}
      {isLoading && <p className="text-gray-400 text-sm">{t('common:loading')}</p>}
      <ul className="space-y-2">
        {entries.map(entry => (
          <li key={entry.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            {editingId === entry.id ? (
              <div className="space-y-2">
                <textarea
                  className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 min-h-[80px]"
                  value={editContent}
                  onChange={e => setEditContent(e.target.value)}
                  aria-label={t('editEntryAriaLabel')}
                  autoFocus
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => updateMutation.mutate({ id: entry.id, content: editContent })}
                    disabled={!editContent.trim() || updateMutation.isPending}
                    className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <Check size={12} aria-hidden /> {t('save')}
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="flex items-center gap-1 text-xs bg-gray-200 dark:bg-gray-700 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <X size={12} aria-hidden /> {t('cancel')}
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-start justify-between gap-3">
                  <p className="text-xs text-gray-400">{formatDateTime(entry.created_at, i18n.language)}</p>
                  <div className="flex gap-1 shrink-0">
                    <button
                      onClick={() => startEdit(entry)}
                      className="text-gray-400 hover:text-blue-500 p-1.5 rounded transition-colors"
                      aria-label={t('editEntry')}
                    >
                      <Pencil size={14} aria-hidden />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(entry.id)}
                      className="text-gray-400 hover:text-red-500 p-1.5 rounded transition-colors"
                      aria-label={t('deleteEntry')}
                    >
                      <Trash2 size={14} aria-hidden />
                    </button>
                  </div>
                </div>
                <p className="text-sm whitespace-pre-line mt-1">{entry.content}</p>
              </>
            )}
          </li>
        ))}
        {!isLoading && entries.length === 0 && (
          <li className="text-gray-400 text-sm text-center py-8">
            {search ? t('noResults') : t('empty')}
          </li>
        )}
      </ul>
    </div>
  )
}
