"""Branchen-Radar (#76, G.3.9): regionale Jobmarkt-Trends aus den
integrierten Portalen aggregiert.

Es gibt in diesem Projekt kein Branchen-Feld auf Job - die "Tags" aus
job_analyzer.py sind freie KI-Stichworte, kein Branchen-Schema, und nur
fuer Jobs gesetzt, bei denen der Nutzer die KI-Analyse manuell
angestossen hat (nicht alle). Eine KI-Klassifikation ueber alle Jobs
schied aus Performance-Gruenden aus: dieses Projekt laeuft CPU-only
Ollama (ai_client.py-Timeout musste schon auf 300s hochgesetzt werden,
~208s pro komplexem Prompt gemessen) - fuer hunderte Jobs bei jedem
Radar-Aufruf voellig unpraktikabel, selbst mit kurzen Prompts.

Deshalb: einfache mehrsprachige Substring-Keyword-Klassifikation
(gleiche Praezisions-Klasse wie die Benefit/Blacklist-Keyword-Filter
aus G.3.1/G.3.2 - kein NLP, dokumentierte Ungenauigkeit statt
False-Precision). Mehrsprachig deshalb, weil die tatsaechlichen Job-
Titel in diesem System aus EURES/Arbetsformedlingen/France Travail
kommen und ueberwiegend NICHT deutsch sind (live in der Produktions-DB
geprueft, 2026-08-28: von 135 gespeicherten Jobs war zum Zeitpunkt des
Baus praktisch jeder einzelne ein IT-Titel auf Deutsch/Franzoesisch/
Schwedisch - "Fachinformatiker", "Developpeur", "Utvecklare" etc.).
Branchen-Kategorien und Stichworte sind bewusst grob gehalten (12
Kategorien statt einer offiziellen Klassifikation wie WZ2008 - eine
echte amtliche Zuordnung waere ein eigenes Recherche-Projekt wie die
NUTS-Regionen bei EURES und fuer diese Groessenordnung unverhaeltnis-
maessig).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

# Reihenfolge = Prioritaet bei mehrdeutigen Titeln (erster Treffer gewinnt).
# Stichworte bewusst als Wortstaemme wo sinnvoll (z.B. "utveckl" statt nur
# "utvecklare"), damit auch Ableitungen wie "Systemutvecklare" oder
# "Webbutveckling" treffen - gleiches Substring-Prinzip wie die Benefit-
# Keyword-Filter aus G.3.1, keine echte Grammatikanalyse.
CATEGORIES: dict[str, list[str]] = {
    "IT & Software": [
        "informatik", "fachinformatiker", "softwareentwickl", "software-entwickl",
        "entwickler", "programmier", "systemintegration", "systemadministrator",
        "administrator", "sysadmin", "devops", "netzwerktechnik", "cloud",
        "data scientist", "data engineer", "frontend", "backend", "full-stack",
        "fullstack", "webentwickl", "it-support", "it support", "security",
        "cyber",
        "developer", "software", "programmer", "it engineer", "software engineer",
        "cloud engineer", "systems engineer",
        "développeur", "developpeur", "informatique", "ingénieur logiciel",
        "utveckl", "it-tekniker", "mjukvaru",
    ],
    "Gesundheit & Pflege": [
        "pflege", "altenpfleger", "krankenschwester", "krankenpfleger",
        "therapeut", "klinik", "reha", "gesundheits", "arzt", "ärztin", "mediz",
        # "care" bewusst NICHT als bare Substring - traf faelschlich auf
        # "career" (allgegenwaertig in Stellenbeschreibungen). Nur klar
        # abgegrenzte Pflege-Begriffe.
        "nurse", "healthcare", "physician", "medical", "elderly care",
        "patient care", "childcare",
        "infirmier", "médecin", "santé",
        "sjuksköterska", "vård", "läkare",
    ],
    "Handwerk & Bau": [
        "handwerk", "baustelle", "elektriker", "installateur", "tischler",
        "maurer", "dachdecker", "sanitär", "schreiner", "klempner",
        "electrician", "carpenter", "construction", "plumber",
        "électricien", "charpentier", "plombier",
        "elektriker", "snickare", "byggnad", "rörmokare",
    ],
    "Industrie & Produktion": [
        "produktion", "fertigung", "maschinenbau", "techniker", "montage",
        "cnc", "schweiß", "qualitätssicherung",
        "manufacturing", "production", "machinist", "assembly",
        "fabrication", "usinage",
        "tillverkning",
    ],
    "Handel & Verkauf": [
        "verkauf", "vertrieb", "einzelhandel", "kassierer", "filialleit",
        "verkäufer", "kundenberater",
        # "sales" bewusst NICHT als bare Substring - traf faelschlich auf
        # "Salesforce" (CRM-Plattform, IT-Kontext) in echten Produktions-
        # Daten. Nur klar abgegrenzte Verkaufs-Begriffe.
        "sales manager", "sales representative", "salesperson", "retail",
        "cashier", "store manager",
        "vente", "commercial", "magasin",
        "försäljning", "butik",
    ],
    "Logistik & Transport": [
        "logistik", "lager", "fahrer", "spedition", "transport", "kurier", "lkw",
        "logistics", "warehouse", "driver", "delivery",
        "logistique", "entrepôt", "chauffeur", "livraison",
        "chaufför",
    ],
    "Finanzen & Versicherung": [
        "versicherung", "finanz", "buchhalt", "controller", "steuerberat",
        "wirtschaftsprüf", "bank",
        "finance", "insurance", "accounting", "banking",
        "assurance", "comptabilité",
        "försäkring", "ekonomi",
    ],
    "Bildung & Soziales": [
        "lehrer", "erzieher", "sozialarbeit", "kita", "pädagog", "bildung",
        "teacher", "educator", "social work",
        "enseignant", "éducateur",
        "lärare", "pedagog", "socialarbetare",
    ],
    "Gastronomie & Tourismus": [
        "koch", "köchin", "kellner", "gastronomie", "tourismus", "restaurant",
        "chef", "waiter", "hotel", "tourism",
        "cuisinier", "serveur", "hôtel", "tourisme",
        "kock", "servitör", "turism",
    ],
    "Marketing & Medien": [
        "marketing", "redakteur", "medien", "kommunikation", "grafik", "content",
        "editor", "media", "communications", "design",
        "rédacteur", "médias", "communication",
        "marknadsföring", "redaktör",
    ],
    "Verwaltung & Öffentlicher Dienst": [
        "verwaltung", "sachbearbeit", "sekretariat", "assistenz", "behörde",
        "administration", "clerk", "government", "public service", "assistant",
        "secrétariat", "fonction publique",
        "förvaltning", "myndighet",
    ],
}
FALLBACK_CATEGORY = "Sonstige"


def classify_job(job: Job) -> str:
    """Ordnet einen Job anhand einfacher mehrsprachiger Stichwoerter einer
    groben Branche zu. Titel zuerst, Beschreibung nur als Fallback (die
    Beschreibung ist laenger und erhoeht das Risiko zufaelliger
    Fehltreffer)."""
    title_lower = (job.title or "").lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in title_lower for kw in keywords):
            return category

    description_lower = (job.description or "").lower()
    if description_lower:
        for category, keywords in CATEGORIES.items():
            if any(kw in description_lower for kw in keywords):
                return category

    return FALLBACK_CATEGORY


def _trend_label(change_pct: float | None) -> str:
    if change_pct is None:
        return "neu"
    if change_pct > 10:
        return "wachsend"
    if change_pct < -10:
        return "schrumpfend"
    return "stabil"


async def get_market_trends(
    db: AsyncSession,
    city: str | None = None,
    postal_code: str | None = None,
    days: int = 30,
) -> dict:
    """Vergleicht zwei aufeinanderfolgende Zeitfenster (je days/2 Tage)
    je Branche, um Wachstum/Schrumpfung sichtbar zu machen. Bezugsdatum:
    published_at (wann die Stelle tatsaechlich veroeffentlicht wurde) mit
    Fallback auf created_at (wann JobHunter sie gefunden hat) - gleiches
    Fallback-Prinzip wie applied_at/created_at bei den Bewerbungen."""
    q = select(Job)
    if city:
        q = q.where(Job.city.ilike(f"%{city}%"))
    if postal_code:
        q = q.where(Job.postal_code.ilike(f"%{postal_code}%"))
    result = await db.execute(q)
    jobs = result.scalars().all()

    now = datetime.now(timezone.utc)
    half = days / 2
    window_start = now - timedelta(days=days)
    mid = now - timedelta(days=half)

    counts_current: dict[str, int] = {}
    counts_previous: dict[str, int] = {}

    for job in jobs:
        bezugsdatum = job.published_at or job.created_at
        if bezugsdatum is None:
            continue
        if bezugsdatum.tzinfo is None:
            bezugsdatum = bezugsdatum.replace(tzinfo=timezone.utc)
        if bezugsdatum < window_start:
            continue

        category = classify_job(job)
        if bezugsdatum >= mid:
            counts_current[category] = counts_current.get(category, 0) + 1
        else:
            counts_previous[category] = counts_previous.get(category, 0) + 1

    all_categories = set(counts_current) | set(counts_previous)
    branchen = []
    for category in all_categories:
        aktuell = counts_current.get(category, 0)
        vorher = counts_previous.get(category, 0)
        if vorher == 0:
            change_pct = None if aktuell > 0 else 0.0
        else:
            change_pct = round((aktuell - vorher) / vorher * 100, 1)
        branchen.append({
            "branche": category,
            "aktuell": aktuell,
            "vorher": vorher,
            "veraenderung_prozent": change_pct,
            "trend": _trend_label(change_pct),
        })

    branchen.sort(key=lambda b: b["aktuell"], reverse=True)

    def _sort_key_wachsend(b: dict) -> tuple[int, float]:
        # "neu" (change_pct is None) zaehlt als staerkstes Wachstum ueberhaupt.
        if b["veraenderung_prozent"] is None:
            return (1, b["aktuell"])
        return (0, b["veraenderung_prozent"])

    wachsend_kandidaten = [b for b in branchen if b["trend"] in ("wachsend", "neu")]
    top_wachsend = sorted(wachsend_kandidaten, key=_sort_key_wachsend, reverse=True)[:5]

    schrumpfend_kandidaten = [b for b in branchen if b["trend"] == "schrumpfend"]
    top_schrumpfend = sorted(schrumpfend_kandidaten, key=lambda b: b["veraenderung_prozent"])[:5]

    return {
        "zeitraum_tage": days,
        "branchen": branchen,
        "top_wachsend": top_wachsend,
        "top_schrumpfend": top_schrumpfend,
    }
