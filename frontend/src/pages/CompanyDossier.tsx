import { useState } from 'react'
import axios from 'axios'
import { Building2, Globe, Users, CalendarDays, ExternalLink, Search, AlertTriangle } from 'lucide-react'

interface Dossier {
  company: string
  description: string | null
  founded: string | null
  employees: string | null
  industry: string | null
  headquarters: string | null
  website: string | null
  wikipedia_url: string | null
  logo_url: string | null
  warning: string | null
  source: string
}

export default function CompanyDossier() {
  const [query, setQuery] = useState('')
  const [dossier, setDossier] = useState<Dossier | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setDossier(null)
    try {
      const { data } = await axios.get('/api/company/dossier', { params: { name: query } })
      setDossier(data)
    } catch {
      setError('Kein Dossier gefunden.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <div className="flex items-center gap-3 mb-6">
        <Building2 size={28} className="text-blue-500" aria-hidden />
        <div>
          <h1 className="text-2xl font-bold">Firmen-Dossier</h1>
          <p className="text-sm text-gray-400">Automatische Recherche zu deiner Zielfirma</p>
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()}
          placeholder="Firmenname, z.B. Siemens AG ..."
          className="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          aria-label="Firmenname suchen"
        />
        <button
          onClick={search}
          disabled={!query.trim() || loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-medium disabled:opacity-50 transition-colors"
        >
          {loading ? <span className="animate-spin text-xs">&#9696;</span> : <Search size={16} aria-hidden />}
          Suchen
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl text-red-600 text-sm mb-4">
          <AlertTriangle size={16} aria-hidden />{error}
        </div>
      )}

      {dossier && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md overflow-hidden">
          {/* Header */}
          <div className="flex items-center gap-4 p-6 border-b border-gray-100 dark:border-gray-700">
            {dossier.logo_url && (
              <img
                src={dossier.logo_url}
                alt={`${dossier.company} Logo`}
                width={56}
                height={56}
                loading="lazy"
                className="w-14 h-14 rounded-xl object-contain bg-gray-50 border border-gray-100 p-1"
                onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
              />
            )}
            <div>
              <h2 className="text-xl font-bold">{dossier.company}</h2>
              {dossier.industry && <p className="text-sm text-gray-400">{dossier.industry}</p>}
            </div>
          </div>

          {/* Body */}
          <div className="p-6 space-y-4">
            {dossier.warning && (
              <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-xl text-yellow-700 dark:text-yellow-300 text-sm">
                <AlertTriangle size={16} aria-hidden />{dossier.warning}
              </div>
            )}

            {dossier.description && (
              <p className="text-sm text-gray-700 dark:text-gray-200 leading-relaxed">{dossier.description}</p>
            )}

            <div className="grid grid-cols-2 gap-3">
              {dossier.founded && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <CalendarDays size={14} className="text-gray-400" aria-hidden />
                  Gegründet {dossier.founded}
                </div>
              )}
              {dossier.employees && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <Users size={14} className="text-gray-400" aria-hidden />
                  {dossier.employees} Mitarbeiter
                </div>
              )}
              {dossier.headquarters && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <Globe size={14} className="text-gray-400" aria-hidden />
                  {dossier.headquarters}
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              {dossier.wikipedia_url && (
                <a
                  href={dossier.wikipedia_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  <ExternalLink size={12} aria-hidden />
                  Wikipedia
                </a>
              )}
              {dossier.website && (
                <a
                  href={dossier.website.startsWith('http') ? dossier.website : `https://${dossier.website}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
                >
                  <Globe size={12} aria-hidden />
                  Website
                </a>
              )}
            </div>

            <p className="text-xs text-gray-300 dark:text-gray-500 pt-2">ℹ️ Quelle: {dossier.source}</p>
          </div>
        </div>
      )}
    </div>
  )
}
