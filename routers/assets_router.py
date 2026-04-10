from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Asset, User
from schemas import AssetCreate, AssetUpdate, AssetOut
from dependencies import RequirePrivilege, get_current_user

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/", response_model=List[AssetOut], dependencies=[Depends(RequirePrivilege("view:inventory"))])
def list_all_assets(status: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Asset)
    if status:   q = q.filter(Asset.status == status)
    if category: q = q.filter(Asset.category == category)
    return q.all()

@router.get("/my", response_model=List[AssetOut], dependencies=[Depends(RequirePrivilege("view:my_gear"))])
def list_my_assets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Asset).filter(Asset.assigned_to_id == current_user.id).all()

@router.get("/{asset_id}", response_model=AssetOut, dependencies=[Depends(RequirePrivilege("view:inventory"))])
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset: raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.post("/", response_model=AssetOut, status_code=201, dependencies=[Depends(RequirePrivilege("create:asset"))])
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    if db.query(Asset).filter(Asset.asset_tag == payload.asset_tag).first():
        raise HTTPException(status_code=400, detail="Asset tag already exists")
    asset = Asset(**payload.model_dump())
    db.add(asset); db.commit(); db.refresh(asset)
    return asset

@router.put("/{asset_id}", response_model=AssetOut, dependencies=[Depends(RequirePrivilege("update:asset"))])
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset: raise HTTPException(status_code=404, detail="Asset not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(asset, field, value)
    db.commit(); db.refresh(asset)
    return asset

@router.delete("/{asset_id}", status_code=204, dependencies=[Depends(RequirePrivilege("delete:asset"))])
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset: raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset); db.commit()
