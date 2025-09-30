"""
Middleware to catch all errors and return structured JSON responses for API endpoints.
"""

import logging
from django.http import JsonResponse
from django.conf import settings

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


class ExceptionMiddleware:
    """
    Middleware to catch all errors for API routes.
    """

    API_PREFIX = "/api/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

            if self._is_api_request(request):
                status_code = getattr(response, "status_code", 500)
                # Extract message from response if available
                details = getattr(response, "data", None)
                message = self._extract_message(details) or response.reason_phrase or "Error"
                if status_code >= 400:
                    return error_response(status_code, message, details)

            return response

        except Exception as exc:
            return self._handle_api_exception(exc)

    def _is_api_request(self, request) -> bool:
        return request.path.startswith(self.API_PREFIX)

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
