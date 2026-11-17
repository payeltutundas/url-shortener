"""API routes for creating and listing links."""
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Link
from app.schemas import LinkCreate, LinkListItem, LinkOut, is_expired

router = APIRouter(prefix="/api")

CODE_CHARS = string.ascii_letters + string.digits
CODE_LENGTH = 7


def make_code() -> str:
    """7 random letters and digits."""
    return "".join(secrets.choice(CODE_CHARS) for _ in range(CODE_LENGTH))


def short_url_for(code: str) -> str:
    return get_settings().base_url.rstrip("/") + "/" + code


def to_out(link: Link) -> dict:
    return {
        "code": link.code,
        "short_url": short_url_for(link.code),
        "original_url": link.original_url,
        "expires_at": link.expires_at,
        "clicks": link.clicks,
        "created_at": link.created_at,
    }


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/links", response_model=LinkOut, status_code=201)
def create_link(data: LinkCreate, db: Session = Depends(get_db)):
    if data.alias:
        # Custom alias: if it is already used, tell the user
        link = Link(code=data.alias, original_url=data.url, expires_at=data.expires_at)
        db.add(link)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="That alias is already taken")
        return to_out(link)

    # Random code: try again if we hit a (very rare) duplicate
    for _ in range(10):
        link = Link(code=make_code(), original_url=data.url, expires_at=data.expires_at)
        db.add(link)
        try:
            db.commit()
            return to_out(link)
        except IntegrityError:
            db.rollback()
    raise HTTPException(status_code=500, detail="Could not create a short code, try again")


@router.get("/links", response_model=list[LinkListItem])
def list_links(db: Session = Depends(get_db)):
    links = db.scalars(select(Link).order_by(Link.created_at.desc(), Link.id.desc())).all()
    result = []
    for link in links:
        item = to_out(link)
        item["status"] = "expired" if is_expired(link.expires_at) else "active"
        result.append(item)
    return result
