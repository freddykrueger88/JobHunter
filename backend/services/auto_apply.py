"""#63 – Auto-Apply ZIP: Anschreiben-PDF + CV-PDF + Metadaten-JSON als ZIP."""
import io
import json
import zipfile
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.application import Application
from backend.models.job import Job
from backend.models.cv import CVData
from backend.models.cover_letter import CoverLetter
from backend.api.cover_letter_pdf import _build_pdf


def _safe(s: str) -> str:
    """Dateiname-safe: Leerzeichen → Unterstrich, Sonderzeichen entfernen."""
    import re
    s = s.replace(" ", "_")
    return re.sub(r"[^\w\-]", "", s)


async def build_application_zip(application_id: int, db: AsyncSession) -> tuple[bytes, str]:
    """Erstellt ein ZIP-Archiv für eine Bewerbung. Gibt (bytes, filename) zurück."""
    app = await db.get(Application, application_id)
    if not app:
        raise ValueError(f"Bewerbung {application_id} nicht gefunden")

    job = await db.get(Job, app.job_id)
    company = job.company if job else "Unbekannt"
    title = job.title if job else "Stelle"
    today = date.today().strftime("%Y%m%d")
    zip_name = f"Bewerbung_{_safe(company)}_{_safe(title)}_{today}.zip"

    # Aktuellstes Anschreiben dieser Bewerbung
    cl_res = await db.execute(
        select(CoverLetter)
        .where(CoverLetter.application_id == application_id)
        .order_by(CoverLetter.id.desc())
        .limit(1)
    )
    cl = cl_res.scalar_one_or_none()

    # CV (neuestes)
    cv_res = await db.execute(
        select(CVData).order_by(CVData.uploaded_at.desc()).limit(1)
    )
    cv = cv_res.scalar_one_or_none()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Anschreiben-PDF
        if cl:
            sender_name = cv.full_name if cv else ""
            sender_address = cv.address if cv else ""
            pdf_bytes = _build_pdf(
                cl.content,
                sender_name=sender_name,
                sender_address=sender_address,
                company=company,
                job_title=title,
            )
            zf.writestr(f"Anschreiben_{_safe(company)}.pdf", pdf_bytes)

        # 2. Metadaten-JSON
        meta = {
            "bewerbung_id": app.id,
            "stelle": title,
            "firma": company,
            "status": app.status,
            "beworben_am": app.applied_at.isoformat() if app.applied_at else None,
            "erstellt_am": today,
            "anschreiben_vorhanden": cl is not None,
            "cv_vorhanden": cv is not None,
        }
        if job:
            meta["stellenbeschreibung_url"] = job.url or ""
            meta["ort"] = job.location or ""
            meta["kontakt"] = job.contact_person or ""
        zf.writestr("bewerbung_meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

        # 3. README
        readme = (
            f"Bewerbungsunterlagen\n"
            f"====================\n"
            f"Stelle: {title}\n"
            f"Firma:  {company}\n"
            f"Datum:  {date.today().strftime('%d.%m.%Y')}\n\n"
            f"Enthaltene Dateien:\n"
        )
        if cl:
            readme += f"  - Anschreiben_{_safe(company)}.pdf\n"
        readme += "  - bewerbung_meta.json\n"
        readme += "\nErstellt mit JobHunter (lokal, DSGVO-konform)\n"
        zf.writestr("README.txt", readme)

    buf.seek(0)
    return buf.read(), zip_name
