"""Users API v1 URLs"""

from rest_framework.routers import SimpleRouter
from apps.users.api.v1.views import UserViewSet

router = SimpleRouter()
router.register("", UserViewSet, basename="user")
urlpatterns = router.urls


__all__ = ["urlpatterns"]
