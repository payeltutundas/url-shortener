"""The public short link: GET /{code} sends the visitor to the original URL."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Link
from app.schemas import is_expired

router = APIRouter()


@router.get("/{code}")
def follow_link(code: str, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.code == code))
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    if is_expired(link.expires_at):
        raise HTTPException(status_code=410, detail="This link has expired")

    # Add 1 click inside the database in one step (safe with many visitors)
    db.execute(update(Link).where(Link.id == link.id).values(clicks=Link.clicks + 1))
    db.commit()
    return RedirectResponse(link.original_url, status_code=307)
