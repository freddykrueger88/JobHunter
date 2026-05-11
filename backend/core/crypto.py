from cryptography.fernet import Fernet
from backend.core.config import settings


def _get_fernet() -> Fernet:
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY ist nicht gesetzt. Bitte setup.sh ausführen.")
    return Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt(value: str) -> str:
    """Verschlüsselt einen Klartext-String (z.B. API-Key) für die DB."""
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    """Entschlüsselt einen verschlüsselten DB-Wert."""
    return _get_fernet().decrypt(value.encode()).decode()
