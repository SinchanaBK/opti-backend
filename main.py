import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth_router, assets_router, users_router, dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Opti Asset Management API",
    description="RBAC-powered asset management system",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
_env_origins = os.getenv("ALLOWED_ORIGINS", "")
_extra = [o.strip() for o in _env_origins.split(",") if o.strip()]

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://opti-frontend-7z18xauv6-sinchanabk13-5254s-projects.vercel.app",  # ← YOUR VERCEL URL
    *_extra,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                                          # ← exact URLs
    allow_origin_regex=r"https://opti-frontend.*\.vercel\.app",    # ← all preview URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=600,
)

app.include_router(auth_router.router)
app.include_router(assets_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Opti Asset Management API is running"}
