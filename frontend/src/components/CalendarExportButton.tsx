import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Calendar, Link2, Check } from 'lucide-react';

interface Props {
  applicationId: number;
}

export default function CalendarExportButton({ applicationId }: Props) {
  const { t } = useTranslation('calendarExportButton');
  const [copied, setCopied] = useState(false);

  const handleDownload = () => {
    const url = `/api/calendar/${applicationId}/ics`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `gespraech_${applicationId}.ics`;
    a.click();
  };

  const handleCopyFeed = async () => {
    const feedUrl = `${window.location.origin}/api/calendar/feed.ics`;
    await navigator.clipboard.writeText(feedUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2">
      {/* Einzeltermin herunterladen */}
      <button
        onClick={handleDownload}
        className="inline-flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700 transition-colors"
        title={t('downloadTitle')}
      >
        <Calendar size={15} />
        {t('download')}
      </button>

      {/* Abo-Feed-URL kopieren */}
      <button
        onClick={handleCopyFeed}
        className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title={t('copyFeedTitle')}
      >
        {copied ? <Check size={15} className="text-emerald-500" /> : <Link2 size={15} />}
        {copied ? t('copied') : t('feedUrl')}
      </button>
    </div>
  );
}
