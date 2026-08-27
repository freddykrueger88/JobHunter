import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { Wand2, Copy, Download, FileDown, Loader2 } from 'lucide-react'

const TONE_VALUES = ['formell', 'direkt', 'modern', 'kreativ'] as const

export default function CoverLetter({ jobId, cvId, applicationId, onGenerated }: { jobId?: number; cvId?: number; applicationId?: number; onGenerated?: () => void }) {
  const { t } = useTranslation('coverLetter')
  const [tone, setTone] = useState('formell')
  const [template, setTemplate] = useState('')
  const [result, setResult] = useState('')
  const [coverLetterId, setCoverLetterId] = useState<number | null>(null)
  const [copied, setCopied] = useState(false)
  const [pdfLoading, setPdfLoading] = useState(false)

  const generateMutation = useMutation({
    mutationFn: () => axios.post('/api/ai/generate-cover-letter', {
      job_id: jobId,
      cv_id: cvId,
      tone,
      template_text: template || null,
      ...(applicationId !== undefined && { application_id: applicationId }),
    }),
    onSuccess: (res) => {
      setResult(res.data.content)
      setCoverLetterId(res.data.id)
      onGenerated?.()
    },
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

  const handleDownloadPdf = async () => {
    if (!coverLetterId) return
    setPdfLoading(true)
    try {
      const res = await axios.post(
        `/api/cover-letters/${coverLetterId}/pdf`,
        { content: result },
        { responseType: 'blob' },
      )
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `anschreiben_${coverLetterId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Wand2 size={18} aria-hidden /> {t('heading')}
      </h2>

      {/* Ton wählen */}
      <div>
        <label className="text-sm text-gray-500 block mb-1">{t('toneLabel')}</label>
        <div className="flex gap-2 flex-wrap">
          {TONE_VALUES.map(value => (
            <button
              key={value}
              onClick={() => setTone(value)}
              className={`text-sm px-3 py-1 rounded-full border transition-colors ${
                tone === value
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
              aria-pressed={tone === value}
            >
              {t(`tones.${value}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Optionale Vorlage */}
      <div>
        <label className="text-sm text-gray-500 block mb-1">
          {t('templateLabel', { placeholder: '{{Ansprechpartner}}' })}
        </label>
        <textarea
          className="w-full h-28 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
          placeholder={t('templatePlaceholder')}
          value={template}
          onChange={e => setTemplate(e.target.value)}
          aria-label={t('templateAriaLabel')}
        />
      </div>

      <button
        onClick={() => generateMutation.mutate()}
        disabled={generateMutation.isPending || !jobId}
        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
      >
        {generateMutation.isPending
          ? <><Loader2 size={15} className="animate-spin" aria-hidden /> {t('generating')}</>
          : <><Wand2 size={15} aria-hidden /> {t('generate')}</>}
      </button>

      {/* Ergebnis */}
      {result && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm text-gray-500">{t('resultLabel')}</label>
            <div className="flex gap-2">
              <button onClick={handleCopy} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                <Copy size={13} aria-hidden /> {copied ? t('copied') : t('copy')}
              </button>
              <button onClick={handleDownload} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                <Download size={13} aria-hidden /> {t('download')}
              </button>
              {coverLetterId && (
                <button
                  onClick={handleDownloadPdf}
                  disabled={pdfLoading}
                  className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1 disabled:opacity-50"
                >
                  {pdfLoading
                    ? <Loader2 size={13} className="animate-spin" aria-hidden />
                    : <FileDown size={13} aria-hidden />} {t('downloadPdf')}
                </button>
              )}
            </div>
          </div>
          <textarea
            className="w-full h-72 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
            value={result}
            onChange={e => setResult(e.target.value)}
            aria-label={t('resultAriaLabel')}
          />
        </div>
      )}
    </div>
  )
}
