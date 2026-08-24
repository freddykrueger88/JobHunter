import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Upload, FileJson, FileSpreadsheet, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

type ImportStatus = { state: 'idle' } | { state: 'loading' } | { state: 'success'; stats: Record<string, number>; version: string } | { state: 'error'; message: string };

export default function ExportImportPanel() {
  const { t } = useTranslation('exportImportPanel');
  const fileRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [status, setStatus] = useState<ImportStatus>({ state: 'idle' });

  // ── Export helpers ──────────────────────────────────────────────────────────
  const triggerDownload = (url: string) => {
    const a = document.createElement('a');
    a.href = url;
    a.click();
  };

  // ── Import ──────────────────────────────────────────────────────────────────
  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.json')) {
      setStatus({ state: 'error', message: t('errorJsonOnly') });
      return;
    }
    setStatus({ state: 'loading' });
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch('/api/export/import', { method: 'POST', body: form });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? t('errorUnknown'));
      }
      const data = await res.json();
      setStatus({ state: 'success', stats: data.imported, version: data.source_version });
    } catch (e) {
      setStatus({ state: 'error', message: e instanceof Error ? e.message : String(e) });
    }
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = '';
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="space-y-6 p-4 max-w-xl">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('heading')}</h2>

      {/* ── Export ── */}
      <section>
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">{t('export')}</h3>
        <div className="flex flex-wrap gap-3">
          {/* JSON */}
          <button
            onClick={() => triggerDownload('/api/export/')}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-800 dark:bg-gray-700 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 dark:hover:bg-gray-600 transition-colors"
          >
            <FileJson size={16} />
            {t('exportJson')}
          </button>

          {/* CSV */}
          <button
            onClick={() => triggerDownload('/api/export/csv')}
            className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 transition-colors"
          >
            <FileText size={16} />
            {t('exportCsv')}
          </button>

          {/* XLSX */}
          <button
            onClick={() => triggerDownload('/api/export/xlsx')}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            <FileSpreadsheet size={16} />
            {t('exportXlsx')}
          </button>
        </div>
        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
          {t('exportHint')}
        </p>
      </section>

      {/* ── Import ── */}
      <section>
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">{t('import')}</h3>

        {/* Drop-Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
            dragging
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          }`}
        >
          <Upload size={28} className="mx-auto mb-2 text-gray-400" />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <span className="font-medium text-blue-600 dark:text-blue-400">{t('chooseFile')}</span> {t('orDrop')}
          </p>
          <p className="text-xs text-gray-400 mt-1">{t('importHint')}</p>
          <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={onInputChange} />
        </div>

        {/* Status-Feedback */}
        {status.state === 'loading' && (
          <div className="mt-3 flex items-center gap-2 text-sm text-gray-500">
            <Loader2 size={16} className="animate-spin" />
            {t('importing')}
          </div>
        )}
        {status.state === 'success' && (
          <div className="mt-3 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700 p-3 text-sm">
            <div className="flex items-center gap-2 font-medium text-emerald-700 dark:text-emerald-400 mb-1">
              <CheckCircle size={16} />
              {t('importSuccess', { version: status.version })}
            </div>
            <ul className="text-emerald-600 dark:text-emerald-500 space-y-0.5">
              {Object.entries(status.stats).map(([k, v]) => (
                <li key={k}>• {v} {t(`statLabels.${k}`, k)}</li>
              ))}
            </ul>
          </div>
        )}
        {status.state === 'error' && (
          <div className="mt-3 flex items-start gap-2 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 p-3 text-sm text-red-700 dark:text-red-400">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            {status.message}
          </div>
        )}
      </section>
    </div>
  );
}
