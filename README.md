# Eduverse Africa — Multi-Tenant School Management Backend

A complete **Multi-Tenant (SaaS)** school management REST API built with **Django 4.2**, **Django REST Framework**, **JWT Auth**, and **Docker**.

## 🚀 Architecture

- **Multi-Tenancy:** True row-level isolation. Each school is a `Tenant` isolated via a `school` ForeignKey on all models.
- **Routing:** Handled automatically by `TenantMiddleware` via URL subdomains (e.g., `https://greenfield.eduverse.com/api/`) or HTTP header (`X-School-ID: 1`).
- **Database:** PostgreSQL.
- **Caching & Brokers:** Redis.
- **Production Server:** Gunicorn behind Nginx running via `docker-compose`.

---

## 🛠️ Project Structure

```
backend/
├── .env                 # Environment variables
├── docker-compose.yml   # Multi-container orchestration
├── Dockerfile           # Django app build instructions
├── entrypoint.sh        # Startup script (migrations, collectstatic, gunicorn)
├── nginx/               # Nginx wildcard reverse proxy
├── eduverse/            # Django project core (settings, urls)
├── tenants/             # SaaS Core: School models, TenantMiddleware, Mixins
├── accounts/            # User models with 8 RBAC roles (tied to a school)
├── students/            # Students, staff, grades, classrooms
├── attendance/          # Daily attendance & reporting
├── fees/                # Fee structures, automated PDF receipts 
├── exams/               # Exam cycles, grade processing, PDF report cards
├── hr/                  # Leave approvals & payroll calculation
├── library/             # Library ledger & penalty tracking
└── portal/              # Notice board, class timetables, dashboards
```

---

## 🐳 Quick Start (Docker)

The fastest and most robust way to run the application is via Docker. Ensure Docker Desktop is running.

### 1. Boot up the containers
```bash
cd backend
docker-compose up --build -d
```
This will start 4 containers: `web` (Django/Gunicorn), `db` (Postgres), `redis` (Cache), and `nginx` (Proxy proxying via port `80`).

### 2. Seed the Database
Run the seed command inside the web container to create your first tenant (`demo`), users, and fake data.
```bash
docker-compose exec web python manage.py seed_data
```

### 3. Access the APIs
Traffic routes over port 80. Add the `demo` subdomain resolution to your local `hosts` file (`127.0.0.1 demo.localhost`), or use the HTTP header bypass.

- **Docs:** `http://localhost/api/docs/`
- **Admin Panel:** `http://localhost/admin/`

---

## 💻 Manual Setup (Virtual Environment)
If you prefer running outside of Docker (for local development/debugging):

```bash
# 1. Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Postgres database, then apply migrations
python manage.py makemigrations
python manage.py migrate

# 4. Seed database & run server
python manage.py seed_data
python manage.py runserver
```

---

## 🔑 Demo Logins (After `seed_data`)

The seed script creates a test school named **Greenfield International** (subdomain: `demo`).

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | School Admin (superuser) |
| `teacher1` | `teacher123` | Teacher (Mary Kamau) |
| `teacher2` | `teacher123` | Teacher (James Odhiambo) |
| `accountant` | `account123` | Accountant |
| `librarian` | `library123` | Librarian |
| `hr` | `hr123456` | HR Admin |
| `parent1` | `parent123` | Parent (John Njoroge) |
| `parent2` | `parent123` | Parent (Alice Achieng) |

---

## 🌐 Connecting a Mobile/Frontend App (Flutter/React Native)

Because the system is multi-tenant, your frontend must let the API know **which school** the user belongs to. 

### Approach A: Subdomains (Web / Production)
Your frontend domain corresponds to the school (e.g. `greenfield.eduverse.com`). Simply set the Base URL for your fetch requests to your subdomain. The `TenantMiddleware` extracts `greenfield` automatically.

### Approach B: HTTP Headers (Mobile / Dev)
In mobile apps, wildcard subdomains don't apply. Instead, set the target school by passing the `X-School-ID` header with every request.

```dart
// Flutter Example 
final headers = {
  'Authorization': 'Bearer $token',
  'X-School-ID': '1', // The ID of the School
  // OR 'X-School-Subdomain': 'demo' 
};
```

---

## 📚 API Endpoints Summary

### Tenant Onboarding
```
POST /api/public/schools/register/      Register a new School & Superadmin
GET  /api/public/check-subdomain/       Check subdomain availability
```

### Authentication
```
POST /api/token/                        Login → JWT access + refresh tokens
POST /api/token/refresh/                Refresh access token
```

### Core Business Logic
*See `http://localhost/api/docs/` for comprehensive Swagger UI documentation covering Students, Fees, HR, Library, Attendance, and Exams endpoints.*
