import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payment import PaymentTransaction
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[PaymentTransaction]):
    """
    Data Access Repository for Payment Transactions using Async SQLAlchemy 2.0.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(PaymentTransaction, db)

    async def get_by_order_id(self, order_id: str) -> Optional[PaymentTransaction]:
        """
        Fetch payment transaction by Razorpay Order ID.
        """
        stmt = (
            select(PaymentTransaction)
            .where(PaymentTransaction.razorpay_order_id == order_id)
            .options(
                selectinload(PaymentTransaction.appointment),
                selectinload(PaymentTransaction.user)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_appointment_id(self, appointment_id: uuid.UUID) -> Optional[PaymentTransaction]:
        """
        Fetch payment transaction by Appointment ID.
        """
        stmt = (
            select(PaymentTransaction)
            .where(PaymentTransaction.appointment_id == appointment_id)
            .options(
                selectinload(PaymentTransaction.appointment),
                selectinload(PaymentTransaction.user)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
