"""#70 – Interview-Simulator API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.job import Job
from backend.models.settings import UserSettings
from backend.services.interview_simulator import generate_interview_questions, evaluate_answer
from backend.services.ai_client import get_ai_client
from backend.models.cv import CVData
from backend.schemas.interview import InterviewQuestionsResponse, AnswerEvaluationResponse
from backend.core.errors import api_error

router = APIRouter(prefix="/api/interview", tags=["Interview-Simulator"])


class EvaluateRequest(BaseModel):
    job_id: int
    question: str
    answer: str


@router.get("/questions/{job_id}", response_model=InterviewQuestionsResponse)
async def get_interview_questions(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise api_error(404, "interview.job_not_found", "Job nicht gefunden")
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"
    questions = await generate_interview_questions(
        job_title=job.title,
        job_description=job.description,
        model=model,
    )
    return {"job_id": job_id, "job_title": job.title, "questions": questions}


@router.post("/evaluate", response_model=AnswerEvaluationResponse)
async def evaluate_interview_answer(data: EvaluateRequest, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, data.job_id)
    if not job:
        raise api_error(404, "interview.job_not_found", "Job nicht gefunden")
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"
    evaluation = await evaluate_answer(
        question=data.question,
        answer=data.answer,
        job_title=job.title,
        model=model,
    )
    return {"question": data.question, "answer": data.answer, **evaluation}


@router.post("/prep/{job_id}")
async def get_interview_prep(
    job_id: int,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """Fragen + Musterantworten zur Vorbereitung (nutzt den zuletzt
    hochgeladenen Lebenslauf, falls vorhanden)."""
    from backend.services.interview_prep import generate_interview_prep

    job = await db.get(Job, job_id)
    if not job:
        raise api_error(404, "interview.job_not_found", "Job nicht gefunden")

    cv_result = await db.execute(select(CVData).order_by(CVData.uploaded_at.desc()).limit(1))
    cv = cv_result.scalar_one_or_none()
    cv_text = cv.raw_text if cv and cv.raw_text else ""

    return await generate_interview_prep(job_id, cv_text, db, ai_client)
