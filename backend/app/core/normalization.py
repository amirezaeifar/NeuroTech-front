from __future__ import annotations

import re

from email_validator import EmailNotValidError, validate_email


def normalize_email(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    try:
        return validate_email(value.strip(), check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        raise ValueError("Invalid email address.") from exc


def normalize_phone(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    raw = value.strip()
    digits = re.sub(r"\D", "", raw)
    if raw.startswith("00"):
        normalized = f"+{digits[2:]}"
    elif raw.startswith("+"):
        normalized = f"+{digits}"
    elif digits.startswith("98") and len(digits) == 12:
        normalized = f"+{digits}"
    elif digits.startswith("09") and len(digits) == 11:
        normalized = f"+98{digits[1:]}"
    else:
        normalized = f"+{digits}"
    if not re.fullmatch(r"\+[1-9]\d{7,14}", normalized):
        raise ValueError("Invalid phone number.")
    return normalized


def normalize_destination(value: str) -> str:
    return normalize_email(value) if "@" in value else (normalize_phone(value) or "")
