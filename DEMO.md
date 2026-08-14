# MediConnect — Local Demo Guide

This branch is optimized for resume demonstrations, not production deployment.

## Start the whole application

From the repository root:

```bash
docker compose -f docker-compose.demo.yml up --build
```

Then open:

- Frontend: http://127.0.0.1:8080
- Backend API: http://127.0.0.1:8000/docs

The backend automatically runs the latest Alembic migrations and seeds realistic demo data on startup.

## Demo accounts

All demo accounts use:

`Demo@123`

| Role | Email | Purpose |
|---|---|---|
| Patient | `demo.patient@mediconnect.local` | Search doctors, appointments, records, prescriptions and lab reports |
| Doctor | `demo.doctor@mediconnect.local` | View schedule and demonstrate verified-doctor workflow |
| Pending Doctor | `pending.doctor@mediconnect.local` | Demonstrate admin verification |
| Admin | `demo.admin@mediconnect.local` | Approve doctors and view platform data |

## Recommended 5-minute demo

1. Login as the Patient.
2. Open Doctor Search and show the verified doctor.
3. Open Schedule and show the confirmed follow-up appointment.
4. Show the patient's medical profile/history.
5. Login as the Doctor and show the clinical schedule.
6. Login as Admin and open Pending Doctor Verification.
7. Approve `Dr. Karan Mehta`.
8. Return to Doctor Search and show the newly verified doctor.

## Reset demo data

Stop and remove the demo volumes, then start again:

```bash
docker compose -f docker-compose.demo.yml down -v
docker compose -f docker-compose.demo.yml up --build
```

The demo database, Redis data and uploaded demo-document volume are isolated from any other local environment.
