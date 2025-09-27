"""
Custom exception handler for DRF.
"""

import logging
from typing import Any, Union
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """
    Handle all exceptions consistently with JSON response.
    """
    response = exception_handler(exc, context)

    logger.error("Unhandled exception: %s", exc, exc_info=True, stack_info=True)

    if response is not None:
        # For ValidationError with serializer.errors
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            response.data = {
                "code": getattr(exc, 'code', response.status_code),
                "detail": exc.detail,
            }
        else:
            # Normalize other exceptions
            detail: Union[str, Any] = response.data.get("detail", str(exc))
            response.data = {
                "code": getattr(exc, 'code', response.status_code),
                "detail": str(detail) if not isinstance(detail, str) else detail,
            }
        return response

    # Fallback generic response
    detail: Union[str, Any] = getattr(exc, "detail", "An unexpected error occurred.")
    return Response(
        {
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(detail) if not isinstance(detail, str) else detail,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
