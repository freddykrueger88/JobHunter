"""#68 – E-Mail-Parsing Endpoints."""
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.services.email_parser import scan_mailbox, ParsedMail

router = APIRouter(prefix="/api/email", tags=["email-parsing"])

# In-Memory-Store für letzten Scan (kein DB-Zwang)
_last_scan: list[dict] = []
_last_config: dict = {}


class IMAPConfig(BaseModel):
    host: str = Field(..., example="imap.gmail.com")
    port: int = Field(993, example=993)
    username: str = Field(..., example="user@gmail.com")
    password: str = Field(..., example="app-password")
    folder: str = Field("INBOX", example="INBOX")
    limit: int = Field(50, ge=1, le=200)
    use_ssl: bool = True


@router.post("/connect")
async def test_connection(config: IMAPConfig):
    """Testet ob die IMAP-Verbindung funktioniert (kein Scan)."""
    import imaplib
    Imap = imaplib.IMAP4_SSL if config.use_ssl else imaplib.IMAP4
    conn = None
    try:
        conn = Imap(config.host, config.port)
        conn.login(config.username, config.password)
        return {"status": "ok", "message": "Verbindung erfolgreich"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verbindung fehlgeschlagen: {e}")
    finally:
        # Ohne finally blieb die Socket-Verbindung offen, sobald login()
        # fehlschlaegt (z.B. falsches Passwort) - conn.logout() stand
        # bisher nur nach einem erfolgreichen Login.
        if conn is not None:
            try:
                conn.logout()
            except Exception:
                pass


@router.post("/scan")
async def scan_emails(config: IMAPConfig):
    """Scannt das Postfach und gibt relevante Bewerbungs-E-Mails zurück."""
    global _last_scan, _last_config
    try:
        mails: list[ParsedMail] = await asyncio.to_thread(
            scan_mailbox,
            config.host, config.port, config.username, config.password,
            config.folder, config.limit, config.use_ssl,
        )
        _last_scan = [
            {
                "uid": m.uid,
                "sender": m.sender,
                "subject": m.subject,
                "date": m.date,
                "snippet": m.snippet,
                "status": m.status,
                "confidence": round(m.confidence, 2),
            }
            for m in mails
        ]
        _last_config = {"host": config.host, "username": config.username}
        return {"count": len(_last_scan), "results": _last_scan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_last_scan():
    """Gibt das Ergebnis des letzten Scans zurück."""
    return {
        "configured": bool(_last_config),
        "account": _last_config.get("username"),
        "count": len(_last_scan),
        "results": _last_scan,
    }
