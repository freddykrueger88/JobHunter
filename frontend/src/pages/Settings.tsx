import { useState, useEffect, useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useTheme, type Theme, type ColorBlindMode } from '../context/ThemeContext'
import { useA11y, type Density } from '../context/AccessibilityContext'
import { Eye, EyeOff, ExternalLink, Download, Upload, Check, Save } from 'lucide-react'
import clsx from 'clsx'

interface SettingsData {
  theme: string; language: string; ai_model: string; ai_tone: string
  default_location: string | null; default_radius_km: number
  hide_ausbildung: boolean; reminder_default_days: number
  has_adzuna_key: boolean; has_linkedin_key: boolean
}

type SaveStatus = 'idle' | 'pending' | 'saved' | 'error'

const AUTOSAVE_DELAY = 1200 // ms

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
  linkedin: 'https://www.linkedin.com/jobs/search/',
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">{title}</h2>
      {children}
    </section>
  )
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

// ─── Auto-Save Toast ────────────────────────────────────────────────────────
function SaveToast({ status }: { status: SaveStatus }) {
  if (status === 'idle') return null
  return (
    <div
      aria-live="polite"
      className={clsx(
        'fixed top-4 right-4 z-50 flex items-center gap-2 px-4 py-2 rounded-xl shadow-lg text-sm font-medium transition-all duration-300',
        status === 'pending' && 'bg-yellow-50 dark:bg-yellow-900/80 text-yellow-700 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-700',
        status === 'saved'   && 'bg-green-50 dark:bg-green-900/80 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-700',
        status === 'error'   && 'bg-red-50 dark:bg-red-900/80 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-700',
      )}
    >
      {status === 'pending' && <><span className="w-3.5 h-3.5 rounded-full border-2 border-yellow-500 border-t-transparent animate-spin" />Speichern…</>}
      {status === 'saved'   && <><Check size={14} aria-hidden />Gespeichert</>}
      {status === 'error'   && <>❌ Fehler beim Speichern</>}
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
    refetchOnWindowFocus: false,
    staleTime: 60_000,
  })

  const [aiModel, setAiModel]                 = useState('mistral')
  const [aiTone, setAiTone]                   = useState('formell')
  const [defaultLocation, setDefaultLocation] = useState('')
  const [defaultRadius, setDefaultRadius]     = useState(25)
  const [hideAusbildung, setHideAusbildung]   = useState(true)
  const [reminderDays, setReminderDays]       = useState(7)
  const [showKeys, setShowKeys]               = useState<Record<string, boolean>>({})
  const [keys, setKeys]                       = useState<Record<string, string>>({
    adzuna_app_id: '', adzuna_api_key: '',
  })
  const [saveStatus, setSaveStatus]           = useState<SaveStatus>('idle')
  const [keysSaved, setKeysSaved]             = useState(false)
  const [importing, setImporting]             = useState(false)
  const [importMsg, setImportMsg]             = useState('')

  const initialized   = useRef(false)
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isFirstRender = useRef(true)

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

  // ─── Core save function (ohne API-Keys) ─────────────────────────────────
  const doSave = useCallback(async (payload: object) => {
    setSaveStatus('pending')
    try {
      await axios.patch('/api/settings/', payload)
      qc.invalidateQueries({ queryKey: ['settings'] })
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
    } catch {
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    }
  }, [qc])

  // ─── Auto-Save Trigger ──────────────────────────────────────────────────
  // Läuft bei jeder Änderung der Einstellungen (außer API-Keys)
  useEffect(() => {
    if (!initialized.current) return
    // Ersten Render nach Initialisierung überspringen
    if (isFirstRender.current) { isFirstRender.current = false; return }

    if (debounceTimer.current) clearTimeout(debounceTimer.current)
    debounceTimer.current = setTimeout(() => {
      doSave({
        theme,
        language: i18n.language,
        ai_model: aiModel,
        ai_tone: aiTone,
        default_location: defaultLocation || null,
        default_radius_km: defaultRadius,
        hide_ausbildung: hideAusbildung,
        reminder_default_days: reminderDays,
        color_blind_mode: colorBlindMode,
      })
    }, AUTOSAVE_DELAY)

    return () => { if (debounceTimer.current) clearTimeout(debounceTimer.current) }
  }, [theme, colorBlindMode, aiModel, aiTone, defaultLocation, defaultRadius, hideAusbildung, reminderDays, i18n.language])

  // ─── API-Keys: manuell speichern ────────────────────────────────────────
  const saveKeysMutation = useMutation({
    mutationFn: () => axios.patch('/api/settings/', {
      ...Object.fromEntries(Object.entries(keys).filter(([, v]) => v !== '')),
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings'] })
      setKeysSaved(true)
      setTimeout(() => setKeysSaved(false), 2500)
      setKeys({ adzuna_app_id: '', adzuna_api_key: '' })
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

  // ─── API-Key Input Helper ───────────────────────────────────────────────
  function ApiKeyInput({
    id, label, placeholder, link,
  }: { id: string; label: string; placeholder: string; link?: string }) {
    return (
      <div>
        <div className="flex items-center justify-between mb-1">
          <label htmlFor={id} className="text-sm text-gray-500">{label}</label>
          {link && (
            <a href={link} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-500 hover:underline flex items-center gap-1">
              Registrieren <ExternalLink size={11} aria-hidden />
            </a>
          )}
        </div>
        <div className="relative">
          <input
            id={id}
            type={showKeys[id] ? 'text' : 'password'}
            value={keys[id] ?? ''}
            onChange={e => setKeys(k => ({ ...k, [id]: e.target.value }))}
            placeholder={placeholder}
            className="w-full rounded-lg px-3 py-2 pr-9 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 font-mono"
          />
          <button
            type="button"
            onClick={() => setShowKeys(s => ({ ...s, [id]: !s[id] }))}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            aria-label={showKeys[id] ? 'Key verbergen' : 'Key anzeigen'}
          >
            {showKeys[id] ? <EyeOff size={15} aria-hidden /> : <Eye size={15} aria-hidden />}
          </button>
        </div>
      </div>
    )
  }

  const hasKeyInput = keys.adzuna_app_id !== '' || keys.adzuna_api_key !== ''

  return (
    <div className="max-w-2xl">
      {/* Auto-Save Toast */}
      <SaveToast status={saveStatus} />

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t('settings.title')}</h1>
        <span className="text-xs text-gray-400 italic">Änderungen werden automatisch gespeichert</span>
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
              {models.length > 0
                ? models.map(m => <option key={m} value={m}>{m}</option>)
                : <option value="mistral">mistral (Standard)</option>
              }
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">Schreibton</label>
            <div className="flex flex-wrap gap-2">
              {TONES.map(tone => (
                <button key={tone} onClick={() => setAiTone(tone)} aria-pressed={aiTone === tone}
                  className={clsx('px-4 py-1.5 rounded-full text-sm font-medium border-2 transition-all capitalize',
                    aiTone === tone ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400')}
                >{tone}</button>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* ── Stellensuche ── */}
      <Section title="🔍 Stellensuche">
        <div className="space-y-4 mb-5">
          <div>
            <label className="text-sm text-gray-500 block mb-1">Standard-Ort</label>
            <input
              value={defaultLocation}
              onChange={e => setDefaultLocation(e.target.value)}
              placeholder="z.B. Bremen, Hamburg …"
              className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
              aria-label="Standard-Ort"
            />
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">Suchradius: {defaultRadius} km</label>
            <input type="range" min={5} max={100} step={5} value={defaultRadius}
              onChange={e => setDefaultRadius(Number(e.target.value))}
              className="w-full accent-blue-600" aria-label="Suchradius"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>5 km</span><span>100 km</span></div>
          </div>
          <ToggleRow
            label="Ausbildungsplätze ausblenden"
            desc="Ausbildungsangebote werden in der Suche nicht angezeigt"
            value={hideAusbildung}
            onChange={setHideAusbildung}
          />
        </div>

        {/* API-Key Bereich */}
        <div className="rounded-xl bg-gray-50 dark:bg-gray-800/50 p-4 space-y-4">
          <div>
            <p className="text-sm font-medium mb-0.5">🔑 API-Zugänge</p>
            <p className="text-xs text-gray-400 leading-relaxed">
              Die Bundesagentur für Arbeit, Stepstone und EURES funktionieren <strong>ohne Registrierung</strong>.
              Für mehr Ergebnisse kannst du optional einen kostenlosen Adzuna-Key hinzufügen.
            </p>
          </div>

          {/* Adzuna */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Adzuna (optional, kostenlos)</p>
            <ApiKeyInput id="adzuna_app_id" label="App ID" placeholder="Deine Adzuna App ID" link={API_LINKS.adzuna} />
            <ApiKeyInput id="adzuna_api_key" label="API Key" placeholder="Dein Adzuna API Key" />
            {remote?.has_adzuna_key && !hasKeyInput && (
              <p className="text-xs text-green-600 dark:text-green-400">✅ Adzuna-Key hinterlegt</p>
            )}
            {hasKeyInput && (
              <button
                onClick={() => saveKeysMutation.mutate()}
                disabled={saveKeysMutation.isPending}
                className={clsx(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors mt-1',
                  keysSaved
                    ? 'bg-green-600 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50'
                )}
              >
                <Save size={12} aria-hidden />
                {keysSaved ? 'Keys gespeichert ✅' : 'Keys speichern'}
              </button>
            )}
          </div>

          {/* LinkedIn */}
          <div className="rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 px-3 py-2.5">
            <p className="text-xs font-semibold text-yellow-700 dark:text-yellow-400 mb-1">⚠️ LinkedIn – kein offizieller API-Key</p>
            <p className="text-xs text-yellow-600 dark:text-yellow-300 leading-relaxed">
              LinkedIn hat seine Job-API für Drittanbieter geschlossen. JobHunter sucht LinkedIn-Stellen
              direkt über die öffentliche Suche – kein Key erforderlich.
            </p>
            <a href={API_LINKS.linkedin} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-1.5">
              LinkedIn Jobs direkt öffnen <ExternalLink size={11} aria-hidden />
            </a>
          </div>

          {/* Bundesagentur Info */}
          <div className="rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 px-3 py-2.5">
            <p className="text-xs font-semibold text-green-700 dark:text-green-400 mb-1">✅ Bundesagentur für Arbeit – automatisch aktiv</p>
            <p className="text-xs text-green-600 dark:text-green-300 leading-relaxed">
              Die offizielle Jobbörse der BA ist vollständig kostenlos und ohne Registrierung nutzbar.
              Keine Eingabe erforderlich.
            </p>
          </div>
        </div>
      </Section>

      {/* ── Erinnerungen ── */}
      <Section title="⏰ Erinnerungen">
        <div>
          <label className="text-sm text-gray-500 block mb-1">Standard-Vorlaufzeit: {reminderDays} Tage</label>
          <input type="range" min={1} max={30} step={1} value={reminderDays}
            onChange={e => setReminderDays(Number(e.target.value))}
            className="w-full accent-blue-600" aria-label="Erinnerungsvorlaufzeit"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>1 Tag</span><span>30 Tage</span></div>
        </div>
      </Section>

      {/* ── Daten ── */}
      <Section title="💾 Daten">
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            <Download size={15} aria-hidden /> Daten exportieren
          </button>
          <label className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors cursor-pointer">
            <Upload size={15} aria-hidden /> Daten importieren
            <input type="file" accept=".zip" onChange={handleImport} className="sr-only" />
          </label>
        </div>
        {importing && <p className="text-sm text-gray-500 mt-2">⏳ Importiere…</p>}
        {importMsg && <p className="text-sm mt-2">{importMsg}</p>}
      </Section>
    </div>
  )
}
