"""Create a small, idempotent verified-doctor directory for local development."""

import asyncio

from sqlalchemy import select

import app.db.base  # noqa: F401  # Register all ORM relationship models before querying.
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.doctor import DoctorAvailability, DoctorProfile, Specialization
from app.models.user import Role, User


DOCTORS = [
    ("Dr. Ananya Sharma", "ananya.sharma.demo@gmail.com", "Cardiology", "MC-2026-1001", 1200, 12, "Cardiologist focused on preventive heart health and hypertension."),
    ("Dr. Vikram Mehta", "vikram.mehta.demo@gmail.com", "General Practice", "MC-2026-1002", 700, 9, "Primary-care clinician for everyday health concerns and follow-ups."),
    ("Dr. Neha Iyer", "neha.iyer.demo@gmail.com", "Neurology", "MC-2026-1003", 1500, 11, "Neurologist with an interest in headaches and sleep-related concerns."),
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        role = (await db.execute(select(Role).where(Role.name == "DOCTOR"))).scalars().first()
        if not role:
            role = Role(name="DOCTOR", description="Clinical provider")
            db.add(role)
            await db.flush()

        for name, email, specialty_name, license_number, fee, experience, bio in DOCTORS:
            user = (await db.execute(select(User).where(User.email == email))).scalars().first()
            if not user:
                user = User(email=email, full_name=name, hashed_password=get_password_hash("DemoDoctor2026!"), is_verified=True)
                user.roles.append(role)
                db.add(user)
                await db.flush()
            specialization = (await db.execute(select(Specialization).where(Specialization.name == specialty_name))).scalars().first()
            if not specialization:
                specialization = Specialization(name=specialty_name, description=f"{specialty_name} care")
                db.add(specialization)
                await db.flush()
            profile = (await db.execute(select(DoctorProfile).where(DoctorProfile.user_id == user.id))).scalars().first()
            if not profile:
                profile = DoctorProfile(user_id=user.id, specialization_id=specialization.id, license_number=license_number, consultation_fee=fee, years_of_experience=experience, bio=bio, is_verified=True)
                db.add(profile)
                await db.flush()
            has_availability = (await db.execute(select(DoctorAvailability).where(DoctorAvailability.doctor_id == profile.id))).scalars().first()
            if not has_availability:
                db.add_all([DoctorAvailability(doctor_id=profile.id, day_of_week=day, start_time="09:00", end_time="17:00") for day in range(5)])

        await db.commit()
        print("Demo doctor directory is ready.")


if __name__ == "__main__":
    asyncio.run(main())
