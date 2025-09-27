"""
Health check endpoint.
"""

from django.http import JsonResponse
from django.views import View
from django.db import connection


class HealthCheckView(View):
    """
    Simple health check endpoint.
    """

    def get(self, _):
        """Return health status."""
        health_data = {"status": "healthy", "checks": {}}

        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_data["checks"]["database"] = "ok"
        except Exception as e:
            health_data["checks"]["database"] = f"error: {str(e)}"
            health_data["status"] = "unhealthy"

        # Return appropriate status code
        status_code = 200 if health_data["status"] == "healthy" else 503

        return JsonResponse(health_data, status=status_code)
