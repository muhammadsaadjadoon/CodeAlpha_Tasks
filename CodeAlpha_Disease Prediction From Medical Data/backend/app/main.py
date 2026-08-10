from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth, health, model_info, prediction


settings = get_settings()
app = FastAPI(
    title="HeartTrack API",
    version="1.0.0",
    description="Heart risk prediction API for HeartTrack.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(prediction.router, prefix="/api")
app.include_router(model_info.router, prefix="/api")


@app.get("/")
def root():
    return {"name": "HeartTrack API", "docs": "/docs", "health": "/api/health"}
