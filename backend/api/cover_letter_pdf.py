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
    """Erstellt ein DIN-5008-nahes PDF mit reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import datetime

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "Normal", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, leading=16, alignment=TA_LEFT,
    )
    small = ParagraphStyle(
        "Small", parent=normal, fontSize=9, textColor="#666666",
    )
    bold = ParagraphStyle(
        "Bold", parent=normal, fontName="Helvetica-Bold",
    )

    story = []

    # Absenderzeile
    if sender_name:
        story.append(Paragraph(sender_name, bold))
    if sender_address:
        story.append(Paragraph(sender_address.replace("\n", "<br/>"), small))
        story.append(Spacer(1, 0.5*cm))

    # Empfänger
    if company:
        story.append(Paragraph(company, normal))
        story.append(Paragraph("z. Hd. Personalabteilung", small))
        story.append(Spacer(1, 0.5*cm))

    # Datum
    story.append(Paragraph(datetime.date.today().strftime("%d.%m.%Y"), normal))
    story.append(Spacer(1, 0.3*cm))

    # Betreff
    if job_title:
        story.append(Paragraph(f"<b>Bewerbung als {job_title}</b>", normal))
        story.append(Spacer(1, 0.5*cm))

    # Fließtext (Zeilenumbrüche erhalten)
    for line in content.split("\n"):
        line = line.strip()
        story.append(Paragraph(line if line else "&nbsp;", normal))

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
