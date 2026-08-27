"""Gamification: Abzeichen-System fuer Meilensteine."""
from __future__ import annotations
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models import Application, CoverLetter, CVData, Job, UserBadge

BADGE_DEFINITIONS = [
    {'key': 'erste_bewerbung',    'label': '🎯 Erste Bewerbung',         'beschreibung': 'Du hast deine erste Bewerbung abgeschickt!'},
    {'key': 'zehn_bewerbungen',   'label': '🔥 10 Bewerbungen',          'beschreibung': '10 Bewerbungen abgeschickt – weiter so!'},
    {'key': 'fuenfzig_bewerbungen','label': '💪 50 Bewerbungen',         'beschreibung': 'Du bist ein Profi!'},
    {'key': 'erste_einladung',    'label': '📬 Erste Einladung',         'beschreibung': 'Du wurdest zum Gespraech eingeladen!'},
    {'key': 'erste_zusage',       'label': '🏆 Erste Zusage',            'beschreibung': 'Herzlichen Glueckwunsch zur Zusage!'},
    {'key': 'streak_3',           'label': '⚡ 3-Tage-Streak',           'beschreibung': '3 Tage in Folge beworben!'},
    {'key': 'streak_7',           'label': '🌟 7-Tage-Streak',           'beschreibung': '7 Tage in Folge – unglaublich!'},
    {'key': 'ki_anschreiben',     'label': '🤖 KI-Anschreiben',          'beschreibung': 'Erstes Anschreiben mit KI generiert'},
    {'key': 'lebenslauf_upload',  'label': '📄 Lebenslauf hochgeladen',  'beschreibung': 'Lebenslauf hochgeladen'},
    {'key': 'foto_upload',        'label': '📸 Foto-Upload',             'beschreibung': 'Erste Stelle per Foto angelegt'},
]

def _longest_daily_streak(dates: list[date]) -> int:
    """Laengste Folge aufeinanderfolgender Kalendertage in `dates`."""
    if not dates:
        return 0
    ordered = sorted(set(dates))
    longest = current = 1
    for prev, curr in zip(ordered, ordered[1:]):
        if (curr - prev).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


async def check_and_award(db: AsyncSession) -> list[dict]:
    """Prueft alle Bedingungen und vergibt fehlende Abzeichen."""
    awarded = []

    existing_result = await db.execute(select(UserBadge.badge_key))
    existing = {row[0] for row in existing_result.all()}

    app_count_result = await db.execute(select(func.count()).select_from(Application))
    app_count = app_count_result.scalar() or 0

    # Status-Vokabular des Projekts: interessant/beworben/interview/
    # angenommen/absage - die urspruenglichen Strings 'eingeladen'/'zusage'
    # existierten in diesem Schema nie, dadurch waren diese beiden
    # Abzeichen niemals erreichbar.
    invited_result = await db.execute(
        select(func.count()).select_from(Application).where(Application.status == 'interview')
    )
    invited_count = invited_result.scalar() or 0

    accepted_result = await db.execute(
        select(func.count()).select_from(Application).where(Application.status == 'angenommen')
    )
    accepted_count = accepted_result.scalar() or 0

    cover_letter_count = (await db.execute(select(func.count()).select_from(CoverLetter))).scalar() or 0
    cv_count = (await db.execute(select(func.count()).select_from(CVData))).scalar() or 0
    foto_job_count = (await db.execute(
        select(func.count()).select_from(Job).where(Job.source_portal == 'foto-upload')
    )).scalar() or 0

    created_dates_result = await db.execute(select(Application.created_at))
    streak = _longest_daily_streak([d.date() for (d,) in created_dates_result.all() if d])

    conditions = [
        ('erste_bewerbung',     app_count >= 1),
        ('zehn_bewerbungen',    app_count >= 10),
        ('fuenfzig_bewerbungen',app_count >= 50),
        ('erste_einladung',     invited_count >= 1),
        ('erste_zusage',        accepted_count >= 1),
        ('streak_3',            streak >= 3),
        ('streak_7',            streak >= 7),
        ('ki_anschreiben',      cover_letter_count >= 1),
        ('lebenslauf_upload',   cv_count >= 1),
        ('foto_upload',         foto_job_count >= 1),
    ]

    for key, condition in conditions:
        if condition and key not in existing:
            badge = UserBadge(badge_key=key, freigeschaltet_am=datetime.utcnow())
            db.add(badge)
            definition = next((b for b in BADGE_DEFINITIONS if b['key'] == key), {})
            awarded.append(definition)

    if awarded:
        await db.commit()
    return awarded

def all_badges_with_status(unlocked_keys: set[str]) -> list[dict]:
    return [
        {**b, 'freigeschaltet': b['key'] in unlocked_keys}
        for b in BADGE_DEFINITIONS
    ]
