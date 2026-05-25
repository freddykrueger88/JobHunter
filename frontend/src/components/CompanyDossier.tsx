import React, { useEffect, useState } from 'react';
import { Building2, Users, Calendar, Globe, ChevronDown, ChevronUp, AlertTriangle, Loader2 } from 'lucide-react';

interface Dossier {
  company: string;
  description: string | null;
  founded: string | null;
  employees: string | null;
  industry: string | null;
  headquarters: string | null;
  website: string | null;
  wikipedia_url: string | null;
  logo_url: string | null;
  warning: string | null;
  source: string;
}

interface Props {
  companyName: string;
}

export default function CompanyDossier({ companyName }: Props) {
  const [open, setOpen] = useState(false);
  const [dossier, setDossier] = useState<Dossier | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Lazy-Load: erst beim ersten Öffnen fetchen
  useEffect(() => {
    if (!open || dossier || loading) return;
    setLoading(true);
    setError(null);
    fetch(`/api/company/dossier?name=${encodeURIComponent(companyName)}`)
      .then((r) => {
        if (!r.ok) throw new Error('Dossier konnte nicht geladen werden');
        return r.json();
      })
      .then((data) => setDossier(data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [open, companyName]);

  return (
    <div className="rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* ── Header / Toggle ── */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
      >
        <span className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <Building2 size={15} />
          Firmen-Dossier: <span className="text-gray-900 dark:text-white">{companyName}</span>
        </span>
        {open ? <ChevronUp size={15} className="text-gray-400" /> : <ChevronDown size={15} className="text-gray-400" />}
      </button>

      {/* ── Content ── */}
      {open && (
        <div className="px-4 py-4 space-y-4 bg-white dark:bg-gray-900">

          {/* Loading */}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <Loader2 size={15} className="animate-spin" />
              Informationen werden geladen…
            </div>
          )}

          {/* Error */}
          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          {/* Dossier */}
          {dossier && !loading && (
            <>
              {/* Warnung */}
              {dossier.warning && (
                <div className="flex items-start gap-2 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 p-3 text-sm text-amber-700 dark:text-amber-400">
                  <AlertTriangle size={15} className="mt-0.5 shrink-0" />
                  {dossier.warning}
                </div>
              )}

              {/* Logo + Beschreibung */}
              <div className="flex gap-3">
                {dossier.logo_url && (
                  <img
                    src={dossier.logo_url}
                    alt={`${dossier.company} Logo`}
                    width={48}
                    height={48}
                    loading="lazy"
                    className="rounded-lg object-contain bg-gray-100 dark:bg-gray-800 p-1 shrink-0"
                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                  />
                )}
                {dossier.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {dossier.description}
                  </p>
                )}
              </div>

              {/* Meta-Chips */}
              <div className="flex flex-wrap gap-2">
                {dossier.founded && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 dark:bg-gray-800 px-3 py-1 text-xs text-gray-600 dark:text-gray-400">
                    <Calendar size={11} />
                    Gegründet {dossier.founded}
                  </span>
                )}
                {dossier.employees && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 dark:bg-gray-800 px-3 py-1 text-xs text-gray-600 dark:text-gray-400">
                    <Users size={11} />
                    {dossier.employees} Mitarbeiter
                  </span>
                )}
                {dossier.industry && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 dark:bg-gray-800 px-3 py-1 text-xs text-gray-600 dark:text-gray-400">
                    {dossier.industry}
                  </span>
                )}
                {dossier.headquarters && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 dark:bg-gray-800 px-3 py-1 text-xs text-gray-600 dark:text-gray-400">
                    📍 {dossier.headquarters}
                  </span>
                )}
              </div>

              {/* Links */}
              <div className="flex gap-3 text-xs">
                {dossier.wikipedia_url && (
                  <a
                    href={dossier.wikipedia_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    <Globe size={11} />
                    Wikipedia
                  </a>
                )}
                {dossier.website && (
                  <a
                    href={dossier.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    <Globe size={11} />
                    Website
                  </a>
                )}
              </div>

              <p className="text-xs text-gray-300 dark:text-gray-600">{dossier.source}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
