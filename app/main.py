from fastapi import FastAPI

from app.database import (
    Base, engine
)

from app.routes import (
    auth_routes,
    session_routes,
    tracking_routes
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Location Tracker",
)

app.include_router(auth_routes.router)
app.include_router(session_routes.router)
app.include_router(tracking_routes.router)

@app.get("/")
def health():
    return {"status": "running"}