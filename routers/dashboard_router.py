from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Asset
from schemas import DashboardStats
from dependencies import RequirePrivilege

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats, dependencies=[Depends(RequirePrivilege("view:inventory"))])
def get_stats(db: Session = Depends(get_db)):
    return DashboardStats(
        total_assets    = db.query(func.count(Asset.id)).scalar(),
        assigned_assets = db.query(func.count(Asset.id)).filter(Asset.status == "assigned").scalar(),
        available_assets= db.query(func.count(Asset.id)).filter(Asset.status == "available").scalar(),
        retired_assets  = db.query(func.count(Asset.id)).filter(Asset.status == "retired").scalar(),
        total_users     = db.query(func.count(User.id)).scalar(),
        total_value     = db.query(func.sum(Asset.value)).scalar() or 0.0,
    )
