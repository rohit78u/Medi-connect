import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base Declarative class for all SQLAlchemy 2.0 ORM models.
    """
    pass


class UUIDMixin:
    """
    Mixin adding a UUID Primary Key `id`.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )


class TimestampMixin:
    """
    Mixin adding UTC `created_at` and `updated_at` timestamp fields.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SoftDeleteMixin:
    """
    Mixin adding soft deletion capability (`is_active` flag and `deleted_at` timestamp).
    """
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )


class BaseModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Abstract Base Model combining UUID Primary Key, Timestamps, and Soft Deletion.
    """
    __abstract__ = True
