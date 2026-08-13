"""Add medical records.

Revision ID: 0002_medical_records
Revises: 0001_initial_schema
Create Date: 2026-08-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_medical_records"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "medical_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("appointment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("record_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("diagnosis", sa.String(length=500), nullable=True),
        sa.Column("symptoms", sa.Text(), nullable=True),
        sa.Column("clinical_notes", sa.Text(), nullable=True),
        sa.Column("treatment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patient_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctor_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_medical_records_id", "medical_records", ["id"])
    op.create_index("ix_medical_records_patient_id", "medical_records", ["patient_id"])
    op.create_index("ix_medical_records_doctor_id", "medical_records", ["doctor_id"])
    op.create_index("ix_medical_records_appointment_id", "medical_records", ["appointment_id"])
    op.create_index("ix_medical_records_record_date", "medical_records", ["record_date"])


def downgrade() -> None:
    op.drop_index("ix_medical_records_record_date", table_name="medical_records")
    op.drop_index("ix_medical_records_appointment_id", table_name="medical_records")
    op.drop_index("ix_medical_records_doctor_id", table_name="medical_records")
    op.drop_index("ix_medical_records_patient_id", table_name="medical_records")
    op.drop_index("ix_medical_records_id", table_name="medical_records")
    op.drop_table("medical_records")
