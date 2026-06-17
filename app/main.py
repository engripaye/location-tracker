from fastapi import FastAPI

from app.routes import auth_routes, session_routes, tracking_routes


app = FastAPI(
    title="Location Tracker",
    description="Secure, consent-based live location tracking API.",
    version="1.0.0",
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
