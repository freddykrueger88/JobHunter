from pydantic import BaseModel


class InterviewQuestion(BaseModel):
    question: str
    category: str


class InterviewQuestionsResponse(BaseModel):
    job_id: int
    job_title: str
    questions: list[InterviewQuestion]


class AnswerEvaluationResponse(BaseModel):
    question: str
    answer: str
    score: int
    feedback: str
    tip: str
