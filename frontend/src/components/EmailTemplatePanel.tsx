/**
 * E-Mail-Vorlagen fuer typische Bewerbungssituationen (Nachfrage,
 * Absage-Antwort, Termin bestaetigen/absagen, Zusage bestaetigen).
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { Mail, Copy, Check } from 'lucide-react'

const TEMPLATE_TYPES = ['followup', 'nachfrage', 'absage_antwort', 'zusage', 'termin_bestaetigen', 'termin_absagen'] as const
type TemplateType = typeof TEMPLATE_TYPES[number]

interface EmailResult { betreff: string; body: string }

interface Props { applicationId: number }

export default function EmailTemplatePanel({ applicationId }: Props) {
  const { t } = useTranslation('emailTemplatePanel')
  const [type, setType] = useState<TemplateType>('nachfrage')
  const [result, setResult] = useState<EmailResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [copiedField, setCopiedField] = useState<'betreff' | 'body' | null>(null)

  const run = async () => {
    setLoading(true)
    try {
      const { data } = await axios.get(`/api/applications/${applicationId}/email-template/${type}`)
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  const copy = (field: 'betreff' | 'body', value: string) => {
    navigator.clipboard.writeText(value)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  return (
    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 gap-2">
        <div>
          <p className="font-semibold text-sm flex items-center gap-1.5">
            <Mail size={14} aria-hidden /> {t('title')}
          </p>
          <p className="text-xs text-gray-400">{t('subtitle')}</p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <select
            value={type}
            onChange={e => setType(e.target.value as TemplateType)}
            className="text-sm px-2 py-1.5 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none"
            aria-label={t('typeAriaLabel')}
          >
            {TEMPLATE_TYPES.map(tt => (
              <option key={tt} value={tt}>{t(`types.${tt}`)}</option>
            ))}
          </select>
          <button
            onClick={run}
            disabled={loading}
            className="px-4 py-1.5 rounded-xl text-sm font-medium bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 transition-colors"
          >
            {loading ? t('generating') : t('generate')}
          </button>
        </div>
      </div>

      {result && (
        <div className="p-4 space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-gray-500">{t('subjectLabel')}</label>
              <button onClick={() => copy('betreff', result.betreff)} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                {copiedField === 'betreff' ? <Check size={12} className="text-green-500" /> : <Copy size={12} />}
                {t('copy')}
              </button>
            </div>
            <input
              className="w-full text-sm px-3 py-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none"
              value={result.betreff}
              onChange={e => setResult({ ...result, betreff: e.target.value })}
              aria-label={t('subjectLabel')}
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-gray-500">{t('bodyLabel')}</label>
              <button onClick={() => copy('body', result.body)} className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1">
                {copiedField === 'body' ? <Check size={12} className="text-green-500" /> : <Copy size={12} />}
                {t('copy')}
              </button>
            </div>
            <textarea
              className="w-full h-40 text-sm px-3 py-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none resize-y"
              value={result.body}
              onChange={e => setResult({ ...result, body: e.target.value })}
              aria-label={t('bodyLabel')}
            />
          </div>
        </div>
      )}
    </div>
  )
}
