from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import calendar, cover_letter_pdf, search_profiles
from backend.routers import (
    ai, applications, badges, blocklist, company_dossier, cover_letter_templates,
    cv, dashboard, diary, email_parsing, export, followups, history,
    interview, jobs, jobs_image, profile, reminders, salary, settings, stats,
)

app = FastAPI(
    title="JobHunter API",
    description="🎯 Lokaler KI-Bewerbungsassistent – DSGVO-konform, vollständig lokal",
    version="1.9.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(settings.router)
app.include_router(cv.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(history.router)
app.include_router(reminders.router)
app.include_router(export.router)
app.include_router(interview.router)
app.include_router(followups.router)
app.include_router(blocklist.router)
app.include_router(calendar.router)
app.include_router(company_dossier.router)
app.include_router(email_parsing.router)
app.include_router(cover_letter_templates.router)
app.include_router(profile.router)
app.include_router(cover_letter_pdf.router)
app.include_router(search_profiles.router)
app.include_router(jobs_image.router)
app.include_router(badges.router)
app.include_router(salary.router)
app.include_router(stats.router)
app.include_router(diary.router)


@app.on_event("startup")
async def start_scheduler():
    """Startet den APScheduler (Suchprofile, Erinnerungs-Mails, Backups) -
    war bisher nirgends aufgerufen, siehe scheduler.init_scheduler()."""
    from backend.services.scheduler import init_scheduler
    await init_scheduler()


@app.get("/health", tags=["System"])
async def health_check():
    from backend.services.scheduler import scheduler

    return {
        "status": "ok",
        "version": "1.9.0",
        "scheduler_running": scheduler.running,
        "scheduled_jobs": [j.id for j in scheduler.get_jobs()],
    }
