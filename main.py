import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routers import auth_router, assets_router, users_router, dashboard_router

Base.metadata.create_all(bind=engine)

def auto_seed():
    from models import Permission, Role, User, Asset
    from core.security import hash_password
    db = SessionLocal()
    try:
        if db.query(User).first():
            return
        print("🌱 Seeding database...")
        PERMS = [
            ("view:inventory","View all assets"),("view:my_gear","View own assets"),
            ("create:asset","Add assets"),("update:asset","Edit assets"),
            ("delete:asset","Remove assets"),("manage:users","Manage users"),
        ]
        perms = {}
        for name, desc in PERMS:
            p = Permission(name=name, description=desc)
            db.add(p); db.flush(); perms[name] = p

        admin_role = Role(name="Admin")
        db.add(admin_role); db.flush()
        admin_role.permissions = list(perms.values())

        emp_role = Role(name="Employee")
        db.add(emp_role); db.flush()
        emp_role.permissions = [perms["view:my_gear"]]
        db.commit()

        USERS = [
            ("Opti Admin","admin@opti.com","admin123",admin_role.id),
            ("John","john@opti.com","john123",emp_role.id),
            ("Akash","akash@opti.com","akash123",emp_role.id),
            
        ]
        user_map = {}
        for full_name, email, pwd, role_id in USERS:
            u = User(full_name=full_name, email=email,
                     hashed_password=hash_password(pwd), role_id=role_id)
            db.add(u); db.flush(); user_map[email] = u
        db.commit()

        ASSETS = [
            ('MacBook Pro 14"','OPTI-001','Laptop','assigned',2499.99,user_map['alice@opti.com'].id),
            ('Dell XPS 15','OPTI-002','Laptop','assigned',1899.00,user_map['bob@opti.com'].id),
            ('LG UltraWide 34"','OPTI-003','Monitor','available',699.00,None),
            ('iPhone 15 Pro','OPTI-004','Phone','assigned',999.00,user_map['carol@opti.com'].id),
            ('Logitech MX Keys','OPTI-005','Keyboard','available',109.99,None),
            ('Sony WH-1000XM5','OPTI-006','Headset','assigned',349.99,user_map['alice@opti.com'].id),
            ('Standing Desk','OPTI-007','Furniture','available',799.00,None),
            ('Cisco IP Phone','OPTI-008','Phone','retired',149.99,None),
            ('Samsung 27" 4K','OPTI-009','Monitor','assigned',549.00,user_map['bob@opti.com'].id),
            ('Ergonomic Chair','OPTI-010','Furniture','available',599.00,None),
        ]
        for name, tag, cat, status, value, uid in ASSETS:
            db.add(Asset(name=name, asset_tag=tag, category=cat,
                         status=status, value=value, assigned_to_id=uid))
        db.commit()
        print("✅ Seeded!  admin@opti.com / admin123")
    except Exception as e:
        db.rollback(); print(f"⚠️ Seed error: {e}")
    finally:
        db.close()

auto_seed()

app = FastAPI(
    title="Opti Asset Management API",
    version="1.0.0",
)

_env_origins = os.getenv("ALLOWED_ORIGINS", "")
_extra = [o.strip() for o in _env_origins.split(",") if o.strip()]

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://opti-frontend-7z18xauv6-sinchanabk13-5254s-projects.vercel.app",
    *_extra,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://opti-frontend.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin",
                   "X-Requested-With", "Access-Control-Request-Method",
                   "Access-Control-Request-Headers"],
    expose_headers=["Authorization"],
    max_age=3600,
)

app.include_router(auth_router.router)
app.include_router(assets_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Opti Asset Management API is running"}
