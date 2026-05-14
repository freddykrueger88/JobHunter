import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useTheme, type Theme, type ColorBlindMode } from '../context/ThemeContext'
import { useA11y, type Density } from '../context/AccessibilityContext'
import { Save, Eye, EyeOff, ExternalLink, Download, Upload, Check } from 'lucide-react'
import clsx from 'clsx'

interface SettingsData {
  theme: string; language: string; ai_model: string; ai_tone: string
  default_location: string | null; default_radius_km: number
  hide_ausbildung: boolean; reminder_default_days: number
  has_adzuna_key: boolean; has_linkedin_key: boolean; has_arbeitsagentur_key: boolean
}

const THEMES: {
  value: Theme
  emoji: string
  label: string
  sublabel: string
  nav: string
  navText: string
  body: string
  card: string
  cardText: string
  accent: string
  accentText: string
}[] = [
  {
    value: 'dark',
    emoji: '🌙', label: 'Dark', sublabel: 'Dunkel & klassisch',
    nav: '#0d1117', navText: '#c9d1d9',
    body: '#161b22', card: '#21262d', cardText: '#e6edf3',
    accent: '#2563eb', accentText: '#fff',
  },
  {
    value: 'light',
    emoji: '☀️', label: 'Hell', sublabel: 'Sauber & klar',
    nav: '#ffffff', navText: '#111827',
    body: '#f9fafb', card: '#ffffff', cardText: '#111827',
    accent: '#2563eb', accentText: '#fff',
  },
  {
    value: 'boys',
    emoji: '🌊', label: 'Ocean', sublabel: 'Tiefes Marineblau',
    nav: '#0a1628', navText: '#cfe0f4',
    body: '#0d1b2e', card: '#112240', cardText: '#e2eaf4',
    accent: '#1d4ed8', accentText: '#fff',
  },
  {
    value: 'girls',
    emoji: '🌺', label: 'Rose', sublabel: 'Warmes Rosa',
    nav: '#fce4ef', navText: '#3b0f24',
    body: '#fdf0f5', card: '#fff4f8', cardText: '#3b0f24',
    accent: '#be185d', accentText: '#fff',
  },
  {
    value: 'sakura',
    emoji: '🌸', label: 'Sakura', sublabel: 'Kirschblüte & Japan',
    nav: '#f3e8dc', navText: '#1c0a10',
    body: '#fef6f8', card: '#fdeef2', cardText: '#1c0a10',
    accent: '#c0392b', accentText: '#fff',
  },
  {
    value: 'dyslexic',
    emoji: '📖', label: 'Lese-Modus', sublabel: 'Legasthenie-optimiert',
    nav: '#f7f6e7', navText: '#1a1a1a',
    body: '#fffef5', card: '#fffef0', cardText: '#1a1a1a',
    accent: '#7c6f1e', accentText: '#fff',
  },
]

const COLOR_BLIND_MODES: { value: ColorBlindMode; label: string; desc: string }[] = [
  { value: 'none',          label: 'Kein Filter',   desc: 'Standard' },
  { value: 'deuteranopia',  label: 'Deuteranopie',  desc: 'Grün-Schwäche (~6% Männer)' },
  { value: 'protanopia',    label: 'Protanopie',    desc: 'Rot-Schwäche (~2% Männer)' },
  { value: 'tritanopia',    label: 'Tritanopie',    desc: 'Blau-Gelb-Schwäche' },
  { value: 'achromatopsia', label: 'Achromatopsie', desc: 'Vollständige Farbenblindheit' },
]
const DENSITY_OPTIONS: { value: Density; label: string; desc: string }[] = [
  { value: 'normal',  label: 'Normal',   desc: 'Komfortabler Abstand' },
  { value: 'compact', label: 'Kompakt',  desc: 'Etwas weniger Abstand' },
  { value: 'minimal', label: 'Minimal',  desc: 'Maximale Dichte' },
]
const TONES = ['formell', 'direkt', 'modern', 'kreativ']
const API_LINKS: Record<string, string> = {
  adzuna: 'https://developer.adzuna.com/',
  arbeitsagentur: 'https://jobsuche.api.bund.dev/',
  linkedin: 'https://developer.linkedin.com/',
}

function ThemeMockup({ t: opt, active }: { t: typeof THEMES[number]; active: boolean }) {
  return (
    <button
      onClick={() => {}}
      aria-pressed={active}
      aria-label={`Theme ${opt.label} auswählen`}
      style={{
        background: opt.body,
        borderColor: active ? '#3b82f6' : 'transparent',
        boxShadow: active ? '0 0 0 3px rgba(59,130,246,0.35)' : undefined,
      }}
      className="relative w-full rounded-2xl border-2 overflow-hidden transition-all hover:scale-[1.02] focus-visible:outline-none text-left"
    >
      {active && (
        <span className="absolute top-2 right-2 z-10 flex items-center justify-center w-5 h-5 rounded-full bg-blue-500" aria-hidden>
          <Check size={12} strokeWidth={3} color="#fff" />
        </span>
      )}
      <div style={{ background: opt.nav, borderBottom: `1px solid ${opt.navText}22` }} className="flex items-center gap-1.5 px-3 py-2">
        {[40, 28, 34].map((w, i) => (
          <span key={i} style={{ width: w, height: 6, background: opt.navText, opacity: i === 0 ? 0.9 : 0.4, borderRadius: 3 }} />
        ))}
        <span style={{ width: 16, height: 16, background: opt.accent, borderRadius: '50%', marginLeft: 'auto' }} />
      </div>
      <div style={{ background: opt.body }} className="px-3 py-3 space-y-2">
        <div style={{ background: opt.card, borderRadius: 6, padding: '6px 8px' }} className="space-y-1.5">
          <span style={{ display: 'block', width: '70%', height: 7, background: opt.cardText, opacity: 0.85, borderRadius: 3 }} />
          <span style={{ display: 'block', width: '50%', height: 5, background: opt.cardText, opacity: 0.35, borderRadius: 3 }} />
          <span style={{ display: 'inline-block', background: opt.accent, color: opt.accentText, borderRadius: 4, fontSize: 8, padding: '2px 7px', marginTop: 2, fontWeight: 600 }}>Öffnen</span>
        </div>
        <div style={{ background: opt.card, borderRadius: 6, padding: '5px 8px', display: 'flex', alignItems: 'center', gap: 5 }}>
          <span style={{ width: 10, height: 10, background: opt.accent, borderRadius: '50%', flexShrink: 0 }} />
          <span style={{ flex: 1, height: 5, background: opt.cardText, opacity: 0.5, borderRadius: 3 }} />
        </div>
      </div>
      <div style={{ background: opt.nav, borderTop: `1px solid ${opt.navText}18`, padding: '8px 12px' }}>
        <span style={{ color: opt.navText, fontWeight: 700, fontSize: 13 }}>{opt.emoji} {opt.label}</span>
        <span style={{ color: opt.navText, opacity: 0.6, fontSize: 11, display: 'block', marginTop: 1 }}>{opt.sublabel}</span>
      </div>
    </button>
  )
}

function ToggleSwitch({ value, onChange, id }: { value: boolean; onChange: (v: boolean) => void; id: string }) {
  return (
    <button
      id={id} role="switch" aria-checked={value}
      onClick={() => onChange(!value)}
      style={{ minHeight: 'unset', minWidth: 'unset' }}
      className={clsx(
        'relative flex-shrink-0 w-11 h-6 rounded-full transition-colors focus-visible:outline-2 focus-visible:outline-offset-2',
        value ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
      )}
    >
      <span className={clsx('absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform', value ? 'translate-x-5' : 'translate-x-0')} />
    </button>
  )
}

function ToggleRow({ label, desc, value, onChange }: { label: string; desc?: string; value: boolean; onChange: (v: boolean) => void }) {
  const id = `toggle-${label.replace(/\s+/g, '-').toLowerCase()}`
  return (
    <div className="flex items-center justify-between gap-4 py-2">
      <label htmlFor={id} className="cursor-pointer flex-1">
        <span className="text-sm font-medium block">{label}</span>
        {desc && <span className="text-xs text-gray-400">{desc}</span>}
      </label>
      <ToggleSwitch id={id} value={value} onChange={onChange} />
    </div>
  )
}

export default function Settings() {
  const { t, i18n } = useTranslation()
  const { theme, setTheme, colorBlindMode, setColorBlindMode } = useTheme()
  const { focusMode, setFocusMode, density, setDensity, reduceMotion, setReduceMotion, adhdMode, setAdhdMode } = useA11y()
  const qc = useQueryClient()

  const { data: remote } = useQuery<SettingsData>({
    queryKey: ['settings'],
    queryFn: () => axios.get('/api/settings/').then(r => r.data),
    // Kein Hintergrund-Refetch während der User tippt
    refetchOnWindowFocus: false,
    staleTime: 60_000,
  })

  const [aiModel, setAiModel]             = useState('mistral')
  const [aiTone, setAiTone]               = useState('formell')
  const [defaultLocation, setDefaultLocation] = useState('')
  const [defaultRadius, setDefaultRadius]     = useState(25)
  const [hideAusbildung, setHideAusbildung]   = useState(true)
  const [reminderDays, setReminderDays]       = useState(7)
  const [showKeys, setShowKeys]   = useState<Record<string, boolean>>({})
  const [keys, setKeys]           = useState<Record<string, string>>({
    adzuna_app_id: '', adzuna_api_key: '', linkedin_api_key: '',
    arbeitsagentur_client_id: '', arbeitsagentur_client_secret: '',
  })
  const [saved, setSaved]         = useState(false)
  const [importing, setImporting] = useState(false)
  const [importMsg, setImportMsg] = useState('')

  // ─── FIX: einmalige Initialisierung aus remote, danach nie wieder überschreiben ───
  const initialized = useRef(false)
  useEffect(() => {
    if (remote && !initialized.current) {
      initialized.current = true
      setAiModel(remote.ai_model)
      setAiTone(remote.ai_tone)
      setDefaultLocation(remote.default_location ?? '')
      setDefaultRadius(remote.default_radius_km)
      setHideAusbildung(remote.hide_ausbildung)
      setReminderDays(remote.reminder_default_days)
    }
  }, [remote])

  const { data: models = [] } = useQuery<string[]>({
    queryKey: ['ai-models'],
    queryFn: () => axios.get('/api/ai/models').then(r => r.data.models),
    staleTime: 300_000,
  })

  const saveMutation = useMutation({
    mutationFn: () => axios.patch('/api/settings/', {
      theme, language: i18n.language, ai_model: aiModel, ai_tone: aiTone,
      default_location: defaultLocation || null, default_radius_km: defaultRadius,
      hide_ausbildung: hideAusbildung, reminder_default_days: reminderDays,
      color_blind_mode: colorBlindMode,
      ...Object.fromEntries(Object.entries(keys).filter(([, v]) => v !== '')),
    }),
    onSuccess: () => {
      // Nach dem Speichern remote neu laden, aber initialized bleibt true
      // → kein State-Überschreiben, nur has_*_key Badges aktualisieren
      qc.invalidateQueries({ queryKey: ['settings'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      setKeys(k => Object.fromEntries(Object.entries(k).map(([key]) => [key, ''])))
    },
  })

  const handleExport = () => { window.location.href = '/api/export/' }
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; if (!file) return
    setImporting(true); setImportMsg('')
    const form = new FormData(); form.append('file', file)
    try {
      const res = await axios.post('/api/export/import', form)
      const d = res.data.imported
      setImportMsg(`✅ Importiert: ${d.jobs} Stellen, ${d.reminders} Erinnerungen, ${d.history} Verlaufseinträge`)
      qc.invalidateQueries()
    } catch (err: any) {
      setImportMsg(`❌ Fehler: ${err.response?.data?.detail ?? err.message}`)
    } finally { setImporting(false); e.target.value = '' }
  }

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
            saved ? 'bg-green-600 text-white' : 'bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50'
          )}
        >
          <Save size={15} aria-hidden />{saved ? 'Gespeichert ✅' : t('common.save')}
        </button>
      </div>

      {/* ── Erscheinungsbild ── */}
      <Section title="🎨 Erscheinungsbild">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {THEMES.map(opt => (
            <div key={opt.value} onClick={() => setTheme(opt.value)} className="cursor-pointer">
              <ThemeMockup t={opt} active={theme === opt.value} />
            </div>
          ))}
        </div>
      </Section>

      {/* ── Farbenblindheits-Filter ── */}
      <Section title="👁️ Farbenblindheits-Filter">
        <div className="grid grid-cols-1 gap-2">
          {COLOR_BLIND_MODES.map(opt => (
            <button
              key={opt.value}
              onClick={() => setColorBlindMode(opt.value)}
              aria-pressed={colorBlindMode === opt.value}
              className={clsx(
                'rounded-xl px-4 py-3 text-left border-2 transition-all flex items-center justify-between',
                colorBlindMode === opt.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              )}
            >
              <span className="font-medium text-sm">{opt.label}</span>
              <span className="text-xs text-gray-400">{opt.desc}</span>
            </button>
          ))}
        </div>
      </Section>

      {/* ── ADHS & Kognition ── */}
      <Section title="🧠 ADHS & Kognition">
        <div className="divide-y divide-gray-100 dark:divide-gray-800 mb-5">
          <ToggleRow label="ADHS-Modus" desc="Aktiviert Fokus-Modus + reduzierte Bewegung" value={adhdMode} onChange={setAdhdMode} />
          <ToggleRow label="Fokus-Modus" desc="Navigation wird ausgeblendet, nur aktiver Bereich sichtbar" value={focusMode} onChange={setFocusMode} />
          <ToggleRow label="Animationen deaktivieren" desc="Alle Transitions und Animationen ausschalten (inkl. Sakura)" value={reduceMotion} onChange={setReduceMotion} />
        </div>
        <div>
          <p className="text-sm text-gray-500 mb-3">Informationsdichte</p>
          <div className="flex gap-3">
            {DENSITY_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setDensity(opt.value)}
                aria-pressed={density === opt.value}
                className={clsx(
                  'flex-1 rounded-xl border-2 transition-all text-left px-3 py-3',
                  density === opt.value
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
                )}
              >
                <div className="text-sm font-semibold mb-1">{opt.label}</div>
                <div className="text-xs text-gray-400 leading-snug">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>
      </Section>

      {/* ── Sprache ── */}
      <Section title={`🌍 ${t('settings.language')}`}>
        <div className="flex gap-3">
          {['de', 'en'].map(lang => (
            <button key={lang} onClick={() => { i18n.changeLanguage(lang); localStorage.setItem('lang', lang) }}
              aria-pressed={i18n.language === lang}
              className={clsx('px-6 py-2 rounded-lg font-medium border-2 transition-all',
                i18n.language === lang ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400')}
            >{lang === 'de' ? '🇩🇪 Deutsch' : '🇬🇧 English'}</button>
          ))}
        </div>
      </Section>

      {/* ── KI ── */}
      <Section title={`🤖 ${t('settings.ai')}`}>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-500 block mb-1">KI-Modell</label>
            <select value={aiModel} onChange={e => setAiModel(e.target.value)}
              className="rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" aria-label="KI-Modell">
              {(models.length ? models : ['mistral', 'llama3', 'phi3']).map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">KI-Ton</label>
            <div className="flex gap-2 flex-wrap">
              {TONES.map(tn => (
                <button key={tn} onClick={() => setAiTone(tn)} aria-pressed={aiTone === tn}
                  className={clsx('text-sm px-3 py-1 rounded-full border transition-colors capitalize',
                    aiTone === tn ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700')}
                >{tn}</button>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* ── Stellensuche ── */}
      <Section title="🔍 Stellensuche">
        <div className="space-y-3">
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="text-sm text-gray-500 block mb-1">Standard-Ort</label>
              <input
                value={defaultLocation}
                onChange={e => setDefaultLocation(e.target.value)}
                className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
                placeholder="z.B. Bremen"
                aria-label="Standard-Ort"
                autoComplete="off"
              />
            </div>
            <div className="w-32">
              <label className="text-sm text-gray-500 block mb-1">Radius (km)</label>
              <select value={defaultRadius} onChange={e => setDefaultRadius(Number(e.target.value))}
                className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" aria-label="Radius">
                {[10, 25, 50, 100].map(r => <option key={r} value={r}>{r} km</option>)}
              </select>
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={hideAusbildung} onChange={e => setHideAusbildung(e.target.checked)} className="rounded" />
            Ausbildungsstellen ausblenden
          </label>
        </div>
      </Section>

      {/* ── Erinnerungen ── */}
      <Section title="🔔 Erinnerungen">
        <div>
          <label className="text-sm text-gray-500 block mb-1">Standard-Vorlaufzeit (Tage)</label>
          <input
            type="number" min={1} max={30}
            value={reminderDays}
            onChange={e => setReminderDays(Number(e.target.value))}
            className="w-24 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
            aria-label="Vorlaufzeit"
          />
        </div>
      </Section>

      {/* ── API Keys ── */}
      <Section title="🔑 API Keys">
        <p className="text-sm text-gray-500 mb-4">Keys werden verschlüsselt gespeichert (AES-256).</p>
        {([
          { key: 'adzuna_app_id',                label: 'Adzuna App ID',            portal: 'adzuna',         hasKey: remote?.has_adzuna_key },
          { key: 'adzuna_api_key',               label: 'Adzuna API Key',           portal: 'adzuna',         hasKey: remote?.has_adzuna_key },
          { key: 'arbeitsagentur_client_id',     label: 'Arbeitsagentur Client ID', portal: 'arbeitsagentur', hasKey: remote?.has_arbeitsagentur_key },
          { key: 'arbeitsagentur_client_secret', label: 'Arbeitsagentur Secret',    portal: 'arbeitsagentur', hasKey: remote?.has_arbeitsagentur_key },
          { key: 'linkedin_api_key',             label: 'LinkedIn API Key',         portal: 'linkedin',       hasKey: remote?.has_linkedin_key },
        ] as const).map(({ key, label, portal, hasKey }) => (
          <div key={key} className="mb-3">
            <div className="flex items-center gap-2 mb-1">
              <label className="text-sm text-gray-500">{label}</label>
              {hasKey && <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full">✓ gesetzt</span>}
              <a href={API_LINKS[portal]} target="_blank" rel="noopener noreferrer"
                className="text-xs text-blue-500 hover:underline flex items-center gap-0.5 ml-auto">
                Registrieren <ExternalLink size={10} aria-hidden />
              </a>
            </div>
            <div className="relative">
              <input
                type={showKeys[key] ? 'text' : 'password'}
                value={keys[key]}
                onChange={e => setKeys(k => ({ ...k, [key]: e.target.value }))}
                placeholder={hasKey ? '•••••••• (zum Überschreiben eingeben)' : 'Leer'}
                className="w-full rounded-lg px-3 py-2 pr-10 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
                aria-label={label}
              />
              <button type="button" onClick={() => setShowKeys(s => ({ ...s, [key]: !s[key] }))}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                aria-label={showKeys[key] ? 'Verbergen' : 'Anzeigen'}
                style={{ minHeight: 'unset', minWidth: 'unset' }}>
                {showKeys[key] ? <EyeOff size={15} aria-hidden /> : <Eye size={15} aria-hidden />}
              </button>
            </div>
          </div>
        ))}
      </Section>

      {/* ── Export / Import ── */}
      <Section title="📦 Daten Export / Import">
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500 mb-2">Alle Daten als JSON exportieren (DSGVO Art. 20)</p>
            <button onClick={handleExport}
              className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              <Download size={15} aria-hidden /> Daten exportieren
            </button>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-2">Backup importieren (.json)</p>
            <label className={clsx('flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer w-fit',
              importing ? 'bg-gray-400' : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600')}>
              {importing ? <>⏳ Importiere...</> : <><Upload size={15} aria-hidden /> Backup importieren</>}
              <input type="file" accept=".json" onChange={handleImport} disabled={importing} className="hidden" aria-label="JSON-Backup importieren" />
            </label>
            {importMsg && <p className="text-sm mt-2" role="status">{importMsg}</p>}
          </div>
        </div>
      </Section>
    </div>
  )
}
