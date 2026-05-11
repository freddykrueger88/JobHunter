from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://jobhunter:changeme@db:5432/jobhunter"
    SECRET_KEY: str = "changeme"
    ENCRYPTION_KEY: str = ""  # Fernet-Key – wird via setup.sh generiert
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    class Config:
        env_file = ".env"


settings = Settings()
