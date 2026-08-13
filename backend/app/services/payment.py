from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom_exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.models.appointment import AppointmentStatus
from app.models.payment import PaymentStatus
from app.models.user import User
from app.payments.razorpay_service import razorpay_service
from app.repositories.appointment import AppointmentRepository
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentOrderCreate, PaymentResponse, PaymentVerifyRequest


class PaymentService:
    """Secure consultation checkout and Razorpay verification service."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.appointment_repo = AppointmentRepository(db)

    async def create_payment_order(
        self,
        current_user: User,
        data: PaymentOrderCreate,
    ) -> PaymentResponse:
        appointment = await self.appointment_repo.get_with_details(data.appointment_id)
        if not appointment:
            raise NotFoundException("Target appointment does not exist.")

        if appointment.patient.user_id != current_user.id:
            raise ForbiddenException("You can only pay for your own appointments.")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise BadRequestException("Cancelled appointments cannot be paid for.")

        existing_tx = await self.payment_repo.get_by_appointment_id(data.appointment_id)
        if existing_tx and existing_tx.status == PaymentStatus.SUCCESS:
            raise BadRequestException("Payment has already been completed for this appointment.")

        # Never trust a client-supplied amount. The doctor's configured fee is authoritative.
        amount = float(appointment.doctor.consultation_fee)
        if amount <= 0:
            raise BadRequestException("Doctor consultation fee is not configured.")

        currency = data.currency.upper()
        razorpay_order = await razorpay_service.create_order(
            amount=amount,
            currency=currency,
            receipt_id=f"appnt_{str(data.appointment_id)[:8]}",
        )

        payment_data = {
            "appointment_id": data.appointment_id,
            "user_id": current_user.id,
            "razorpay_order_id": razorpay_order["id"],
            "amount": amount,
            "currency": currency,
            "status": PaymentStatus.CREATED,
        }

        payment_tx = await self.payment_repo.create(payment_data)
        await self.db.commit()
        refetched = await self.payment_repo.get_by_id(payment_tx.id)
        return PaymentResponse.model_validate(refetched)

    async def verify_payment(
        self,
        current_user: User,
        data: PaymentVerifyRequest,
    ) -> PaymentResponse:
        tx = await self.payment_repo.get_by_order_id(data.razorpay_order_id)
        if not tx:
            raise NotFoundException("Payment transaction for order ID not found.")

        if tx.user_id != current_user.id:
            raise ForbiddenException("You can only verify your own payment transaction.")

        if tx.status == PaymentStatus.SUCCESS:
            raise BadRequestException("Payment has already been verified.")

        appointment = await self.appointment_repo.get_with_details(tx.appointment_id)
        if not appointment or appointment.patient.user_id != current_user.id:
            raise ForbiddenException("Payment is not associated with your appointment.")

        is_valid = razorpay_service.verify_payment_signature(
            razorpay_order_id=data.razorpay_order_id,
            razorpay_payment_id=data.razorpay_payment_id,
            razorpay_signature=data.razorpay_signature,
        )

        if not is_valid:
            await self.payment_repo.update(tx, {"status": PaymentStatus.FAILED})
            await self.db.commit()
            raise BadRequestException("Invalid payment signature verification failed.")

        updated_tx = await self.payment_repo.update(tx, {
            "status": PaymentStatus.SUCCESS,
            "razorpay_payment_id": data.razorpay_payment_id,
            "razorpay_signature": data.razorpay_signature,
        })

        await self.appointment_repo.update(
            appointment,
            {"status": AppointmentStatus.CONFIRMED},
        )
        await self.db.commit()

        refetched = await self.payment_repo.get_by_id(updated_tx.id)
        return PaymentResponse.model_validate(refetched)
