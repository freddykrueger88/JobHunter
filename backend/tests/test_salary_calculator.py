"""
Tests fuer backend/services/salary_calculator.py + POST /api/salary/
calculate-netto.

Bugfix-Sweep 2026-08-27: der Service konnte gar nicht importiert werden -
`steuerklasse: SteuerklassE = 1` referenzierte einen Typo (korrekt:
`Steuerklasse`, der oben im Modul definierte Type-Alias). Jeder Import
des Moduls waere mit NameError gecrasht. Kein Router existierte
ausserdem ueberhaupt.
"""
from __future__ import annotations

import httpx
import pytest

pytestmark = pytest.mark.asyncio


class TestCalculateNetto:
    async def test_returns_plausible_net_salary(self, client: httpx.AsyncClient):
        res = await client.post("/api/salary/calculate-netto", json={
            "brutto_jaehrlich": 60000,
            "steuerklasse": 1,
            "hat_kinder": False,
        })

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["brutto_jaehrlich"] == 60000
        assert 0 < body["netto_monatlich"] < body["brutto_monatlich"]
        assert body["netto_jaehrlich"] == round(body["netto_monatlich"] * 12, 2)

    async def test_default_tax_class_is_one(self, client: httpx.AsyncClient):
        res = await client.post("/api/salary/calculate-netto", json={"brutto_jaehrlich": 50000})

        assert res.status_code == 200, res.text
        assert res.json()["steuerklasse"] == 1

    async def test_tax_class_three_yields_more_net_than_five(self, client: httpx.AsyncClient):
        res3 = await client.post("/api/salary/calculate-netto", json={
            "brutto_jaehrlich": 50000, "steuerklasse": 3,
        })
        res5 = await client.post("/api/salary/calculate-netto", json={
            "brutto_jaehrlich": 50000, "steuerklasse": 5,
        })

        assert res3.json()["netto_monatlich"] > res5.json()["netto_monatlich"]
