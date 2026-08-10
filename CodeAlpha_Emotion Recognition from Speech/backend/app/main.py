from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from app.api import analysis, auth, health, profile
from app.config import settings
from app.services.inference import inference_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    inference_service.load()
    yield


app = FastAPI(title="INFLECT API", version="1.0.0", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list + ["testserver"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


def _apply_private_response_headers(response):
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.middleware("http")
async def origin_guard(request: Request, call_next):
    if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
        origin = request.headers.get("origin")
        if origin and origin != settings.frontend_origin:
            response = JSONResponse(status_code=403, content={"detail": "Request origin is not permitted."})
            return _apply_private_response_headers(response)

    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        _apply_private_response_headers(response)
    return response

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(analysis.router)
