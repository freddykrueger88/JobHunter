import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { GripVertical, X, Clock, Plus, Calendar, ChevronRight } from 'lucide-react'
import clsx from 'clsx'
import { useNavigate } from 'react-router-dom'
import JobSearchDropdown, { type JobOption } from '../components/JobSearchDropdown'

interface Application {
  id: number
  job_id: number
  status: string
  notes: string | null
  kanban_position: number
  applied_at: string | null
  interview_at: string | null
}
interface Job {
  id: number
  title: string
  company: string
  city: string | null
  url: string | null
}
interface TimelineEntry {
  status: string
  changed_at: string
}

const COLUMNS: { key: string; label: string; colorClass: string; borderClass: string; bgClass: string }[] = [
  { key: 'interessant', label: 'Interessant',  colorClass: 'text-purple-600 dark:text-purple-400',  borderClass: 'border-t-purple-400',  bgClass: 'bg-purple-50 dark:bg-purple-950/30' },
  { key: 'beworben',    label: 'Beworben',     colorClass: 'text-blue-600 dark:text-blue-400',     borderClass: 'border-t-blue-400',    bgClass: 'bg-blue-50 dark:bg-blue-950/30' },
  { key: 'interview',   label: 'Interview',    colorClass: 'text-yellow-600 dark:text-yellow-400', borderClass: 'border-t-yellow-400',  bgClass: 'bg-yellow-50 dark:bg-yellow-950/30' },
  { key: 'angenommen',  label: 'Angenommen',   colorClass: 'text-green-600 dark:text-green-400',   borderClass: 'border-t-green-400',   bgClass: 'bg-green-50 dark:bg-green-950/30' },
  { key: 'absage',      label: 'Absage',       colorClass: 'text-red-500 dark:text-red-400',       borderClass: 'border-t-red-400',     bgClass: 'bg-red-50 dark:bg-red-950/30' },
]

const STATUS_ICONS: Record<string, string> = {
  interessant: '⭐',
  beworben: '📤',
  interview: '💬',
  angenommen: '✅',
  absage: '❌',
}

function formatDate(iso: string | null): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Kanban() {
  const qc = useQueryClient()
  const navigate = useNavigate()

  // Drag state
  const [draggingId, setDraggingId] = useState<number | null>(null)
  const [dragOverCol, setDragOverCol] = useState<string | null>(null)
  const [dragOverCardId, setDragOverCardId] = useState<number | null>(null)

  // Keyboard drag state
  const [kbSelected, setKbSelected] = useState<number | null>(null)

  // Detail modal
  const [detailApp, setDetailApp] = useState<Application | null>(null)

  // Inline note editing
  const [editingNotes, setEditingNotes] = useState<number | null>(null)
  const [notesValue, setNotesValue] = useState('')
  const notesRef = useRef<HTMLTextAreaElement>(null)

  // Quick-Add state per column
  const [quickAddCol, setQuickAddCol] = useState<string | null>(null)

  // Interview date edit
  const [editingInterview, setEditingInterview] = useState(false)
  const [interviewValue, setInterviewValue] = useState('')

  // ───── Queries ─────
  const { data: applications = [] } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: () => axios.get('/api/applications/').then(r => r.data),
  })

  const { data: jobs = [], isLoading: jobsLoading } = useQuery<Job[]>({
    queryKey: ['jobs-all'],
    queryFn: () => axios.get('/api/jobs/?hide_hidden=false').then(r => r.data),
  })
  const jobMap = Object.fromEntries(jobs.map(j => [j.id, j]))

  // IDs aller Jobs mit bestehender Bewerbung
  const appliedJobIds = new Set(applications.map(a => a.job_id))

  // Jobs als JobOption Array für Dropdown
  const jobOptions: JobOption[] = jobs.map(j => ({
    id: j.id,
    title: j.title,
    company: j.company,
    city: j.city,
  }))

  const { data: timeline = [], refetch: fetchTimeline } = useQuery<TimelineEntry[]>({
    queryKey: ['timeline', detailApp?.id],
    queryFn: () =>
      detailApp
        ? axios.get(`/api/applications/${detailApp.id}/timeline`).then(r => r.data)
        : Promise.resolve([]),
    enabled: !!detailApp,
  })

  // ───── Mutations ─────
  const moveMutation = useMutation({
    mutationFn: ({ id, status, kanban_position }: { id: number; status: string; kanban_position?: number }) =>
      axios.patch(`/api/applications/${id}`, { status, ...(kanban_position !== undefined && { kanban_position }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  })

  const notesMutation = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes: string }) =>
      axios.patch(`/api/applications/${id}`, { notes }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      setEditingNotes(null)
    },
  })

  const interviewMutation = useMutation({
    mutationFn: ({ id, interview_at }: { id: number; interview_at: string | null }) =>
      axios.patch(`/api/applications/${id}`, { interview_at }),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      setDetailApp(prev => prev ? { ...prev, interview_at: data.data.interview_at } : null)
      setEditingInterview(false)
    },
  })

  const createMutation = useMutation({
    mutationFn: ({ job_id, status }: { job_id: number; status: string }) =>
      axios.post('/api/applications/', { job_id, status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      setQuickAddCol(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => axios.delete(`/api/applications/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] })
      setDetailApp(null)
    },
  })

  // ───── Drag helpers ─────
  const getColApps = useCallback(
    (colKey: string) =>
      applications
        .filter(a => a.status === colKey)
        .sort((a, b) => a.kanban_position - b.kanban_position),
    [applications]
  )

  const handleDrop = (targetColKey: string, targetCardId: number | null) => {
    if (draggingId === null) return
    const dragged = applications.find(a => a.id === draggingId)
    if (!dragged) return

    const colApps = getColApps(targetColKey).filter(a => a.id !== draggingId)

    let newPosition: number
    if (targetCardId === null) {
      newPosition = colApps.length > 0 ? colApps[colApps.length - 1].kanban_position + 1 : 0
    } else {
      const targetIndex = colApps.findIndex(a => a.id === targetCardId)
      const before = colApps[targetIndex - 1]?.kanban_position ?? -1
      const after = colApps[targetIndex]?.kanban_position ?? colApps.length
      newPosition = Math.floor((before + after) / 2)
      if (newPosition === before || newPosition === after) {
        newPosition = targetIndex
      }
    }

    moveMutation.mutate({ id: draggingId, status: targetColKey, kanban_position: newPosition })
    setDraggingId(null)
    setDragOverCol(null)
    setDragOverCardId(null)
  }

  // ───── Keyboard drag ─────
  const handleCardKeyDown = (e: React.KeyboardEvent, app: Application) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault()
      setKbSelected(kbSelected === app.id ? null : app.id)
    }
    if (kbSelected === app.id) {
      const colIdx = COLUMNS.findIndex(c => c.key === app.status)
      if (e.key === 'ArrowRight' && colIdx < COLUMNS.length - 1) {
        e.preventDefault()
        moveMutation.mutate({ id: app.id, status: COLUMNS[colIdx + 1].key })
        setKbSelected(null)
      }
      if (e.key === 'ArrowLeft' && colIdx > 0) {
        e.preventDefault()
        moveMutation.mutate({ id: app.id, status: COLUMNS[colIdx - 1].key })
        setKbSelected(null)
      }
      if (e.key === 'Escape') setKbSelected(null)
    }
  }

  // ───── Notes helpers ─────
  const startEditNotes = (app: Application) => {
    setEditingNotes(app.id)
    setNotesValue(app.notes ?? '')
    setTimeout(() => notesRef.current?.focus(), 50)
  }

  const saveNotes = (id: number) => {
    notesMutation.mutate({ id, notes: notesValue })
  }

  // ───── Quick-Add via Dropdown ─────
  const handleJobSelect = (job: JobOption, colKey: string) => {
    createMutation.mutate({ job_id: job.id, status: colKey })
  }

  // ───── Render ─────
  return (
    <div className="h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Kanban-Board</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {applications.length} Bewerbung{applications.length !== 1 ? 'en' : ''}
        </p>
      </div>

      {/* Keyboard hint */}
      {kbSelected && (
        <div className="mb-3 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg text-xs text-blue-700 dark:text-blue-300">
          Karte ausgewählt –{' '}
          <kbd className="font-mono bg-white dark:bg-gray-800 px-1 rounded border">←</kbd>{' '}
          <kbd className="font-mono bg-white dark:bg-gray-800 px-1 rounded border">→</kbd>{' '}
          zum Verschieben,{' '}
          <kbd className="font-mono bg-white dark:bg-gray-800 px-1 rounded border">Esc</kbd> zum Abbrechen
        </div>
      )}

      {/* Board */}
      <div className="flex gap-3 overflow-x-auto pb-4 items-start">
        {COLUMNS.map(col => {
          const cards = getColApps(col.key)
          const isDropTarget = dragOverCol === col.key
          const isQuickAdd = quickAddCol === col.key

          return (
            <div
              key={col.key}
              className={clsx(
                'flex-shrink-0 w-64 rounded-xl transition-all duration-150',
                isDropTarget && dragOverCardId === null ? 'ring-2 ring-blue-400 ring-offset-1' : ''
              )}
              onDragOver={e => { e.preventDefault(); setDragOverCol(col.key) }}
              onDragLeave={() => { setDragOverCol(null); setDragOverCardId(null) }}
              onDrop={e => { e.preventDefault(); handleDrop(col.key, dragOverCardId) }}
              role="region"
              aria-label={`Spalte: ${col.label}`}
            >
              {/* Column header */}
              <div className={clsx('border-t-4 rounded-t-xl px-3 py-2 flex items-center justify-between', col.borderClass, col.bgClass)}>
                <span className={clsx('font-semibold text-sm', col.colorClass)}>
                  {STATUS_ICONS[col.key]} {col.label}
                </span>
                <span className="text-xs bg-white/60 dark:bg-gray-800/60 rounded-full px-2 py-0.5 font-mono">
                  {cards.length}
                </span>
              </div>

              {/* Cards area */}
              <div
                className={clsx(
                  'rounded-b-xl p-2 space-y-2 min-h-[8rem] transition-colors duration-150',
                  isDropTarget && dragOverCardId === null
                    ? 'bg-blue-50/80 dark:bg-blue-900/20'
                    : 'bg-gray-50 dark:bg-gray-900'
                )}
              >
                {cards.map(app => {
                  const job = jobMap[app.job_id]
                  const isKbSelected = kbSelected === app.id
                  const isDraggingThis = draggingId === app.id
                  const isDropAbove = dragOverCardId === app.id && dragOverCol === col.key

                  return (
                    <div key={app.id}>
                      {isDropAbove && (
                        <div className="h-1 bg-blue-400 rounded-full mx-1 mb-1 transition-all" aria-hidden />
                      )}
                      <div
                        draggable
                        onDragStart={() => { setDraggingId(app.id); setKbSelected(null) }}
                        onDragEnd={() => { setDraggingId(null); setDragOverCol(null); setDragOverCardId(null) }}
                        onDragOver={e => { e.preventDefault(); e.stopPropagation(); setDragOverCardId(app.id); setDragOverCol(col.key) }}
                        onDrop={e => { e.preventDefault(); e.stopPropagation(); handleDrop(col.key, app.id) }}
                        tabIndex={0}
                        onKeyDown={e => handleCardKeyDown(e, app)}
                        aria-label={`${job?.title ?? 'Stelle'} bei ${job?.company ?? '?'} – Status: ${col.label}. Enter zum Auswählen und mit Pfeiltasten verschieben.`}
                        className={clsx(
                          'bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm border transition-all cursor-grab active:cursor-grabbing select-none',
                          isKbSelected ? 'border-blue-500 ring-2 ring-blue-400' : 'border-transparent hover:border-gray-200 dark:hover:border-gray-600',
                          isDraggingThis && 'opacity-40 scale-95',
                          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400'
                        )}
                      >
                        {/* Card header – click to open detail */}
                        <div
                          className="flex items-start gap-1 cursor-pointer"
                          onClick={() => {
                            setDetailApp(app)
                            fetchTimeline()
                            setEditingInterview(false)
                            setInterviewValue(app.interview_at ? app.interview_at.slice(0, 16) : '')
                          }}
                          role="button"
                          tabIndex={-1}
                          aria-label={`${job?.title ?? 'Stelle'} Details öffnen`}
                        >
                          <GripVertical size={14} className="text-gray-300 mt-0.5 shrink-0" aria-hidden />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium truncate">{job?.title ?? `Stelle #${app.job_id}`}</p>
                            <p className="text-xs text-gray-500 truncate">{job?.company}</p>
                            {job?.city && <p className="text-xs text-gray-400">{job.city}</p>}
                          </div>
                          <ChevronRight size={12} className="text-gray-300 mt-0.5 shrink-0" aria-hidden />
                        </div>

                        {/* Interview date badge */}
                        {app.interview_at && (
                          <div className="mt-1.5 flex items-center gap-1 text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 rounded px-1.5 py-0.5">
                            <Calendar size={10} aria-hidden />
                            <span>{formatDate(app.interview_at)}</span>
                          </div>
                        )}

                        {/* Inline notes */}
                        {editingNotes === app.id ? (
                          <textarea
                            ref={notesRef}
                            value={notesValue}
                            onChange={e => setNotesValue(e.target.value)}
                            onBlur={() => saveNotes(app.id)}
                            onKeyDown={e => {
                              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); saveNotes(app.id) }
                              if (e.key === 'Escape') setEditingNotes(null)
                            }}
                            onClick={e => e.stopPropagation()}
                            className="mt-2 w-full text-xs rounded px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-blue-400 focus:outline-none resize-none"
                            rows={2}
                            aria-label="Notiz bearbeiten"
                          />
                        ) : (
                          <p
                            className="mt-1.5 text-xs text-gray-400 italic cursor-text hover:text-gray-600 dark:hover:text-gray-300 transition-colors line-clamp-2"
                            onDoubleClick={e => { e.stopPropagation(); startEditNotes(app) }}
                            title="Doppelklick zum Bearbeiten"
                          >
                            {app.notes || '+ Notiz hinzufügen…'}
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })}

                {/* Empty state */}
                {cards.length === 0 && !isQuickAdd && (
                  <p className="text-xs text-gray-400 text-center py-4 select-none">Leer – hierher ziehen</p>
                )}

                {/* Quick-Add – Dropdown */}
                {isQuickAdd ? (
                  <div className="pt-1">
                    <JobSearchDropdown
                      jobs={jobOptions}
                      appliedJobIds={appliedJobIds}
                      loading={jobsLoading}
                      onSelect={job => handleJobSelect(job, col.key)}
                      onCancel={() => setQuickAddCol(null)}
                      placeholder={`Stelle für "${col.label}" suchen…`}
                    />
                    {createMutation.isPending && (
                      <p className="text-xs text-gray-400 text-center pt-1">Wird hinzugefügt…</p>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => setQuickAddCol(col.key)}
                    className="w-full flex items-center justify-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded-lg py-2 transition-colors"
                    aria-label={`Bewerbung in Spalte ${col.label} hinzufügen`}
                  >
                    <Plus size={12} aria-hidden /> Hinzufügen
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Detail Modal */}
      {detailApp &&
        (() => {
          const job = jobMap[detailApp.job_id]
          return (
            <div
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
              role="dialog"
              aria-modal="true"
              aria-labelledby="detail-modal-title"
              onClick={() => setDetailApp(null)}
            >
              <div
                className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl space-y-4 max-h-[90vh] overflow-y-auto"
                onClick={e => e.stopPropagation()}
              >
                {/* Modal header */}
                <div className="flex items-start justify-between">
                  <div className="min-w-0 pr-2">
                    <h2 id="detail-modal-title" className="text-lg font-bold truncate">
                      {job?.title ?? `Stelle #${detailApp.job_id}`}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {job?.company}{job?.city && ` • ${job.city}`}
                    </p>
                  </div>
                  <button
                    onClick={() => setDetailApp(null)}
                    aria-label="Schließen"
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors shrink-0"
                  >
                    <X size={20} aria-hidden />
                  </button>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {job?.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 text-center text-xs px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                    >
                      🔗 Stellenanzeige
                    </a>
                  )}
                  <button
                    onClick={() => navigate(`/jobs?highlight=${detailApp.job_id}`)}
                    className="flex-1 text-xs px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                  >
                    📋 Zur Stelle
                  </button>
                </div>

                {/* Status buttons */}
                <div>
                  <label className="text-xs text-gray-500 mb-1.5 block">Status ändern</label>
                  <div className="flex flex-wrap gap-1">
                    {COLUMNS.map(col => (
                      <button
                        key={col.key}
                        onClick={() => {
                          moveMutation.mutate({ id: detailApp.id, status: col.key })
                          setDetailApp({ ...detailApp, status: col.key })
                        }}
                        className={clsx(
                          'text-xs px-3 py-1 rounded-full border transition-colors',
                          detailApp.status === col.key
                            ? 'bg-blue-600 text-white border-blue-600'
                            : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
                        )}
                        aria-pressed={detailApp.status === col.key}
                      >
                        {STATUS_ICONS[col.key]} {col.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Interview date */}
                <div>
                  <label className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                    <Calendar size={12} aria-hidden /> Gesprächstermin
                  </label>
                  {editingInterview ? (
                    <div className="flex gap-2">
                      <input
                        type="datetime-local"
                        value={interviewValue}
                        onChange={e => setInterviewValue(e.target.value)}
                        className="flex-1 text-xs px-2 py-1 rounded border border-blue-400 bg-gray-50 dark:bg-gray-700 focus:outline-none"
                        aria-label="Gesprächstermin Datum und Uhrzeit"
                      />
                      <button
                        onClick={() => interviewMutation.mutate({ id: detailApp.id, interview_at: interviewValue || null })}
                        className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      >
                        Speichern
                      </button>
                      <button
                        onClick={() => setEditingInterview(false)}
                        className="text-xs px-2 py-1 text-gray-500 hover:text-gray-700 transition-colors"
                      >
                        Abbrechen
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setEditingInterview(true)}
                      className="text-xs text-left text-gray-600 dark:text-gray-300 hover:underline"
                    >
                      {detailApp.interview_at ? formatDate(detailApp.interview_at) : '+ Termin setzen'}
                    </button>
                  )}
                </div>

                {/* Applied date */}
                {detailApp.applied_at && (
                  <p className="text-xs text-gray-500">
                    Beworben am: <span className="text-gray-700 dark:text-gray-300">{formatDate(detailApp.applied_at)}</span>
                  </p>
                )}

                {/* Timeline */}
                {timeline.length > 0 && (
                  <div>
                    <label className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                      <Clock size={12} aria-hidden /> Statusverlauf
                    </label>
                    <ol className="relative border-l border-gray-200 dark:border-gray-700 ml-2 space-y-3">
                      {timeline.map((entry, i) => (
                        <li key={i} className="ml-4">
                          <span className="absolute -left-1.5 w-3 h-3 rounded-full bg-blue-500 border-2 border-white dark:border-gray-800" aria-hidden />
                          <p className="text-xs font-medium">{STATUS_ICONS[entry.status] ?? '🟡'} {entry.status}</p>
                          <p className="text-xs text-gray-400">{formatDateTime(entry.changed_at)}</p>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* Delete */}
                <button
                  onClick={() => {
                    if (window.confirm('Bewerbung wirklich entfernen?')) deleteMutation.mutate(detailApp.id)
                  }}
                  disabled={deleteMutation.isPending}
                  className="flex items-center gap-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                >
                  <X size={14} aria-hidden /> Entfernen
                </button>
              </div>
            </div>
          )
        })()}
    </div>
  )
}
