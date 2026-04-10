from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role
from schemas import LoginRequest, Token, UserCreate, UserOut
from core.security import verify_password, hash_password, create_access_token
from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer", user=user, permissions=user.permission_names)

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user = User(full_name=payload.full_name, email=payload.email,
                hashed_password=hash_password(payload.password), role_id=payload.role_id)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
