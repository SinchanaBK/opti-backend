from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload:
        raise exc
    user_id = payload.get("sub")
    if not user_id:
        raise exc
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise exc
    return user

class RequirePrivilege:
    def __init__(self, privilege: str):
        self.privilege = privilege

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_privilege(self.privilege):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required privilege: '{self.privilege}'"
            )
        return current_user
