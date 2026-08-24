"""Fehlercode-Helfer fuer i18n-faehige Backend-Fehler (Rework-Plan Phase C.4,
docs/i18n/KONZEPT.md "Backend-Fehlertexte").

Statt HTTPException.detail von String auf ein verschachteltes Objekt
umzustellen (haette mehrere bereits migrierte Frontend-Aufrufstellen
gebrochen, die response.data.detail direkt als String verwenden), wird der
maschinenlesbare Fehlercode als HTTP-Header X-Error-Code mitgeschickt.
detail bleibt exakt wie bisher der deutsche Klartext - reine Ergaenzung,
kein Breaking Change.

Frontend: frontend/src/lib/api.ts liest den Header und uebersetzt ihn
ueber den common:errors-Namespace, falls dort ein Eintrag existiert, sonst
faellt es auf den deutschen Klartext aus detail zurueck.
"""
from fastapi import HTTPException


def api_error(status_code: int, error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=message,
        headers={"X-Error-Code": error_code},
    )
