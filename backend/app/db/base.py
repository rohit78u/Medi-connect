# Import Declarative Base and Models for Alembic autogenerate discovery
from app.models.base import Base  # noqa: F401
from app.models.user import User, Role, UserRole  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.patient import PatientProfile  # noqa: F401
from app.models.doctor import DoctorProfile, Specialization, DoctorAvailability  # noqa: F401
from app.models.appointment import Appointment  # noqa: F401
from app.models.payment import PaymentTransaction  # noqa: F401
from app.models.medical_record import MedicalRecord  # noqa: F401
from app.models.prescription import Prescription  # noqa: F401
