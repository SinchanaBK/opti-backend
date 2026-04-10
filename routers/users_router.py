from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role
from schemas import UserCreate, UserUpdate, UserOut
from core.security import hash_password
from dependencies import RequirePrivilege

router = APIRouter(prefix="/users", tags=["Users"])
MANAGE = Depends(RequirePrivilege("manage:users"))

@router.get("/", response_model=List[UserOut], dependencies=[MANAGE])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{user_id}", response_model=UserOut, dependencies=[MANAGE])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserOut, status_code=201, dependencies=[MANAGE])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role: raise HTTPException(status_code=404, detail="Role not found")
    user = User(full_name=payload.full_name, email=payload.email,
                hashed_password=hash_password(payload.password), role_id=payload.role_id)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserOut, dependencies=[MANAGE])
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit(); db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=204, dependencies=[MANAGE])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    db.delete(user); db.commit()
