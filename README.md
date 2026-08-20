# 🏥 MediConnect

> A backend-focused healthcare platform built with **Python and FastAPI**, with secure authentication, role-based access control, asynchronous database workflows, background processing, automated testing, and containerized development.

## 📌 Overview

MediConnect connects patients, doctors, and administrators through a structured REST API and healthcare workflow system. The project demonstrates practical backend engineering with authentication, authorization, PostgreSQL, asynchronous SQLAlchemy, Redis/Celery, Alembic migrations, testing, Docker, and CI/CD.

## ✨ Core Features

- 🔐 JWT authentication with access and refresh tokens
- 🔒 Role-based authorization for patients, doctors, and administrators
- 🔁 Refresh-token rotation with hashed token persistence
- ✉️ Email verification workflow
- 👨‍⚕️ Doctor profiles and administrator verification workflow
- 📅 Appointment management with role and verified-doctor checks
- 🩺 Patient and medical-record workflows
- 💊 Prescription and lab-report workflows
- 💳 Payment integration structure
- 🤖 AI-assisted healthcare workflow integration
- ⚡ Redis and Celery background processing
- 🗄️ PostgreSQL with SQLAlchemy 2.0 and asyncpg
- 🔄 Alembic database migrations
- 🧪 pytest-based automated tests with coverage
- 🐳 Docker and Docker Compose development setup
- 📚 FastAPI Swagger/OpenAPI documentation
- ⚙️ GitHub Actions CI/CD with Ruff, tests, coverage, compilation checks, and Docker builds

## 🏗️ Architecture

```text
Client / Frontend
       │
       ▼
FastAPI REST API
       │
       ├── Authentication / RBAC
       ├── Request Validation
       ├── Service Layer
       └── Repository Layer
              │
       ┌──────┴──────────┐
       ▼                 ▼
 PostgreSQL         Redis / Celery
 SQLAlchemy         Background Jobs
       │
       ▼
    Alembic
   Migrations
```

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| API | REST, Swagger/OpenAPI |
| Validation | Pydantic, Pydantic Settings |
| Database | PostgreSQL, SQLAlchemy 2.0, asyncpg |
| Migrations | Alembic |
| Authentication | JWT, bcrypt, RBAC |
| Background Processing | Redis, Celery |
| AI | Gemini API integration |
| Payments | Razorpay integration |
| Testing | pytest, pytest-asyncio, pytest-cov |
| Quality | Ruff, compile checks |
| DevOps | Docker, Docker Compose, GitHub Actions |

## 🔐 Authentication & Authorization

```text
Registration
    ↓
Email Verification
    ↓
Login
    ↓
Access + Refresh Tokens
    ↓
Authenticated Request
    ↓
RBAC / Resource Authorization
```

Refresh tokens are rotated and persisted in hashed form rather than storing the raw credential in the database.

## 🔄 Request Flow

```text
Client Request
      ↓
FastAPI Router
      ↓
Authentication / Authorization
      ↓
Pydantic Validation
      ↓
Service Layer
      ↓
Repository Layer
      ↓
Async SQLAlchemy
      ↓
PostgreSQL
```

Long-running or asynchronous work can be delegated through:

```text
FastAPI → Celery Task → Redis → Celery Worker
```

## 📁 Project Structure

```text
Medi-connect/
├── .github/workflows/    # CI/CD
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Configuration, security, dependencies
│   │   ├── models/       # SQLAlchemy models
│   │   ├── repositories/ # Data-access layer
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── ai/           # AI integration
│   │   └── payments/     # Payment integration
│   ├── alembic/          # Database migrations
│   └── tests/            # Automated tests
├── frontend/             # Frontend client
├── ROADMAP.md            # Future improvements
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Git
- Docker (recommended)

### Backend

```bash
cd backend
python -m venv .venv
```

Activate the environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using `backend/.env.example` as the template.

Run the API:

```bash
uvicorn app.main:app --reload
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Docker

The backend includes Docker and Docker Compose configuration for local development and service integration.

## 🧪 Testing

```bash
cd backend
pytest -v
```

Coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Linting:

```bash
ruff check app tests
```

## 🔄 Database Migrations

```bash
cd backend
alembic upgrade head
```

Create a migration when the schema changes:

```bash
alembic revision --autogenerate -m "migration message"
```

## ⚙️ CI/CD

GitHub Actions validates the backend using:

- Ruff linting
- PostgreSQL and Redis service containers
- pytest with coverage
- Python compilation checks
- Docker image build

The workflow runs on pushes to `main`/phase branches and pull requests targeting `main`.

## 🎯 What This Project Demonstrates

- Designing REST APIs with FastAPI
- Implementing JWT authentication and RBAC
- Protecting role-specific healthcare workflows
- Building asynchronous database access with SQLAlchemy 2.0
- Managing PostgreSQL schemas with Alembic
- Using Redis and Celery for background processing
- Integrating external AI and payment services
- Writing automated backend tests
- Containerizing services with Docker
- Enforcing code quality through CI/CD

## 📌 Project Status

MediConnect is a **portfolio and learning project**. Core backend workflows are implemented and the repository is being continuously hardened. Production deployment, monitoring, backups, and additional operational hardening remain future improvements.

## 📄 License

MIT
