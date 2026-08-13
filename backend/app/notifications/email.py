from app.core.logging import logger


class EmailNotificationService:
    """
    Transactional Email Notification Service.
    """
    @staticmethod
    def send_appointment_confirmation(
        recipient_email: str,
        patient_name: str,
        doctor_name: str,
        appointment_date: str
    ) -> bool:
        """
        Send appointment confirmation email payload.
        """
        subject = f"Appointment Confirmed with {doctor_name}"
        body = (
            f"Dear {patient_name},\n\n"
            f"Your clinical appointment with {doctor_name} has been successfully scheduled for {appointment_date}.\n\n"
            f"Thank you,\nMediConnect AI Healthcare Team"
        )
        logger.info(f"[EMAIL MOCK SENT] To: {recipient_email} | Subject: {subject} | Body Snippet: {body[:60]}...")
        return True

    @staticmethod
    def send_status_update_notification(
        recipient_email: str,
        patient_name: str,
        status_str: str,
        clinical_notes: str | None = None
    ) -> bool:
        """
        Send appointment status change notification.
        """
        subject = f"Appointment Update: Status changed to {status_str}"
        body = (
            f"Dear {patient_name},\n\n"
            f"Your appointment status is now [{status_str}].\n"
            f"Notes: {clinical_notes or 'N/A'}\n\n"
            f"MediConnect AI Healthcare Team"
        )
        logger.info(f"[EMAIL MOCK SENT] To: {recipient_email} | Subject: {subject}")
        return True
