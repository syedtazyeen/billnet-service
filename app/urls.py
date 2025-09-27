"""
URL configuration for the app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth.views import AuthViewSet
from .users.views import UserViewSet
from .health import HealthCheckView


router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("", include(router.urls)),
]
