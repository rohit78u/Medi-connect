from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_db
from app.models.user import User
from app.schemas.payment import PaymentOrderCreate, PaymentResponse, PaymentVerifyRequest
from app.schemas.response import APIResponse
from app.services.payment import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments & Gateway"])


@router.post(
    "/create-order",
    response_model=APIResponse[PaymentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Razorpay consultation payment order"
)
async def create_payment_order(
    data: PaymentOrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Initializes a Razorpay order for an appointment consultation checkout.
    """
    service = PaymentService(db)
    payment_response = await service.create_payment_order(current_user, data)
    return APIResponse(
        success=True,
        message="Razorpay payment order created successfully",
        data=payment_response
    )


@router.post(
    "/verify",
    response_model=APIResponse[PaymentResponse],
    status_code=status.HTTP_200_OK,
    summary="Verify Razorpay HMAC payment signature"
)
async def verify_payment(
    data: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Verifies Razorpay HMAC signature, marks payment as SUCCESS, and confirms appointment.
    """
    service = PaymentService(db)
    payment_response = await service.verify_payment(current_user, data)
    return APIResponse(
        success=True,
        message="Payment verified successfully. Appointment confirmed.",
        data=payment_response
    )
