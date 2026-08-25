import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  FileText, Upload, Trash2, Download, Loader2, Info, Plus, X,
  Wand2, ChevronDown, ChevronUp, AlertCircle,
} from 'lucide-react'
import clsx from 'clsx'

/* ─── Types ──────────────────────────────────────────────────── */

interface Template {
  id: number
  name: string
  filename: string
  placeholders: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

interface PlaceholderInfo {
  name: string
  description: string
}

interface Job {
  id: number
  title: string
  company: string
}

interface CV {
  id: number
  filename: string
  full_name: string | null
}

/* ─── API helpers ────────────────────────────────────────────── */

const api = {
  listTemplates: () => axios.get<Template[]>('/api/cover-letter-templates/').then(r => r.data),
  getPlaceholders: () => axios.get<PlaceholderInfo[]>('/api/cover-letter-templates/placeholders').then(r => r.data),
  uploadTemplate: (file: File, name: string) => {
    const fd = new FormData()
    fd.append('file', file)
    if (name) fd.append('name', name)
    return axios.post<Template>('/api/cover-letter-templates/upload', fd).then(r => r.data)
  },
  deleteTemplate: (id: number) => axios.delete(`/api/cover-letter-templates/${id}`),
  generateDoc: (templateId: number, jobId: number, cvId: number | null, tone: string, model: string) =>
    axios.post(`/api/cover-letter-templates/${templateId}/generate`, {
      job_id: jobId, cv_id: cvId, tone, model,
    }, { responseType: 'blob' }),
  listJobs: () => axios.get<Job[]>('/api/jobs/').then(r => r.data),
  listCvs: () => axios.get<CV[]>('/api/cv/').then(r => r.data),
}

/* ─── Constants ──────────────────────────────────────────────── */

const TONES = [
  { value: 'formell', label: '👔 Formell' },
  { value: 'direkt',  label: '⚡ Direkt' },
  { value: 'modern',  label: '✨ Modern' },
  { value: 'kreativ', label: '🎨 Kreativ' },
]

/* ─── UploadZone ─────────────────────────────────────────────── */

function UploadZone({ onUpload }: { onUpload: (file: File, name: string) => void }) {
  const [dragOver, setDragOver] = useState(false)
  const [name, setName] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.docx')) {
      alert('Nur .docx-Dateien erlaubt')
      return
    }
    setSelectedFile(file)
    if (!name) setName(file.name.replace(/\.docx$/i, ''))
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0])
  }, [name])

  const handleSubmit = () => {
    if (selectedFile) {
      onUpload(selectedFile, name)
      setSelectedFile(null)
      setName('')
    }
  }

  return (
    <div className="space-y-3">
      <div
        className={clsx(
          'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer',
          dragOver
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400',
        )}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('template-file-input')?.click()}
        role="button"
        tabIndex={0}
        aria-label="DOCX-Vorlage hochladen – klicken oder Datei hierher ziehen"
        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') document.getElementById('template-file-input')?.click() }}
      >
        <Upload size={32} className="mx-auto mb-2 text-gray-400" aria-hidden />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {selectedFile
            ? <><FileText size={14} className="inline mr-1" aria-hidden />{selectedFile.name}</>
            : 'DOCX-Datei hierher ziehen oder klicken zum Auswählen'
          }
        </p>
        <input
          id="template-file-input"
          type="file"
          accept=".docx"
          className="hidden"
          onChange={e => { if (e.target.files?.[0]) handleFile(e.target.files[0]) }}
        />
      </div>

      {selectedFile && (
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="text-xs text-gray-500 block mb-1">Vorlagenname</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="z.B. Meine Bewerbungsvorlage"
              aria-label="Name der Vorlage"
            />
          </div>
          <button
            onClick={handleSubmit}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <Plus size={15} aria-hidden /> Hochladen
          </button>
          <button
            onClick={() => { setSelectedFile(null); setName('') }}
            className="p-2 text-gray-400 hover:text-red-500 transition-colors"
            aria-label="Abbrechen"
          >
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  )
}

/* ─── PlaceholderHint ────────────────────────────────────────── */

function PlaceholderHint({ placeholders }: { placeholders: PlaceholderInfo[] }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-4">
      <button
        className="flex items-center gap-2 text-sm font-medium text-blue-700 dark:text-blue-300 w-full"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <Info size={16} aria-hidden />
        Verfügbare Platzhalter
        {open ? <ChevronUp size={14} className="ml-auto" /> : <ChevronDown size={14} className="ml-auto" />}
      </button>
      {open && (
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
          {placeholders.map(p => (
            <div key={p.name} className="flex items-start gap-2 text-sm">
              <code className="bg-blue-100 dark:bg-blue-800/50 text-blue-800 dark:text-blue-200 px-1.5 py-0.5 rounded text-xs font-mono whitespace-nowrap">
                {`{{${p.name}}}`}
              </code>
              <span className="text-gray-600 dark:text-gray-400 text-xs">{p.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ─── GenerateModal ──────────────────────────────────────────── */

function GenerateModal({
  template,
  onClose,
}: {
  template: Template
  onClose: () => void
}) {
  const [jobId, setJobId] = useState<number | ''>('')
  const [cvId, setCvId] = useState<number | ''>('')
  const [tone, setTone] = useState('formell')
  const [model, setModel] = useState('mistral')
  const [error, setError] = useState('')

  const { data: jobs = [] } = useQuery({ queryKey: ['jobs'], queryFn: api.listJobs })
  const { data: cvs = [] } = useQuery({ queryKey: ['cvs'], queryFn: api.listCvs })

  const generateMutation = useMutation({
    mutationFn: () => {
      if (!jobId) throw new Error('Bitte eine Stelle auswählen')
      return api.generateDoc(template.id, jobId as number, cvId || null, tone, model)
    },
    onSuccess: (res) => {
      // Download the blob
      const blob = new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const disposition = res.headers['content-disposition']
      const filenameMatch = disposition?.match(/filename="?(.+?)"?$/)
      a.download = filenameMatch?.[1] || 'Anschreiben.docx'
      a.click()
      URL.revokeObjectURL(url)
      setError('')
    },
    onError: (err: unknown) => {
      const detail = axios.isAxiosError(err) ? err.response?.data?.detail : undefined
      setError(detail || (err instanceof Error ? err.message : 'Fehler bei der Generierung'))
    },
  })

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
      role="dialog"
      aria-modal="true"
      aria-label={`Anschreiben generieren mit Vorlage: ${template.name}`}
    >
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg mx-4 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Wand2 size={18} aria-hidden />
            Anschreiben generieren
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded" aria-label="Schließen">
            <X size={18} />
          </button>
        </div>

        <p className="text-sm text-gray-500">
          Vorlage: <strong>{template.name}</strong> ({template.placeholders.length} Platzhalter)
        </p>

        {/* Stelle wählen */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">Stelle *</label>
          <select
            value={jobId}
            onChange={e => setJobId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Stelle auswählen"
            required
          >
            <option value="">— Stelle wählen —</option>
            {jobs.map((j: Job) => (
              <option key={j.id} value={j.id}>
                {j.title} – {j.company}
              </option>
            ))}
          </select>
        </div>

        {/* CV wählen */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">Lebenslauf (optional)</label>
          <select
            value={cvId}
            onChange={e => setCvId(e.target.value ? Number(e.target.value) : '')}
            className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Lebenslauf auswählen"
          >
            <option value="">— Kein CV —</option>
            {cvs.map((c: CV) => (
              <option key={c.id} value={c.id}>
                {c.full_name || c.filename}
              </option>
            ))}
          </select>
        </div>

        {/* Ton */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">KI-Ton</label>
          <div className="flex gap-2 flex-wrap">
            {TONES.map(t => (
              <button
                key={t.value}
                onClick={() => setTone(t.value)}
                className={clsx(
                  'text-sm px-3 py-1 rounded-full border transition-colors',
                  tone === t.value
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700',
                )}
                aria-pressed={tone === t.value}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* KI-Modell */}
        <div>
          <label className="text-sm text-gray-500 block mb-1">KI-Modell</label>
          <input
            type="text"
            value={model}
            onChange={e => setModel(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="mistral"
            aria-label="KI-Modell"
          />
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded-lg px-3 py-2">
            <AlertCircle size={14} aria-hidden /> {error}
          </div>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Abbrechen
          </button>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending || !jobId}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            {generateMutation.isPending
              ? <><Loader2 size={15} className="animate-spin" aria-hidden /> KI generiert...</>
              : <><Download size={15} aria-hidden /> DOCX generieren &amp; herunterladen</>
            }
          </button>
        </div>
      </div>
    </div>
  )
}

/* ─── TemplateCard ───────────────────────────────────────────── */

function TemplateCard({
  template,
  onDelete,
  onGenerate,
}: {
  template: Template
  onDelete: (id: number) => void
  onGenerate: (t: Template) => void
}) {
  const [confirmDelete, setConfirmDelete] = useState(false)

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-xl p-4 space-y-3 bg-white dark:bg-gray-800 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <FileText size={20} className="text-blue-500 flex-shrink-0" aria-hidden />
          <div>
            <h4 className="font-medium text-sm">{template.name}</h4>
            <p className="text-xs text-gray-400">{template.filename}</p>
          </div>
        </div>
        <span className="text-xs text-gray-400">
          {new Date(template.created_at).toLocaleDateString('de-DE')}
        </span>
      </div>

      {/* Platzhalter */}
      {template.placeholders.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {template.placeholders.map(p => (
            <span
              key={p}
              className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded-full font-mono"
            >
              {`{{${p}}}`}
            </span>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 pt-1">
        <button
          onClick={() => onGenerate(template)}
          className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
          aria-label={`Anschreiben generieren mit ${template.name}`}
        >
          <Wand2 size={13} aria-hidden /> Generieren
        </button>

        {confirmDelete ? (
          <div className="flex items-center gap-1 ml-auto">
            <span className="text-xs text-red-500">Wirklich löschen?</span>
            <button
              onClick={() => { onDelete(template.id); setConfirmDelete(false) }}
              className="text-xs text-red-600 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              Ja
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="text-xs text-gray-400 hover:text-gray-600 px-2 py-1"
            >
              Nein
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="ml-auto p-1.5 text-gray-400 hover:text-red-500 rounded transition-colors"
            aria-label={`Vorlage ${template.name} löschen`}
          >
            <Trash2 size={14} />
          </button>
        )}
      </div>
    </div>
  )
}

/* ─── Main Page ──────────────────────────────────────────────── */

export default function Templates() {
  const queryClient = useQueryClient()
  const [generateTarget, setGenerateTarget] = useState<Template | null>(null)

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: api.listTemplates,
  })

  const { data: placeholders = [] } = useQuery({
    queryKey: ['template-placeholders'],
    queryFn: api.getPlaceholders,
  })

  const uploadMutation = useMutation({
    mutationFn: ({ file, name }: { file: File; name: string }) => api.uploadTemplate(file, name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.deleteTemplate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['templates'] }),
  })

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <FileText size={24} aria-hidden /> Anschreiben-Vorlagen
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Lade deine eigene DOCX-Vorlage mit Platzhaltern hoch. Die KI befüllt sie automatisch für jede Stelle.
        </p>
      </div>

      {/* Platzhalter-Info */}
      <PlaceholderHint placeholders={placeholders} />

      {/* Upload */}
      <div>
        <h3 className="text-sm font-medium text-gray-500 mb-2">Vorlage hochladen</h3>
        <UploadZone onUpload={(file, name) => uploadMutation.mutate({ file, name })} />
        {uploadMutation.isPending && (
          <p className="text-sm text-blue-500 mt-2 flex items-center gap-1">
            <Loader2 size={14} className="animate-spin" /> Wird hochgeladen...
          </p>
        )}
        {uploadMutation.isError && (
          <p className="text-sm text-red-500 mt-2 flex items-center gap-1">
            <AlertCircle size={14} /> Fehler beim Hochladen: {(axios.isAxiosError(uploadMutation.error) ? uploadMutation.error.response?.data?.detail : undefined) || 'Unbekannter Fehler'}
          </p>
        )}
        {uploadMutation.isSuccess && (
          <p className="text-sm text-green-600 mt-2">✓ Vorlage erfolgreich hochgeladen!</p>
        )}
      </div>

      {/* Template List */}
      <div>
        <h3 className="text-sm font-medium text-gray-500 mb-3">
          Meine Vorlagen ({templates.length})
        </h3>

        {isLoading ? (
          <div className="flex items-center gap-2 text-gray-400 py-8 justify-center">
            <Loader2 size={18} className="animate-spin" /> Vorlagen werden geladen...
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <FileText size={40} className="mx-auto mb-3 opacity-50" />
            <p className="text-sm">Noch keine Vorlagen vorhanden.</p>
            <p className="text-xs mt-1">Lade eine DOCX-Datei mit Platzhaltern hoch, um loszulegen.</p>
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {templates.map(t => (
              <TemplateCard
                key={t.id}
                template={t}
                onDelete={id => deleteMutation.mutate(id)}
                onGenerate={setGenerateTarget}
              />
            ))}
          </div>
        )}
      </div>

      {/* Generate Modal */}
      {generateTarget && (
        <GenerateModal
          template={generateTarget}
          onClose={() => setGenerateTarget(null)}
        />
      )}
    </div>
  )
}
