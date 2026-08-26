"""
Tests fuer backend/api/cover_letter_pdf.py::_build_pdf.

Regressionsschutz fuer die DIN-5008-Formatierung aus Backlog Phase K.5
(Nutzerwunsch: Anschreiben-PDF muss der DIN-5008-Norm fuer Geschaeftsbriefe
entsprechen - siehe docs/analysis/BACKLOG.md Phase K.5). Prueft die konkret
umgesetzten Vorgaben ueber echte Textkoordinaten im gerenderten PDF, nicht
nur "laeuft ohne Fehler durch".
"""
from __future__ import annotations

import io

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLineHorizontal

from backend.api.cover_letter_pdf import _build_pdf

MM_PER_PT = 25.4 / 72

_CONTENT = """Sehr geehrte Damen und Herren,

mit grossem Interesse habe ich Ihre Stellenanzeige gelesen.

Ich freue mich auf ein Gespraech.

Mit freundlichen Gruessen
Max Mustermann"""


def _render_lines() -> list[tuple[float, float, float, str]]:
    """Rendert ein Test-PDF und gibt (top_mm, left_mm, right_mm, text) je Zeile zurueck."""
    pdf_bytes = _build_pdf(
        _CONTENT,
        sender_name="Max Mustermann",
        sender_address="Musterstrasse 1\n12345 Musterstadt",
        company="Beispiel GmbH\nHauptstrasse 5\n54321 Beispielstadt",
        job_title="Softwareentwickler",
    )
    page = next(extract_pages(io.BytesIO(pdf_bytes)))
    lines = []
    for element in page:
        if isinstance(element, LTTextContainer):
            for line in element:
                if isinstance(line, LTTextLineHorizontal):
                    text = line.get_text().strip()
                    if not text:
                        continue
                    top_mm = (page.height - line.y1) * MM_PER_PT
                    left_mm = line.x0 * MM_PER_PT
                    right_mm = line.x1 * MM_PER_PT
                    lines.append((top_mm, left_mm, right_mm, text))
    return lines


class TestDin5008Layout:
    def test_address_field_starts_near_45mm_from_top(self):
        """DIN 5008: Anschriftfeld beginnt 44,7mm (hier: 45mm) ab Blattoberkante."""
        lines = _render_lines()
        first_line_top = lines[0][0]
        assert 44.0 <= first_line_top <= 47.0

    def test_left_margin_at_least_25mm(self):
        """DIN 5008: linker Seitenrand mindestens 2,5cm."""
        lines = _render_lines()
        assert all(left_mm >= 25.0 for _, left_mm, _, _ in lines)

    def test_date_is_right_aligned(self):
        """DIN 5008: Datum rechtsbuendig, nicht linksbuendig wie zuvor."""
        lines = _render_lines()
        date_lines = [l for l in lines if l[3].count(".") == 2 and l[3][:2].isdigit()]
        assert date_lines, "Datumszeile nicht im PDF gefunden"
        _, _, right_mm, _ = date_lines[0]
        # Rechter Rand liegt bei 210mm (A4) - 20mm (rightMargin) = 190mm.
        assert right_mm >= 180.0

    def test_two_blank_lines_before_subject(self):
        """DIN 5008: mind. 2 Leerzeilen zwischen Datum und Betreff."""
        lines = _render_lines()
        date_top = next(top for top, _, _, text in lines if text.count(".") == 2 and text[:2].isdigit())
        subject_top = next(top for top, _, _, text in lines if text.startswith("Bewerbung als"))
        line_height_mm = 15.5 * MM_PER_PT
        assert (subject_top - date_top) >= 2.5 * line_height_mm

    def test_one_blank_line_between_salutation_and_body(self):
        """DIN 5008: genau 1 Leerzeile zwischen Anrede und Fliesstext."""
        lines = _render_lines()
        salutation_top = next(top for top, _, _, text in lines if text.startswith("Sehr geehrte"))
        body_top = next(top for top, _, _, text in lines if text.startswith("mit grossem"))
        line_height_mm = 15.5 * MM_PER_PT
        gap = body_top - salutation_top
        assert 1.5 * line_height_mm <= gap <= 2.5 * line_height_mm
