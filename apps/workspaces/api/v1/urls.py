"""Workspaces API v1 URLs"""

from rest_framework.routers import SimpleRouter
from apps.workspaces.api.v1.views import WorkspaceViewSet

router = SimpleRouter()
router.register("", WorkspaceViewSet, basename="workspace")
urlpatterns = router.urls


__all__ = ["urlpatterns"]
