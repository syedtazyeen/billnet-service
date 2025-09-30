"""
OTP service for generating, storing, sending, and validating OTPs.
"""

import uuid
import secrets
import re
import threading
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from app.core.email_service import EmailService

logger = logging.getLogger(__name__)

class OTPService:
    """
    Service for managing OTP lifecycle (generate, store, send, validate).
    """

    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE_REGEX = r"^\+?[1-9]\d{1,14}$"

    @staticmethod
    def generate_otp() -> str:
        """
        Generate OTP.
        """
        length = getattr(settings, "OTP_LENGTH", 6)
        if settings.DEBUG:
            return "000000"
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    @staticmethod
    def generate_request_id() -> str:
        """
        Generate request ID.
        """
        return str(uuid.uuid4())

    @staticmethod
    def is_valid_identifier(identifier: str) -> bool:
        """
        Check if identifier is valid (email or phone).
        """
        email_pattern = OTPService.EMAIL_REGEX
        phone_pattern = OTPService.PHONE_REGEX
        return bool(
            re.match(email_pattern, identifier) or re.match(phone_pattern, identifier)
        )

    @staticmethod
    def get_identifier_type(identifier: str) -> str:
        """
        Get identifier type (email or phone).
        """
        if re.match(OTPService.EMAIL_REGEX, identifier):
            return "email"
        if re.match(OTPService.PHONE_REGEX, identifier):
            return "phone"
        raise ValidationError("Invalid identifier format")

    @staticmethod
    def store_otp(request_id: str, identifier: str, otp: str) -> None:
        """
        Store OTP in cache.
        """
        expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
        cache_timeout = expiry_minutes * 60

        otp_data = {
            "otp": otp,
            "identifier": identifier,
            "created_at": datetime.now().isoformat(),
            "expires_at": (
                datetime.now() + timedelta(minutes=expiry_minutes)
            ).isoformat(),
        }

        cache.set(f"otp:{request_id}", otp_data, cache_timeout)

    @staticmethod
    def get_otp_data(request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get OTP data from cache.
        """
        return cache.get(f"otp:{request_id}")

    @staticmethod
    def validate_otp(identifier: str, request_id: str, provided_otp: str):
        """
        Validate OTP.
        """
        otp_data = OTPService.get_otp_data(request_id)
        if not otp_data:
            return False

        if otp_data["otp"] == provided_otp and otp_data["identifier"] == identifier:
            # cache.delete(f"otp:{request_id}")
            return True

        return False

    @staticmethod
    def send_otp(identifier: str, otp: str, request_id: str) -> bool:
        """
        Send OTP to identifier (email or phone).
        """
        identifier_type = OTPService.get_identifier_type(identifier)
        if identifier_type == "email":
            return EmailService.send_otp_email(identifier, otp, request_id)
        raise NotImplementedError("SMS OTP is not implemented yet")

    @staticmethod
    def create_and_send_otp(identifier: str):
        """
        Create and send OTP to identifier (email or phone).
        """
        if not OTPService.is_valid_identifier(identifier):
            raise ValidationError("Invalid identifier format")

        request_id = OTPService.generate_request_id()

        otp = OTPService.generate_otp()
        OTPService.store_otp(request_id, identifier, otp)

        # Send OTP in background thread
        def send_otp_async():
            try:
                OTPService.send_otp(identifier, otp, request_id)
            except Exception as e:
                logger.error("Failed to send OTP to %s: %s", identifier, e)

        thread = threading.Thread(target=send_otp_async, daemon=True)
        thread.start()

        return {"request_id": request_id}
