import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// Namespace-Struktur statt Inline-Objekt, siehe docs/i18n/KONZEPT.md
// (Rework-Plan Phase C.2) und ADR-0003. Jede Datei unter locales/{de,en}/
// ist ein eigenständiger i18next-Namespace, geladen unter demselben
// Schlüssel wie ihr Dateiname - automatisch per import.meta.glob, damit
// neue Namespace-Dateien hier NICHT manuell nachgetragen werden müssen
// (Fehlerquelle bei der schrittweisen Migration in Phase C).
const deModules = import.meta.glob('./locales/de/*.json', { eager: true }) as Record<string, { default: Record<string, unknown> }>
const enModules = import.meta.glob('./locales/en/*.json', { eager: true }) as Record<string, { default: Record<string, unknown> }>

function toNamespaceResources(modules: Record<string, { default: Record<string, unknown> }>) {
  const out: Record<string, Record<string, unknown>> = {}
  for (const path in modules) {
    const ns = path.split('/').pop()!.replace('.json', '')
    out[ns] = modules[path].default
  }
  return out
}

const deResources = toNamespaceResources(deModules)
const enResources = toNamespaceResources(enModules)

i18n.use(initReactI18next).init({
  resources: { de: deResources, en: enResources },
  ns: Object.keys(deResources),
  defaultNS: 'common',
  lng: localStorage.getItem('lang') || 'de',
  fallbackLng: 'de',
  interpolation: { escapeValue: false },
})

export default i18n
