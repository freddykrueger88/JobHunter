/**
 * Gehaltsnegotiations-Coach Modal.
 * Zeigt 3 Szenarien mit konkreten Formulierungen fuer E-Mail und Telefonat.
 */
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { X, TrendingUp, Copy, Check } from 'lucide-react'
import { formatCurrencyEur } from '../lib/formatDate'

interface Szenario {
  typ: 'konservativ' | 'realistisch' | 'optimistisch'
  betrag: number
  begruendung: string
  formulierung_email: string
  formulierung_telefonat: string
}

interface NegResult {
  analyse: string
  szenarien: Szenario[]
  tipps: string[]
}

const TYP_COLORS = {
  konservativ: 'border-gray-200 bg-gray-50 dark:bg-gray-800',
  realistisch: 'border-blue-300 bg-blue-50 dark:bg-blue-900/20 ring-2 ring-blue-300',
  optimistisch: 'border-green-200 bg-green-50 dark:bg-green-900/20',
}

function CopyButton({ text }: { text: string }) {
  const { t } = useTranslation('salaryNegotiationModal')
  const [copied, setCopied] = useState(false)
  const copy = () => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000) }
  return (
    <button onClick={copy} className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors">
      {copied ? <Check size={12} className="text-green-500" /> : <Copy size={12} />}
      {copied ? t('copied') : t('copy')}
    </button>
  )
}

interface Props {
  applicationId: number
  stelle: string
  ort: string
  gehaltWunsch: number
  gehaltMin?: number
  gehaltMax?: number
  erfahrungJahre: number
  onClose: () => void
}

export default function SalaryNegotiationModal(props: Props) {
  const { t, i18n } = useTranslation('salaryNegotiationModal')
  const [result, setResult] = useState<NegResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'email' | 'telefon'>('email')

  const run = async () => {
    setLoading(true)
    try {
      const { data } = await axios.post('/api/salary/negotiate', {
        stelle: props.stelle, ort: props.ort,
        erfahrung_jahre: props.erfahrungJahre,
        gehalt_wunsch: props.gehaltWunsch,
        gehalt_anzeige_min: props.gehaltMin,
        gehalt_anzeige_max: props.gehaltMax,
      })
      setResult(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal aria-label={t('dialogAriaLabel')}>
      <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between p-5 border-b border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <TrendingUp size={20} className="text-blue-500" />
            <h2 className="font-semibold">{t('heading')}</h2>
          </div>
          <button onClick={props.onClose} aria-label={t('close')}><X size={20} /></button>
        </div>

        <div className="p-5 space-y-5">
          {!result && (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">{t('introPrefix')} <strong>{props.stelle}</strong></p>
              <button onClick={run} disabled={loading}
                className="px-6 py-2 rounded-xl bg-blue-500 text-white font-medium hover:bg-blue-600 disabled:opacity-50 transition-colors">
                {loading ? t('generating') : t('generate')}
              </button>
            </div>
          )}

          {result && (
            <>
              <p className="text-sm text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 rounded-xl p-3">{result.analyse}</p>

              {/* Tab-Umschalter */}
              <div className="flex gap-2">
                {(['email', 'telefon'] as const).map(tab => (
                  <button key={tab} onClick={() => setActiveTab(tab)}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                      activeTab === tab ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                    }`}>
                    {tab === 'email' ? t('tabEmail') : t('tabPhone')}
                  </button>
                ))}
              </div>

              {/* Szenarien */}
              <div className="space-y-3">
                {result.szenarien.map(s => (
                  <div key={s.typ} className={`rounded-xl border p-4 space-y-2 ${TYP_COLORS[s.typ]}`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-semibold text-sm">{t(`scenarioTypes.${s.typ}`)}</p>
                        <p className="text-lg font-bold">{t('perYear', { amount: formatCurrencyEur(s.betrag, i18n.language) })}</p>
                      </div>
                      <CopyButton text={activeTab === 'email' ? s.formulierung_email : s.formulierung_telefonat} />
                    </div>
                    <p className="text-xs text-gray-500">{s.begruendung}</p>
                    <div className="bg-white/60 dark:bg-black/20 rounded-lg p-2.5 text-xs text-gray-700 dark:text-gray-200 whitespace-pre-line">
                      {activeTab === 'email' ? s.formulierung_email : s.formulierung_telefonat}
                    </div>
                  </div>
                ))}
              </div>

              {/* Tipps */}
              {result.tipps?.length > 0 && (
                <div className="text-xs space-y-1">
                  <p className="font-medium text-gray-500">{t('generalTips')}</p>
                  {result.tipps.map((tipp, i) => <p key={i} className="text-gray-600 dark:text-gray-300">• {tipp}</p>)}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
