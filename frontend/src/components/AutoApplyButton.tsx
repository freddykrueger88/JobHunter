import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { Package, Download, FileText, FileJson, X, Loader2 } from 'lucide-react'

interface Props {
  applicationId: number
  jobTitle?: string
  company?: string
  hasCoverLetter?: boolean
  hasCV?: boolean
}

export default function AutoApplyButton({
  applicationId,
  jobTitle,
  company,
  hasCoverLetter = false,
  hasCV = false,
}: Props) {
  const { t } = useTranslation(['autoApplyButton', 'common'])
  jobTitle = jobTitle ?? t('fallbackJobTitle')
  company = company ?? t('fallbackCompany')
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleDownload = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/applications/${applicationId}/zip`, {
        responseType: 'blob',
      })
      const url = URL.createObjectURL(response.data)
      const today = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      const safeCompany = company.replace(/[^\w]/g, '_')
      const safeTitle = jobTitle.replace(/[^\w]/g, '_')
      const a = document.createElement('a')
      a.href = url
      a.download = `Bewerbung_${safeCompany}_${safeTitle}_${today}.zip`
      a.click()
      URL.revokeObjectURL(url)
      setShowModal(false)
    } catch {
      alert(t('errorZip'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
        title={t('downloadTitle')}
      >
        <Package size={16} aria-hidden />
        {t('button')}
      </button>

      {showModal && (
        <>
          <div
            className="fixed inset-0 bg-black/40 z-50"
            onClick={() => setShowModal(false)}
            aria-hidden
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label={t('dialogAriaLabel')}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Package size={20} className="text-green-600" aria-hidden />
                  {t('heading')}
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label={t('close')}
                >
                  <X size={18} aria-hidden />
                </button>
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                {t('filesIntro')}
              </p>

              <ul className="space-y-2 mb-6">
                <li className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                  hasCoverLetter
                    ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                    : 'bg-gray-50 dark:bg-gray-700/50 text-gray-400 line-through'
                }`}>
                  <FileText size={16} aria-hidden />
                  Anschreiben_{company.replace(/[^\w]/g, '_')}.pdf
                  {!hasCoverLetter && <span className="text-xs ml-auto">{t('notPresent')}</span>}
                </li>
                <li className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                  <FileJson size={16} aria-hidden />
                  bewerbung_meta.json
                </li>
                <li className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm bg-gray-50 dark:bg-gray-700/50 text-gray-500">
                  <FileText size={16} aria-hidden />
                  README.txt
                </li>
              </ul>

              <p className="text-xs text-gray-400 mb-5">
                {t('filename')} <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">
                  Bewerbung_{company.replace(/[^\w]/g, '_')}_{jobTitle.replace(/[^\w]/g, '_')}_{new Date().toISOString().slice(0, 10).replace(/-/g, '')}.zip
                </code>
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-600 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  {t('common:cancel')}
                </button>
                <button
                  onClick={handleDownload}
                  disabled={loading}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white text-sm font-medium transition-colors disabled:opacity-50"
                >
                  {loading ? (
                    <><Loader2 size={16} className="animate-spin" aria-hidden /> {t('creatingZip')}</>
                  ) : (
                    <><Download size={16} aria-hidden /> {t('download')}</>
                  )}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  )
}
