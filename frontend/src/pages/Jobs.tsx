import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { Search, EyeOff, ExternalLink, MapPin, Building2, Loader2, Camera, X, SlidersHorizontal, Ban } from 'lucide-react'
import clsx from 'clsx'
import ImageJobUpload from '../components/ImageJobUpload'
import DuplicateJobsPanel from '../components/DuplicateJobsPanel'
import JobAnalysisPanel from '../components/JobAnalysisPanel'
import GhostJobBadge from '../components/GhostJobBadge'
import TimingHintBadge from '../components/TimingHintBadge'

interface GhostJobResult {
  ghost_score: number
  ist_ghost_job: boolean
  wahrscheinlichkeit: 'hoch' | 'mittel' | 'niedrig'
  gruende: string[]
}

interface Job {
  id: number
  title: string
  company: string
  city: string | null
  description: string | null
  url: string | null
  source_portal: string | null
  job_type: string | null
  is_hidden: boolean
  published_at: string | null
  created_at: string
  ghost_job: GhostJobResult
}

interface DaysUntilEntry {
  key: string
  total: number
  beantwortet: number
  quote: number
}

const portalBadgeColor: Record<string, string> = {
  arbeitsagentur: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  adzuna: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  eures: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
  karriere_nrw: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  service_bund: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  france_travail: 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200',
  arbetsformedlingen: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
  default: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
}

interface EuresCountry { code: string; name: string }

export default function Jobs() {
  const { t } = useTranslation(['jobs', 'common'])
  const qc = useQueryClient()
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('')
  const [radius, setRadius] = useState(25)
  const [countryCode, setCountryCode] = useState('DE')
  const [hideAusbildung, setHideAusbildung] = useState(true)
  const [benefitKeywordsInput, setBenefitKeywordsInput] = useState('')
  const [blacklistKeywordsInput, setBlacklistKeywordsInput] = useState('')
  const [benefitKeywords, setBenefitKeywords] = useState('')
  const [blacklistKeywords, setBlacklistKeywords] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedJob, setSelectedJob] = useState<Job | null>(null)
  const [showPhotoUpload, setShowPhotoUpload] = useState(false)

  // Freitext-Filter (#88) erst nach kurzer Tippschreib-Pause anwenden,
  // statt bei jedem Tastendruck eine neue Anfrage auszuloesen.
  useEffect(() => {
    const timer = setTimeout(() => setBenefitKeywords(benefitKeywordsInput), 500)
    return () => clearTimeout(timer)
  }, [benefitKeywordsInput])
  useEffect(() => {
    const timer = setTimeout(() => setBlacklistKeywords(blacklistKeywordsInput), 500)
    return () => clearTimeout(timer)
  }, [blacklistKeywordsInput])

  const { data: jobs = [], isLoading: loadingJobs } = useQuery<Job[]>({
    queryKey: ['jobs', hideAusbildung, benefitKeywords, blacklistKeywords],
    queryFn: () => axios.get('/api/jobs/', {
      params: {
        hide_ausbildung: hideAusbildung,
        benefit_keywords: benefitKeywords || undefined,
        blacklist_keywords: blacklistKeywords || undefined,
      },
    }).then(r => r.data),
  })

  const { data: euresCountries = [] } = useQuery<EuresCountry[]>({
    queryKey: ['eures-countries'],
    queryFn: () => axios.get('/api/jobs/eures-countries').then(r => r.data),
    staleTime: Infinity,
  })

  // Gleicher Query-Key wie ResponseRatePanel.tsx (Dashboard) - React
  // Query dedupliziert/teilt den Cache automatisch, kein Extra-Request
  // noetig wenn beide Seiten in derselben Session besucht werden.
  const { data: responseRates } = useQuery<{ by_days_until_applied: DaysUntilEntry[] }>({
    queryKey: ['response-rates'],
    queryFn: () => axios.get('/api/stats/response-rates').then(r => r.data),
  })

  const searchMutation = useMutation({
    mutationFn: () => axios.get('/api/jobs/search', {
      params: { keywords, location, radius_km: radius, country_code: countryCode, save: true },
    }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const hideMutation = useMutation({
    mutationFn: (id: number) => axios.patch(`/api/jobs/${id}/hide`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jobs'] }),
  })

  const blockCompanyMutation = useMutation({
    mutationFn: (company: string) => axios.post('/api/blocklist/', { firma: company, grund: 'Über Jobs-Seite blockiert' }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['jobs'] })
      setSelectedJob(null)
    },
  })

  return (
    <div className="flex gap-6">
      {/* Linke Spalte: Suche + Liste */}
      <div className="flex-1 min-w-0">
        <h1 className="text-2xl font-bold mb-4">{t('title')}</h1>

        {/* Suchmaske */}
        <div className="bg-gray-100 dark:bg-gray-800 rounded-xl p-4 mb-4 space-y-3">
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Suchbegriff, z.B. IT-Support"
              value={keywords}
              onChange={e => setKeywords(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && searchMutation.mutate()}
              aria-label="Suchbegriff"
            />
            <input
              className="w-44 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ort, PLZ"
              value={location}
              onChange={e => setLocation(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && searchMutation.mutate()}
              aria-label="Ort oder Postleitzahl"
              maxLength={80}
            />
            <select
              className="w-28 rounded-lg px-2 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm"
              value={radius}
              onChange={e => setRadius(Number(e.target.value))}
              aria-label="Radius"
            >
              {[10, 25, 50, 100].map(r => <option key={r} value={r}>{r} km</option>)}
            </select>
            <select
              className="w-36 rounded-lg px-2 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm"
              value={countryCode}
              onChange={e => setCountryCode(e.target.value)}
              aria-label="Land (EURES)"
              title="Land für die EU-weite EURES-Suche – Ort/Radius gelten nur für die deutschen Portale"
            >
              {euresCountries.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
            </select>
          </div>
          {countryCode !== 'DE' && (
            <p className="text-xs text-gray-400">
              EU-weite Suche über EURES in {euresCountries.find(c => c.code === countryCode)?.name ?? countryCode}. Ort und Radius gelten nur für die deutschen Portale (Arbeitsagentur, StepStone) und werden hier ignoriert.
            </p>
          )}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={hideAusbildung}
                  onChange={e => setHideAusbildung(e.target.checked)}
                  className="rounded"
                />
                Ausbildungsstellen ausblenden
              </label>
              <button
                onClick={() => setShowFilters(s => !s)}
                className={clsx(
                  'flex items-center gap-1.5 text-sm transition-colors',
                  (benefitKeywords || blacklistKeywords) ? 'text-blue-600 dark:text-blue-400 font-medium' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                )}
                aria-expanded={showFilters}
              >
                <SlidersHorizontal size={14} aria-hidden />
                Filter{(benefitKeywords || blacklistKeywords) ? ' (aktiv)' : ''}
              </button>
            </div>
            <button
              onClick={() => searchMutation.mutate()}
              disabled={searchMutation.isPending || !keywords || !location}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              aria-label="Stellensuche starten"
            >
              {searchMutation.isPending
                ? <Loader2 size={16} className="animate-spin" aria-hidden />
                : <Search size={16} aria-hidden />}
              {t('search')}
            </button>
          </div>
          {showFilters && (
            <div className="grid grid-cols-2 gap-3 pt-1">
              <div>
                <label htmlFor="benefit-keywords" className="text-xs text-gray-500 block mb-1">
                  Gewünschte Begriffe (Komma-getrennt)
                </label>
                <input
                  id="benefit-keywords"
                  className="w-full rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm"
                  placeholder="z.B. Homeoffice, Dienstwagen"
                  value={benefitKeywordsInput}
                  onChange={e => setBenefitKeywordsInput(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="blacklist-keywords" className="text-xs text-gray-500 block mb-1">
                  Ausschluss-Begriffe (Komma-getrennt)
                </label>
                <input
                  id="blacklist-keywords"
                  className="w-full rounded-lg px-3 py-1.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm"
                  placeholder="z.B. Zeitarbeit, Callcenter"
                  value={blacklistKeywordsInput}
                  onChange={e => setBlacklistKeywordsInput(e.target.value)}
                />
              </div>
            </div>
          )}
        </div>

        {/* Foto-Upload */}
        <div className="mb-4">
          <button
            onClick={() => setShowPhotoUpload(s => !s)}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            {showPhotoUpload ? <X size={14} aria-hidden /> : <Camera size={14} aria-hidden />}
            {showPhotoUpload ? 'Foto-Upload schließen' : 'Stelle per Foto erfassen'}
          </button>
          {showPhotoUpload && (
            <div className="mt-3">
              <ImageJobUpload
                onJobCreated={() => {
                  qc.invalidateQueries({ queryKey: ['jobs'] })
                  setShowPhotoUpload(false)
                }}
              />
            </div>
          )}
        </div>

        {/* Ergebnisliste */}
        {loadingJobs && <p className="text-gray-400 text-sm">{t('common:loading')}</p>}
        <ul className="space-y-2">
          {jobs.map(job => (
            <li
              key={job.id}
              onClick={() => setSelectedJob(job)}
              className={clsx(
                'rounded-xl p-4 cursor-pointer transition-all border-2',
                selectedJob?.id === job.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-transparent bg-gray-100 dark:bg-gray-800 hover:border-gray-400'
              )}
              tabIndex={0}
              onKeyDown={e => e.key === 'Enter' && setSelectedJob(job)}
              aria-selected={selectedJob?.id === job.id}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="font-semibold truncate">{job.title}</p>
                  <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                    <span className="flex items-center gap-1"><Building2 size={12} aria-hidden />{job.company}</span>
                    {job.city && <span className="flex items-center gap-1"><MapPin size={12} aria-hidden />{job.city}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <GhostJobBadge result={job.ghost_job} />
                  <TimingHintBadge
                    publishedAt={job.published_at}
                    createdAt={job.created_at}
                    byDaysUntilApplied={responseRates?.by_days_until_applied}
                  />
                  {job.source_portal && (
                    <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium',
                      portalBadgeColor[job.source_portal] ?? portalBadgeColor.default)}>
                      {job.source_portal}
                    </span>
                  )}
                  <button
                    onClick={e => { e.stopPropagation(); hideMutation.mutate(job.id) }}
                    className="text-gray-400 hover:text-red-500 transition-colors p-1 rounded"
                    title="Ausblenden"
                    aria-label={`${job.title} ausblenden`}
                  >
                    <EyeOff size={15} aria-hidden />
                  </button>
                </div>
              </div>
            </li>
          ))}
          {!loadingJobs && jobs.length === 0 && (
            <li className="text-gray-400 text-sm text-center py-8">
              {(benefitKeywords || blacklistKeywords)
                ? 'Keine Stellen entsprechen den aktuellen Filtern.'
                : 'Noch keine Stellen – starte eine Suche oben 👆'}
            </li>
          )}
        </ul>
      </div>

      {/* Rechte Spalte: Detailansicht */}
      {selectedJob && (
        <aside className="w-96 shrink-0">
          <div className="sticky top-20 bg-gray-100 dark:bg-gray-800 rounded-xl p-5 space-y-3">
            <h2 className="text-lg font-bold">{selectedJob.title}</h2>
            <p className="text-sm text-gray-500">{selectedJob.company} {selectedJob.city && `• ${selectedJob.city}`}</p>
            {selectedJob.description && (
              <p className="text-sm text-gray-600 dark:text-gray-300 whitespace-pre-line max-h-60 overflow-y-auto">
                {selectedJob.description}
              </p>
            )}
            <div className="flex gap-2 pt-2">
              {selectedJob.url && (
                <a
                  href={selectedJob.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-sm bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <ExternalLink size={14} aria-hidden /> Original öffnen
                </a>
              )}
              <button
                onClick={() => hideMutation.mutate(selectedJob.id)}
                className="flex items-center gap-1.5 text-sm bg-gray-200 dark:bg-gray-700 px-3 py-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
              >
                <EyeOff size={14} aria-hidden /> Ausblenden
              </button>
              <button
                onClick={() => {
                  if (window.confirm(`Alle Stellen von "${selectedJob.company}" dauerhaft ausblenden (auch bei zukünftigen Suchen)?`)) {
                    blockCompanyMutation.mutate(selectedJob.company)
                  }
                }}
                title="Firma auf die Blocklist setzen"
                className="flex items-center gap-1.5 text-sm bg-gray-200 dark:bg-gray-700 px-3 py-2 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
              >
                <Ban size={14} aria-hidden /> Firma blockieren
              </button>
            </div>
          </div>
          <div className="mt-3">
            <DuplicateJobsPanel jobId={selectedJob.id} />
          </div>
          <div className="mt-3">
            <JobAnalysisPanel jobId={selectedJob.id} />
          </div>
        </aside>
      )}
    </div>
  )
}
