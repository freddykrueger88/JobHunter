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

Empfehlungen werden nur ausgesprochen, wenn mindestens zwei Kategorien
einer Dimension je >= MIN_SAMPLE_FOR_RECOMMENDATION Bewerbungen haben -
sonst waere ein Vergleich (z.B. 1 von 1 vs. 0 von 2) statistisch
bedeutungslos und irrefuehrend.
"""
from __future__ import annotations

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


def _length_bucket(word_count: int) -> str:
    if word_count < 200:
        return "kurz"
    if word_count <= 350:
        return "mittel"
    return "lang"


def _rate(total: int, responded: int) -> float:
    return round(responded / total * 100, 1) if total else 0.0


async def get_response_rate_analysis(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Application, Job.source_portal)
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

    for app, source_portal in rows:
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

    return {
        "by_portal": portal_entries,
        "by_weekday": weekday_entries,
        "by_cover_letter_length": length_entries,
        "empfehlungen": _build_recommendations(portal_entries, weekday_entries, length_entries),
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


def _build_recommendations(portal_entries: list[dict], weekday_entries: list[dict], length_entries: list[dict]) -> list[str]:
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

    return empfehlungen
