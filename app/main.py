from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_local_database
from app.routes import auth_routes, session_routes, tracking_routes


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_local_database()
    yield


app = FastAPI(
    title="Location Tracker",
    description="Secure, consent-based live location tracking API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "running"}


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_routes.router)
app.include_router(session_routes.router)
app.include_router(tracking_routes.router)
