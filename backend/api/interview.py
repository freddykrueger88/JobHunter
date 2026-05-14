"""#70 – Interview-Simulator API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.job import Job
from backend.models.settings import UserSettings
from backend.services.interview_simulator import generate_interview_questions, evaluate_answer

router = APIRouter(prefix="/interview", tags=["Interview-Simulator"])


class EvaluateRequest(BaseModel):
    job_id: int
    question: str
    answer: str


@router.get("/questions/{job_id}")
async def get_interview_questions(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"
    questions = await generate_interview_questions(
        job_title=job.title,
        job_description=job.description,
        model=model,
    )
    return {"job_id": job_id, "job_title": job.title, "questions": questions}


@router.post("/evaluate")
async def evaluate_interview_answer(data: EvaluateRequest, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, data.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
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
