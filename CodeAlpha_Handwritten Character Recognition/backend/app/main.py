from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .middleware import PrivateNoStoreMiddleware
from .routers import auth, profile, recognition, history, model_info

app=FastAPI(title="WriteLens API",version="1.0.0",description="Backend for WriteLens — See What You Write ✨")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_middleware(PrivateNoStoreMiddleware)
app.include_router(auth.router); app.include_router(profile.router); app.include_router(recognition.router); app.include_router(history.router); app.include_router(model_info.router)

@app.get("/api/health")
def health(): return {"status":"ok","app":"WriteLens"}
