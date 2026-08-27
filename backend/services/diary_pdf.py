"""PDF-Export des Bewerbungs-Tagebuchs (#80, G.3.6).

Nutzt reportlab wie der bestehende Uebersichts-PDF-Export
(backend/services/pdf_overview.py) - kein neues Abhaengigkeitspaket.
Anders als die tabellarische Bewerbungsuebersicht sind Tagebucheintraege
freier Fliesstext, deshalb hier Absaetze statt einer Tabelle."""
from __future__ import annotations

import io
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import DiaryEntry


async def generate_diary_pdf(db: AsyncSession, search: str | None = None) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from xml.sax.saxutils import escape

    q = select(DiaryEntry).order_by(DiaryEntry.created_at.desc(), DiaryEntry.id.desc())
    if search:
        q = q.where(DiaryEntry.content.ilike(f"%{search}%"))
    result = await db.execute(q)
    entries = result.scalars().all()

    date_style = ParagraphStyle("Date", fontName="Helvetica-Bold", fontSize=10, textColor="#1d4ed8", spaceAfter=4)
    content_style = ParagraphStyle("Content", fontName="Helvetica", fontSize=10, leading=14, alignment=TA_LEFT)
    title_style = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=16)
    meta_style = ParagraphStyle("Meta", fontName="Helvetica", fontSize=9, textColor="#666666")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    story = [
        Paragraph("JobHunter – Bewerbungs-Tagebuch", title_style),
        Paragraph(
            f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Einträge: {len(entries)}"
            + (f" | Suche: \"{escape(search)}\"" if search else ""),
            meta_style,
        ),
        Spacer(1, 0.7 * cm),
    ]

    for entry in entries:
        datum = entry.created_at.strftime("%d.%m.%Y %H:%M") if entry.created_at else "–"
        story.append(Paragraph(datum, date_style))
        # Zeilenumbrueche im Freitext als <br/> erhalten, HTML-Sonderzeichen escapen
        text_html = escape(entry.content).replace("\n", "<br/>")
        story.append(Paragraph(text_html, content_style))
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="100%", color=colors.HexColor("#e5e7eb"), thickness=0.5))
        story.append(Spacer(1, 0.3 * cm))

    if not entries:
        story.append(Paragraph("Keine Einträge.", content_style))

    doc.build(story)
    buf.seek(0)
    return buf.read()
