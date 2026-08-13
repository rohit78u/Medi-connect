"""Add lab reports.

Revision ID: 0004_lab_reports
Revises: 0003_prescriptions
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_lab_reports"
down_revision: Union[str, Sequence[str], None] = "0003_prescriptions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lab_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("medical_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("test_name", sa.String(length=255), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("reference_range", sa.String(length=255), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patient_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctor_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["medical_record_id"], ["medical_records.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_lab_reports_id", "lab_reports", ["id"])
    op.create_index("ix_lab_reports_patient_id", "lab_reports", ["patient_id"])
    op.create_index("ix_lab_reports_doctor_id", "lab_reports", ["doctor_id"])
    op.create_index("ix_lab_reports_medical_record_id", "lab_reports", ["medical_record_id"])
    op.create_index("ix_lab_reports_report_date", "lab_reports", ["report_date"])


def downgrade() -> None:
    op.drop_index("ix_lab_reports_report_date", table_name="lab_reports")
    op.drop_index("ix_lab_reports_medical_record_id", table_name="lab_reports")
    op.drop_index("ix_lab_reports_doctor_id", table_name="lab_reports")
    op.drop_index("ix_lab_reports_patient_id", table_name="lab_reports")
    op.drop_index("ix_lab_reports_id", table_name="lab_reports")
    op.drop_table("lab_reports")
