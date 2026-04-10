from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, Float
from sqlalchemy.orm import relationship
from database import Base

role_permissions = Table(
    "role_permissions", Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

class Permission(Base):
    __tablename__ = "permissions"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    roles       = relationship("Role", secondary=role_permissions, back_populates="permissions")

class Role(Base):
    __tablename__ = "roles"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), unique=True, nullable=False)
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users       = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    full_name       = Column(String(150), nullable=False)
    email           = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    role_id         = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role            = relationship("Role", back_populates="users")
    assets          = relationship("Asset", back_populates="assigned_user")

    def has_privilege(self, privilege: str) -> bool:
        return any(p.name == privilege for p in self.role.permissions)

    @property
    def permission_names(self) -> list[str]:
        return [p.name for p in self.role.permissions]

class Asset(Base):
    __tablename__ = "assets"
    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(150), nullable=False)
    asset_tag      = Column(String(50), unique=True, nullable=False)
    category       = Column(String(100), nullable=False)
    status         = Column(String(50), default="available")
    value          = Column(Float, default=0.0)
    description    = Column(Text, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    assigned_user  = relationship("User", back_populates="assets")
