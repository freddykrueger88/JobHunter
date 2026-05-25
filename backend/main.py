from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import jobs, applications, settings, cv, ai, dashboard, history, reminders
from backend.api import export, interview, company, eures
from backend.api import calendar, company_dossier
from backend.routers import followups

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
app.include_router(company.router)
app.include_router(eures.router)
app.include_router(followups.router)
app.include_router(calendar.router)
app.include_router(company_dossier.router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": "1.9.0"}
