"""#68 – E-Mail-Parsing via IMAP (lokal, Opt-in, DSGVO-konform)."""
import imaplib
import email
import re
from email.header import decode_header
from dataclasses import dataclass, field
from typing import Literal

StatusType = Literal["absage", "einladung", "nachfrage", "unbekannt"]

# ── Erkennungs-Pattern ────────────────────────────────────────────────────────────
ABSAGE_PATTERNS = [
    r"leider.*nicht.*ber\u00fccksichtigen",
    r"haben.*uns.*f\u00fcr.*anderen.*kandidaten",
    r"absage", r"nicht.*einladen", r"bedauern.*mitteilen",
    r"we regret", r"not moving forward", r"not selected",
    r"unsuccessful", r"decided not to",
]
EINLADUNG_PATTERNS = [
    r"einladen.*gespr\u00e4ch", r"vorstellungsgespr\u00e4ch",
    r"interview.*einladung", r"invite.*interview",
    r"we.*like.*meet", r"pleased.*invite",
    r"termin.*vereinbaren", r"gespr\u00e4ch.*vereinbaren",
]
NACHFRAGE_PATTERNS = [
    r"r\u00fcckfrage", r"nachfrage", r"weitere.*informationen",
    r"k\u00f6nnen.*sie.*best\u00e4tigen", r"bitte.*r\u00fcckmeldung",
    r"could you.*confirm", r"additional.*information",
]


@dataclass
class ParsedMail:
    uid: str
    sender: str
    subject: str
    date: str
    snippet: str
    status: StatusType
    confidence: float  # 0.0 – 1.0
    raw_matches: list[str] = field(default_factory=list)


def _decode_str(value: str) -> str:
    parts = decode_header(value or "")
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def _classify(text: str) -> tuple[StatusType, float, list[str]]:
    text_lower = text.lower()
    matches: list[str] = []

    for p in ABSAGE_PATTERNS:
        if re.search(p, text_lower):
            matches.append(p)
    if matches:
        return "absage", min(0.6 + 0.1 * len(matches), 1.0), matches

    for p in EINLADUNG_PATTERNS:
        if re.search(p, text_lower):
            matches.append(p)
    if matches:
        return "einladung", min(0.6 + 0.1 * len(matches), 1.0), matches

    for p in NACHFRAGE_PATTERNS:
        if re.search(p, text_lower):
            matches.append(p)
    if matches:
        return "nachfrage", 0.6, matches

    return "unbekannt", 0.0, []


def _get_body(msg: email.message.Message) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return body[:2000]  # Nur erste 2000 Zeichen analysieren


def scan_mailbox(
    host: str,
    port: int,
    username: str,
    password: str,
    folder: str = "INBOX",
    limit: int = 50,
    use_ssl: bool = True,
) -> list[ParsedMail]:
    """Verbindet sich per IMAP, liest die letzten `limit` E-Mails
    und klassifiziert Bewerbungs-relevante Nachrichten."""
    results: list[ParsedMail] = []

    Imap = imaplib.IMAP4_SSL if use_ssl else imaplib.IMAP4
    conn = Imap(host, port)
    try:
        conn.login(username, password)
        conn.select(folder, readonly=True)

        _, data = conn.search(None, "ALL")
        uids = data[0].split()
        # Neueste zuerst
        uids = uids[-limit:][::-1]

        for uid in uids:
            _, msg_data = conn.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject = _decode_str(msg.get("Subject", ""))
            sender = _decode_str(msg.get("From", ""))
            date = msg.get("Date", "")
            body = _get_body(msg)

            combined = f"{subject} {body}"
            status, confidence, raw_matches = _classify(combined)

            if status == "unbekannt":
                continue  # Nur relevante Mails zurückgeben

            results.append(ParsedMail(
                uid=uid.decode(),
                sender=sender,
                subject=subject,
                date=date,
                snippet=body[:200].replace("\n", " ").strip(),
                status=status,
                confidence=confidence,
                raw_matches=raw_matches,
            ))
    finally:
        try:
            conn.logout()
        except Exception:
            pass

    return results
