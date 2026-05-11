import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useTheme } from '../context/ThemeContext'
import type { Theme } from '../context/ThemeContext'
import { Save, Eye, EyeOff, ExternalLink } from 'lucide-react'
import clsx from 'clsx'

interface SettingsData {
  theme: string
  language: string
  ai_model: string
  ai_tone: string
  default_location: string | null
  default_radius_km: number
  hide_ausbildung: boolean
  reminder_default_days: number
  has_adzuna_key: boolean
  has_linkedin_key: boolean
  has_arbeitsagentur_key: boolean
}

const THEMES: { value: Theme; label: string; desc: string }[] = [
  { value: 'dark',  label: '🌙 Dark Mode',  desc: 'Dunkel, klassisch' },
  { value: 'light', label: '☀️ Light Mode', desc: 'Hell, klar' },
  { value: 'boys',  label: '💙 Boys Mode',  desc: 'Dark Blue' },
  { value: 'girls', label: '🌸 Girls Mode', desc: 'Pink Fluffy Wonderfully ✨' },
]

const TONES = ['formell', 'direkt', 'modern', 'kreativ']

const API_LINKS: Record<string, string> = {
  adzuna: 'https://developer.adzuna.com/',
  arbeitsagentur: 'https://jobsuche.api.bund.dev/',
  linkedin: 'https://developer.linkedin.com/',
}

export default function Settings() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme } = useTheme()
  const qc = useQueryClient()

  const { data: remote } = useQuery<SettingsData>({
    queryKey: ['settings'],
    queryFn: () => axios.get('/api/settings/').then(r => r.data),
  })

  const [aiModel, setAiModel] = useState('mistral')
  const [aiTone, setAiTone] = useState('formell')
  const [defaultLocation, setDefaultLocation] = useState('')
  const [defaultRadius, setDefaultRadius] = useState(25)
  const [hideAusbildung, setHideAusbildung] = useState(true)
  const [reminderDays, setReminderDays] = useState(7)
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})
  const [keys, setKeys] = useState<Record<string, string>>({
    adzuna_app_id: '', adzuna_api_key: '', linkedin_api_key: '',
    arbeitsagentur_client_id: '', arbeitsagentur_client_secret: '',
  })
  const [saved, setSaved] = useState(false)

  const { data: models = [] } = useQuery<string[]>({
    queryKey: ['ai-models'],
    queryFn: () => axios.get('/api/ai/models').then(r => r.data.models),
  })

  useEffect(() => {
    if (remote) {
      setAiModel(remote.ai_model)
      setAiTone(remote.ai_tone)
      setDefaultLocation(remote.default_location ?? '')
      setDefaultRadius(remote.default_radius_km)
      setHideAusbildung(remote.hide_ausbildung)
      setReminderDays(remote.reminder_default_days)
    }
  }, [remote])

  const saveMutation = useMutation({
    mutationFn: () => axios.patch('/api/settings/', {
      theme, language: i18n.language,
      ai_model: aiModel, ai_tone: aiTone,
      default_location: defaultLocation || null,
      default_radius_km: defaultRadius,
      hide_ausbildung: hideAusbildung,
      reminder_default_days: reminderDays,
      ...Object.fromEntries(Object.entries(keys).filter(([, v]) => v !== '')),
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      setKeys(k => Object.fromEntries(Object.entries(k).map(([key]) => [key, ''])))
    },
  })

  const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <section className="mb-8">
      <h2 className="text-lg font-semibold mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">{title}</h2>
      {children}
    </section>
  )

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t('settings.title')}</h1>
        <button
          onClick={() => saveMutation.mutate()}
          disabled={saveMutation.isPending}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            saved
              ? 'bg-green-600 text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50'
          )}
        >
          <Save size={15} aria-hidden />
          {saved ? 'Gespeichert ✅' : t('common.save')}
        </button>
      </div>

      {/* Design */}
      <Section title={`🎨 ${t('settings.theme')}`}>
        <div className="grid grid-cols-2 gap-3">
          {THEMES.map(opt => (
            <button key={opt.value} onClick={() => setTheme(opt.value)}
              className={clsx('rounded-xl p-4 text-left border-2 transition-all',
                theme === opt.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              )}
              aria-pressed={theme === opt.value}
            >
              <div className="font-medium">{opt.label}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">{opt.desc}</div>
            </button>
          ))}
        </div>
      </Section>

      {/* Sprache */}
      <Section title={`🌍 ${t('settings.language')}`}>
        <div className="flex gap-3">
          {['de', 'en'].map(lang => (
            <button key={lang}
              onClick={() => { i18n.changeLanguage(lang); localStorage.setItem('lang', lang) }}
              className={clsx('px-6 py-2 rounded-lg font-medium border-2 transition-all',
                i18n.language === lang
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              )}
              aria-pressed={i18n.language === lang}
            >
              {lang === 'de' ? '🇩🇪 Deutsch' : '🇬🇧 English'}
            </button>
          ))}
        </div>
      </Section>

      {/* KI */}
      <Section title={`🤖 ${t('settings.ai')}`}>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-500 block mb-1">KI-Modell</label>
            <select value={aiModel} onChange={e => setAiModel(e.target.value)}
              className="rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="KI-Modell wählen"
            >
              {(models.length ? models : ['mistral', 'llama3', 'phi3']).map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">KI-Ton</label>
            <div className="flex gap-2 flex-wrap">
              {TONES.map(t => (
                <button key={t} onClick={() => setAiTone(t)}
                  className={clsx('text-sm px-3 py-1 rounded-full border transition-colors capitalize',
                    aiTone === t
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
                  )}
                  aria-pressed={aiTone === t}
                >{t}</button>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* Suche */}
      <Section title="🔍 Stellensuche">
        <div className="space-y-3">
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="text-sm text-gray-500 block mb-1">Standard-Ort</label>
              <input value={defaultLocation} onChange={e => setDefaultLocation(e.target.value)}
                className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="z.B. Bremen" aria-label="Standard-Ort"
              />
            </div>
            <div className="w-32">
              <label className="text-sm text-gray-500 block mb-1">Radius (km)</label>
              <select value={defaultRadius} onChange={e => setDefaultRadius(Number(e.target.value))}
                className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
                aria-label="Standard-Radius"
              >
                {[10,25,50,100].map(r => <option key={r} value={r}>{r} km</option>)}
              </select>
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={hideAusbildung} onChange={e => setHideAusbildung(e.target.checked)} className="rounded" />
            Ausbildungsstellen standardmäßig ausblenden
          </label>
        </div>
      </Section>

      {/* Erinnerungen */}
      <Section title="🔔 Erinnerungen">
        <div>
          <label className="text-sm text-gray-500 block mb-1">Standard-Vorlaufzeit (Tage)</label>
          <input type="number" min={1} max={30} value={reminderDays} onChange={e => setReminderDays(Number(e.target.value))}
            className="w-24 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Standard-Erinnerungszeit in Tagen"
          />
        </div>
      </Section>

      {/* API Keys */}
      <Section title="🔑 API Keys">
        <p className="text-sm text-gray-500 mb-4">Keys werden verschlüsselt gespeichert. Aktuelle Keys werden nie angezeigt.</p>
        {([
          { key: 'adzuna_app_id',              label: 'Adzuna App ID',             portal: 'adzuna',         hasKey: remote?.has_adzuna_key },
          { key: 'adzuna_api_key',             label: 'Adzuna API Key',            portal: 'adzuna',         hasKey: remote?.has_adzuna_key },
          { key: 'arbeitsagentur_client_id',   label: 'Arbeitsagentur Client ID',  portal: 'arbeitsagentur', hasKey: remote?.has_arbeitsagentur_key },
          { key: 'arbeitsagentur_client_secret', label: 'Arbeitsagentur Secret',   portal: 'arbeitsagentur', hasKey: remote?.has_arbeitsagentur_key },
          { key: 'linkedin_api_key',           label: 'LinkedIn API Key',          portal: 'linkedin',       hasKey: remote?.has_linkedin_key },
        ] as const).map(({ key, label, portal, hasKey }) => (
          <div key={key} className="flex items-center gap-2 mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <label className="text-sm text-gray-500">{label}</label>
                {hasKey && <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full">✓ gesetzt</span>}
                <a href={API_LINKS[portal]} target="_blank" rel="noopener noreferrer"
                  className="text-xs text-blue-500 hover:underline flex items-center gap-0.5 ml-auto"
                  aria-label={`${label} API-Seite öffnen`}
                >
                  Registrieren <ExternalLink size={10} aria-hidden />
                </a>
              </div>
              <div className="relative">
                <input
                  type={showKeys[key] ? 'text' : 'password'}
                  value={keys[key]}
                  onChange={e => setKeys(k => ({ ...k, [key]: e.target.value }))}
                  placeholder={hasKey ? '•••••••• (vorhanden, zum Überschreiben eingeben)' : 'Leer'}
                  className="w-full rounded-lg px-3 py-2 pr-10 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label={label}
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(s => ({ ...s, [key]: !s[key] }))}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showKeys[key] ? 'Key verbergen' : 'Key anzeigen'}
                >
                  {showKeys[key] ? <EyeOff size={15} aria-hidden /> : <Eye size={15} aria-hidden />}
                </button>
              </div>
            </div>
          </div>
        ))}
      </Section>
    </div>
  )
}
