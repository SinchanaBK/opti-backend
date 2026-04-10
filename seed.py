"""
Run once:  python seed.py
Creates roles, permissions, users, and 10 sample assets.
"""
from database import SessionLocal, engine, Base
from models import Permission, Role, User, Asset
from core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

PERMS = [
    ("view:inventory",  "View all assets"),
    ("view:my_gear",    "View own assigned assets"),
    ("create:asset",    "Add new assets"),
    ("update:asset",    "Edit existing assets"),
    ("delete:asset",    "Remove assets"),
    ("manage:users",    "Create / update / delete users"),
]

perms = {}
for name, desc in PERMS:
    p = db.query(Permission).filter(Permission.name == name).first()
    if not p:
        p = Permission(name=name, description=desc)
        db.add(p); db.flush()
    perms[name] = p

admin_role = db.query(Role).filter(Role.name == "Admin").first()
if not admin_role:
    admin_role = Role(name="Admin")
    db.add(admin_role); db.flush()
    admin_role.permissions = list(perms.values())

emp_role = db.query(Role).filter(Role.name == "Employee").first()
if not emp_role:
    emp_role = Role(name="Employee")
    db.add(emp_role); db.flush()
    emp_role.permissions = [perms["view:my_gear"]]

db.commit()

USERS = [
    ("Opti Admin",    "admin@opti.com",  "admin123",  admin_role.id),
    ("Alice Johnson", "alice@opti.com",  "alice123",  emp_role.id),
    ("Bob Martinez",  "bob@opti.com",    "bob123",    emp_role.id),
    ("Carol White",   "carol@opti.com",  "carol123",  emp_role.id),
]
user_map = {}
for full_name, email, pwd, role_id in USERS:
    u = db.query(User).filter(User.email == email).first()
    if not u:
        u = User(full_name=full_name, email=email,
                 hashed_password=hash_password(pwd), role_id=role_id)
        db.add(u); db.flush()
    user_map[email] = u
db.commit()

ASSETS = [
    ('MacBook Pro 14"',   'OPTI-001', 'Laptop',    'assigned',  2499.99, user_map['alice@opti.com'].id),
    ('Dell XPS 15',       'OPTI-002', 'Laptop',    'assigned',  1899.00, user_map['bob@opti.com'].id),
    ('LG UltraWide 34"',  'OPTI-003', 'Monitor',   'available',  699.00, None),
    ('iPhone 15 Pro',     'OPTI-004', 'Phone',     'assigned',   999.00, user_map['carol@opti.com'].id),
    ('Logitech MX Keys',  'OPTI-005', 'Keyboard',  'available',  109.99, None),
    ('Sony WH-1000XM5',   'OPTI-006', 'Headset',   'assigned',   349.99, user_map['alice@opti.com'].id),
    ('Standing Desk',     'OPTI-007', 'Furniture', 'available',  799.00, None),
    ('Cisco IP Phone',    'OPTI-008', 'Phone',     'retired',    149.99, None),
    ('Samsung 27" 4K',    'OPTI-009', 'Monitor',   'assigned',   549.00, user_map['bob@opti.com'].id),
    ('Ergonomic Chair',   'OPTI-010', 'Furniture', 'available',  599.00, None),
]
for name, tag, cat, status, value, uid in ASSETS:
    if not db.query(Asset).filter(Asset.asset_tag == tag).first():
        db.add(Asset(name=name, asset_tag=tag, category=cat,
                     status=status, value=value, assigned_to_id=uid))
db.commit()
db.close()

print("✅  Database seeded!")
print("\n  Admin    → admin@opti.com  /  admin123")
print("  Employee → alice@opti.com  /  alice123")
print("  Employee → bob@opti.com    /  bob123")
