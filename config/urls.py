"""
URL configuration for project.
"""

from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


API_VERSIONS = {
    "v1": [
        path("users/", include("apps.users.api.v1.urls")),
        path("auth/", include("apps.auth.api.v1.urls")),
    ],
}

urlpatterns = []

# Add API documentation and patterns for each version
for version, patterns in API_VERSIONS.items():
    urlpatterns.extend(
        [
            # API Documentation
            path(
                f"api/{version}/docs/",
                SpectacularSwaggerView.as_view(url_name=f"schema-{version}"),
                name=f"docs-{version}",
            ),
            path(
                f"api/{version}/schema/",
                SpectacularAPIView.as_view(),
                name=f"schema-{version}",
            ),
            # API endpoints
            path(f"api/{version}/", include(patterns)),
        ]
    )
