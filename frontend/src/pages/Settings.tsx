import { useState, useEffect, useRef, useCallback } from 'react'
import { useTranslation, Trans } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useTheme, type Theme, type ColorBlindMode } from '../context/ThemeContext'
import { useA11y, type Density } from '../context/AccessibilityContext'
import { Eye, EyeOff, ExternalLink, Check, Save, AlertCircle, Mail } from 'lucide-react'
import clsx from 'clsx'
import ExportImportPanel from '../components/ExportImportPanel'

interface SettingsData {
  theme: string; language: string; ai_model: string; ai_tone: string
  default_location: string | null; default_radius_km: number
  hide_ausbildung: boolean; reminder_default_days: number
  has_adzuna_key: boolean; has_linkedin_key: boolean; has_francetravail_key: boolean
  smtp_host: string | null; smtp_port: number | null
  smtp_user: string | null; smtp_recipient: string | null
  has_smtp_password: boolean
}

type SaveStatus = 'idle' | 'pending' | 'saved' | 'error'
type KeysSaveStatus = 'idle' | 'pending' | 'saved' | 'error'

const AUTOSAVE_DELAY = 1200 // ms

const THEMES: {
  value: Theme
  emoji: string
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
    emoji: '🌙',
    nav: '#0d1117', navText: '#c9d1d9',
    body: '#161b22', card: '#21262d', cardText: '#e6edf3',
    accent: '#2563eb', accentText: '#fff',
  },
  {
    value: 'light',
    emoji: '☀️',
    nav: '#ffffff', navText: '#111827',
    body: '#f9fafb', card: '#ffffff', cardText: '#111827',
    accent: '#2563eb', accentText: '#fff',
  },
  {
    value: 'boys',
    emoji: '🌊',
    nav: '#0a1628', navText: '#cfe0f4',
    body: '#0d1b2e', card: '#112240', cardText: '#e2eaf4',
    accent: '#1d4ed8', accentText: '#fff',
  },
  {
    value: 'girls',
    emoji: '🌺',
    nav: '#fce4ef', navText: '#3b0f24',
    body: '#fdf0f5', card: '#fff4f8', cardText: '#3b0f24',
    accent: '#be185d', accentText: '#fff',
  },
  {
    value: 'sakura',
    emoji: '🌸',
    nav: '#f3e8dc', navText: '#1c0a10',
    body: '#fef6f8', card: '#fdeef2', cardText: '#1c0a10',
    accent: '#c0392b', accentText: '#fff',
  },
  {
    value: 'dyslexic',
    emoji: '📖',
    nav: '#f7f6e7', navText: '#1a1a1a',
    body: '#fffef5', card: '#fffef0', cardText: '#1a1a1a',
    accent: '#7c6f1e', accentText: '#fff',
  },
]

const COLOR_BLIND_MODE_VALUES: ColorBlindMode[] = ['none', 'deuteranopia', 'protanopia', 'tritanopia', 'achromatopsia']
const DENSITY_VALUES: Density[] = ['normal', 'compact', 'minimal']
const TONES = ['formell', 'direkt', 'modern', 'kreativ']
const API_LINKS: Record<string, string> = {
  adzuna: 'https://developer.adzuna.com/',
  linkedin: 'https://www.linkedin.com/jobs/search/',
  francetravail: 'https://francetravail.io/inscription',
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-lg font-semibold mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">{title}</h2>
      {children}
    </section>
  )
}

function ThemeMockup({ opt, active }: { opt: typeof THEMES[number]; active: boolean }) {
  const { t } = useTranslation('settings')
  const label = t(`themes.${opt.value}.label`)
  const sublabel = t(`themes.${opt.value}.sublabel`)
  return (
    <button
      onClick={() => {}}
      aria-pressed={active}
      aria-label={t('themeSelectAriaLabel', { label })}
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
          <span style={{ display: 'inline-block', background: opt.accent, color: opt.accentText, borderRadius: 4, fontSize: 8, padding: '2px 7px', marginTop: 2, fontWeight: 600 }}>{t('themeMockupOpenLabel')}</span>
        </div>
        <div style={{ background: opt.card, borderRadius: 6, padding: '5px 8px', display: 'flex', alignItems: 'center', gap: 5 }}>
          <span style={{ width: 10, height: 10, background: opt.accent, borderRadius: '50%', flexShrink: 0 }} />
          <span style={{ flex: 1, height: 5, background: opt.cardText, opacity: 0.5, borderRadius: 3 }} />
        </div>
      </div>
      <div style={{ background: opt.nav, borderTop: `1px solid ${opt.navText}18`, padding: '8px 12px' }}>
        <span style={{ color: opt.navText, fontWeight: 700, fontSize: 13 }}>{opt.emoji} {label}</span>
        <span style={{ color: opt.navText, opacity: 0.6, fontSize: 11, display: 'block', marginTop: 1 }}>{sublabel}</span>
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
  const { t } = useTranslation('settings')
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
      {status === 'pending' && <><span className="w-3.5 h-3.5 rounded-full border-2 border-yellow-500 border-t-transparent animate-spin" />{t('saveToastPending')}</>}
      {status === 'saved'   && <><Check size={14} aria-hidden />{t('saveToastSaved')}</>}
      {status === 'error'   && <>{t('saveToastError')}</>}
    </div>
  )
}

export default function Settings() {
  const { t, i18n } = useTranslation('settings')
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
    francetravail_client_id: '', francetravail_client_secret: '',
  })
  const [saveStatus, setSaveStatus]           = useState<SaveStatus>('idle')
  const [smtpHost, setSmtpHost]               = useState('')
  const [smtpPort, setSmtpPort]               = useState('')
  const [smtpUser, setSmtpUser]               = useState('')
  const [smtpRecipient, setSmtpRecipient]     = useState('')
  const [smtpPassword, setSmtpPassword]       = useState('')
  const [smtpSaveStatus, setSmtpSaveStatus]   = useState<KeysSaveStatus>('idle')
  const [testMailStatus, setTestMailStatus]   = useState<'idle' | 'pending' | 'success' | 'error'>('idle')
  // keysSaveStatus: 'idle' = Button normal, 'pending' = lädt,
  // 'saved' = grün (Keys noch sichtbar), 'error' = rot
  const [keysSaveStatus, setKeysSaveStatus]   = useState<KeysSaveStatus>('idle')

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
      setSmtpHost(remote.smtp_host ?? '')
      setSmtpPort(remote.smtp_port ? String(remote.smtp_port) : '')
      setSmtpUser(remote.smtp_user ?? '')
      setSmtpRecipient(remote.smtp_recipient ?? '')
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
  useEffect(() => {
    if (!initialized.current) return
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
    onMutate: () => {
      setKeysSaveStatus('pending')
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings'] })
      setKeysSaveStatus('saved')
      // Zuerst Feedback zeigen, DANN Felder leeren
      setTimeout(() => {
        setKeys({ adzuna_app_id: '', adzuna_api_key: '', francetravail_client_id: '', francetravail_client_secret: '' })
        setKeysSaveStatus('idle')
      }, 1500)
    },
    onError: () => {
      setKeysSaveStatus('error')
      setTimeout(() => setKeysSaveStatus('idle'), 3000)
    },
  })

  // ─── SMTP: manuell speichern ────────────────────────────────────────────
  const saveSmtpMutation = useMutation({
    mutationFn: () => axios.patch('/api/settings/', {
      smtp_host: smtpHost || null,
      smtp_port: smtpPort ? Number(smtpPort) : null,
      smtp_user: smtpUser || null,
      smtp_recipient: smtpRecipient || null,
      ...(smtpPassword !== '' && { smtp_password: smtpPassword }),
    }),
    onMutate: () => setSmtpSaveStatus('pending'),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings'] })
      setSmtpSaveStatus('saved')
      setTimeout(() => { setSmtpPassword(''); setSmtpSaveStatus('idle') }, 1500)
    },
    onError: () => {
      setSmtpSaveStatus('error')
      setTimeout(() => setSmtpSaveStatus('idle'), 3000)
    },
  })

  const testMailMutation = useMutation({
    mutationFn: () => axios.post('/api/settings/test-mail').then(r => r.data),
    onMutate: () => setTestMailStatus('pending'),
    onSuccess: (data: { success: boolean }) => {
      setTestMailStatus(data.success ? 'success' : 'error')
      setTimeout(() => setTestMailStatus('idle'), 4000)
    },
    onError: () => {
      setTestMailStatus('error')
      setTimeout(() => setTestMailStatus('idle'), 4000)
    },
  })

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
              {t('registerLink')} <ExternalLink size={11} aria-hidden />
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
            aria-label={showKeys[id] ? t('hideKeyAriaLabel') : t('showKeyAriaLabel')}
          >
            {showKeys[id] ? <EyeOff size={15} aria-hidden /> : <Eye size={15} aria-hidden />}
          </button>
        </div>
      </div>
    )
  }

  // Button ist sichtbar solange Keys eingegeben ODER Feedback läuft
  const showKeysButton = keys.adzuna_app_id !== '' || keys.adzuna_api_key !== ''
    || keys.francetravail_client_id !== '' || keys.francetravail_client_secret !== '' || keysSaveStatus !== 'idle'

  return (
    <div className="max-w-2xl">
      {/* Auto-Save Toast */}
      <SaveToast status={saveStatus} />

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <span className="text-xs text-gray-400 italic">{t('autosaveNote')}</span>
      </div>

      {/* ── Erscheinungsbild ── */}
      <Section title={`🎨 ${t('appearanceTitle')}`}>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {THEMES.map(opt => (
            <div key={opt.value} onClick={() => setTheme(opt.value)} className="cursor-pointer">
              <ThemeMockup opt={opt} active={theme === opt.value} />
            </div>
          ))}
        </div>
      </Section>

      {/* ── Farbenblindheits-Filter ── */}
      <Section title={`👁️ ${t('colorBlindTitle')}`}>
        <div className="grid grid-cols-1 gap-2">
          {COLOR_BLIND_MODE_VALUES.map(value => (
            <button
              key={value}
              onClick={() => setColorBlindMode(value)}
              aria-pressed={colorBlindMode === value}
              className={clsx(
                'rounded-xl px-4 py-3 text-left border-2 transition-all flex items-center justify-between',
                colorBlindMode === value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              )}
            >
              <span className="font-medium text-sm">{t(`colorBlindModes.${value}.label`)}</span>
              <span className="text-xs text-gray-400">{t(`colorBlindModes.${value}.desc`)}</span>
            </button>
          ))}
        </div>
      </Section>

      {/* ── ADHS & Kognition ── */}
      <Section title={`🧠 ${t('cognitionTitle')}`}>
        <div className="divide-y divide-gray-100 dark:divide-gray-800 mb-5">
          <ToggleRow label={t('adhdModeLabel')} desc={t('adhdModeDesc')} value={adhdMode} onChange={setAdhdMode} />
          <ToggleRow label={t('focusModeLabel')} desc={t('focusModeDesc')} value={focusMode} onChange={setFocusMode} />
          <ToggleRow label={t('reduceMotionLabel')} desc={t('reduceMotionDesc')} value={reduceMotion} onChange={setReduceMotion} />
        </div>
        <div>
          <p className="text-sm text-gray-500 mb-3">{t('densityLabel')}</p>
          <div className="flex gap-3">
            {DENSITY_VALUES.map(value => (
              <button
                key={value}
                onClick={() => setDensity(value)}
                aria-pressed={density === value}
                className={clsx(
                  'flex-1 rounded-xl border-2 transition-all text-left px-3 py-3',
                  density === value
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
                )}
              >
                <div className="text-sm font-semibold mb-1">{t(`density.${value}.label`)}</div>
                <div className="text-xs text-gray-400 leading-snug">{t(`density.${value}.desc`)}</div>
              </button>
            ))}
          </div>
        </div>
      </Section>

      {/* ── Sprache ── */}
      <Section title={`🌍 ${t('language')}`}>
        <div className="flex gap-3">
          {['de', 'en'].map(lang => (
            <button key={lang} onClick={() => { i18n.changeLanguage(lang); localStorage.setItem('lang', lang) }}
              aria-pressed={i18n.language === lang}
              className={clsx('px-6 py-2 rounded-lg font-medium border-2 transition-all',
                i18n.language === lang ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400')}
            >{lang === 'de' ? t('languageDe') : t('languageEn')}</button>
          ))}
        </div>
      </Section>

      {/* ── KI ── */}
      <Section title={`🤖 ${t('ai')}`}>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-500 block mb-1">{t('aiModelLabel')}</label>
            <select value={aiModel} onChange={e => setAiModel(e.target.value)}
              className="rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" aria-label={t('aiModelAriaLabel')}>
              {models.length > 0
                ? models.map(m => <option key={m} value={m}>{m}</option>)
                : <option value="mistral">{t('aiModelDefaultOption')}</option>
              }
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">{t('toneLabel')}</label>
            <div className="flex flex-wrap gap-2">
              {TONES.map(tone => (
                <button key={tone} onClick={() => setAiTone(tone)} aria-pressed={aiTone === tone}
                  className={clsx('px-4 py-1.5 rounded-full text-sm font-medium border-2 transition-all',
                    aiTone === tone ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400')}
                >{t(`tones.${tone}`)}</button>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* ── Stellensuche ── */}
      <Section title={`🔍 ${t('jobSearchTitle')}`}>
        <div className="space-y-4 mb-5">
          <div>
            <label className="text-sm text-gray-500 block mb-1">{t('locationLabel')}</label>
            <input
              value={defaultLocation}
              onChange={e => setDefaultLocation(e.target.value)}
              placeholder={t('locationPlaceholder')}
              className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600"
              aria-label={t('locationAriaLabel')}
            />
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">{t('radiusLabel', { km: defaultRadius })}</label>
            <input type="range" min={5} max={100} step={5} value={defaultRadius}
              onChange={e => setDefaultRadius(Number(e.target.value))}
              className="w-full accent-blue-600" aria-label={t('radiusAriaLabel')}
            />
            <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>{t('radiusMin')}</span><span>{t('radiusMax')}</span></div>
          </div>
          <ToggleRow
            label={t('hideAusbildungLabel')}
            desc={t('hideAusbildungDesc')}
            value={hideAusbildung}
            onChange={setHideAusbildung}
          />
        </div>

        {/* API-Key Bereich */}
        <div className="rounded-xl bg-gray-50 dark:bg-gray-800/50 p-4 space-y-4">
          <div>
            <p className="text-sm font-medium mb-0.5">{t('apiKeysHeading')}</p>
            <p className="text-xs text-gray-400 leading-relaxed">
              <Trans i18nKey="settings:apiKeysIntro" components={{ strong: <strong /> }} />
            </p>
          </div>

          {/* Adzuna */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{t('adzunaSectionLabel')}</p>
            <ApiKeyInput id="adzuna_app_id" label={t('appIdLabel')} placeholder={t('appIdPlaceholder')} link={API_LINKS.adzuna} />
            <ApiKeyInput id="adzuna_api_key" label={t('apiKeyLabel')} placeholder={t('apiKeyPlaceholder')} />
            {remote?.has_adzuna_key && keys.adzuna_app_id === '' && keys.adzuna_api_key === '' && keysSaveStatus === 'idle' && (
              <p className="text-xs text-green-600 dark:text-green-400">{t('adzunaKeyStored')}</p>
            )}
          </div>

          {/* France Travail */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{t('francetravailSectionLabel')}</p>
            <p className="text-xs text-gray-400 leading-relaxed">{t('francetravailIntro')}</p>
            <ApiKeyInput id="francetravail_client_id" label={t('francetravailClientIdLabel')} placeholder={t('francetravailClientIdPlaceholder')} link={API_LINKS.francetravail} />
            <ApiKeyInput id="francetravail_client_secret" label={t('francetravailClientSecretLabel')} placeholder={t('francetravailClientSecretPlaceholder')} />
            {remote?.has_francetravail_key && keys.francetravail_client_id === '' && keys.francetravail_client_secret === '' && keysSaveStatus === 'idle' && (
              <p className="text-xs text-green-600 dark:text-green-400">{t('francetravailKeyStored')}</p>
            )}
            {showKeysButton && (
              <button
                onClick={() => saveKeysMutation.mutate()}
                disabled={keysSaveStatus === 'pending' || keysSaveStatus === 'saved'}
                className={clsx(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all mt-1',
                  keysSaveStatus === 'saved'   && 'bg-green-600 text-white cursor-default',
                  keysSaveStatus === 'error'   && 'bg-red-600 hover:bg-red-700 text-white',
                  keysSaveStatus === 'pending' && 'bg-blue-400 text-white cursor-wait',
                  keysSaveStatus === 'idle'    && 'bg-blue-600 hover:bg-blue-700 text-white',
                )}
              >
                {keysSaveStatus === 'pending' && <span className="w-3 h-3 rounded-full border-2 border-white border-t-transparent animate-spin" />}
                {keysSaveStatus === 'saved'   && <Check size={12} aria-hidden />}
                {keysSaveStatus === 'error'   && <AlertCircle size={12} aria-hidden />}
                {keysSaveStatus === 'idle'    && <Save size={12} aria-hidden />}
                {keysSaveStatus === 'pending' && t('saveKeysPending')}
                {keysSaveStatus === 'saved'   && t('saveKeysSaved')}
                {keysSaveStatus === 'error'   && t('saveKeysError')}
                {keysSaveStatus === 'idle'    && t('saveKeysIdle')}
              </button>
            )}
          </div>

          {/* LinkedIn */}
          <div className="rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 px-3 py-2.5">
            <p className="text-xs font-semibold text-yellow-700 dark:text-yellow-400 mb-1">{t('linkedinHeading')}</p>
            <p className="text-xs text-yellow-600 dark:text-yellow-300 leading-relaxed">
              {t('linkedinBody')}
            </p>
            <a href={API_LINKS.linkedin} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-500 hover:underline flex items-center gap-1 mt-1.5">
              {t('linkedinOpenLink')} <ExternalLink size={11} aria-hidden />
            </a>
          </div>

          {/* Bundesagentur Info */}
          <div className="rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 px-3 py-2.5">
            <p className="text-xs font-semibold text-green-700 dark:text-green-400 mb-1">{t('arbeitsagenturHeading')}</p>
            <p className="text-xs text-green-600 dark:text-green-300 leading-relaxed">
              {t('arbeitsagenturBody')}
            </p>
          </div>
        </div>
      </Section>

      {/* ── Erinnerungen ── */}
      <Section title={`⏰ ${t('remindersTitle')}`}>
        <div>
          <label className="text-sm text-gray-500 block mb-1">{t('reminderLeadTimeLabel', { days: reminderDays })}</label>
          <input type="range" min={1} max={30} step={1} value={reminderDays}
            onChange={e => setReminderDays(Number(e.target.value))}
            className="w-full accent-blue-600" aria-label={t('reminderLeadTimeAriaLabel')}
          />
          <div className="flex justify-between text-xs text-gray-400 mt-0.5"><span>{t('reminderLeadTimeMin')}</span><span>{t('reminderLeadTimeMax')}</span></div>
        </div>
      </Section>

      {/* ── E-Mail-Benachrichtigungen ── */}
      <Section title={`✉️ ${t('smtpTitle')}`}>
        <p className="text-xs text-gray-400 leading-relaxed">{t('smtpIntro')}</p>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="smtp_host" className="text-sm text-gray-500 block mb-1">{t('smtpHostLabel')}</label>
            <input id="smtp_host" value={smtpHost} onChange={e => setSmtpHost(e.target.value)}
              placeholder="smtp.gmail.com"
              className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" />
          </div>
          <div>
            <label htmlFor="smtp_port" className="text-sm text-gray-500 block mb-1">{t('smtpPortLabel')}</label>
            <input id="smtp_port" type="number" value={smtpPort} onChange={e => setSmtpPort(e.target.value)}
              placeholder="587"
              className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" />
          </div>
        </div>
        <div>
          <label htmlFor="smtp_user" className="text-sm text-gray-500 block mb-1">{t('smtpUserLabel')}</label>
          <input id="smtp_user" value={smtpUser} onChange={e => setSmtpUser(e.target.value)}
            className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" />
        </div>
        <div>
          <label htmlFor="smtp_password" className="text-sm text-gray-500 block mb-1">{t('smtpPasswordLabel')}</label>
          <div className="relative">
            <input
              id="smtp_password"
              type={showKeys.smtp_password ? 'text' : 'password'}
              value={smtpPassword}
              onChange={e => setSmtpPassword(e.target.value)}
              placeholder={remote?.has_smtp_password ? t('smtpPasswordStoredPlaceholder') : ''}
              className="w-full rounded-lg px-3 py-2 pr-9 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 font-mono"
            />
            <button
              type="button"
              onClick={() => setShowKeys(s => ({ ...s, smtp_password: !s.smtp_password }))}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              aria-label={showKeys.smtp_password ? t('hideKeyAriaLabel') : t('showKeyAriaLabel')}
            >
              {showKeys.smtp_password ? <EyeOff size={15} aria-hidden /> : <Eye size={15} aria-hidden />}
            </button>
          </div>
        </div>
        <div>
          <label htmlFor="smtp_recipient" className="text-sm text-gray-500 block mb-1">{t('smtpRecipientLabel')}</label>
          <input id="smtp_recipient" type="email" value={smtpRecipient} onChange={e => setSmtpRecipient(e.target.value)}
            className="w-full rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600" />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => saveSmtpMutation.mutate()}
            disabled={smtpSaveStatus === 'pending' || smtpSaveStatus === 'saved'}
            className={clsx(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all',
              smtpSaveStatus === 'saved'   && 'bg-green-600 text-white cursor-default',
              smtpSaveStatus === 'error'   && 'bg-red-600 hover:bg-red-700 text-white',
              smtpSaveStatus === 'pending' && 'bg-blue-400 text-white cursor-wait',
              smtpSaveStatus === 'idle'    && 'bg-blue-600 hover:bg-blue-700 text-white',
            )}
          >
            {smtpSaveStatus === 'pending' && <span className="w-3 h-3 rounded-full border-2 border-white border-t-transparent animate-spin" />}
            {smtpSaveStatus === 'saved'   && <Check size={12} aria-hidden />}
            {smtpSaveStatus === 'error'   && <AlertCircle size={12} aria-hidden />}
            {smtpSaveStatus === 'idle'    && <Save size={12} aria-hidden />}
            {smtpSaveStatus === 'pending' && t('saveKeysPending')}
            {smtpSaveStatus === 'saved'   && t('saveKeysSaved')}
            {smtpSaveStatus === 'error'   && t('saveKeysError')}
            {smtpSaveStatus === 'idle'    && t('saveKeysIdle')}
          </button>

          <button
            onClick={() => testMailMutation.mutate()}
            disabled={testMailStatus === 'pending' || !remote?.smtp_host}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 transition-colors"
          >
            <Mail size={12} aria-hidden />
            {testMailStatus === 'pending' ? t('sendingTestMail') : t('sendTestMail')}
          </button>
          {testMailStatus === 'success' && <span className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1"><Check size={12} /> {t('testMailSuccess')}</span>}
          {testMailStatus === 'error' && <span className="text-xs text-red-500 flex items-center gap-1"><AlertCircle size={12} /> {t('testMailError')}</span>}
        </div>
      </Section>

      {/* ── Daten ── */}
      <Section title={`💾 ${t('dataTitle')}`}>
        <ExportImportPanel />
      </Section>
    </div>
  )
}
