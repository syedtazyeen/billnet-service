"""
OTP service for generating, storing, sending, and validating OTPs.
"""

import uuid
import random
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
from app.core.email_service import EmailService


class OTPService:
    """
    Service for managing OTP lifecycle (generate, store, send, validate).
    """

    @staticmethod
    def generate_otp() -> str:
        """
        Generate OTP.
        """
        length = getattr(settings, "OTP_LENGTH", 6)
        return str(random.randint(10 ** (length - 1), 10**length - 1))

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
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        phone_pattern = r"^\+?[1-9]\d{1,14}$"
        return bool(
            re.match(email_pattern, identifier) or re.match(phone_pattern, identifier)
        )

    @staticmethod
    def get_identifier_type(identifier: str) -> str:
        """
        Get identifier type (email or phone).
        """
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", identifier):
            return "email"
        if re.match(r"^\+?[1-9]\d{1,14}$", identifier):
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
            "attempts": 0,
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
    def validate_otp(request_id: str, provided_otp: str) -> Dict[str, Any]:
        """
        Validate OTP.
        """
        otp_data = OTPService.get_otp_data(request_id)
        if not otp_data:
            return {"valid": False, "error": "OTP expired or invalid request ID"}

        max_attempts = getattr(settings, "OTP_MAX_ATTEMPTS", 3)

        if otp_data["attempts"] >= max_attempts:
            cache.delete(f"otp:{request_id}")
            return {
                "valid": False,
                "error": "Maximum attempts exceeded. Please request a new OTP.",
            }

        otp_data["attempts"] += 1
        expiry_minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
        cache.set(f"otp:{request_id}", otp_data, expiry_minutes * 60)

        if otp_data["otp"] == provided_otp:
            cache.delete(f"otp:{request_id}")
            return {"valid": True, "identifier": otp_data["identifier"]}

        return {
            "valid": False,
            "error": "Invalid OTP",
            "attempts_remaining": max_attempts - otp_data["attempts"],
        }

    @staticmethod
    def send_otp(identifier: str, otp: str, request_id: str) -> bool:
        """
        Send OTP to identifier (email or phone).
        """
        identifier_type = OTPService.get_identifier_type(identifier)
        if identifier_type == "email":
            return EmailService.send_otp_email(identifier, otp, request_id)
        raise NotImplementedError("SMS OTP is not implemented yet")

    @classmethod
    def create_and_send_otp(cls, identifier: str) -> Dict[str, Any]:
        """
        Create and send OTP to identifier (email or phone).
        """
        if not cls.is_valid_identifier(identifier):
            raise ValidationError("Invalid identifier format")

        request_id = cls.generate_request_id()
        otp = cls.generate_otp()
        cls.store_otp(request_id, identifier, otp)
        sent = cls.send_otp(identifier, otp, request_id)

        return {"success": sent, "request_id": request_id, "identifier": identifier}
