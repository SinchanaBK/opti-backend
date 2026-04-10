from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class PermissionOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}

class RoleOut(BaseModel):
    id: int
    name: str
    permissions: List[PermissionOut] = []
    model_config = {"from_attributes": True}

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    is_active: bool
    created_at: datetime
    role: RoleOut
    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role_id: int

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    permissions: List[str]

class AssetBase(BaseModel):
    name: str
    asset_tag: str
    category: str
    status: str = "available"
    value: float = 0.0
    description: Optional[str] = None

class AssetCreate(AssetBase):
    assigned_to_id: Optional[int] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = None
    description: Optional[str] = None
    assigned_to_id: Optional[int] = None

class AssetOut(AssetBase):
    id: int
    created_at: datetime
    assigned_to_id: Optional[int] = None
    assigned_user: Optional[UserOut] = None
    model_config = {"from_attributes": True}

class DashboardStats(BaseModel):
    total_assets: int
    assigned_assets: int
    available_assets: int
    retired_assets: int
    total_users: int
    total_value: float
