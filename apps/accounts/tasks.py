from celery import shared_task

from api.v1.accounts.utils import send_otp_email


@shared_task(bind=True, max_retries=3)
def send_otp_email_task(self, email, otp, purpose):
    try:
        send_otp_email(email=email, otp=otp, purpose=purpose)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)