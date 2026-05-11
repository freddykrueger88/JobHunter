import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { Wand2, Copy, Download, Loader2 } from 'lucide-react'

const TONES = [
  { value: 'formell', label: '👔 Formell' },
  { value: 'direkt',  label: '⚡ Direkt' },
  { value: 'modern',  label: '✨ Modern' },
  { value: 'kreativ', label: '🎨 Kreativ' },
]

export default function CoverLetter({ jobId, cvId }: { jobId?: number; cvId?: number }) {
  const [tone, setTone] = useState('formell')
  const [template, setTemplate] = useState('')
  const [result, setResult] = useState('')
  const [copied, setCopied] = useState(false)

  const generateMutation = useMutation({
    mutationFn: () => axios.post('/api/ai/generate-cover-letter', {
      job_id: jobId,
      cv_id: cvId,
      tone,
      template_text: template || null,
    }),
    onSuccess: (res) => setResult(res.data.content),
  })

  const handleCopy = () => {
    navigator.clipboard.writeText(result)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([result], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'anschreiben.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Wand2 size={18} aria-hidden /> Anschreiben generieren
      </h2>

      {/* Ton wählen */}
      <div>
        <label className="text-sm text-gray-500 block mb-1">KI-Ton</label>
        <div className="flex gap-2 flex-wrap">
          {TONES.map(t => (
            <button
              key={t.value}
              onClick={() => setTone(t.value)}
              className={`text-sm px-3 py-1 rounded-full border transition-colors ${
                tone === t.value
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              aria-pressed={tone === t.value}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Optionale Vorlage */}
      <div>
        <label className="text-sm text-gray-500 block mb-1">
          Vorlage (optional) – Platzhalter wie {{Ansprechpartner}} werden ersetzt
        </label>
        <textarea
          className="w-full h-28 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          placeholder="Vorlage hier einfügen oder leer lassen für automatische Erstellung..."
          value={template}
          onChange={e => setTemplate(e.target.value)}
          aria-label="Anschreiben-Vorlage"
        />
      </div>

      <button
        onClick={() => generateMutation.mutate()}
        disabled={generateMutation.isPending || !jobId}
        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        {generateMutation.isPending
          ? <><Loader2 size={15} className="animate-spin" aria-hidden /> KI generiert...</>
          : <><Wand2 size={15} aria-hidden /> Anschreiben erstellen</>}
      </button>

      {/* Ergebnis */}
      {result && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-500">Generiertes Anschreiben</label>
            <div className="flex gap-2">
              <button onClick={handleCopy} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                <Copy size={13} aria-hidden /> {copied ? 'Kopiert!' : 'Kopieren'}
              </button>
              <button onClick={handleDownload} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                <Download size={13} aria-hidden /> Download
              </button>
            </div>
          </div>
          <textarea
            className="w-full h-72 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
            value={result}
            onChange={e => setResult(e.target.value)}
            aria-label="Generiertes Anschreiben (bearbeitbar)"
          />
        </div>
      )}
    </div>
  )
}
