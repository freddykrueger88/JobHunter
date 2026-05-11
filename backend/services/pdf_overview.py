"""PDF-Druckansicht der Bewerbungsuebersicht."""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, Job

async def generate_overview_html(db: AsyncSession, since: datetime | None = None, status: str | None = None) -> str:
    """Generiert HTML fuer weasyprint-PDF-Export."""
    query = select(Application, Job).join(Job, Application.job_id == Job.id, isouter=True)
    if since:
        query = query.where(Application.bewerbungsdatum >= since)
    if status:
        query = query.where(Application.status == status)
    query = query.order_by(Application.bewerbungsdatum.desc())

    result = await db.execute(query)
    rows = result.all()

    rows_html = ''
    for app, job in rows:
        datum = app.bewerbungsdatum.strftime('%d.%m.%Y') if app.bewerbungsdatum else '–'
        frist = job.bewerbungsfrist.strftime('%d.%m.%Y') if job and job.bewerbungsfrist else '–'
        rows_html += f"""
        <tr>
          <td>{datum}</td>
          <td>{job.firma if job else '–'}</td>
          <td>{job.titel if job else '–'}</td>
          <td>{app.status or '–'}</td>
          <td>{frist}</td>
          <td>{(app.notiz or '')[:80]}</td>
        </tr>"""

    return f"""
    <!DOCTYPE html><html lang="de"><head>
    <meta charset="UTF-8">
    <style>
      body {{ font-family: Arial, sans-serif; font-size: 11px; }}
      h1 {{ font-size: 16px; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th {{ background: #1d4ed8; color: white; padding: 6px; text-align: left; }}
      td {{ padding: 5px; border-bottom: 1px solid #e5e7eb; }}
      tr:nth-child(even) {{ background: #f9fafb; }}
    </style></head><body>
    <h1>JobHunter – Bewerbungsuebersicht</h1>
    <p>Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Gesamt: {len(rows)} Eintraege</p>
    <table>
      <thead><tr>
        <th>Datum</th><th>Firma</th><th>Stelle</th>
        <th>Status</th><th>Frist</th><th>Notiz</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table></body></html>"""
