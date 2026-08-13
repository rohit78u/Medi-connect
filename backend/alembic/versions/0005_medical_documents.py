"""add medical documents

Revision ID: 0005_medical_documents
Revises: 0004_lab_reports
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_medical_documents"
down_revision = "0004_lab_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "medical_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), nullable=False),
        sa.Column("medical_record_id", sa.Uuid(), nullable=True),
        sa.Column("lab_report_id", sa.Uuid(), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patient_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["medical_record_id"], ["medical_records.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lab_report_id"], ["lab_reports.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index("ix_medical_documents_patient_id", "medical_documents", ["patient_id"])
    op.create_index("ix_medical_documents_uploaded_by", "medical_documents", ["uploaded_by"])
    op.create_index("ix_medical_documents_medical_record_id", "medical_documents", ["medical_record_id"])
    op.create_index("ix_medical_documents_lab_report_id", "medical_documents", ["lab_report_id"])


def downgrade() -> None:
    op.drop_index("ix_medical_documents_lab_report_id", table_name="medical_documents")
    op.drop_index("ix_medical_documents_medical_record_id", table_name="medical_documents")
    op.drop_index("ix_medical_documents_uploaded_by", table_name="medical_documents")
    op.drop_index("ix_medical_documents_patient_id", table_name="medical_documents")
    op.drop_table("medical_documents")
