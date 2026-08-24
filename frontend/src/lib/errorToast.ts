/**
 * Globaler Fehler-Toast-Kanal (Rework-Plan Phase D.1).
 *
 * lib/api.ts (ein axios-Interceptor, kein React-Kontext) ruft showError()
 * auf; components/ErrorToastContainer.tsx (innerhalb des React-Baums)
 * hoert auf das Event und zeigt den Toast an. Ein simples
 * window-CustomEvent statt Context/Redux, weil der Sender ausserhalb
 * jedes React-Kontexts liegt.
 */
export const API_ERROR_EVENT = 'jobhunter:api-error'

export function showError(message: string) {
  window.dispatchEvent(new CustomEvent<string>(API_ERROR_EVENT, { detail: message }))
}
