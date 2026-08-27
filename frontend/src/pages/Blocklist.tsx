import { useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Plus, Trash2, Ban, Download, Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { formatDate } from '../lib/formatDate'

interface BlocklistEntry {
  id: number
  firma: string | null
  recruiter_name: string | null
  grund: string | null
  erstellt_am: string
}

type ImportStatus =
  | { state: 'idle' }
  | { state: 'loading' }
  | { state: 'success'; imported: number; skipped: number }
  | { state: 'error'; message: string }

export default function Blocklist() {
  const { t, i18n } = useTranslation(['blocklist', 'common'])
  const qc = useQueryClient()
  const fileRef = useRef<HTMLInputElement>(null)
  const [firma, setFirma] = useState('')
  const [recruiterName, setRecruiterName] = useState('')
  const [grund, setGrund] = useState('')
  const [importStatus, setImportStatus] = useState<ImportStatus>({ state: 'idle' })

  const { data: entries = [], isLoading } = useQuery<BlocklistEntry[]>({
    queryKey: ['blocklist'],
    queryFn: () => axios.get('/api/blocklist/').then(r => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => axios.post('/api/blocklist/', {
      firma: firma || null,
      recruiter_name: recruiterName || null,
      grund: grund || null,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['blocklist'] })
      qc.invalidateQueries({ queryKey: ['jobs'] })
      setFirma(''); setRecruiterName(''); setGrund('')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/blocklist/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['blocklist'] })
      qc.invalidateQueries({ queryKey: ['jobs'] })
    },
  })

  const handleExport = () => {
    const payload = entries.map(({ firma, recruiter_name, grund }) => ({ firma, recruiter_name, grund }))
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `jobhunter-blocklist-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleImportFile = async (file: File) => {
    setImportStatus({ state: 'loading' })
    try {
      const text = await file.text()
      const parsed = JSON.parse(text)
      const res = await axios.post('/api/blocklist/import', parsed)
      setImportStatus({ state: 'success', imported: res.data.imported, skipped: res.data.skipped })
      qc.invalidateQueries({ queryKey: ['blocklist'] })
      qc.invalidateQueries({ queryKey: ['jobs'] })
    } catch (e) {
      setImportStatus({
        state: 'error',
        message: e instanceof Error ? e.message : t('common:error', 'Fehler'),
      })
    }
  }

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleImportFile(file)
    e.target.value = ''
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Ban size={22} aria-hidden /> {t('title')}
      </h1>
      <p className="text-sm text-gray-500 mb-6">{t('intro')}</p>

      {/* Neuer Eintrag */}
      <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 mb-6 space-y-3">
        <h2 className="text-sm font-semibold text-gray-500">{t('newEntry')}</h2>
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={t('firmaPlaceholder')}
            value={firma}
            onChange={e => setFirma(e.target.value)}
            aria-label={t('firmaAriaLabel')}
          />
          <input
            className="w-48 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={t('recruiterPlaceholder')}
            value={recruiterName}
            onChange={e => setRecruiterName(e.target.value)}
            aria-label={t('recruiterAriaLabel')}
          />
        </div>
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={t('grundPlaceholder')}
            value={grund}
            onChange={e => setGrund(e.target.value)}
            aria-label={t('grundAriaLabel')}
          />
          <button
            onClick={() => createMutation.mutate()}
            disabled={(!firma && !recruiterName) || createMutation.isPending}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shrink-0"
          >
            <Plus size={15} aria-hidden /> {t('addEntry')}
          </button>
        </div>
      </div>

      {/* Export/Import */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={handleExport}
          disabled={entries.length === 0}
          className="flex items-center gap-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 px-3 py-2 rounded-lg transition-colors"
        >
          <Download size={14} aria-hidden /> {t('export')}
        </button>
        <button
          onClick={() => fileRef.current?.click()}
          disabled={importStatus.state === 'loading'}
          className="flex items-center gap-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 px-3 py-2 rounded-lg transition-colors"
        >
          {importStatus.state === 'loading'
            ? <Loader2 size={14} className="animate-spin" aria-hidden />
            : <Upload size={14} aria-hidden />}
          {t('import')}
        </button>
        <input ref={fileRef} type="file" accept="application/json" className="hidden" onChange={onFileInputChange} />
        {importStatus.state === 'success' && (
          <span className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400">
            <CheckCircle size={14} aria-hidden /> {t('importSuccess', { imported: importStatus.imported, skipped: importStatus.skipped })}
          </span>
        )}
        {importStatus.state === 'error' && (
          <span className="flex items-center gap-1 text-sm text-red-500">
            <AlertCircle size={14} aria-hidden /> {importStatus.message}
          </span>
        )}
      </div>

      {/* Liste */}
      {isLoading && <p className="text-gray-400 text-sm">{t('common:loading')}</p>}
      <ul className="space-y-2">
        {entries.map(entry => (
          <li key={entry.id} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700 flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="font-semibold truncate">
                {entry.firma || entry.recruiter_name}
                {entry.firma && entry.recruiter_name && (
                  <span className="font-normal text-gray-500"> · {entry.recruiter_name}</span>
                )}
              </p>
              {entry.grund && <p className="text-sm text-gray-500 mt-0.5">{entry.grund}</p>}
              <p className="text-xs text-gray-400 mt-1">{formatDate(entry.erstellt_am, i18n.language)}</p>
            </div>
            <button
              onClick={() => deleteMutation.mutate(entry.id)}
              className="text-red-400 hover:text-red-600 p-2 rounded transition-colors shrink-0"
              aria-label={t('deleteEntry', { name: entry.firma || entry.recruiter_name || '' })}
            >
              <Trash2 size={15} aria-hidden />
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
