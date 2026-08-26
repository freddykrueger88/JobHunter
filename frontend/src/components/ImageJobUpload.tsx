/**
 * Foto-Upload Komponente fuer Stellenanzeigen.
 * Unterstuetzt Drag & Drop, Klick-Upload und Kamera (Mobile).
 */
import { useState, useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { Camera, Upload, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import axios from 'axios'
import clsx from 'clsx'

interface ParsedJob {
  id: number
  title: string
  company: string
  city: string | null
  description: string | null
}

interface Props {
  onJobCreated: (job: ParsedJob) => void
}

type State = 'idle' | 'dragging' | 'uploading' | 'success' | 'error'

export default function ImageJobUpload({ onJobCreated }: Props) {
  const { t } = useTranslation('imageJobUpload')
  const [state, setState] = useState<State>('idle')
  const [preview, setPreview] = useState<string | null>(null)
  const [result, setResult] = useState<{ job: ParsedJob; ocr_text: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const upload = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError(t('errorImagesOnly'))
      setState('error')
      return
    }
    setPreview(URL.createObjectURL(file))
    setState('uploading')
    setError(null)

    const form = new FormData()
    form.append('file', file)

    try {
      const { data } = await axios.post('/api/jobs/from-image', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
      setState('success')
      onJobCreated(data.job)
    } catch (err) {
      const detail = axios.isAxiosError(err) ? (err.response?.data as { detail?: string } | undefined)?.detail : undefined
      setError(detail ?? t('errorUploadFailed'))
      setState('error')
    }
  }, [onJobCreated, t])

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setState('idle')
    const file = e.dataTransfer.files[0]
    if (file) upload(file)
  }, [upload])

  const reset = () => {
    setState('idle')
    setPreview(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="space-y-4">
      {/* Upload-Zone */}
      <div
        onDrop={onDrop}
        onDragOver={e => { e.preventDefault(); setState('dragging') }}
        onDragLeave={() => setState('idle')}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label={t('uploadAriaLabel')}
        onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
        className={clsx(
          'relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all',
          state === 'dragging' && 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
          state === 'idle'     && 'border-gray-300 dark:border-gray-600 hover:border-blue-400',
          state === 'success'  && 'border-green-500 bg-green-50 dark:bg-green-900/20',
          state === 'error'    && 'border-red-400 bg-red-50 dark:bg-red-900/20',
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          className="hidden"
          onChange={e => e.target.files?.[0] && upload(e.target.files[0])}
        />

        {state === 'idle' && (
          <div className="space-y-3">
            <div className="flex justify-center gap-3">
              <Upload size={28} className="text-gray-400" aria-hidden />
              <Camera size={28} className="text-gray-400" aria-hidden />
            </div>
            <p className="font-medium text-gray-700 dark:text-gray-300">{t('dropHere')}</p>
            <p className="text-sm text-gray-400">{t('fileTypes')}</p>
            <p className="text-xs text-gray-400">{t('cameraHint')}</p>
          </div>
        )}

        {state === 'uploading' && (
          <div className="flex flex-col items-center gap-3">
            {preview && <img src={preview} alt={t('previewAlt')} className="h-24 w-auto rounded-lg object-cover" />}
            <Loader2 size={24} className="animate-spin text-blue-500" aria-hidden />
            <p className="text-sm text-gray-500">{t('analyzing')}</p>
          </div>
        )}

        {state === 'success' && result && (
          <div className="text-left space-y-2">
            <div className="flex items-center gap-2 text-green-600 font-medium mb-3">
              <CheckCircle size={18} aria-hidden /> {t('jobDetected')}
            </div>
            <p><span className="text-gray-400 text-xs">{t('titleLabel')}</span><br /><strong>{result.job.title || '–'}</strong></p>
            <p><span className="text-gray-400 text-xs">{t('companyLabel')}</span><br />{result.job.company || '–'}</p>
            <p><span className="text-gray-400 text-xs">{t('locationLabel')}</span><br />{result.job.city || '–'}</p>
          </div>
        )}

        {state === 'error' && (
          <div className="flex flex-col items-center gap-2 text-red-500">
            <AlertCircle size={24} aria-hidden />
            <p className="font-medium">{t('error')}</p>
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>

      {(state === 'success' || state === 'error') && (
        <button onClick={reset}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors">
          <X size={14} aria-hidden /> {t('newUpload')}
        </button>
      )}
    </div>
  )
}
