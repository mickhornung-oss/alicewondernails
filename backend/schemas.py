from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from backend.models import INTEREST_OPTIONS, LEAD_STATUSES

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_INTEREST_ALIASES = {
    "haendler-/studiointeresse": "Händler-/Studiointeresse",
    "händler-/studiointeresse": "Händler-/Studiointeresse",
    "h?ndler-/studiointeresse": "Händler-/Studiointeresse",
}


class LeadCreateSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str
    privacy_accepted: bool
    one_time_notice_accepted: bool = False
    name: str | None = None
    interest: str | None = None
    message: str | None = None
    website: str | None = None  # Honeypot

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not _EMAIL_RE.match(value):
            raise ValueError("ungueltige E-Mail-Adresse")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return normalized[:120]

    @field_validator("interest")
    @classmethod
    def validate_interest(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if normalized in INTEREST_OPTIONS:
            return normalized

        lower = normalized.lower()
        alias = _INTEREST_ALIASES.get(lower)
        if alias is not None:
            return alias

        if normalized not in INTEREST_OPTIONS:
            raise ValueError("ungueltiger Interesse-Wert")
        return normalized

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return normalized[:4000]

    @field_validator("website")
    @classmethod
    def normalize_website(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_privacy(self) -> "LeadCreateSchema":
        if self.privacy_accepted is not True:
            raise ValueError("Datenschutz muss akzeptiert sein")
        return self


class AdminLoginSchema(BaseModel):
    username: str
    password: str
    csrf_token: str

    @field_validator("username", "password", "csrf_token")
    @classmethod
    def non_empty(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Pflichtfeld fehlt")
        return normalized


class AdminLeadUpdateSchema(BaseModel):
    status: str
    admin_note: str | None = None
    csrf_token: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in LEAD_STATUSES:
            raise ValueError("ungueltiger Status")
        return normalized

    @field_validator("admin_note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return normalized[:2000]

    @field_validator("csrf_token")
    @classmethod
    def csrf_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("ungueltiger CSRF-Token")
        return normalized


class AdminActionSchema(BaseModel):
    csrf_token: str
    anonymize_now: bool = False

    @field_validator("csrf_token")
    @classmethod
    def csrf_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("ungueltiger CSRF-Token")
        return normalized


class LeadResponseSchema(BaseModel):
    id: int
    created_at: str
    email: str
    name: str | None
    interest: str | None
    message: str | None
    privacy_accepted: bool
    one_time_notice_accepted: bool
    status: str
    admin_note: str | None
    notice_sent_at: str | None
    exported_at: str | None
    delete_after: str
    deleted_at: str | None


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "on", "ja", "y"}
