"""PDF-Export für generierte Anschreiben."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.models.cover_letter import CoverLetter
from backend.models.application import Application
from backend.models.job import Job
from backend.models.cv import CVData
import io

router = APIRouter(prefix="/cover-letters", tags=["Anschreiben"])


def _build_pdf(content: str, sender_name: str = "", sender_address: str = "",
               company: str = "", job_title: str = "") -> bytes:
    """Erstellt ein DIN-5008-konformes PDF (Fassung März 2020) mit reportlab.

    Umgesetzte Vorgaben:
    - Seitenränder: 2,5cm links, 2cm rechts/oben/unten.
    - Anschriftfeld beginnt 45mm ab Blattoberkante (DIN 5008: 44,7mm
      allgemein, 62,7mm bei Fensterbriefumschlägen – hier der Normalwert).
    - Datum rechtsbündig.
    - Je 2 Leerzeilen zwischen Anschrift→Datum, Datum→Betreff, Betreff→Anrede;
      1 Leerzeile zwischen Anrede und Fließtext.
    - Betreff fett, ohne das Wort "Betreff:" (aktuelle Fassung seit 2011).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT, TA_RIGHT
    import datetime

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    normal = ParagraphStyle(
        "Normal", fontName="Helvetica", fontSize=11, leading=15.5, alignment=TA_LEFT,
    )
    right = ParagraphStyle("Right", parent=normal, alignment=TA_RIGHT)
    small = ParagraphStyle("Small", parent=normal, fontSize=9, textColor="#666666")

    blank_line = Spacer(1, normal.leading)
    story = []

    # Anschriftfeld beginnt 45mm ab Blattoberkante (DIN 5008); topMargin
    # deckt davon bereits 2cm ab, dazu kommt reportlabs Standard-Frame-
    # Padding von 6pt, der Rest wird per Spacer aufgefüllt.
    story.append(Spacer(1, 45*mm - doc.topMargin - 6))

    # Rücksendeangabe (kleine Absenderzeile über der Empfängeradresse)
    if sender_name:
        story.append(Paragraph(sender_name, small))
    if sender_address:
        story.append(Paragraph(sender_address.replace("\n", "<br/>"), small))

    # Empfänger
    if company:
        story.append(Paragraph(company, normal))
        story.append(Paragraph("z. Hd. Personalabteilung", normal))

    # 2 Leerzeilen zwischen Anschrift und Datum
    story.append(blank_line)
    story.append(blank_line)

    # Datum, rechtsbündig
    story.append(Paragraph(datetime.date.today().strftime("%d.%m.%Y"), right))

    # 2 Leerzeilen zwischen Datum und Betreff
    story.append(blank_line)
    story.append(blank_line)

    # Betreff (fett, ohne Präfix "Betreff:")
    if job_title:
        story.append(Paragraph(f"<b>Bewerbung als {job_title}</b>", normal))

    # 2 Leerzeilen zwischen Betreff und Anrede
    story.append(blank_line)
    story.append(blank_line)

    # Fließtext in Absätze gruppieren (durch Leerzeilen getrennte Blöcke).
    # Erster Block = Anrede, danach exakt 1 Leerzeile (DIN 5008), restliche
    # Absätze durch je 1 Leerzeile getrennt.
    raw_lines = [line.strip() for line in content.replace("\r\n", "\n").strip().split("\n")]
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in raw_lines:
        if line:
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    if not blocks:
        blocks = [[""]]

    for i, block in enumerate(blocks):
        for line in block:
            story.append(Paragraph(line, normal))
        if i < len(blocks) - 1:
            story.append(blank_line)

    doc.build(story)
    buf.seek(0)
    return buf.read()


@router.get("/{cl_id}/pdf")
async def download_pdf(cl_id: int, db: AsyncSession = Depends(get_db)):
    cl = await db.get(CoverLetter, cl_id)
    if not cl:
        raise HTTPException(status_code=404, detail="Anschreiben nicht gefunden")

    sender_name = ""
    sender_address = ""
    company = ""
    job_title = ""

    # Metadaten aus verknüpfter Bewerbung & Job holen
    if cl.application_id:
        app = await db.get(Application, cl.application_id)
        if app:
            job = await db.get(Job, app.job_id)
            if job:
                company = job.company or ""
                job_title = job.title or ""
            # CV-Daten für Absender
            cv_res = await db.execute(
                __import__("sqlalchemy", fromlist=["select"]).select(CVData).order_by(CVData.uploaded_at.desc()).limit(1)
            )
            cv = cv_res.scalar_one_or_none()
            if cv:
                sender_name = cv.full_name or ""
                sender_address = cv.address or ""

    pdf_bytes = _build_pdf(cl.content, sender_name, sender_address, company, job_title)
    filename = f"anschreiben_{cl_id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
