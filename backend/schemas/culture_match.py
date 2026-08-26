from pydantic import BaseModel


class CultureMatchResult(BaseModel):
    score: int
    unternehmenstyp_erkannt: str
    passende_punkte: list[str]
    abweichende_punkte: list[str]
    kurzfazit: str
