import hashlib
import hmac
import uuid
from app.core.config import settings
from app.core.logging import logger


class RazorpayService:
    """
    Razorpay Client SDK & Payment Gateway Integration.
    Handles order initialization and SHA256 HMAC signature verification.
    """
    def __init__(self, key_id: str = "rzp_test_mediconnect", key_secret: str = "rzp_secret_mediconnect_123"):
        self.key_id = key_id
        self.key_secret = key_secret

    def create_order(self, amount: float, currency: str = "INR", receipt_id: str | None = None) -> dict:
        """
        Create a new Razorpay checkout order.
        Amount in smallest currency unit (e.g., Paise for INR).
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
        logger.info(f"[RAZORPAY ORDER CREATED] Order ID: {generated_order_id} | Amount: {amount} {currency}")
        return order_payload

    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verifies Razorpay HMAC-SHA256 Payment Signature.
        Formula: HMAC_SHA256(order_id + "|" + payment_id, secret) == signature
        """
        msg = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
        generated_signature = hmac.new(
            self.key_secret.encode("utf-8"),
            msg,
            hashlib.sha256
        ).hexdigest()

        is_valid = hmac.compare_digest(generated_signature, razorpay_signature)
        if not is_valid:
            logger.warning(
                f"[RAZORPAY SIGNATURE MISMATCH] Order: {razorpay_order_id} | Received: {razorpay_signature} | Computed: {generated_signature}"
            )
        return is_valid


razorpay_service = RazorpayService()
