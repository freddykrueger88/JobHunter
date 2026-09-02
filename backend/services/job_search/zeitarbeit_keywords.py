"""
Begriffsliste zur Erkennung von Zeitarbeitsfirmen und privaten
Arbeitsvermittlern (auf Nutzerwunsch, 2026-09-02) - wird von
GET /api/jobs/ genutzt, um solche Stellen standardmaessig auszublenden.

Zwei Kategorien:
- STRUKTUR_BEGRIFFE: generische Begriffe, die auf die Geschaeftsform
  hindeuten (stehen haeufig direkt im Firmennamen, z.B.
  "XYZ Personaldienstleistungen GmbH").
- BEKANNTE_ANBIETER: Namen grosser, bekannter deutscher/internationaler
  Zeitarbeits- und Personalvermittlungsfirmen, die nicht zwingend einen
  der Strukturbegriffe im Namen tragen (z.B. "Randstad", "Hays").

Reiner Substring-Abgleich (case-insensitive) gegen den Firmennamen -
wie jeder andere Keyword-Filter in diesem Projekt (siehe
backend/routers/blocklist.py) kein NLP, daher unvermeidlich unvollstaendig:
erkennt keine neuen/kleinen Anbieter ohne einschlaegigen Namen. Wird
regelmaessig erweiterbar sein, sollte der Nutzer weitere Anbieter melden.
"""

STRUKTUR_BEGRIFFE: list[str] = [
    "zeitarbeit",
    "leiharbeit",
    "arbeitnehmerüberlassung",
    "arbeitnehmerueberlassung",
    "personaldienstleist",
    "personalvermittlung",
    "personalvermittler",
    "arbeitsvermittlung",
    "arbeitsvermittler",
    "stellenvermittlung",
    "personalservice",
    "personal-service",
    "personalleasing",
    "zeitpersonal",
    "personalberatung",
    "bemanning",  # schwedisch fuer "Zeitarbeit/Personaleinsatz" (Arbetsformedlingen-Quelle)
]

BEKANNTE_ANBIETER: list[str] = [
    "randstad",
    "adecco",
    "manpower",
    "hays",
    "dis ag",
    "tempton",
    "trenkwalder",
    "persona service",
    "piening",
    "orizon",
    "amadeus fire",
    "unique personalservice",
    "aktiv personal",
    "arwa personaldienstleistungen",
    "bindan",
    "pink personalmanagement",
    "timepartner",
    "avitea",
    "hofmann personal",
    "i.k. hofmann",
    "kelly services",
    "expertum",
    "impuls personal",
    "tuja",
    "gis personaldienstleistungen",
    "papp personal",
    "plana personal",
    "robert half",
    "academic work",
    "studitemps",
    "alphaconsult",
    "jobactive",
    "jobtimum",
    "neo temp",
    "onepartnergroup",
    "michael page",
]

ZEITARBEIT_KEYWORDS: list[str] = STRUKTUR_BEGRIFFE + BEKANNTE_ANBIETER
