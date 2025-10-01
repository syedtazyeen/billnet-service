"""
Email service for sending emails asynchronously in background threads.
"""

import logging
import threading
from typing import Dict, Any, Optional, Sequence
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails with support for multiple formats and templates.
    """

    @staticmethod
    def _send_email_task(
        subject: str,
        message: str,
        recipients: Sequence[str],
        html_message: Optional[str],
        sender: str,
    ) -> None:
        """
        Internal task for sending emails in background threads.
        
        Args:
            subject (str): Email subject line
            message (str): Plain text email body
            recipients (Sequence[str]): List of recipient email addresses
            html_message (Optional[str]): HTML version of email body, if provided
            sender (str): Sender email address
        """
        try:
            if html_message:
                email = EmailMultiAlternatives(subject, message, sender, recipients)
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                send_mail(subject, message, sender, recipients)
            logger.info("Email sent to %s", recipients)
        except Exception as e:
            logger.error("Failed to send email to %s: %s", recipients, e, exc_info=True)

    @classmethod
    def send_email(
        cls,
        subject: str,
        message: str,
        recipients: Sequence[str],
        html_message: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send an email asynchronously with optional HTML content.
        
        Args:
            subject (str): Email subject line
            message (str): Plain text email body
            recipients (Sequence[str]): List of recipient email addresses
            html_message (Optional[str], optional): HTML version of email body.
                If provided, recipients will receive both text and HTML versions.
            from_email (Optional[str], optional): Sender email address.
                If not provided, uses DEFAULT_FROM_EMAIL from settings.
                
        Returns:
            bool: Always returns True as sending is initiated asynchronously.
                Check logs for actual delivery status.
        """
        sender = from_email or settings.DEFAULT_FROM_EMAIL
        threading.Thread(
            target=cls._send_email_task,
            args=(subject, message, recipients, html_message, sender),
            daemon=True,
        ).start()
        return True

    @classmethod
    def send_template_email(
        cls,
        template_name: str,
        context: Dict[str, Any],
        subject: str,
        recipients: Sequence[str],
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send an email using Django templates for content generation.
        
        Args:
            template_name (str): Base name of the template (without extension).
                Templates should be located at:
                - HTML: templates/emails/{template_name}.html
                - Text: templates/emails/{template_name}.txt (optional)
            context (Dict[str, Any]): Template context variables for rendering
            subject (str): Email subject line
            recipients (Sequence[str]): List of recipient email addresses
            from_email (Optional[str], optional): Sender email address.
                If not provided, uses DEFAULT_FROM_EMAIL from settings.
                
        Returns:
            bool: True if template rendering and email sending initiated successfully,
                False if template rendering failed.
        """
        try:
            html_message = render_to_string(f"{template_name}.html", context)
            text_message = strip_tags(html_message)
            return cls.send_email(subject, text_message, recipients, html_message, from_email)
        except Exception as e:
            logger.error(
                "Failed to render template email '%s' to %s: %s",
                template_name,
                recipients,
                e,
                exc_info=True,
            )
            return False

    @classmethod
    def send_otp_email(cls, email: str, otp: str, request_id: str) -> bool:
        """
        Send OTP verification email using template.
 
        Args:
            email (str): Recipient email address
            otp (str): The OTP code to include in the email
            request_id (str): Unique identifier for tracking this OTP request
            
        Returns:
            bool: True if email sending was initiated successfully, False otherwise
        """
        context = {
            "otp": otp,
            "request_id": request_id,
            "expiry_minutes": getattr(settings, "OTP_EXPIRY_MINUTES", 5),
            "support_email": getattr(settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL),
        }
        subject = f"{otp} is your verification code"
        logger.info("Sending OTP email to %s", email)

        return cls.send_template_email("otp_verification", context, subject, [email])
