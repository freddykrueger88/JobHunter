import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { GripVertical, X, Clock } from 'lucide-react'
import clsx from 'clsx'

interface Application {
  id: number; job_id: number; status: string
  notes: string | null; kanban_position: number
  applied_at: string | null; interview_at: string | null
}
interface Job { id: number; title: string; company: string; city: string | null }
interface TimelineEntry { status: string; changed_at: string }

const COLUMNS = [
  { key: 'interessant', label: '⭐ Interessant',  color: 'border-purple-400' },
  { key: 'beworben',    label: '📤 Beworben',    color: 'border-blue-400' },
  { key: 'interview',   label: '💬 Interview',   color: 'border-yellow-400' },
  { key: 'angenommen',  label: '✅ Angenommen',  color: 'border-green-400' },
  { key: 'absage',      label: '❌ Absage',      color: 'border-red-400' },
]

const STATUS_ICONS: Record<string, string> = {
  interessant: '⭐', beworben: '📤', interview: '💬', angenommen: '✅', absage: '❌',
}

export default function Kanban() {
  const qc = useQueryClient()
  const [dragging, setDragging] = useState<number | null>(null)
  const [detailApp, setDetailApp] = useState<Application | null>(null)
  const [editingNotes, setEditingNotes] = useState<number | null>(null)
  const [notesValue, setNotesValue] = useState('')
  const notesRef = useRef<HTMLTextAreaElement>(null)

  const { data: applications = [] } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: () => axios.get('/api/applications/').then(r => r.data),
  })
  const { data: jobs = [] } = useQuery<Job[]>({
    queryKey: ['jobs-all'],
    queryFn: () => axios.get('/api/jobs/?hide_hidden=false').then(r => r.data),
  })
  const jobMap = Object.fromEntries(jobs.map(j => [j.id, j]))

  const { data: timeline = [], refetch: fetchTimeline } = useQuery<TimelineEntry[]>({
    queryKey: ['timeline', detailApp?.id],
    queryFn: () => detailApp ? axios.get(`/api/applications/${detailApp.id}/timeline`).then(r => r.data) : [],
    enabled: !!detailApp,
  })

  const moveMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => axios.patch(`/api/applications/${id}`, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  })
  const notesMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes: string }) => axios.patch(`/api/applications/${id}`, { notes }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }); setEditingNotes(null) },
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/applications/${id}`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['applications'] }); setDetailApp(null) },
  })

  const startEditNotes = (app: Application) => {
    setEditingNotes(app.id)
    setNotesValue(app.notes ?? '')
    setTimeout(() => notesRef.current?.focus(), 50)
  }

  const saveNotes = (id: number) => {
    notesMutation.mutate({ id, notes: notesValue })
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Bewerbungen</h1>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {COLUMNS.map(col => {
          const cards = applications.filter(a => a.status === col.key)
          return (
            <div key={col.key} className="flex-shrink-0 w-64"
              onDragOver={e => e.preventDefault()}
              onDrop={e => { e.preventDefault(); if (dragging !== null) { moveMutation.mutate({ id: dragging, status: col.key }); setDragging(null) } }}
              role="region" aria-label={col.label}>
              <div className={clsx('border-t-4 rounded-t-lg px-3 py-2 bg-gray-100 dark:bg-gray-800 flex items-center justify-between', col.color)}>
                <span className="font-semibold text-sm">{col.label}</span>
                <span className="text-xs bg-gray-200 dark:bg-gray-700 rounded-full px-2 py-0.5">{cards.length}</span>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-b-lg p-2 space-y-2 min-h-32">
                {cards.map(app => {
                  const job = jobMap[app.job_id]
                  const isEditingThis = editingNotes === app.id
                  return (
                    <div key={app.id} draggable onDragStart={() => setDragging(app.id)}
                      className={clsx('bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm border border-transparent hover:border-blue-400 transition-all', dragging === app.id && 'opacity-40')}>
                      {/* Klickbarer Header */}
                      <div className="flex items-start gap-1 cursor-pointer" onClick={() => { setDetailApp(app); fetchTimeline() }}
                        role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && setDetailApp(app)}
                        aria-label={`${job?.title ?? 'Stelle'} Details öffnen`}>
                        <GripVertical size={14} className="text-gray-300 mt-0.5 shrink-0" aria-hidden />
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{job?.title ?? `Stelle #${app.job_id}`}</p>
                          <p className="text-xs text-gray-500 truncate">{job?.company}</p>
                          {job?.city && <p className="text-xs text-gray-400">{job.city}</p>}
                        </div>
                      </div>
                      {/* Inline-Notizen */}
                      {isEditingThis ? (
                        <textarea
                          ref={notesRef}
                          value={notesValue}
                          onChange={e => setNotesValue(e.target.value)}
                          onBlur={() => saveNotes(app.id)}
                          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); saveNotes(app.id) } if (e.key === 'Escape') setEditingNotes(null) }}
                          className="mt-2 w-full text-xs rounded px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-blue-400 focus:outline-none resize-none"
                          rows={2}
                          aria-label="Notiz bearbeiten"
                        />
                      ) : (
                        <p
                          className="mt-1.5 text-xs text-gray-400 italic cursor-text hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                          onDoubleClick={() => startEditNotes(app)}
                          title="Doppelklick zum Bearbeiten"
                        >
                          {app.notes || '➕ Notiz hinzufügen...'}
                        </p>
                      )}
                    </div>
                  )
                })}
                {cards.length === 0 && <p className="text-xs text-gray-400 text-center py-4">Leer</p>}
              </div>
            </div>
          )
        })}
      </div>

      {/* Detail-Modal mit Zeitstrahl */}
      {detailApp && (() => {
        const job = jobMap[detailApp.job_id]
        return (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            role="dialog" aria-modal="true" aria-label="Bewerbungsdetails"
            onClick={() => setDetailApp(null)}>
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl space-y-4"
              onClick={e => e.stopPropagation()}>
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-bold">{job?.title ?? `Stelle #${detailApp.job_id}`}</h2>
                  <p className="text-sm text-gray-500">{job?.company}{job?.city && ` • ${job.city}`}</p>
                </div>
                <button onClick={() => setDetailApp(null)} aria-label="Schließen" className="text-gray-400 hover:text-gray-600"><X size={20} aria-hidden /></button>
              </div>

              {/* Status ändern */}
              <div>
                <label className="text-xs text-gray-500 mb-1 block">Status ändern</label>
                <div className="flex flex-wrap gap-1">
                  {COLUMNS.map(col => (
                    <button key={col.key}
                      onClick={() => { moveMutation.mutate({ id: detailApp.id, status: col.key }); setDetailApp({ ...detailApp, status: col.key }) }}
                      className={clsx('text-xs px-3 py-1 rounded-full border transition-colors',
                        detailApp.status === col.key ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700')}
                      aria-pressed={detailApp.status === col.key}>{col.label}</button>
                  ))}
                </div>
              </div>

              {/* Zeitstrahl */}
              {timeline.length > 0 && (
                <div>
                  <label className="text-xs text-gray-500 mb-2 flex items-center gap-1"><Clock size={12} aria-hidden /> Statusverlauf</label>
                  <ol className="relative border-l border-gray-200 dark:border-gray-700 ml-2 space-y-3">
                    {timeline.map((entry, i) => (
                      <li key={i} className="ml-4">
                        <span className="absolute -left-1.5 w-3 h-3 rounded-full bg-blue-500 border-2 border-white dark:border-gray-800" aria-hidden />
                        <p className="text-xs font-medium">{STATUS_ICONS[entry.status] ?? '🟡'} {entry.status}</p>
                        <p className="text-xs text-gray-400">{new Date(entry.changed_at).toLocaleString('de-DE')}</p>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              <button onClick={() => deleteMutation.mutate(detailApp.id)}
                className="flex items-center gap-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-lg transition-colors">
                <X size={14} aria-hidden /> Entfernen
              </button>
            </div>
          </div>
        )
      })()}
    </div>
  )
}
