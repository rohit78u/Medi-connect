import hashlib
import hmac

import httpx

from app.core.config import settings
from app.core.logging import logger


class RazorpayService:
    """Small async Razorpay REST client used by the payment service."""

    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.base_url = settings.RAZORPAY_API_BASE_URL.rstrip("/")

    def _require_credentials(self) -> None:
        if not self.key_id or not self.key_secret:
            raise RuntimeError("Razorpay credentials are not configured")

    async def create_order(
        self,
        amount: float,
        currency: str = "INR",
        receipt_id: str | None = None,
    ) -> dict:
        """Create a real Razorpay order. Amount is converted from INR to paise."""
        self._require_credentials()
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

        payload = {
            "amount": int(round(amount * 100)),
            "currency": currency.upper(),
            "receipt": receipt_id,
            "payment_capture": 1,
        }
        if not payload["receipt"]:
            payload.pop("receipt")

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{self.base_url}/orders",
                json=payload,
                auth=(self.key_id, self.key_secret),
            )

        if response.is_error:
            logger.error("Razorpay order creation failed: %s", response.text[:500])
            raise RuntimeError("Razorpay order creation failed")

        return response.json()

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> bool:
        """Verify Razorpay's HMAC-SHA256 checkout signature."""
        if not self.key_secret:
            logger.error("Razorpay secret is not configured")
            return False

        message = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
        generated_signature = hmac.new(
            self.key_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(generated_signature, razorpay_signature)


razorpay_service = RazorpayService()
