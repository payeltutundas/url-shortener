"""Rules for URLs, aliases and expiry dates. Each function raises ValueError
with a message that is safe to show to the user."""
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.config import get_settings

MAX_URL_LENGTH = 2048
ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
RESERVED_ALIASES = {
    "api", "docs", "redoc", "openapi.json",
    "health", "static", "assets", "favicon.ico",
}

# Host names that all mean "this computer"
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _default_port(parsed) -> int | None:
    """Port in the URL, or the default one for http / https."""
    if parsed.port:
        return parsed.port
    return 443 if parsed.scheme.lower() == "https" else 80


def validate_url(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("URL is required")
    if len(value) > MAX_URL_LENGTH:
        raise ValueError(f"URL is too long (max {MAX_URL_LENGTH} characters)")
    try:
        parsed = urlparse(value)
        host = parsed.hostname
        this_port = _default_port(parsed)
    except ValueError:
        raise ValueError("URL is not valid")
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed")
    if not host:
        raise ValueError("URL must have a host name")

    # Block links that point back at this app (they would loop forever)
    own = urlparse(get_settings().base_url)
    own_host = (own.hostname or "").lower()
    same_port = this_port == _default_port(own)
    same_host = host.lower() == own_host
    # If the app runs on a loopback address, every loopback name on the
    # same port is the app itself (localhost, 127.0.0.1, ::1, 0.0.0.0)
    both_loopback = own_host in LOOPBACK_HOSTS and host.lower() in LOOPBACK_HOSTS
    if same_port and (same_host or both_loopback):
        raise ValueError("You cannot shorten a link that points to this service")
    return value


def validate_alias(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    if not ALIAS_PATTERN.match(value):
        raise ValueError(
            "Alias must be 3 to 32 characters: letters, numbers, - and _ only"
        )
    if value.lower() in RESERVED_ALIASES:
        raise ValueError("That alias is reserved")
    return value


def validate_expiry(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    # If no time zone was given, treat it as UTC
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    if value <= datetime.now(timezone.utc):
        raise ValueError("Expiry must be in the future")
    return value
