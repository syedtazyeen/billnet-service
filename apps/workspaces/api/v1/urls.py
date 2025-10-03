"""Workspaces API v1 URLs"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.workspaces.api.v1.views import WorkspaceViewSet, UserWorkspaceViewSet

router = SimpleRouter()
router.register("", WorkspaceViewSet, basename="workspace")
router.register("", UserWorkspaceViewSet, basename="user-workspace")
urlpatterns = [
    *router.urls,
    path("<uuid:workspace_id>/invoices/", include("apps.invoices.api.v1.urls")),
    path("<uuid:workspace_id>/agent-conversations/", include("apps.agents.api.v1.urls")),
]


__all__ = ["urlpatterns"]
