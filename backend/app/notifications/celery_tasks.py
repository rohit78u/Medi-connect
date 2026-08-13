from app.core.celery_app import celery_app
from app.notifications.email import EmailNotificationService


@celery_app.task(name="send_appointment_confirmation_email_task", bind=True, max_retries=3)
def send_appointment_confirmation_email_task(
    self,
    recipient_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str
):
    """
    Celery background task delivering appointment confirmation emails asynchronously.
    """
    try:
        return EmailNotificationService.send_appointment_confirmation(
            recipient_email=recipient_email,
            patient_name=patient_name,
            doctor_name=doctor_name,
            appointment_date=appointment_date
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_status_update_email_task", bind=True, max_retries=3)
def send_status_update_email_task(
    self,
    recipient_email: str,
    patient_name: str,
    status_str: str,
    clinical_notes: str | None = None
):
    """
    Celery background task delivering appointment status change notifications.
    """
    try:
        return EmailNotificationService.send_status_update_notification(
            recipient_email=recipient_email,
            patient_name=patient_name,
            status_str=status_str,
            clinical_notes=clinical_notes
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
