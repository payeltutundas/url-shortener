"""App entry point. Run it with uvicorn (see README.md for the exact command)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_tables
from app.routes import links, redirect


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: make sure the tables exist
    create_tables()
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)

# Only the front end's address may call the API from a browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().frontend_origin],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(links.router)
# The redirect route must come last because "/{code}" matches almost anything
app.include_router(redirect.router)
