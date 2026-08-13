import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import BadRequestException, NotFoundException
from app.models.appointment import AppointmentStatus
from app.models.payment import PaymentStatus
from app.models.user import User
from app.payments.razorpay_service import razorpay_service
from app.repositories.appointment import AppointmentRepository
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentOrderCreate, PaymentResponse, PaymentVerifyRequest


class PaymentService:
    """
    Business Logic Service for consultation checkout, Razorpay orders, and payment verification.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.appointment_repo = AppointmentRepository(db)

    async def create_payment_order(
        self,
        current_user: User,
        data: PaymentOrderCreate
    ) -> PaymentResponse:
        """
        Initialize a Razorpay checkout order for an appointment consultation fee.
        """
        appointment = await self.appointment_repo.get_by_id(data.appointment_id)
        if not appointment or not appointment.is_active:
            raise NotFoundException("Target appointment does not exist.")

        # Check existing transaction
        existing_tx = await self.payment_repo.get_by_appointment_id(data.appointment_id)
        if existing_tx and existing_tx.status == PaymentStatus.SUCCESS:
            raise BadRequestException("Payment has already been completed for this appointment.")

        # Call Razorpay SDK
        razorpay_order = razorpay_service.create_order(
            amount=data.amount,
            currency=data.currency,
            receipt_id=f"appnt_{str(data.appointment_id)[:8]}"
        )

        payment_data = {
            "appointment_id": data.appointment_id,
            "user_id": current_user.id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": data.amount,
            "currency": data.currency,
            "status": PaymentStatus.CREATED
        }

        payment_tx = await self.payment_repo.create(payment_data)
        await self.db.commit()

        refetched = await self.payment_repo.get_by_id(payment_tx.id)
        return PaymentResponse.model_validate(refetched)

    async def verify_payment(
        self,
        current_user: User,
        data: PaymentVerifyRequest
    ) -> PaymentResponse:
        """
        Verify Razorpay HMAC signature and confirm appointment payment.
        """
        tx = await self.payment_repo.get_by_order_id(data.razorpay_order_id)
        if not tx:
            raise NotFoundException("Payment transaction for order ID not found.")

        # Verify HMAC Signature
        is_valid = razorpay_service.verify_payment_signature(
            razorpay_order_id=data.razorpay_order_id,
            razorpay_payment_id=data.razorpay_payment_id,
            razorpay_signature=data.razorpay_signature
        )

        if not is_valid:
            await self.payment_repo.update(tx, {"status": PaymentStatus.FAILED})
            await self.db.commit()
            raise BadRequestException("Invalid payment signature verification failed.")

        # Update transaction status to SUCCESS
        updated_tx = await self.payment_repo.update(tx, {
            "status": PaymentStatus.SUCCESS,
            "razorpay_payment_id": data.razorpay_payment_id,
            "razorpay_signature": data.razorpay_signature
        })

        # Update appointment status to CONFIRMED
        appointment = await self.appointment_repo.get_by_id(tx.appointment_id)
        if appointment:
            await self.appointment_repo.update(appointment, {"status": AppointmentStatus.CONFIRMED})

        await self.db.commit()

        refetched = await self.payment_repo.get_by_id(tx.id)
        return PaymentResponse.model_validate(refetched)
