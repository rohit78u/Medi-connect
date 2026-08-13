# MediConnect AI – Intelligent Healthcare Platform

MediConnect AI is an enterprise-grade, production-ready healthcare SaaS platform backend built with **FastAPI**, **Python 3.13+**, **Async SQLAlchemy 2.0**, **PostgreSQL**, **Redis**, **Celery**, and **Google Gemini AI**.

The codebase strictly adheres to **Clean Architecture**, **SOLID principles**, **Dependency Injection**, **Async Python**, and **Role-Based Access Control (RBAC)**.

---

## 🚀 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | FastAPI (Async Native) |
| **Language** | Python 3.13+ / Python 3.11 |
| **Database** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2.0 (AsyncSession) |
| **Migrations** | Alembic (Async) |
| **Validation** | Pydantic v2 |
| **Security** | JWT Access (30m) + Refresh Tokens (7d), Bcrypt (Passlib) |
| **Background Jobs** | Celery + Redis |
| **Cache & Realtime** | Redis 7 & WebSockets (`/ws/notifications/{user_id}`) |
| **Payments** | Razorpay Gateway (SHA256 HMAC Verification) |
| **AI Assistant** | Google Gemini API + LangChain |
| **Containerization** | Docker & Docker Compose |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX |

---

## 🏗️ Clean Architecture & Layer Separation

```
HTTP Client / Web / Mobile App
              │
              ▼
    API Routers (`app/api/v1/`)
              │
              ▼
     Services (`app/services/`)
              │
              ▼
   Repositories (`app/repositories/`)
              │
              ▼
  Database Models (`app/models/`) & PostgreSQL
```

* **API Routers**: Validate input schemas (Pydantic v2), enforce security guards, and delegate directly to Services. Zero raw SQL or business logic inside routes.
* **Services**: Enforce domain business rules, double-booking checks, transactions, background notification triggers, and Razorpay/AI integrations.
* **Repositories**: Abstract data access using strongly-typed Async SQLAlchemy 2.0 `select`, `update`, and `delete` statements.
* **Models**: SQLAlchemy 2.0 Declarative Mappings with `Mapped` attributes, UUID primary keys, and mixins for audit timestamps and soft deletion.

---

## 📬 Standardized Response Envelopes

### Success Envelope (`HTTP 200/201`)
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}
```

### Error Envelope (`HTTP 400/401/403/404/409/422/500`)
```json
{
  "success": false,
  "message": "Resource conflict or validation failure",
  "errors": ["Doctor already has a confirmed appointment at requested slot."]
}
```

---

## 📁 Project Folder Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── router.py                  # V1 Router Aggregator
│   │   └── endpoints/                 # API Route Modules
│   │       ├── auth.py                # Register, Login, Refresh, RBAC Guard
│   │       ├── patients.py            # Patient Profiles
│   │       ├── doctors.py             # Doctor Profiles & Availability
│   │       ├── appointments.py       # Scheduling & Status State Machine
│   │       ├── payments.py            # Razorpay Order Creation & HMAC Verification
│   │       ├── ai.py                  # Google Gemini AI Symptom Triage & Report Parsing
│   │       ├── health.py              # System Health Checks
│   │       └── websocket.py           # Realtime Notification Streams
│   ├── core/
│   │   ├── config.py                  # Pydantic v2 BaseSettings Loader
│   │   ├── security.py                # Bcrypt & JWT Access/Refresh Token Engine
│   │   ├── dependencies.py            # OAuth2 & RBAC Role Authorization Guards
│   │   ├── celery_app.py              # Celery Instance Configuration
│   │   └── logging.py                 # Structured Logger
│   ├── db/
│   │   ├── session.py                 # Async Engine & Sessionmaker
│   │   └── base.py                    # Alembic Metadata Registry
│   ├── models/                        # SQLAlchemy 2.0 ORM Models
│   │   ├── base.py                    # UUID, Timestamps, & Soft Delete Mixins
│   │   ├── user.py                    # User, Role, UserRole
│   │   ├── refresh_token.py            # RefreshToken
│   │   ├── patient.py                 # PatientProfile
│   │   ├── doctor.py                  # DoctorProfile, Specialization, DoctorAvailability
│   │   ├── appointment.py             # Appointment & AppointmentStatus Enum
│   │   └── payment.py                 # PaymentTransaction & PaymentStatus Enum
│   ├── schemas/                       # Pydantic v2 Input/Output Schemas
│   ├── repositories/                  # Async SQLAlchemy Repositories
│   ├── services/                      # Business Logic Domain Services
│   ├── middleware/                    # Global Exception Middleware
│   ├── notifications/                 # Email & Celery Async Background Tasks
│   ├── websocket/                     # ConnectionManager for Live WS Alerts
│   ├── payments/                      # Razorpay Client SDK & Signature Verifier
│   └── ai/                            # Google Gemini AI Clinical Engine
├── alembic/                           # Async Alembic Database Migrations
├── tests/                             # Pytest Suite (Integration & Unit)
├── Dockerfile                         # Multi-stage Container Build
├── docker-compose.yml                 # Full Stack Compose Setup
└── main.py                            # FastAPI Application Factory
```

---

## 🛠️ Quickstart with Docker Compose

### 1. Clone Repository & Setup Environment
```bash
cp .env.example .env
```

### 2. Launch Full Stack Infrastructure
```bash
docker-compose up --build -d
```
This starts:
* **FastAPI Application Server**: `http://localhost:8000`
* **Swagger OpenAPI Documentation**: `http://localhost:8000/docs`
* **PostgreSQL Database**: `localhost:5432`
* **Redis Cache & Broker**: `localhost:6379`
* **Celery Worker**: Background task executor

---

## 🧪 Running Pytest Integration Tests

```bash
pytest -v --cov=app tests/
```

Test Suites:
* `tests/test_health.py`: Database connection & health checks.
* `tests/test_auth.py`: Registration, login, token refresh, and RBAC guards.
* `tests/test_appointments.py`: Booking workflow, double-booking prevention, and state transitions.
* `tests/test_websocket.py`: Connection manager lifecycle & realtime push message streaming.
* `tests/test_payments.py`: Razorpay checkout order generation & HMAC signature verification.
* `tests/test_ai.py`: Google Gemini AI symptom triage and medical report parsing.

---

## 🛡️ License & Contact
MediConnect AI – Intelligent Healthcare Platform © 2026. Built with Clean Architecture & Best Industry Engineering Practices.
