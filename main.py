import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routers import auth_router, assets_router, users_router, dashboard_router

app = FastAPI(title="Opti Asset Management API", version="1.0.0")

# -------------------- SEED FUNCTION --------------------
def auto_seed():
    from models import Permission, Role, User, Asset
    from core.security import hash_password

    db = SessionLocal()
    try:
        if db.query(User).first():
            print("✅ DB already seeded")
            return

        print("🌱 Seeding...")

        def get_or_create_perm(name, desc):
            p = db.query(Permission).filter(Permission.name == name).first()
            if not p:
                p = Permission(name=name, description=desc)
                db.add(p)
                db.flush()
            return p

        perms = {
            name: get_or_create_perm(name, desc)
            for name, desc in [
                ("view:inventory", "View all assets"),
                ("view:my_gear", "View own assigned assets"),
                ("create:asset", "Add new assets"),
                ("update:asset", "Edit existing assets"),
                ("delete:asset", "Remove assets"),
                ("manage:users", "Manage users"),
            ]
        }

        # Roles
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin")
            db.add(admin_role)
            db.flush()
            admin_role.permissions = list(perms.values())

        emp_role = db.query(Role).filter(Role.name == "Employee").first()
        if not emp_role:
            emp_role = Role(name="Employee")
            db.add(emp_role)
            db.flush()
            emp_role.permissions = [perms["view:my_gear"]]

        db.commit()

        # Users
        users_data = [
            ("Opti Admin", "admin@opti.com", "admin123", admin_role.id),
            ("John", "john@opti.com", "john123", emp_role.id),
            ("Ram", "ram@opti.com", "ram12", emp_role.id),
            ("Akash", "akash@opti.com", "akash123", emp_role.id),
        ]

        user_map = {}
        for full_name, email, pwd, role_id in users_data:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                u = User(
                    full_name=full_name,
                    email=email,
                    hashed_password=hash_password(pwd),
                    role_id=role_id,
                )
                db.add(u)
                db.flush()
            user_map[email] = u

        db.commit()

        # Assets (FIXED USERS ✅)
        assets_data = [
            ('MacBook Pro 14"', 'OPTI-001','Laptop', 'assigned', 2499.99, user_map['admin@opti.com'].id),
            ('Dell XPS 15', 'OPTI-002','Laptop', 'assigned', 1899.00, user_map['john@opti.com'].id),
            ('LG UltraWide', 'OPTI-003','Monitor', 'available', 699.00, None),
            ('iPhone 15 Pro', 'OPTI-004','Phone', 'assigned', 999.00, user_map['ram@opti.com'].id),
            ('Logitech MX Keys','OPTI-005','Keyboard','available',109.99,None),
            ('Sony WH-1000XM5','OPTI-006','Headset','assigned',349.99,user_map['akash@opti.com'].id),
            ('Standing Desk','OPTI-007','Furniture','available',799.00,None),
            ('Cisco IP Phone','OPTI-008','Phone','retired',149.99,None),
            ('Samsung 27" 4K','OPTI-009','Monitor','assigned',549.00,user_map['john@opti.com'].id),
            ('Ergonomic Chair','OPTI-010','Furniture','available',599.00,None),
        ]

        for name, tag, cat, status, value, uid in assets_data:
            if not db.query(Asset).filter(Asset.asset_tag == tag).first():
                db.add(
                    Asset(
                        name=name,
                        asset_tag=tag,
                        category=cat,
                        status=status,
                        value=value,
                        assigned_to_id=uid,
                    )
                )

        db.commit()
        print("✅ Seeded! admin@opti.com / admin123")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
    finally:
        db.close()


# -------------------- STARTUP EVENT --------------------
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        auto_seed()
        print("✅ DB Ready & Seeded")
    except Exception as e:
        print("❌ Startup error:", e)


# -------------------- CORS --------------------
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
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- ROUTERS --------------------
app.include_router(auth_router.router)
app.include_router(assets_router.router)
app.include_router(users_router.router)
app.include_router(dashboard_router.router)


# -------------------- ROUTES --------------------
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Opti API running"}


@app.get("/health", tags=["Health"])
def health():
    from models import User
    db = SessionLocal()
    try:
        count = db.query(User).count()
        return {"status": "ok", "users_in_db": count}
    finally:
        db.close()
