"""PDF-Druckansicht der Bewerbungsuebersicht.

Nutzt reportlab statt des urspruenglich vorgesehenen weasyprint - kein
neues schweres System-Abhaengigkeitspaket (Pango/Cairo/GTK) noetig,
reportlab wird im Projekt bereits fuer den Anschreiben-PDF-Export
genutzt (backend/api/cover_letter_pdf.py)."""
from datetime import datetime
import io

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models import Application, Job


async def generate_overview_pdf(
    db: AsyncSession,
    since: datetime | None = None,
    status: str | None = None,
) -> bytes:
    """Erstellt ein PDF mit einer Tabelle aller Bewerbungen."""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT

    query = select(Application, Job).join(Job, Application.job_id == Job.id, isouter=True)
    if since:
        query = query.where(Application.applied_at >= since)
    if status:
        query = query.where(Application.status == status)
    query = query.order_by(Application.applied_at.desc())

    result = await db.execute(query)
    rows = result.all()

    normal = ParagraphStyle("Normal", fontName="Helvetica", fontSize=8, leading=10, alignment=TA_LEFT)

    header = ["Datum", "Firma", "Stelle", "Status", "Notiz"]
    table_data = [header]
    for app, job in rows:
        datum = app.applied_at.strftime("%d.%m.%Y") if app.applied_at else "–"
        table_data.append([
            datum,
            Paragraph(job.company if job else "–", normal),
            Paragraph(job.title if job else "–", normal),
            app.status or "–",
            Paragraph((app.notes or "")[:80], normal),
        ])

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )

    title_style = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=16)
    meta_style = ParagraphStyle("Meta", fontName="Helvetica", fontSize=9, textColor="#666666")

    story = [
        Paragraph("JobHunter – Bewerbungsübersicht", title_style),
        Paragraph(
            f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Gesamt: {len(rows)} Einträge",
            meta_style,
        ),
        Spacer(1, 0.5 * cm),
    ]

    table = Table(table_data, colWidths=[2.2 * cm, 5 * cm, 6 * cm, 2.5 * cm, 8 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    doc.build(story)
    buf.seek(0)
    return buf.read()
