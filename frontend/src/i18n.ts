import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  de: {
    translation: {
      nav: {
        dashboard: 'Dashboard', jobs: 'Stellensuche', kanban: 'Bewerbungen',
        reminders: 'Erinnerungen', history: 'Verlauf', settings: 'Einstellungen',
      },
      dashboard: {
        title: 'Dashboard', applied: 'Beworben', rejected: 'Absagen',
        accepted: 'Angenommen', interview: 'Interview', open: 'Interessant',
      },
      jobs: { title: 'Stellensuche', search: 'Suchen', hide: 'Ausblenden' },
      settings: { title: 'Einstellungen', theme: 'Design', language: 'Sprache', ai: 'KI-Einstellungen' },
      common: { save: 'Speichern', cancel: 'Abbrechen', delete: 'Löschen', loading: 'Lädt...' },
    },
  },
  en: {
    translation: {
      nav: {
        dashboard: 'Dashboard', jobs: 'Job Search', kanban: 'Applications',
        reminders: 'Reminders', history: 'History', settings: 'Settings',
      },
      dashboard: {
        title: 'Dashboard', applied: 'Applied', rejected: 'Rejected',
        accepted: 'Accepted', interview: 'Interview', open: 'Interesting',
      },
      jobs: { title: 'Job Search', search: 'Search', hide: 'Hide' },
      settings: { title: 'Settings', theme: 'Theme', language: 'Language', ai: 'AI Settings' },
      common: { save: 'Save', cancel: 'Cancel', delete: 'Delete', loading: 'Loading...' },
    },
  },
}

i18n.use(initReactI18next).init({
  resources,
  lng: localStorage.getItem('lang') || 'de',
  fallbackLng: 'de',
  interpolation: { escapeValue: false },
})

export default i18n
