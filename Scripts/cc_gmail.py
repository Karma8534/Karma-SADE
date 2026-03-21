"""
CC Gmail utility — reads credentials from .gmail-cc-creds on P1.
Provides send_to_colby() and check_inbox() for autonomous use.

Credential file format (C:\\Users\\raest\\Documents\\Karma_SADE\\.gmail-cc-creds):
  address: paybackh1@gmail.com
  Name: CC Ascendant
  app_password: xxxx xxxx xxxx xxxx
"""
import imaplib
import smtplib
import email
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
from pathlib import Path

CREDS_FILE = Path(r"C:\Users\raest\Documents\Karma_SADE\.gmail-cc-creds")
COLBY_ADDRESS = "rae.steele76@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
IMAP_HOST = "imap.gmail.com"


def _load_creds() -> tuple[str, str]:
    """Load (address, app_password) from .gmail-cc-creds. Raises if missing."""
    if not CREDS_FILE.exists():
        raise FileNotFoundError(f"Credentials file not found: {CREDS_FILE}")
    creds = {}
    for line in CREDS_FILE.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            creds[key.strip().lower()] = val.strip()
    addr = creds.get("address", "")
    pwd  = creds.get("app_password", "")
    if not addr or not pwd:
        raise ValueError("Credentials file missing 'address' or 'app_password'")
    return addr, pwd


def send_to_colby(subject: str, body: str) -> dict:
    """
    Send an email from CC to Colby.
    Returns {"ok": True} or {"ok": False, "error": str}.
    """
    try:
        addr, pwd = _load_creds()
        msg = MIMEMultipart()
        msg["From"]    = f"CC Ascendant <{addr}>"
        msg["To"]      = COLBY_ADDRESS
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(addr, pwd)
            server.send_message(msg)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def check_inbox(limit: int = 10) -> list[dict]:
    """
    Fetch the most recent `limit` messages from CC's inbox.
    Returns list of {from, subject, date, body} dicts.
    """
    try:
        addr, pwd = _load_creds()
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(addr, pwd)
        mail.select("inbox")
        _, msgs = mail.search(None, "ALL")
        ids = msgs[0].split()[-limit:]
        results = []
        for mid in reversed(ids):
            _, data = mail.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            subj_raw = msg.get("Subject", "")
            subj, enc = decode_header(subj_raw)[0]
            if isinstance(subj, bytes):
                subj = subj.decode(enc or "utf-8")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8", errors="replace"
                        )
                        break
            else:
                raw = msg.get_payload(decode=True)
                if raw:
                    body = raw.decode(msg.get_content_charset() or "utf-8", errors="replace")
            results.append({
                "from":    msg.get("From", ""),
                "subject": subj,
                "date":    msg.get("Date", ""),
                "body":    body.strip(),
            })
        mail.logout()
        return results
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    # Quick self-test: check inbox
    msgs = check_inbox(5)
    for m in msgs:
        if "error" in m:
            print(f"ERROR: {m['error']}")
        else:
            print(f"From: {m['from']}\nSubject: {m['subject']}\nDate: {m['date']}\n")
