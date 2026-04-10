# Opti Asset Management — FastAPI Backend

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database
python seed.py

# 4. Run the server
uvicorn main:app --reload
```

- API running at: http://localhost:8000
- Swagger docs at: http://localhost:8000/docs

## Login Credentials

| Role     | Email              | Password  |
|----------|--------------------|-----------|
| Admin    | admin@opti.com     | admin123  |
| Employee | alice@opti.com     | alice123  |
| Employee | bob@opti.com       | bob123    |

## RBAC Privileges

| Privilege        | Role     | Endpoint               |
|------------------|----------|------------------------|
| view:inventory   | Admin    | GET /assets/           |
| view:my_gear     | Employee | GET /assets/my         |
| create:asset     | Admin    | POST /assets/          |
| update:asset     | Admin    | PUT /assets/{id}       |
| delete:asset     | Admin    | DELETE /assets/{id}    |
| manage:users     | Admin    | /users/*               |
