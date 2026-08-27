"""Ghost-Job-Erkennung: Erkennt veraltete oder fiktive Stellenanzeigen."""
from __future__ import annotations
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

# Typische Boilerplate-Phrasen in Ghost Jobs
BOILERPLATE_PHRASES = [
    r'wir sind ein dynamisches team',
    r'wir bieten ihnen eine herausfordernde',
    r'join our growing team',
    r'competitive salary',
    r'we are looking for a motivated',
    r'einsenden ihrer vollst.ndigen unterlagen',
    r'ihre aufgaben umfassen unter anderem',
    r'nach absprache',
    r'je nach qualifikation',
]

WEIGHTS = {
    'alter':           35,  # Anzeige > 30 Tage alt
    'kein_name':       20,  # Kein Ansprechpartner genannt
    'kein_gehalt':     15,  # Keine Gehaltsspanne
    'boilerplate':     20,  # Generische Floskeln
    'kurze_beschr':    10,  # Beschreibung < 150 Woerter
}


def detect_ghost_job(
    beschreibung: str,
    veroeffentlicht: Optional[datetime] = None,
    kontakt_name: Optional[str] = None,
    gehalt_min: Optional[float] = None,
    gehalt_max: Optional[float] = None,
) -> dict:
    """Berechnet Ghost-Job-Wahrscheinlichkeit (0-100)."""
    score = 0
    gruende = []

    # 1. Alter
    if veroeffentlicht:
        # veroeffentlicht kommt aus einer timezone-aware DB-Spalte -
        # datetime.utcnow() ist naiv und wuerde die Subtraktion mit
        # "can't subtract offset-naive and offset-aware datetimes" crashen.
        now = datetime.now(timezone.utc)
        vgl = veroeffentlicht if veroeffentlicht.tzinfo else veroeffentlicht.replace(tzinfo=timezone.utc)
        alter = (now - vgl).days
        if alter > 30:
            score += WEIGHTS['alter']
            gruende.append(f'Anzeige ist {alter} Tage alt (>30 Tage)')
    else:
        score += WEIGHTS['alter'] // 2  # kein Datum = halb so schlimm
        gruende.append('Kein Veroeffentlichungsdatum angegeben')

    # 2. Kein Ansprechpartner
    if not kontakt_name or kontakt_name.lower() in ('hr', 'personal', 'recruiting', 'team'):
        score += WEIGHTS['kein_name']
        gruende.append('Kein konkreter Ansprechpartner angegeben')

    # 3. Keine Gehaltsspanne
    if not gehalt_min and not gehalt_max:
        gehalt_in_text = bool(re.search(
            r'(\d{2,3}\.?\d{0,3}\s*€|gehalt|salary|vhb|nach.absprache)',
            beschreibung, re.IGNORECASE
        ))
        if not gehalt_in_text:
            score += WEIGHTS['kein_gehalt']
            gruende.append('Keine Gehaltsinformation')

    # 4. Boilerplate
    bp_count = sum(
        1 for phrase in BOILERPLATE_PHRASES
        if re.search(phrase, beschreibung, re.IGNORECASE)
    )
    if bp_count >= 2:
        score += WEIGHTS['boilerplate']
        gruende.append(f'{bp_count} generische Floskeln erkannt')
    elif bp_count == 1:
        score += WEIGHTS['boilerplate'] // 2

    # 5. Kurze Beschreibung
    wortanzahl = len(beschreibung.split())
    if wortanzahl < 150:
        score += WEIGHTS['kurze_beschr']
        gruende.append(f'Sehr kurze Beschreibung ({wortanzahl} Woerter)')

    score = min(score, 100)

    return {
        'ghost_score': score,
        'ist_ghost_job': score >= 55,
        'wahrscheinlichkeit': 'hoch' if score >= 70 else 'mittel' if score >= 45 else 'niedrig',
        'gruende': gruende,
    }
