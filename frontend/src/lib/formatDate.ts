// Gemeinsame, locale-abhaengige Datumsformatierung (docs/i18n/KONZEPT.md:
// Intl statt hartcodierter 'de-DE'-Locale). i18nLanguage kommt aus
// useTranslation().i18n.language ('de' oder 'en').

function toIntlLocale(i18nLanguage: string): string {
  return i18nLanguage === 'de' ? 'de-DE' : 'en-US'
}

export function formatDate(iso: string | null | undefined, i18nLanguage: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(toIntlLocale(i18nLanguage), {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function formatDateTime(iso: string | null | undefined, i18nLanguage: string): string {
  if (!iso) return ''
  return new Date(iso).toLocaleString(toIntlLocale(i18nLanguage), {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
