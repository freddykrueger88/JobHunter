"""Netto-Brutto-Rechner fuer Deutschland (vereinfacht, Steuerklassen 1-6).

Keine externen API-Calls, vollstaendig lokal berechnet.
Basis: Steuerjahr 2025, gesetzliche KV/PV/RV/AV-Saetze.
"""
from dataclasses import dataclass
from typing import Literal

Steuerklasse = Literal[1, 2, 3, 4, 5, 6]

# Sozialversicherung 2025 (AN-Anteil)
KV_SATZ = 0.073      # Krankenversicherung Basisbeitrag AN
PV_SATZ = 0.018      # Pflegeversicherung AN (ohne Kinder, +0.6%)
RV_SATZ = 0.093      # Rentenversicherung AN
AV_SATZ = 0.013      # Arbeitslosenversicherung AN
BBG_KV  = 66150      # Beitragsbemessungsgrenze KV/PV (jaehrlich)
BBG_RV  = 90600      # Beitragsbemessungsgrenze RV/AV (jaehrlich)

# Pauschal-Lohnsteuer-Approximation nach Steuerklasse (vereinfacht)
STEUER_FAKTOR = {
    1: 0.20, 2: 0.18, 3: 0.12,
    4: 0.20, 5: 0.30, 6: 0.35,
}

@dataclass
class NettoErgebnis:
    brutto_jaehrlich: float
    brutto_monatlich: float
    netto_monatlich: float
    netto_jaehrlich: float
    sv_monatlich: float
    lohnsteuer_monatlich: float
    steuerklasse: int

def berechne_netto(
    brutto_jaehrlich: float,
    steuerklasse: Steuerklasse = 1,
    hat_kinder: bool = False,
) -> NettoErgebnis:
    brutto_m = brutto_jaehrlich / 12

    # Sozialversicherung
    kv = min(brutto_jaehrlich, BBG_KV) / 12 * KV_SATZ
    pv_satz = PV_SATZ if hat_kinder else PV_SATZ + 0.006
    pv = min(brutto_jaehrlich, BBG_KV) / 12 * pv_satz
    rv = min(brutto_jaehrlich, BBG_RV) / 12 * RV_SATZ
    av = min(brutto_jaehrlich, BBG_RV) / 12 * AV_SATZ
    sv_m = kv + pv + rv + av

    # Lohnsteuer (vereinfacht)
    lst_m = brutto_m * STEUER_FAKTOR.get(steuerklasse, 0.20)

    netto_m = brutto_m - sv_m - lst_m

    return NettoErgebnis(
        brutto_jaehrlich=round(brutto_jaehrlich, 2),
        brutto_monatlich=round(brutto_m, 2),
        netto_monatlich=round(netto_m, 2),
        netto_jaehrlich=round(netto_m * 12, 2),
        sv_monatlich=round(sv_m, 2),
        lohnsteuer_monatlich=round(lst_m, 2),
        steuerklasse=steuerklasse,
    )
