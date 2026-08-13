"""Initial MediConnect schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _uuid_column(nullable: bool = False):
    return sa.Column(
        "id",
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        nullable=nullable,
    )


def _common_columns():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    appointment_status = postgresql.ENUM(
        "PENDING", "CONFIRMED", "COMPLETED", "CANCELLED",
        name="appointmentstatus",
    )
    payment_status = postgresql.ENUM(
        "CREATED", "SUCCESS", "FAILED", "REFUNDED",
        name="paymentstatus",
    )
    appointment_status.create(op.get_bind(), checkfirst=True)
    payment_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "roles",
        _uuid_column(),
        *_common_columns(),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_roles_id", "roles", ["id"])
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "users",
        _uuid_column(),
        *_common_columns(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        *_common_columns()[:2],
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "refresh_tokens",
        _uuid_column(),
        *_common_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)

    op.create_table(
        "specializations",
        _uuid_column(),
        *_common_columns(),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_specializations_id", "specializations", ["id"])
    op.create_index("ix_specializations_name", "specializations", ["name"], unique=True)

    op.create_table(
        "patient_profiles",
        _uuid_column(),
        *_common_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("blood_group", sa.String(length=10), nullable=True),
        sa.Column("emergency_contact", sa.String(length=20), nullable=True),
        sa.Column("medical_history_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_patient_profiles_id", "patient_profiles", ["id"])
    op.create_index("ix_patient_profiles_user_id", "patient_profiles", ["user_id"], unique=True)

    op.create_table(
        "doctor_profiles",
        _uuid_column(),
        *_common_columns(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("specialization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("license_number", sa.String(length=50), nullable=False),
        sa.Column("consultation_fee", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("years_of_experience", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["specialization_id"], ["specializations.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_doctor_profiles_id", "doctor_profiles", ["id"])
    op.create_index("ix_doctor_profiles_user_id", "doctor_profiles", ["user_id"], unique=True)
    op.create_index("ix_doctor_profiles_specialization_id", "doctor_profiles", ["specialization_id"])
    op.create_index("ix_doctor_profiles_license_number", "doctor_profiles", ["license_number"], unique=True)

    op.create_table(
        "doctor_availabilities",
        _uuid_column(),
        *_common_columns(),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.String(length=10), nullable=False),
        sa.Column("end_time", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctor_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_doctor_availabilities_id", "doctor_availabilities", ["id"])
    op.create_index("ix_doctor_availabilities_doctor_id", "doctor_availabilities", ["doctor_id"])

    op.create_table(
        "appointments",
        _uuid_column(),
        *_common_columns(),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("appointment_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", appointment_status, nullable=False, server_default="PENDING"),
        sa.Column("reason_for_visit", sa.String(length=255), nullable=True),
        sa.Column("clinical_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patient_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctor_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_appointments_id", "appointments", ["id"])
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_appointment_date", "appointments", ["appointment_date"])
    op.create_index("ix_appointments_status", "appointments", ["status"])

    op.create_table(
        "payment_transactions",
        _uuid_column(),
        *_common_columns(),
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("razorpay_order_id", sa.String(length=100), nullable=False),
        sa.Column("razorpay_payment_id", sa.String(length=100), nullable=True),
        sa.Column("razorpay_signature", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("status", payment_status, nullable=False, server_default="CREATED"),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_payment_transactions_id", "payment_transactions", ["id"])
    op.create_index("ix_payment_transactions_appointment_id", "payment_transactions", ["appointment_id"])
    op.create_index("ix_payment_transactions_user_id", "payment_transactions", ["user_id"])
    op.create_index("ix_payment_transactions_razorpay_order_id", "payment_transactions", ["razorpay_order_id"], unique=True)
    op.create_index("ix_payment_transactions_razorpay_payment_id", "payment_transactions", ["razorpay_payment_id"])
    op.create_index("ix_payment_transactions_status", "payment_transactions", ["status"])


def downgrade() -> None:
    op.drop_table("payment_transactions")
    op.drop_table("appointments")
    op.drop_table("doctor_availabilities")
    op.drop_table("doctor_profiles")
    op.drop_table("patient_profiles")
    op.drop_table("specializations")
    op.drop_table("refresh_tokens")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")

    bind = op.get_bind()
    postgresql.ENUM(name="paymentstatus").drop(bind, checkfirst=True)
    postgresql.ENUM(name="appointmentstatus").drop(bind, checkfirst=True)
