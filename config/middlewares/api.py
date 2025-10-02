"""
Combined API Middleware for versioning and exception handling.
"""

import logging
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


def error_response(status_code: int, message: str, details=None) -> JsonResponse:
    """
    Standardized JSON response for API errors.
    """
    payload = {
        "code": status_code,
        "message": message,
    }
    if details:
        payload["details"] = details
    return JsonResponse(payload, status=status_code)


class APIMiddleware(MiddlewareMixin):
    """
    Combined middleware to handle API versioning and exception handling.
    """

    def process_request(self, request):
        """Process API versioning for incoming requests."""
        path = request.path_info

        # Extract version from path
        path_parts = path.split("/")
        if len(path_parts) >= 3 and path_parts[1] == "api":
            version = path_parts[2]

            try:
                from config.urls import API_VERSIONS as urls_api_versions  # pylint: disable=import-outside-toplevel

                if version not in urls_api_versions:
                    return error_response(400, "Unsupported API version")
            except ImportError:
                # If import fails, skip validation
                pass

        return None

    def process_response(self, _, response):
        """Process API responses for error handling."""
        status_code = getattr(response, "status_code", 500)
        # Extract message from response if available
        details = getattr(response, "data", None)
        message = self._extract_message(details) or response.reason_phrase or "Error"
        if status_code >= 400:
            return error_response(status_code, message, details)

        return response

    def process_exception(self, _, exception):
        """Handle exceptions for API requests."""
        return self._handle_api_exception(exception)

    def _handle_api_exception(self, exc) -> JsonResponse:
        """
        Handle exceptions and return structured JSON with code, message, and details.
        """
        logger.exception("Unhandled exception: %s", exc)

        status_code = getattr(exc, "status_code", 500)
        details = getattr(exc, "detail", str(exc))  # DRF exceptions usually have .detail
        message = self._extract_message(details) or type(exc).__name__

        # In production, fallback to generic message for 500 errors
        if not settings.DEBUG and status_code == 500:
            message = "Internal Server Error"
            details = None

        return error_response(status_code, message, details)

    @staticmethod
    def _extract_message(details):
        """
        Extract a short string message.
        """
        if isinstance(details, (list, tuple)) and details:
            return str(details[0])
        if isinstance(details, dict):
            # Return first value in dict
            for val in details.values():
                if isinstance(val, (list, tuple)) and val:
                    return str(val[0])
                return str(val)
        if isinstance(details, str):
            return details
        return None
