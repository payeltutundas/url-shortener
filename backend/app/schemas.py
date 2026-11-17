"""Shapes of the data going in and out of the API."""
from datetime import datetime, timezone

from pydantic import BaseModel, field_validator

from app import validation


class LinkCreate(BaseModel):
    url: str
    alias: str | None = None
    expires_at: datetime | None = None

    @field_validator("url")
    @classmethod
    def check_url(cls, v):
        return validation.validate_url(v)

    @field_validator("alias")
    @classmethod
    def check_alias(cls, v):
        return validation.validate_alias(v)

    @field_validator("expires_at")
    @classmethod
    def check_expiry(cls, v):
        return validation.validate_expiry(v)


class LinkOut(BaseModel):
    code: str
    short_url: str
    original_url: str
    expires_at: datetime | None
    clicks: int
    created_at: datetime


class LinkListItem(LinkOut):
    status: str  # "active" or "expired"


def is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at <= datetime.now(timezone.utc)
