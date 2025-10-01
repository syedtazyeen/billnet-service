"""
Auth API v1 URLs
"""

from rest_framework.routers import SimpleRouter
from apps.auth.api.v1.views import AuthViewSet

router = SimpleRouter()
router.register("", AuthViewSet, basename="auth")
urlpatterns = router.urls


__all__ = ["urlpatterns"]
