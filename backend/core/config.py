from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Keine unsicheren Defaults fuer sicherheitsrelevante Werte: fehlen sie
    # in der Umgebung/.env, soll der Start hart fehlschlagen statt mit
    # schwachen Platzhaltern weiterzulaufen (Audit REPOSITORY_AUDIT_DE.md
    # 1.3/1.6, "changeme" als stiller Fallback).
    DATABASE_URL: str
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    class Config:
        env_file = ".env"

    @model_validator(mode="after")
    def _reject_placeholder_secrets(self) -> "Settings":
        placeholders = {
            "SECRET_KEY": ("changeme", "changeme_very_long_random_secret_key_here"),
            "ENCRYPTION_KEY": ("changeme", "changeme_fernet_key_here"),
        }
        for field, bad_values in placeholders.items():
            value = getattr(self, field)
            if not value or value in bad_values:
                raise ValueError(
                    f"{field} ist nicht gesetzt oder verwendet noch den "
                    f"Platzhalterwert aus .env.example. Bitte einen echten "
                    f"Wert generieren (siehe .env.example) und in .env eintragen."
                )
        return self


settings = Settings()
