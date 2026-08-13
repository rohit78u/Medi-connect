# MediConnect Development Roadmap

MediConnect is developed in phases. Each phase is implemented on its own branch and merged into `main` only after the phase is tested and reviewed.

## Branch strategy

- `main` — stable baseline only
- `phase-1-reliability` — security, repository hygiene, migrations, tests, CI/CD and Docker reliability
- `phase-2-core-workflow` — doctor availability, real Razorpay integration, secure payments and real Gemini integration
- `phase-3-user-experience` — patient, doctor and admin dashboards plus doctor verification
- `phase-4-healthcare-features` — medical records, prescriptions, lab reports, document uploads and consultation history
- `phase-5-production` — deployment, production databases/services, HTTPS, monitoring and backups

## Phase 1 — Make existing system reliable

- [ ] Remove `.env` from Git and keep only `.env.example`
- [ ] Remove hard-coded credentials/secrets
- [ ] Prevent public ADMIN registration
- [ ] Remove `__pycache__`, `.pyc` and local database files from Git
- [ ] Add/verify `.gitignore`
- [ ] Create and verify proper Alembic migration
- [ ] Run the complete test suite and fix failures
- [ ] Validate GitHub Actions CI/CD
- [ ] Verify Docker Compose end-to-end

## Phase 2 — Finish core healthcare workflow

- [ ] Implement real doctor availability checking during booking
- [ ] Integrate the real Razorpay Checkout/API flow
- [ ] Calculate payment amount server-side from the doctor's consultation fee
- [ ] Verify payment ownership and appointment ownership
- [ ] Integrate Google Gemini API for AI triage/report analysis
- [ ] Add strict structured-output validation and medical safety guardrails

## Phase 3 — Complete user experience

- [ ] Patient dashboard
- [ ] Patient profile UI
- [ ] Doctor dashboard
- [ ] Doctor availability management UI
- [ ] Admin dashboard
- [ ] Doctor verification/approval workflow

## Phase 4 — Healthcare features

- [ ] Medical records
- [ ] Prescription management
- [ ] Lab report storage
- [ ] Secure medical document upload
- [ ] Consultation history

## Phase 5 — Production

- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Production PostgreSQL
- [ ] Production Redis
- [ ] Celery worker deployment
- [ ] HTTPS/TLS
- [ ] Monitoring and structured logging
- [ ] Database/file backup strategy

## Workflow for every phase

1. Create a phase branch from the latest stable `main`.
2. Implement one logical feature at a time with focused commits.
3. Add/update tests for backend behavior.
4. Run tests and build checks.
5. Open a Pull Request into `main`.
6. Review the diff and CI results.
7. Merge only when the phase acceptance criteria are satisfied.
8. Tag the completed phase when appropriate.
