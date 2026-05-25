import React, { useState } from 'react';
import { Mail, Wifi, Search, CheckCircle, AlertCircle, Loader2, ChevronDown, ChevronUp, Tag } from 'lucide-react';

interface IMAPConfig {
  host: string;
  port: number;
  username: string;
  password: string;
  folder: string;
  limit: number;
  use_ssl: boolean;
}

interface ScanResult {
  uid: string;
  sender: string;
  subject: string;
  date: string;
  snippet: string;
  status: 'absage' | 'einladung' | 'nachfrage';
  confidence: number;
}

const STATUS_STYLE = {
  absage:    { label: 'Absage',    bg: 'bg-red-100 dark:bg-red-900/30',    text: 'text-red-700 dark:text-red-400' },
  einladung: { label: 'Einladung', bg: 'bg-emerald-100 dark:bg-emerald-900/30', text: 'text-emerald-700 dark:text-emerald-400' },
  nachfrage: { label: 'Nachfrage', bg: 'bg-blue-100 dark:bg-blue-900/30',  text: 'text-blue-700 dark:text-blue-400' },
};

const DEFAULT_CONFIG: IMAPConfig = {
  host: '', port: 993, username: '', password: '', folder: 'INBOX', limit: 50, use_ssl: true,
};

export default function EmailParsingSetup() {
  const [config, setConfig] = useState<IMAPConfig>(DEFAULT_CONFIG);
  const [configOpen, setConfigOpen] = useState(true);
  const [connState, setConnState] = useState<'idle' | 'testing' | 'ok' | 'error'>('idle');
  const [connMsg, setConnMsg] = useState('');
  const [scanState, setScanState] = useState<'idle' | 'scanning' | 'done' | 'error'>('idle');
  const [results, setResults] = useState<ScanResult[]>([]);
  const [scanError, setScanError] = useState('');

  const set = (k: keyof IMAPConfig, v: any) => setConfig((c) => ({ ...c, [k]: v }));

  const testConnection = async () => {
    setConnState('testing');
    try {
      const res = await fetch('/api/email/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setConnState('ok');
      setConnMsg(data.message);
    } catch (e: any) {
      setConnState('error');
      setConnMsg(e.message);
    }
  };

  const startScan = async () => {
    setScanState('scanning');
    setScanError('');
    try {
      const res = await fetch('/api/email/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setResults(data.results);
      setScanState('done');
      setConfigOpen(false);
    } catch (e: any) {
      setScanError(e.message);
      setScanState('error');
    }
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
        <Mail size={18} /> E-Mail-Parsing
      </h2>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Verbinde dein Postfach per IMAP (lokal, kein Cloud-Dienst). JobHunter erkennt automatisch
        Absagen, Einladungen und Rückfragen.
      </p>

      {/* ── Konfiguration ── */}
      <div className="rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <button
          onClick={() => setConfigOpen((v) => !v)}
          className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
        >
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">IMAP-Konfiguration</span>
          {configOpen ? <ChevronUp size={15} className="text-gray-400" /> : <ChevronDown size={15} className="text-gray-400" />}
        </button>

        {configOpen && (
          <div className="p-4 space-y-3 bg-white dark:bg-gray-900">
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2 sm:col-span-1">
                <label className="block text-xs font-medium text-gray-500 mb-1">IMAP-Server</label>
                <input
                  type="text" placeholder="imap.gmail.com"
                  value={config.host} onChange={(e) => set('host', e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Port</label>
                <input
                  type="number" value={config.port} onChange={(e) => set('port', Number(e.target.value))}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-500 mb-1">E-Mail-Adresse</label>
                <input
                  type="email" placeholder="deine@email.de"
                  value={config.username} onChange={(e) => set('username', e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-xs font-medium text-gray-500 mb-1">Passwort / App-Passwort</label>
                <input
                  type="password" placeholder="••••••••"
                  value={config.password} onChange={(e) => set('password', e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-400 mt-1">Bei Gmail: App-Passwort verwenden (nicht dein Google-Passwort).</p>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Ordner</label>
                <input
                  type="text" value={config.folder} onChange={(e) => set('folder', e.target.value)}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Letzte X E-Mails</label>
                <input
                  type="number" min={10} max={200} value={config.limit} onChange={(e) => set('limit', Number(e.target.value))}
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="col-span-2 flex items-center gap-2">
                <input type="checkbox" id="ssl" checked={config.use_ssl} onChange={(e) => set('use_ssl', e.target.checked)} className="rounded" />
                <label htmlFor="ssl" className="text-sm text-gray-600 dark:text-gray-400">SSL verwenden (empfohlen)</label>
              </div>
            </div>

            {/* Verbindung testen */}
            <div className="flex items-center gap-3 pt-1">
              <button
                onClick={testConnection}
                disabled={connState === 'testing' || !config.host || !config.username}
                className="inline-flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-600 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 transition-colors"
              >
                {connState === 'testing' ? <Loader2 size={14} className="animate-spin" /> : <Wifi size={14} />}
                Verbindung testen
              </button>
              {connState === 'ok' && <span className="flex items-center gap-1 text-sm text-emerald-600"><CheckCircle size={14} />{connMsg}</span>}
              {connState === 'error' && <span className="flex items-center gap-1 text-sm text-red-500"><AlertCircle size={14} />{connMsg}</span>}
            </div>
          </div>
        )}
      </div>

      {/* ── Scan starten ── */}
      <button
        onClick={startScan}
        disabled={scanState === 'scanning' || !config.host || !config.username || !config.password}
        className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {scanState === 'scanning' ? <Loader2 size={15} className="animate-spin" /> : <Search size={15} />}
        {scanState === 'scanning' ? 'Scanne Postfach…' : 'Postfach scannen'}
      </button>
      {scanState === 'error' && <p className="text-sm text-red-500">{scanError}</p>}

      {/* ── Ergebnisse ── */}
      {scanState === 'done' && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {results.length === 0 ? 'Keine relevanten E-Mails gefunden.' : `${results.length} relevante E-Mail${results.length > 1 ? 's' : ''} gefunden`}
          </h3>
          {results.map((r) => {
            const style = STATUS_STYLE[r.status];
            return (
              <div key={r.uid} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3 space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{r.subject}</p>
                  <span className={`shrink-0 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${style.bg} ${style.text}`}>
                    <Tag size={10} />{style.label}
                  </span>
                </div>
                <p className="text-xs text-gray-500">{r.sender} · {r.date}</p>
                <p className="text-xs text-gray-400 line-clamp-2">{r.snippet}</p>
                <p className="text-xs text-gray-300 dark:text-gray-600">Konfidenz: {Math.round(r.confidence * 100)} %</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
