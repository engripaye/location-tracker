from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import auth_routes, session_routes, tracking_routes


settings = get_settings()

app = FastAPI(
    title="Location Tracker",
    description="Secure, consent-based live location tracking API.",
    version="1.0.0",
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
