import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.doctor import DoctorAvailability, DoctorProfile, Specialization
from app.models.lab_report import LabReport
from app.models.medical_record import MedicalRecord
from app.models.payment import PaymentStatus, PaymentTransaction
from app.models.patient import PatientProfile
from app.models.prescription import Prescription
from app.models.user import Role, User

DEMO_PASSWORD = "Demo@123"

USERS = {
    "patient": "demo.patient@mediconnect.local",
    "doctor": "demo.doctor@mediconnect.local",
    "pending_doctor": "pending.doctor@mediconnect.local",
    "admin": "demo.admin@mediconnect.local",
}


async def get_or_create_role(session, name, description):
    role = (await session.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
    if role:
        return role
    role = Role(name=name, description=description)
    session.add(role)
    await session.flush()
    return role


async def get_or_create_user(session, key, full_name, role, verified=True, superuser=False):
    email = USERS[key]
    user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user:
        user.hashed_password = get_password_hash(DEMO_PASSWORD)
        user.is_verified = verified
        user.is_superuser = superuser
        if role not in user.roles:
            user.roles.append(role)
        return user
    user = User(
        email=email,
        hashed_password=get_password_hash(DEMO_PASSWORD),
        full_name=full_name,
        phone_number="+91 90000 00000",
        is_verified=verified,
        is_superuser=superuser,
    )
    user.roles.append(role)
    session.add(user)
    await session.flush()
    return user


async def seed():
    async with AsyncSessionLocal() as session:
        patient_role = await get_or_create_role(session, "PATIENT", "Patient demo account")
        doctor_role = await get_or_create_role(session, "DOCTOR", "Doctor demo account")
        admin_role = await get_or_create_role(session, "ADMIN", "Administrator demo account")

        patient_user = await get_or_create_user(session, "patient", "Aarav Sharma", patient_role)
        doctor_user = await get_or_create_user(session, "doctor", "Dr. Ananya Rao", doctor_role, verified=True)
        pending_doctor_user = await get_or_create_user(
            session, "pending_doctor", "Dr. Karan Mehta", doctor_role, verified=False
        )
        admin_user = await get_or_create_user(session, "admin", "MediConnect Admin", admin_role, verified=True, superuser=True)

        session.add(PatientProfile(
            user_id=patient_user.id,
            date_of_birth=date(1999, 5, 14),
            gender="Male",
            blood_group="O+",
            emergency_contact="+91 98765 43210",
            medical_history_summary="Seasonal allergies. No known chronic conditions.",
        )) if not (await session.execute(select(PatientProfile).where(PatientProfile.user_id == patient_user.id))).scalar_one_or_none() else None

        cardiology = (await session.execute(select(Specialization).where(Specialization.name == "Cardiology"))).scalar_one_or_none()
        if not cardiology:
            cardiology = Specialization(name="Cardiology", description="Diagnosis and management of heart conditions")
            session.add(cardiology)
            await session.flush()

        pediatrics = (await session.execute(select(Specialization).where(Specialization.name == "Pediatrics"))).scalar_one_or_none()
        if not pediatrics:
            pediatrics = Specialization(name="Pediatrics", description="Medical care for children and adolescents")
            session.add(pediatrics)
            await session.flush()

        doctor = (await session.execute(select(DoctorProfile).where(DoctorProfile.user_id == doctor_user.id))).scalar_one_or_none()
        if not doctor:
            doctor = DoctorProfile(
                user_id=doctor_user.id,
                specialization_id=cardiology.id,
                license_number="KA-DEMO-1001",
                consultation_fee=700,
                years_of_experience=8,
                bio="Board-certified cardiologist focused on preventive care and lifestyle-based heart health.",
            )
            session.add(doctor)
            await session.flush()

        pending_doctor = (await session.execute(select(DoctorProfile).where(DoctorProfile.user_id == pending_doctor_user.id))).scalar_one_or_none()
        if not pending_doctor:
            pending_doctor = DoctorProfile(
                user_id=pending_doctor_user.id,
                specialization_id=pediatrics.id,
                license_number="KA-DEMO-1002",
                consultation_fee=500,
                years_of_experience=5,
                bio="Pediatrician demo account awaiting administrator verification.",
            )
            session.add(pending_doctor)
            await session.flush()

        availability = (await session.execute(select(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor.id))).scalars().all()
        if not availability:
            for day in (0, 2, 4):
                session.add(DoctorAvailability(doctor_id=doctor.id, day_of_week=day, start_time="09:00", end_time="13:00"))

        patient = (await session.execute(select(PatientProfile).where(PatientProfile.user_id == patient_user.id))).scalar_one()
        now = datetime.now(timezone.utc)
        upcoming_date = now + timedelta(days=2)
        past_date = now - timedelta(days=14)

        completed = (await session.execute(select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.doctor_id == doctor.id,
            Appointment.status == AppointmentStatus.COMPLETED,
        ))).scalar_one_or_none()
        if not completed:
            completed = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=past_date,
                status=AppointmentStatus.COMPLETED,
                reason_for_visit="Routine cardiac check-up",
                clinical_notes="Patient reports improved energy. Continue exercise and hydration plan.",
            )
            session.add(completed)
            await session.flush()

        upcoming = (await session.execute(select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.doctor_id == doctor.id,
            Appointment.status == AppointmentStatus.CONFIRMED,
        ))).scalar_one_or_none()
        if not upcoming:
            upcoming = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=upcoming_date.replace(hour=10, minute=30, second=0, microsecond=0),
                status=AppointmentStatus.CONFIRMED,
                reason_for_visit="Follow-up consultation",
            )
            session.add(upcoming)
            await session.flush()

        record = (await session.execute(select(MedicalRecord).where(MedicalRecord.appointment_id == completed.id))).scalar_one_or_none()
        if not record:
            record = MedicalRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_id=completed.id,
                record_date=past_date,
                diagnosis="Mild hypertension risk",
                symptoms="Occasional fatigue",
                clinical_notes="Vitals stable. Discussed low-sodium diet and regular aerobic activity.",
                treatment="Lifestyle modification and home blood-pressure monitoring.",
            )
            session.add(record)
            await session.flush()

        prescription = (await session.execute(select(Prescription).where(
            Prescription.patient_id == patient.id,
            Prescription.doctor_id == doctor.id,
            Prescription.medical_record_id == record.id,
        ))).scalar_one_or_none()
        if not prescription:
            session.add(Prescription(
                patient_id=patient.id,
                doctor_id=doctor.id,
                medical_record_id=record.id,
                medicine_name="Amlodipine 5 mg",
                dosage="5 mg",
                frequency="Once daily",
                duration="30 days",
                instructions="Take after breakfast. Monitor blood pressure twice weekly.",
                prescribed_date=past_date.date(),
            ))

        lab = (await session.execute(select(LabReport).where(
            LabReport.patient_id == patient.id,
            LabReport.medical_record_id == record.id,
            LabReport.test_name == "Lipid Profile",
        ))).scalar_one_or_none()
        if not lab:
            session.add(LabReport(
                patient_id=patient.id,
                doctor_id=doctor.id,
                medical_record_id=record.id,
                test_name="Lipid Profile",
                result="Total Cholesterol: 182 mg/dL; LDL: 104 mg/dL; HDL: 52 mg/dL",
                reference_range="Total < 200 mg/dL; LDL < 130 mg/dL",
                report_date=past_date.date(),
                notes="Within expected range for this demo patient.",
            ))

        payment = (await session.execute(select(PaymentTransaction).where(PaymentTransaction.appointment_id == completed.id))).scalar_one_or_none()
        if not payment:
            session.add(PaymentTransaction(
                appointment_id=completed.id,
                user_id=patient_user.id,
                razorpay_order_id="demo_order_001",
                razorpay_payment_id="demo_payment_001",
                razorpay_signature="demo_signature",
                amount=700,
                currency="INR",
                status=PaymentStatus.SUCCESS,
            ))

        await session.commit()
        print("Demo data seeded successfully.")
        print("Patient:        demo.patient@mediconnect.local / Demo@123")
        print("Doctor:         demo.doctor@mediconnect.local / Demo@123")
        print("Pending Doctor: pending.doctor@mediconnect.local / Demo@123")
        print("Admin:          demo.admin@mediconnect.local / Demo@123")


if __name__ == "__main__":
    asyncio.run(seed())
