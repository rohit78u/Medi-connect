"""Add explicit doctor verification status.

Revision ID: 0006_doctor_verification
Revises: 0005_medical_documents
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_doctor_verification"
down_revision = "0005_medical_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "doctor_profiles",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_doctor_profiles_is_verified", "doctor_profiles", ["is_verified"])


def downgrade() -> None:
    op.drop_index("ix_doctor_profiles_is_verified", table_name="doctor_profiles")
    op.drop_column("doctor_profiles", "is_verified")
