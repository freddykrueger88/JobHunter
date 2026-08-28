"""#71 – Firmen-Dossier: öffentliche Infos zur Zielfirma aggregieren."""
import httpx
import re
from urllib.parse import quote

_CACHE: dict[str, dict] = {}  # In-Memory-Cache (pro Prozess-Laufzeit)


async def fetch_company_dossier(company_name: str) -> dict:
    """Sammelt öffentliche Daten via Wikipedia-API + Open Corporates Hint."""
    if company_name in _CACHE:
        return _CACHE[company_name]

    result = {
        "company": company_name,
        "description": None,
        "founded": None,
        "employees": None,
        "industry": None,
        "headquarters": None,
        "website": None,
        "wikipedia_url": None,
        "logo_url": None,
        "warning": None,
        "source": "Wikipedia (lokal gecacht)",
        # Kununu/Glassdoor bieten keine kostenlose oeffentliche API (Stand
        # 2026-08-28, live recherchiert) - Glassdoor seit 2024 nur noch
        # Enterprise-Vertraege, Kununu nur ueber kostenpflichtige
        # Dritt-Scraper, die selbst gegen deren ToS verstossen. Statt einen
        # ungeprueften internen Such-Parameter dieser Portale zu raten (mit
        # dem Risiko eines still leeren Ergebnisses wie zuvor bei
        # Karriere.NRWs `ort`), verlinken wir ueber Googles `site:`-Suche -
        # syntaktisch garantiert korrekt, kein Scraping, keine Kosten.
        "kununu_search_url": f"https://www.google.com/search?q={quote('site:kununu.com ' + company_name)}",
        "glassdoor_search_url": f"https://www.google.com/search?q={quote('site:glassdoor.com ' + company_name)}",
    }

    try:
        # Wikimedia verlangt seit 2026 einen identifizierenden User-Agent
        # (https://w.wiki/4wJS) - ohne ihn kommt ein 403 mit HTML-Body statt
        # JSON zurueck, was .json() als generischen Fehler tarnte.
        headers = {"User-Agent": "JobHunter/1.0 (https://github.com/freddykrueger88/JobHunter; self-hosted job tracker)"}
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            # Wikipedia-Suche (DE zuerst, dann EN)
            for lang in ("de", "en"):
                search_url = (
                    f"https://{lang}.wikipedia.org/w/api.php"
                    f"?action=query&list=search&srsearch={quote(company_name)}"
                    f"&format=json&srlimit=1"
                )
                sr = await client.get(search_url)
                hits = sr.json().get("query", {}).get("search", [])
                if not hits:
                    continue

                page_title = hits[0]["title"]
                extract_url = (
                    f"https://{lang}.wikipedia.org/w/api.php"
                    f"?action=query&prop=extracts|pageimages|info"
                    f"&exintro=true&explaintext=true&pithumbsize=200"
                    f"&inprop=url&titles={quote(page_title)}&format=json"
                )
                er = await client.get(extract_url)
                pages = er.json().get("query", {}).get("pages", {})
                page = next(iter(pages.values()), {})

                extract = page.get("extract", "")
                if extract:
                    # Erste 3 Sätze
                    sentences = re.split(r"(?<=[.!?])\s+", extract.strip())
                    result["description"] = " ".join(sentences[:3])

                thumb = page.get("thumbnail", {}).get("source")
                if thumb:
                    result["logo_url"] = thumb

                result["wikipedia_url"] = page.get("fullurl")

                # Gründungsjahr aus Text extrahieren
                year_match = re.search(r"gegründet\s+(\d{4})|founded\s+in\s+(\d{4})", extract, re.IGNORECASE)
                if year_match:
                    result["founded"] = year_match.group(1) or year_match.group(2)

                # Mitarbeiterzahl
                emp_match = re.search(r"(\d[\d\.,]+)\s+(Mitarbeiter|employees|Beschäftigte)", extract, re.IGNORECASE)
                if emp_match:
                    result["employees"] = emp_match.group(1)

                break  # Erster Treffer genügt

            # Clearbit Logo als Fallback
            if not result["logo_url"]:
                domain_guess = company_name.lower().replace(" ", "") + ".com"
                result["logo_url"] = f"https://logo.clearbit.com/{domain_guess}"

    except Exception as e:
        # Nicht cachen: ein transienter Netzwerkfehler wuerde sonst fuer
        # die gesamte Prozesslaufzeit als "Ergebnis" fuer diese Firma
        # zurueckgegeben, ununterscheidbar von einer echten Recherche.
        result["description"] = f"Recherche fehlgeschlagen: {e}"
        return result

    _CACHE[company_name] = result
    return result
