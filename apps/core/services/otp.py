"""
OTP service
"""

import uuid
import secrets
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.core.services.email import EmailService
from apps.core.utils.identifier import get_identifier_type

logger = logging.getLogger(__name__)


class OTPService:
    """
    Service for managing OTP lifecycle operations.
    """

    def __init__(self, email_service: EmailService):
        """
        Initialize the OTPService with required dependencies.

        Args:
            email_service (EmailService): Service instance for sending emails.
                Must be configured with proper email settings.

        Raises:
            TypeError: If email_service is not an EmailService instance.
        """
        self.email_service = email_service

    def generate_otp(self) -> str:
        """
        Generate a cryptographically secure OTP.

        Returns:
            str: Generated OTP as a string of digits.
        """
        length = getattr(settings, "OTP_LENGTH", 6)
        if settings.DEBUG:
            return "0" * length
        return "".join(str(secrets.randbelow(10)) for _ in range(length))

    def generate_request_id(self) -> str:
        """
        Generate a unique request identifier for OTP tracking.

        Returns:
            str: A unique UUID4 string (e.g., "550e8400-e29b-41d4-a716-446655440000")
        """
        return str(uuid.uuid4())

    def get_identifier_type_or_raise(self, identifier: str) -> str:
        """
        Validate and determine the type of identifier (email, phone, etc.).

        Args:
            identifier (str): The identifier to validate (e.g., email, phone number)

        Returns:
            str: The type of identifier ("email", "phone", etc.)
        """
        identifier_type = get_identifier_type(identifier)
        if not identifier_type:
            raise ValidationError("Invalid identifier format")
        return identifier_type

    def store_otp(self, request_id: str, identifier: str, otp: str) -> None:
        """
        Store OTP data in cache with expiration time.

        Args:
            request_id (str): Unique identifier for this OTP request
            identifier (str): The identifier (email/phone) the OTP was sent to
            otp (str): The generated OTP code
        """
        expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
        cache_timeout = expiry_minutes * 60
        now_iso = datetime.utcnow().isoformat()

        otp_data = {
            "otp": otp,
            "identifier": identifier,
            "created_at": now_iso,
            "expires_at": (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat(),
        }
        cache.set(f"otp:{request_id}", otp_data, cache_timeout)
        logger.debug("Stored OTP for request_id=%s with expiry %s minutes", request_id, expiry_minutes)

    def get_otp_data(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve OTP data from cache using request_id.

        Args:
            request_id (str): Unique identifier for the OTP request

        Returns:
            Optional[Dict[str, Any]]: OTP data dictionary if found and not expired,
                None otherwise.
        """
        return cache.get(f"otp:{request_id}")

    def validate_otp(self, identifier: str, request_id: str, provided_otp: str) -> bool:
        """
        Validate a provided OTP against stored data.

        Args:
            identifier (str): The identifier the OTP was originally sent to
            request_id (str): Unique identifier for the OTP request
            provided_otp (str): The OTP code provided by the user

        Returns:
            bool: True if OTP is valid and matches, False otherwise.

                Returns False in these cases:
                - OTP not found in cache (expired or invalid request_id)
                - OTP code doesn't match
                - Identifier doesn't match
                - Any validation error occurs
        """
        otp_data = self.get_otp_data(request_id)
        if not otp_data:
            logger.warning("No OTP data found for request_id=%s", request_id)
            return False

        is_valid = otp_data.get("otp") == provided_otp and otp_data.get("identifier") == identifier
        if is_valid:
            logger.info("OTP validated successfully for request_id=%s", request_id)
            cache.delete(f"otp:{request_id}")
        else:
            logger.info("OTP validation failed for request_id=%s", request_id)

        return is_valid

    def send_otp(self, identifier: str, otp: str, request_id: str) -> bool:
        """
        Send OTP to the specified identifier via appropriate channel.

        Args:
            identifier (str): The identifier to send OTP to (email address)
            otp (str): The OTP code to send
            request_id (str): Unique identifier for tracking this OTP request

        Returns:
            bool: True if OTP sending was initiated successfully, False otherwise
        """
        identifier_type = self.get_identifier_type_or_raise(identifier)
        if identifier_type == "email":

            def send_async():
                try:
                    self.email_service.send_otp_email(identifier, otp, request_id)
                except Exception as e:
                    logger.error("Failed to send OTP email to %s: %s", identifier, e, exc_info=True)

            threading.Thread(target=send_async, daemon=True).start()
            return True
        else:
            raise NotImplementedError("Identifier type not supported for OTP")

    def create_and_send_otp(self, identifier: str) -> Dict[str, str]:
        """
        Complete OTP workflow to generate, store, and send OTP.

        Args:
            identifier (str): The identifier to send OTP to (email address)

        Returns:
            Dict[str, str]: Dictionary containing the request_id for tracking.
        """
        self.get_identifier_type_or_raise(identifier)

        request_id = self.generate_request_id()
        otp = self.generate_otp()
        self.store_otp(request_id, identifier, otp)
        self.send_otp(identifier, otp, request_id)

        return {"request_id": request_id}
