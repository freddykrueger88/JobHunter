from pydantic import BaseModel


class ModelsResponse(BaseModel):
    models: list[str]


class ChatResponse(BaseModel):
    reply: str
    model: str


class CoverLetterResponse(BaseModel):
    id: int
    content: str
    tone: str
    model: str
