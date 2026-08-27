"""Bewerbungs-Qualitaetsscore: Gewichteter Gesamt-Score aus allen vorhandenen KI-Tools.

Ursprungsversion griff auf Application.anschreiben/anschreiben_score/
cv_pfad/ats_score zu - keines davon existierte je auf dem Modell
(Anschreiben liegen in einer eigenen Tabelle, CVs sind global statt pro
Bewerbung, ATS-/Anschreiben-Scores wurden nirgends zwischengespeichert).
Jetzt: CoverLetter.quality_score + Application.ats_score werden von
cover_letter_evaluator.py bzw. dem ats-check-Endpoint befuellt, sobald
sie einmal gelaufen sind; CV-Vorhandensein ist global wie ueberall sonst
im Projekt (skill_gap, job_analyzer, ats_scorer nutzen denselben
"zuletzt hochgeladener CV"-Ansatz)."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models import Application, CoverLetter, CVData, Job

# Gewichtung der einzelnen Komponenten
WEIGHTS = {
    'anschreiben':       20,  # vorhanden?
    'anschreiben_score': 25,  # KI-Bewertung (cover_letter_evaluator.py)
    'cv_vorhanden':      15,  # Lebenslauf hochgeladen?
    'ats_score':         25,  # ATS-Keyword-Match
    'skill_gap':         15,  # Skill-Gap-Score (job_analyzer/skill_gap.py)
}

CHECKS = [
    {'key': 'anschreiben',       'label': 'Anschreiben vorhanden'},
    {'key': 'anschreiben_score', 'label': 'Anschreiben bewertet'},
    {'key': 'cv_vorhanden',      'label': 'Lebenslauf hochgeladen'},
    {'key': 'ats_score',         'label': 'ATS-Score berechnet'},
    {'key': 'skill_gap',         'label': 'Skill-Gap analysiert'},
]


async def get_quality_score(application_id: int, db: AsyncSession) -> dict:
    """Berechnet den Qualitaetsscore einer Bewerbung."""
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise ValueError('Bewerbung nicht gefunden')

    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()

    cl_result = await db.execute(
        select(CoverLetter)
        .where(CoverLetter.application_id == application_id)
        .order_by(CoverLetter.created_at.desc())
        .limit(1)
    )
    cover_letter = cl_result.scalar_one_or_none()

    cv_count = (await db.execute(select(func.count()).select_from(CVData))).scalar() or 0

    components = {
        'anschreiben': 100 if cover_letter else 0,
        'anschreiben_score': min(cover_letter.quality_score, 100) if cover_letter and cover_letter.quality_score else 0,
        'cv_vorhanden': 100 if cv_count > 0 else 0,
        'ats_score': min(app.ats_score, 100) if app.ats_score else 0,
        'skill_gap': min(job.skill_gap_score, 100) if job and job.skill_gap_score else 0,
    }

    total_weight = sum(WEIGHTS.values())
    weighted_sum = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)
    gesamt_score = round(weighted_sum / total_weight)

    checklist = []
    for check in CHECKS:
        key = check['key']
        done = components[key] > 0
        checklist.append({
            'key': key,
            'label': check['label'],
            'erledigt': done,
            'score': components[key],
            # Kein Deep-Link ins Kanban-Board fuer eine einzelne Bewerbung
            # moeglich (keine entsprechende Route) - bewusst kein Link
            # statt eines toten.
            'link': None,
        })

    fehlende = [c for c in checklist if not c['erledigt']]
    naechster_schritt = fehlende[0] if fehlende else None

    return {
        'gesamt_score': gesamt_score,
        'ampel': 'gruen' if gesamt_score >= 70 else 'gelb' if gesamt_score >= 45 else 'rot',
        'komponenten': components,
        'checklist': checklist,
        'naechster_schritt': naechster_schritt,
        'vollstaendig': len(fehlende) == 0,
    }
