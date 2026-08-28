"""Ruecklaufquoten-Tracker (#78, G.3.8): welche Portale/Wochentage/
Anschreiben-Laengen zu Antworten fuehren, mit Empfehlungen.

"Beantwortet" = die Bewerbung hat den Status interview/angenommen/absage
erreicht - irgendeine Reaktion des Arbeitgebers, egal ob positiv oder
negativ. "beworben" ohne weiteren Statuswechsel zaehlt als noch offen,
nicht als Nicht-Antwort (die Antwort steht ja noch aus, das ist kein
Fehlschlag). "interessant" (noch nicht abgeschickt) zaehlt gar nicht mit
- gleiche Definition von "tatsaechliche Bewerbung" wie in Phase L.1
(exclude_status=interessant im PDF-Export).

Bezugsdatum fuer den Wochentag: applied_at falls gesetzt, sonst
created_at - identisches Fallback-Muster wie routers/applications.py
("bezugsdatum = app.applied_at or app.created_at").

Anschreiben-Laenge in Woertern (len(text.split()), gleiches simple
Zaehlmuster wie ghost_job_detector.py), gebuckt an der von ai_prompts.py
selbst vorgegebenen KI-Zielspanne von 250-350 Woertern statt einer
willkuerlichen eigenen Grenze.

Zwei weitere Dimensionen (#74, G.3.11 "Bewerbungs-Timing-KI" - das
"optimaler Wochentag"-Ziel dieses Issues ist bereits durch by_weekday
oben abgedeckt, hier nur die genuin neuen Teile):
- Tageszeit (by_hour): NUR aus applied_at, kein created_at-Fallback -
  anders als beim Wochentag ist eine Uhrzeit ohne echten Zeitstempel
  bedeutungslos, nicht nur ungenau.
- Tage bis zur Bewerbung (by_days_until_applied): Job.published_at
  (Fallback created_at) vs. Application.applied_at - wie lange nach
  Veroeffentlichung wurde beworben, und hat das die Rueckantwortquote
  beeinflusst. Bewusst NICHT die im GitHub-Issue vorgeschlagene
  "Jan/Feb sind Hochsaison"-Pauschalaussage uebernommen - das waere eine
  unbelegte allgemeine Behauptung ohne Bezug zu den eigenen Daten dieses
  Nutzers, das Gegenteil des in diesem Projekt etablierten Anti-
  Erfindungs-Prinzips (siehe z.B. die NUTS-Regionen-Recherche bei EURES
  statt einer geratenen PLZ-Zuordnung).

Empfehlungen werden nur ausgesprochen, wenn mindestens zwei Kategorien
einer Dimension je >= MIN_SAMPLE_FOR_RECOMMENDATION Bewerbungen haben -
sonst waere ein Vergleich (z.B. 1 von 1 vs. 0 von 2) statistisch
bedeutungslos und irrefuehrend.
"""
from __future__ import annotations

from datetime import timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.cover_letter import CoverLetter
from backend.models.job import Job

RESPONDED_STATUSES = {"interview", "angenommen", "absage"}
MIN_SAMPLE_FOR_RECOMMENDATION = 3

WEEKDAY_LABELS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

LENGTH_BUCKETS = ["kurz", "mittel", "lang"]
LENGTH_LABELS_DE = {
    "kurz": "Kurz (<200 Wörter)",
    "mittel": "Mittel (200-350 Wörter)",
    "lang": "Lang (>350 Wörter)",
}

HOUR_BUCKETS = ["morgens", "mittags", "nachmittags", "abends"]
HOUR_LABELS_DE = {
    "morgens": "Morgens (6-11 Uhr)",
    "mittags": "Mittags (11-15 Uhr)",
    "nachmittags": "Nachmittags (15-19 Uhr)",
    "abends": "Abends/Nachts (19-6 Uhr)",
}

DAYS_UNTIL_BUCKETS = ["sofort", "kurz", "mittel", "spaet"]
DAYS_UNTIL_LABELS_DE = {
    "sofort": "Sofort (gleicher Tag)",
    "kurz": "1-3 Tage später",
    "mittel": "4-7 Tage später",
    "spaet": "Mehr als 7 Tage später",
}


def _length_bucket(word_count: int) -> str:
    if word_count < 200:
        return "kurz"
    if word_count <= 350:
        return "mittel"
    return "lang"


def _hour_bucket(hour: int) -> str:
    if 6 <= hour < 11:
        return "morgens"
    if 11 <= hour < 15:
        return "mittags"
    if 15 <= hour < 19:
        return "nachmittags"
    return "abends"


def _days_until_bucket(days: int) -> str:
    if days <= 0:
        return "sofort"
    if days <= 3:
        return "kurz"
    if days <= 7:
        return "mittel"
    return "spaet"


def _aware(dt):
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _rate(total: int, responded: int) -> float:
    return round(responded / total * 100, 1) if total else 0.0


async def get_response_rate_analysis(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Application, Job.source_portal, Job.published_at, Job.created_at)
        .join(Job, Application.job_id == Job.id)
        .where(Application.status != "interessant")
    )
    rows = result.all()

    cl_result = await db.execute(
        select(CoverLetter.application_id, CoverLetter.content)
        .where(CoverLetter.application_id.isnot(None))
        # id DESC als Tiebreaker: SQLite's created_at-Aufloesung ist zu
        # grob, um zwei kurz hintereinander erzeugte Anschreiben sicher zu
        # ordnen (gleiches Muster wie diary_pdf.py).
        .order_by(CoverLetter.created_at.desc(), CoverLetter.id.desc())
    )
    # Bei mehreren Anschreiben pro Bewerbung zaehlt das neueste (erster
    # Treffer dank ORDER BY ... DESC).
    cover_letter_words: dict[int, int] = {}
    for app_id, content in cl_result.all():
        if app_id not in cover_letter_words:
            cover_letter_words[app_id] = len(content.split())

    by_portal: dict[str, list[int]] = {}
    by_weekday: dict[int, list[int]] = {i: [0, 0] for i in range(7)}
    by_length: dict[str, list[int]] = {b: [0, 0] for b in LENGTH_BUCKETS}
    by_hour: dict[str, list[int]] = {b: [0, 0] for b in HOUR_BUCKETS}
    by_days_until: dict[str, list[int]] = {b: [0, 0] for b in DAYS_UNTIL_BUCKETS}

    for app, source_portal, job_published_at, job_created_at in rows:
        responded = 1 if app.status in RESPONDED_STATUSES else 0

        portal_key = source_portal or "unbekannt"
        by_portal.setdefault(portal_key, [0, 0])
        by_portal[portal_key][0] += 1
        by_portal[portal_key][1] += responded

        bezugsdatum = app.applied_at or app.created_at
        if bezugsdatum is not None:
            weekday = bezugsdatum.weekday()
            by_weekday[weekday][0] += 1
            by_weekday[weekday][1] += responded

        words = cover_letter_words.get(app.id)
        if words is not None:
            bucket = _length_bucket(words)
            by_length[bucket][0] += 1
            by_length[bucket][1] += responded

        if app.applied_at is not None:
            hour_bucket = _hour_bucket(app.applied_at.hour)
            by_hour[hour_bucket][0] += 1
            by_hour[hour_bucket][1] += responded

            job_ref_date = job_published_at or job_created_at
            if job_ref_date is not None:
                applied_at = _aware(app.applied_at)
                job_ref_date = _aware(job_ref_date)
                days_diff = (applied_at.date() - job_ref_date.date()).days
                days_bucket = _days_until_bucket(days_diff)
                by_days_until[days_bucket][0] += 1
                by_days_until[days_bucket][1] += responded

    portal_entries = [
        {"key": key, "total": total, "beantwortet": responded, "quote": _rate(total, responded)}
        for key, (total, responded) in sorted(by_portal.items(), key=lambda kv: -kv[1][0])
    ]
    weekday_entries = [
        {
            "key": i,
            "label": WEEKDAY_LABELS_DE[i],
            "total": by_weekday[i][0],
            "beantwortet": by_weekday[i][1],
            "quote": _rate(by_weekday[i][0], by_weekday[i][1]),
        }
        for i in range(7)
    ]
    length_entries = [
        {
            "key": bucket,
            "label": LENGTH_LABELS_DE[bucket],
            "total": by_length[bucket][0],
            "beantwortet": by_length[bucket][1],
            "quote": _rate(by_length[bucket][0], by_length[bucket][1]),
        }
        for bucket in LENGTH_BUCKETS
    ]
    hour_entries = [
        {
            "key": bucket,
            "label": HOUR_LABELS_DE[bucket],
            "total": by_hour[bucket][0],
            "beantwortet": by_hour[bucket][1],
            "quote": _rate(by_hour[bucket][0], by_hour[bucket][1]),
        }
        for bucket in HOUR_BUCKETS
    ]
    days_until_entries = [
        {
            "key": bucket,
            "label": DAYS_UNTIL_LABELS_DE[bucket],
            "total": by_days_until[bucket][0],
            "beantwortet": by_days_until[bucket][1],
            "quote": _rate(by_days_until[bucket][0], by_days_until[bucket][1]),
        }
        for bucket in DAYS_UNTIL_BUCKETS
    ]

    return {
        "by_portal": portal_entries,
        "by_weekday": weekday_entries,
        "by_cover_letter_length": length_entries,
        "by_hour": hour_entries,
        "by_days_until_applied": days_until_entries,
        "empfehlungen": _build_recommendations(
            portal_entries, weekday_entries, length_entries, hour_entries, days_until_entries,
        ),
    }


def _best_vs_rest(entries: list[dict]) -> tuple[dict, dict] | None:
    qualified = [e for e in entries if e["total"] >= MIN_SAMPLE_FOR_RECOMMENDATION]
    if len(qualified) < 2:
        return None
    best = max(qualified, key=lambda e: e["quote"])
    worst = min(qualified, key=lambda e: e["quote"])
    if best["quote"] <= worst["quote"]:
        return None
    return best, worst


def _build_recommendations(
    portal_entries: list[dict],
    weekday_entries: list[dict],
    length_entries: list[dict],
    hour_entries: list[dict],
    days_until_entries: list[dict],
) -> list[str]:
    empfehlungen = []

    portal_cmp = _best_vs_rest(portal_entries)
    if portal_cmp:
        best, worst = portal_cmp
        empfehlungen.append(
            f"Bewerbungen über \"{best['key']}\" haben mit {best['quote']}% die höchste "
            f"Rücklaufquote (vs. {worst['quote']}% über \"{worst['key']}\")."
        )

    weekday_cmp = _best_vs_rest(weekday_entries)
    if weekday_cmp:
        best, worst = weekday_cmp
        empfehlungen.append(
            f"{best['label']} verschickte Bewerbungen haben mit {best['quote']}% die höchste "
            f"Rücklaufquote (vs. {worst['quote']}% am {worst['label']})."
        )

    length_cmp = _best_vs_rest(length_entries)
    if length_cmp:
        best, worst = length_cmp
        empfehlungen.append(
            f"Anschreiben der Länge \"{best['label']}\" erzielen mit {best['quote']}% die höchste "
            f"Rücklaufquote (vs. {worst['quote']}% bei \"{worst['label']}\")."
        )

    hour_cmp = _best_vs_rest(hour_entries)
    if hour_cmp:
        best, worst = hour_cmp
        empfehlungen.append(
            f"Bewerbungen \"{best['label']}\" verschickt haben mit {best['quote']}% die höchste "
            f"Rücklaufquote (vs. {worst['quote']}% \"{worst['label']}\")."
        )

    days_until_cmp = _best_vs_rest(days_until_entries)
    if days_until_cmp:
        best, worst = days_until_cmp
        empfehlungen.append(
            f"Bewerbungen \"{best['label']}\" nach Veröffentlichung haben mit {best['quote']}% die "
            f"höchste Rücklaufquote (vs. {worst['quote']}% bei \"{worst['label']}\")."
        )

    return empfehlungen
