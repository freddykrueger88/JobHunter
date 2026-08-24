import axios, { AxiosError } from 'axios'
import type { TFunction } from 'i18next'

/**
 * Zentraler API-Client - loest den in REPOSITORY_AUDIT_DE.md Abschnitt 1.2
 * dokumentierten Befund "kein zentraler Frontend-API-Client" auf
 * (Rework-Plan Phase B.4). baseURL bleibt leer/same-origin, damit bestehende
 * Aufrufe mit vollem "/api/..."-Pfad unveraendert weiterfunktionieren -
 * neue bzw. migrierte Aufrufe nutzen relative Pfade ab "/api".
 *
 * Migration der bestehenden 22 direkten axios-Aufrufe erfolgt schrittweise
 * in Phase C/D (siehe docs/analysis/REWORK_PLAN_DE.md), nicht in einem
 * grossen Schritt.
 */
export const api = axios.create({
  baseURL: '/api',
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const detail = error.response?.data?.detail
    const message = detail || error.message || 'Unbekannter Fehler'
    // Einheitlicher Log-Punkt fuer alle API-Fehler. UI-seitige, uebersetzte
    // Fehleranzeige folgt in Rework-Plan Phase D (Produktqualitaet) -
    // hier bewusst nur die zentrale Stelle geschaffen, an der das spaeter
    // andockt (z.B. Toast-Komponente statt console.error).
    console.error(`[API-Fehler] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`)
    return Promise.reject(error)
  },
)

/**
 * Liefert eine nutzersichtbare Fehlermeldung fuer einen API-Fehler.
 *
 * Backend-Endpunkte, die auf core.errors.api_error() umgestellt wurden
 * (Rework-Plan Phase C.4), senden den Fehlercode im X-Error-Code-Header.
 * Existiert dafuer ein Eintrag unter common:errors.<code>, wird dieser
 * uebersetzt zurueckgegeben - sonst faellt es auf den deutschen Klartext
 * aus response.data.detail zurueck (bei noch nicht migrierten Endpunkten).
 *
 * t muss den "common"-Namespace geladen haben (useTranslation([..., 'common'])).
 */
export function getApiErrorMessage(error: unknown, t: TFunction): string {
  if (axios.isAxiosError(error)) {
    const code = error.response?.headers?.['x-error-code'] as string | undefined
    if (code && t('common:errors.' + code, { defaultValue: '' })) {
      return t('common:errors.' + code)
    }
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail
    if (detail) return detail
    return error.message
  }
  return t('common:errors.unknown')
}

export default api
