"""Absagen-Analyse (#73, G.3.12): systemische Muster in erhaltenen
Absagen erkennen.

Es gibt kein absage_text-Feld im Datenmodell (siehe
services/rejection_analyzer.py - bewusste Entscheidung in einer
frueheren Session, kein Freitext-Absagegrund persistiert, stattdessen
zustandslose Pro-Absage-Analyse mit vom Nutzer eingegebenem Text). Eine
KI-Mustererkennung ueber ALLE Absagen wuerde also entweder Freitext
voraussetzen, den es nicht gibt, oder einen Ollama-Call pro Absage bei
jedem Dashboard-Aufruf brauchen - aus denselben Performance-Gruenden
verworfen wie schon bei market_trends.py/response_rate_analyzer.py
(CPU-only Host).

Stattdessen: eine rein deterministische Korrelationsanalyse gegen
strukturierte Signale, die dieses Projekt an anderer Stelle bereits
berechnet und cacht - kein neuer KI-Call noetig:
- Skill-Gap-Score (services/skill_gap.py, CV-vs-Job-Match, 0-100,
  gecacht auf Job.skill_gap_score)
- ATS-Score (services/ats_scorer.py, Keyword-Match, 0-100, gecacht auf
  Application.ats_score)
- Anschreiben-Qualitaetsscore (services/cover_letter_evaluator.py,
  0-100, gecacht auf CoverLetter.quality_score)
- Senioritaets-Abgleich: Stellentitel-Level per mehrsprachiger
  Keyword-Klassifikation (gleiches Prinzip wie market_trends.py's
  Branchen-Klassifikation - Live-Check der Produktions-DB zeigte
  bereits einmal, dass echte Jobtitel hier ueberwiegend nicht deutsch
  sind) gegen UserProfile.erfahrungsjahre - genau das im GitHub-Issue
  genannte Beispiel ("Du bewirbst dich oft auf Senior-Stellen mit
  Junior-Profil").

Fuer jedes Signal: Absage-Quote in der "Risiko"-Gruppe (z.B. niedriger
Skill-Gap-Score) vs. der Referenz-Gruppe, nur als auffaellig markiert
wenn beide Gruppen >= MIN_SAMPLE Bewerbungen haben UND der Unterschied
> 10 Prozentpunkte betraegt - gleiche Zurueckhaltung wie in
market_trends.py/response_rate_analyzer.py, um keinen Zufall als
Muster zu verkaufen.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.job import Job
from backend.models.user_profile import UserProfile

MIN_SAMPLE = 3
MIN_ABSAGEN_FOR_ANALYSIS = 10  # wie im GitHub-Issue selbst gefordert
NOTABLE_DIFF_PP = 10  # Prozentpunkte

LOW_SCORE_THRESHOLD = 60

JUNIOR_KEYWORDS = [
    "junior", "praktikant", "trainee", "einsteiger", "azubi", "auszubildende",
    "werkstudent", "intern", "entry level", "graduate",
    "stagiaire", "débutant", "alternance",
    "praktik",
]
SENIOR_KEYWORDS = [
    "senior", "lead", "teamleiter", "teamleitung", "leiter", "leitung",
    "manager", "direktor", "principal", "head of", "erfahrener",
    "responsable", "chef de", "directeur", "expert",
    "ledare", "chef", "erfaren",
]
LEVEL_ORDER = {"junior": 0, "mid": 1, "senior": 2}


def _job_level(title: str) -> str:
    title_lower = (title or "").lower()
    if any(kw in title_lower for kw in JUNIOR_KEYWORDS):
        return "junior"
    if any(kw in title_lower for kw in SENIOR_KEYWORDS):
        return "senior"
    return "mid"


def _profile_level(erfahrungsjahre: int | None) -> str | None:
    if erfahrungsjahre is None:
        return None
    if erfahrungsjahre < 3:
        return "junior"
    if erfahrungsjahre <= 6:
        return "mid"
    return "senior"


def _group_stats(total: int, absagen: int) -> dict:
    return {
        "total": total,
        "absagen": absagen,
        "absage_quote": round(absagen / total * 100, 1) if total else 0.0,
    }


def _compare(risiko: dict, referenz: dict) -> bool:
    """Auffaellig = beide Gruppen ausreichend Stichprobe UND Risiko-Gruppe
    hat eine merklich hoehere Absage-Quote."""
    if risiko["total"] < MIN_SAMPLE or referenz["total"] < MIN_SAMPLE:
        return False
    return risiko["absage_quote"] - referenz["absage_quote"] > NOTABLE_DIFF_PP


async def get_rejection_patterns(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Application, Job.title, Job.skill_gap_score)
        .join(Job, Application.job_id == Job.id)
        # Gleiche Denominator-Definition wie response_rate_analyzer.py:
        # alle tatsaechlich abgeschickten Bewerbungen, "interessant" zaehlt
        # nicht mit. "beworben" (noch offen) zaehlt als "bisher keine
        # Absage" - spiegelt den aktuellen Wissensstand, nicht eine
        # endgueltige Bewertung.
        .where(Application.status != "interessant")
    )
    rows = result.all()

    profile_result = await db.execute(select(UserProfile).where(UserProfile.id == 1))
    profile = profile_result.scalar_one_or_none()
    profile_level = _profile_level(profile.erfahrungsjahre if profile else None)

    gesamt_bewerbungen = len(rows)
    gesamt_absagen = sum(1 for app, _, _ in rows if app.status == "absage")

    # Skill-Gap-Score: niedrig (Risiko) vs. hoch (Referenz)
    skill_gap_low = [0, 0]
    skill_gap_high = [0, 0]
    for app, _, skill_gap_score in rows:
        if skill_gap_score is None:
            continue
        is_absage = 1 if app.status == "absage" else 0
        bucket = skill_gap_low if skill_gap_score < LOW_SCORE_THRESHOLD else skill_gap_high
        bucket[0] += 1
        bucket[1] += is_absage

    # ATS-Score: niedrig (Risiko) vs. hoch (Referenz)
    ats_low = [0, 0]
    ats_high = [0, 0]
    for app, _, _ in rows:
        if app.ats_score is None:
            continue
        is_absage = 1 if app.status == "absage" else 0
        bucket = ats_low if app.ats_score < LOW_SCORE_THRESHOLD else ats_high
        bucket[0] += 1
        bucket[1] += is_absage

    # Senioritaet: Bewerbung ueber dem eigenen Profil-Level (Risiko) vs.
    # auf/unter Profil-Level (Referenz) - nur moeglich, wenn erfahrungsjahre
    # im Profil gepflegt ist.
    seniority_over = [0, 0]
    seniority_at_or_below = [0, 0]
    if profile_level is not None:
        for app, title, _ in rows:
            job_level = _job_level(title)
            is_absage = 1 if app.status == "absage" else 0
            bucket = (
                seniority_over
                if LEVEL_ORDER[job_level] > LEVEL_ORDER[profile_level]
                else seniority_at_or_below
            )
            bucket[0] += 1
            bucket[1] += is_absage

    signale = []

    skill_gap_risiko = _group_stats(*skill_gap_low)
    skill_gap_referenz = _group_stats(*skill_gap_high)
    signale.append({
        "signal": "skill_gap",
        "label": "Niedriger CV-Skill-Match",
        "risiko_gruppe": skill_gap_risiko,
        "referenz_gruppe": skill_gap_referenz,
        "auffaellig": _compare(skill_gap_risiko, skill_gap_referenz),
    })

    ats_risiko = _group_stats(*ats_low)
    ats_referenz = _group_stats(*ats_high)
    signale.append({
        "signal": "ats",
        "label": "Niedriger ATS-Keyword-Match",
        "risiko_gruppe": ats_risiko,
        "referenz_gruppe": ats_referenz,
        "auffaellig": _compare(ats_risiko, ats_referenz),
    })

    if profile_level is not None:
        seniority_risiko = _group_stats(*seniority_over)
        seniority_referenz = _group_stats(*seniority_at_or_below)
        signale.append({
            "signal": "seniority",
            "label": "Bewerbung über dem eigenen Erfahrungslevel",
            "risiko_gruppe": seniority_risiko,
            "referenz_gruppe": seniority_referenz,
            "auffaellig": _compare(seniority_risiko, seniority_referenz),
        })

    return {
        "gesamt_bewerbungen": gesamt_bewerbungen,
        "gesamt_absagen": gesamt_absagen,
        "genug_daten": gesamt_absagen >= MIN_ABSAGEN_FOR_ANALYSIS,
        "signale": signale,
        "empfehlungen": _build_recommendations(signale),
    }


def _build_recommendations(signale: list[dict]) -> list[str]:
    empfehlungen = []
    for s in signale:
        if not s["auffaellig"]:
            continue
        risiko = s["risiko_gruppe"]
        referenz = s["referenz_gruppe"]
        if s["signal"] == "skill_gap":
            empfehlungen.append(
                f"Bewerbungen mit niedrigem CV-Skill-Match enden mit {risiko['absage_quote']}% deutlich "
                f"häufiger in einer Absage als solche mit gutem Match ({referenz['absage_quote']}%) - "
                f"nutze den Skill-Gap-Check vor dem Absenden."
            )
        elif s["signal"] == "ats":
            empfehlungen.append(
                f"Bewerbungen mit niedrigem ATS-Keyword-Match enden mit {risiko['absage_quote']}% deutlich "
                f"häufiger in einer Absage als solche mit gutem Match ({referenz['absage_quote']}%) - "
                f"passe deinen CV stärker an die jeweilige Stellenbeschreibung an."
            )
        elif s["signal"] == "seniority":
            empfehlungen.append(
                f"Bewerbungen auf Stellen über deinem eigenen Erfahrungslevel enden mit "
                f"{risiko['absage_quote']}% deutlich häufiger in einer Absage als passende Stellen "
                f"({referenz['absage_quote']}%) - erwäge, dich zunächst auf Stellen auf deinem Level zu bewerben."
            )
    return empfehlungen
