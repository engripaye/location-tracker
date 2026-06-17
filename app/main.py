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
    title="Locaiton Tracker",
)