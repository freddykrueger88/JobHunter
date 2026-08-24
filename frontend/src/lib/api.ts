import axios, { AxiosError } from 'axios'

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

export default api
