# 🏥 MediConnect

> A backend-focused healthcare platform built with **Python and FastAPI**, designed around secure authentication, role-based access, database-driven workflows, asynchronous processing, and scalable backend architecture.

## 📌 Overview

MediConnect is a healthcare application designed to connect patients, doctors, and administrators through a structured backend system.

The project focuses on practical backend engineering concepts including **REST API development, JWT authentication, RBAC, asynchronous database access, Redis/Celery background processing, database migrations, automated testing, and clean architecture**.

## ✨ Key Features

- 🔐 **Authentication & Authorization** — JWT-based authentication with access/refresh tokens
- ✉️ **Email Verification** — Account verification workflow using email-based verification
- 👥 **Role-Based Access Control** — Separate access for patients, doctors, and administrators
- 👨‍⚕️ **Doctor Management** — Doctor profiles and management workflows
- 🗄️ **Async Database Layer** — SQLAlchemy 2.0 with PostgreSQL/asyncpg
- ⚡ **Background Processing** — Redis and Celery for asynchronous tasks
- 🔄 **Database Migrations** — Alembic-based schema migration workflow
- 🧪 **Automated Testing** — pytest and pytest-asyncio
- 🐳 **Containerized Development** — Docker-based development workflow
- 📚 **API Documentation** — FastAPI-generated Swagger/OpenAPI documentation

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      Frontend        │
                    └──────────┬───────────┘
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Routes / Services    │
                    │ Auth / RBAC          │
                    │ Business Logic       │
                    └──────┬─────────┬─────┘
                           │         │
                ┌──────────▼──┐  ┌──▼─────────────┐
                │ PostgreSQL  │  │ Redis + Celery │
                │ SQLAlchemy  │  │ Background Jobs│
                └─────────────┘  └────────────────┘
```

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| API | REST, Swagger/OpenAPI |
| Validation & Configuration | Pydantic, Pydantic Settings |
| Database | PostgreSQL, SQLAlchemy 2.0, asyncpg |
| Migrations | Alembic |
| Authentication | JWT, bcrypt, RBAC |
| Background Processing | Redis, Celery |
| Testing | pytest, pytest-asyncio, pytest-cov |
| Development | Docker |

## 🔐 Authentication Flow

```text
User Registration
       ↓
Email Verification
       ↓
Login
       ↓
JWT Access + Refresh Tokens
       ↓
Authenticated API Requests
       ↓
Role-Based Authorization
```

## 🔄 Core Backend Workflow

```text
Client Request
      ↓
FastAPI Router
      ↓
Authentication / Authorization
      ↓
Pydantic Validation
      ↓
Service / Business Logic
      ↓
SQLAlchemy Async Session
      ↓
PostgreSQL
```

Background tasks can be delegated through:

```text
FastAPI
   ↓
Celery Task
   ↓
Redis Broker
   ↓
Celery Worker
```

## 📁 Project Structure

```text
Medi-connect/
├── .github/             # CI/CD workflows
├── backend/              # FastAPI backend
│   ├── app/              # Application source code
│   ├── tests/            # Backend tests
│   └── requirements.txt  # Python dependencies
├── frontend/             # Frontend application
├── ROADMAP.md            # Development roadmap
└── .gitignore
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Git
- Docker (recommended)

### Backend Setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

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

Configure the required environment variables using the project's environment configuration.

Run the API with:

```bash
uvicorn app.main:app --reload
```

Once running, FastAPI provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## 🧪 Testing

Run the backend test suite with:

```bash
cd backend
pytest -v
```

For coverage:

```bash
pytest --cov
```

## 🔄 Database Migrations

The project uses Alembic for database schema migrations.

Typical workflow:

```bash
alembic revision --autogenerate -m "migration message"
alembic upgrade head
```

## 🐳 Docker

Docker is part of the project's development and reliability workflow. The repository roadmap includes validating the complete Docker Compose setup before production deployment. fileciteturn13file0L2-L2

## 📚 Development Roadmap

The project is being developed in phases covering reliability, the core healthcare workflow, user experience, healthcare features, and production deployment. fileciteturn13file0L2-L2

Current planned areas include doctor availability, secure payments, AI-assisted healthcare workflows, dashboards, medical records, prescriptions, deployment, monitoring, and backups.

## 🎯 What This Project Demonstrates

- Building backend applications with **FastAPI and Python**
- Designing **REST APIs**
- Implementing **JWT authentication and RBAC**
- Working with **SQLAlchemy 2.0 and asynchronous database access**
- Using **PostgreSQL and Alembic migrations**
- Designing **background processing with Redis and Celery**
- Writing automated backend tests with **pytest**
- Structuring backend systems for maintainability and scalability
- Applying a phase-based development and CI/CD workflow

## 📌 Project Status

MediConnect is an actively developed portfolio project. The roadmap tracks the remaining implementation and production-hardening work.

## 📄 License

MIT
