"""Bewerbungs-Qualitaetsscore: Gewichteter Gesamt-Score aus allen vorhandenen KI-Tools."""
from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, Job

# Gewichtung der einzelnen Komponenten
WEIGHTS = {
    'anschreiben':       20,  # vorhanden?
    'anschreiben_score': 25,  # Bewertung aus v1.5
    'cv_vorhanden':      15,  # Lebenslauf hochgeladen?
    'ats_score':         25,  # ATS-Keyword-Match (v1.8)
    'skill_gap':         15,  # Skill-Gap-Score (v1.5)
}

CHECKS = [
    {'key': 'anschreiben',       'label': 'Anschreiben vorhanden',     'link': 'anschreiben'},
    {'key': 'anschreiben_score', 'label': 'Anschreiben bewertet',      'link': 'anschreiben-bewertung'},
    {'key': 'cv_vorhanden',      'label': 'Lebenslauf hochgeladen',    'link': 'lebenslauf'},
    {'key': 'ats_score',         'label': 'ATS-Score berechnet',       'link': 'ats-check'},
    {'key': 'skill_gap',         'label': 'Skill-Gap analysiert',      'link': 'skill-gap'},
]


async def get_quality_score(application_id: int, db: AsyncSession) -> dict:
    """Berechnet den Qualitaetsscore einer Bewerbung."""
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise ValueError('Bewerbung nicht gefunden')

    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()

    # Einzelkomponenten bewerten
    components = {}

    # Anschreiben vorhanden (0 oder 100)
    components['anschreiben'] = 100 if app.anschreiben else 0

    # Anschreiben-Score aus DB (aus cover_letter_evaluator v1.5)
    if hasattr(app, 'anschreiben_score') and app.anschreiben_score:
        components['anschreiben_score'] = min(int(app.anschreiben_score), 100)
    else:
        components['anschreiben_score'] = 0

    # CV vorhanden
    components['cv_vorhanden'] = 100 if getattr(app, 'cv_pfad', None) else 0

    # ATS-Score aus DB
    if hasattr(app, 'ats_score') and app.ats_score:
        components['ats_score'] = min(int(app.ats_score), 100)
    else:
        components['ats_score'] = 0

    # Skill-Gap-Score aus Job (gecacht in v1.5)
    if job and hasattr(job, 'skill_gap_score') and job.skill_gap_score:
        components['skill_gap'] = min(int(job.skill_gap_score), 100)
    else:
        components['skill_gap'] = 0

    # Gewichteter Gesamt-Score
    total_weight = sum(WEIGHTS.values())
    weighted_sum = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)
    gesamt_score = round(weighted_sum / total_weight)

    # Checkliste mit Status und Schnelllinks
    checklist = []
    for check in CHECKS:
        key = check['key']
        done = components[key] > 0
        checklist.append({
            'key': key,
            'label': check['label'],
            'erledigt': done,
            'score': components[key],
            'link': f'/bewerbung/{application_id}/{check["link"]}' if not done else None,
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
