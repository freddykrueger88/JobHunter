from pydantic import BaseModel


class ProfileRead(BaseModel):
    ueber_mich: str | None
    kernkompetenzen: str | None
    wunschrolle: str | None
    erfahrungsjahre: int | None
    soft_skills: str | None
    arbeitsstil: str | None
    werte: str | None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    ueber_mich: str | None = None
    kernkompetenzen: str | None = None
    wunschrolle: str | None = None
    erfahrungsjahre: int | None = None
    soft_skills: str | None = None
    arbeitsstil: str | None = None
    werte: str | None = None
