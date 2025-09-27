"""
Email service for sending emails.
"""

import logging
from typing import Dict, Any, Optional, List
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending emails.
    """

    @staticmethod
    def send_email(
        subject: str,
        message: str,
        recipients: List[str],
        html_message: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send a plain-text or HTML email.
        """
        try:
            sender = from_email or settings.DEFAULT_FROM_EMAIL

            if html_message:
                # Send HTML email with plain text fallback
                email = EmailMultiAlternatives(subject, message, sender, recipients)
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                # Send plain text email
                send_mail(subject, message, sender, recipients)

            logger.info("Email sent to %s", recipients)
            return True
        except Exception as e:
            logger.error("Email send failed to %s: %s", recipients, e)
            return False

    @classmethod
    def send_template_email(
        cls,
        template: str,
        context: Dict[str, Any],
        subject: str,
        recipients: List[str],
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Render and send an email using HTML + optional TXT template.
        """
        try:
            # Render HTML template
            html_message = render_to_string(f"emails/{template}.html", context)

            # Try rendering TXT fallback template, else strip HTML
            try:
                text_message = render_to_string(f"emails/{template}.txt", context)
            except Exception:
                text_message = strip_tags(html_message)

            return cls.send_email(
                subject, text_message, recipients, html_message, from_email
            )
        except Exception as e:
            logger.error("Template email %s failed: %s", template, e)
            return False

    @classmethod
    def send_otp_email(cls, email: str, otp: str, request_id: str) -> bool:
        """
        Send an OTP verification email with expiry and support info.
        """
        context = {
            "otp": otp,
            "request_id": request_id,
            "expiry_minutes": getattr(settings, "OTP_EXPIRY_MINUTES", 5),
            "support_email": getattr(
                settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL
            ),
        }

        subject = f"{otp} is your verification code"
        logger.info("Sending OTP email to %s", email)

        return cls.send_template_email("otp_verification", context, subject, [email])
