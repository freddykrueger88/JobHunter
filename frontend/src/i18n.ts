import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Namespace-Struktur statt Inline-Objekt, siehe docs/i18n/KONZEPT.md
// (Rework-Plan Phase C.2) und ADR-0003. Jede Datei hier ist ein
// eigenständiger i18next-Namespace, geladen unter demselben Schlüssel
// wie ihr Dateiname.
import deCommon from './locales/de/common.json'
import deNav from './locales/de/nav.json'
import deDashboard from './locales/de/dashboard.json'
import deJobs from './locales/de/jobs.json'
import deSettings from './locales/de/settings.json'

import enCommon from './locales/en/common.json'
import enNav from './locales/en/nav.json'
import enDashboard from './locales/en/dashboard.json'
import enJobs from './locales/en/jobs.json'
import enSettings from './locales/en/settings.json'

const resources = {
  de: {
    common: deCommon,
    nav: deNav,
    dashboard: deDashboard,
    jobs: deJobs,
    settings: deSettings,
  },
  en: {
    common: enCommon,
    nav: enNav,
    dashboard: enDashboard,
    jobs: enJobs,
    settings: enSettings,
  },
}

i18n.use(initReactI18next).init({
  resources,
  ns: Object.keys(resources.de),
  defaultNS: 'common',
  lng: localStorage.getItem('lang') || 'de',
  fallbackLng: 'de',
  interpolation: { escapeValue: false },
})

export default i18n
