import hashlib
import hmac
import uuid

from app.core.config import settings
from app.core.logging import logger


class RazorpayService:
    """
    Razorpay client abstraction.

    Phase 1 removes hard-coded credentials. Phase 2 will replace the current
    local order simulation with the real Razorpay API/Checkout integration.
    """
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET

    def create_order(self, amount: float, currency: str = "INR", receipt_id: str | None = None) -> dict:
        """
        Create a local test order representation.

        The actual Razorpay order API integration is intentionally deferred to
        Phase 2. No gateway credentials are hard-coded here.
        """
        amount_in_paise = int(amount * 100)
        generated_order_id = f"order_{uuid.uuid4().hex[:14]}"

        order_payload = {
            "id": generated_order_id,
            "entity": "order",
            "amount": amount_in_paise,
            "currency": currency.upper(),
            "receipt": receipt_id or f"rcpt_{uuid.uuid4().hex[:10]}",
            "status": "created"
        }
        logger.info(f"[TEST PAYMENT ORDER CREATED] Order ID: {generated_order_id} | Amount: {amount} {currency}")
        return order_payload

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify a Razorpay HMAC-SHA256 payment signature when a gateway secret is configured.
        """
        if not self.key_secret:
            logger.error("Razorpay secret is not configured; payment verification cannot run.")
            return False

        msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
        generated_signature = hmac.new(
            self.key_secret.encode("utf-8"),
            msg,
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(generated_signature, razorpay_signature)
        if not is_valid:
            logger.warning(
                f"[RAZORPAY SIGNATURE MISMATCH] Order: {razorpay_order_id}"
            )
        return is_valid


razorpay_service = RazorpayService()
