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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(assets_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Opti Asset Management API is running"}
