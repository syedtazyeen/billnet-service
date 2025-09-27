"""
Permissions for the API.
"""

from rest_framework import permissions


class IsAuthenticatedForWrite(permissions.BasePermission):
    """
    Custom permission that requires authentication for write operations,
    but allows unauthenticated access for read operations.
    """

    def has_permission(self, request, view):
        # Allow unauthenticated access for read operations
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication for write operations
        return request.user and request.user.is_authenticated


class PublicReadAuthenticatedWrite(permissions.BasePermission):
    """
    Permission class that allows public read access but requires authentication for writes.
    """

    def has_permission(self, request, view):
        # Allow all read operations
        if request.method in permissions.SAFE_METHODS:
            return True

        # Require authentication for write operations
        return request.user and request.user.is_authenticated


class AuthenticatedOnly(permissions.BasePermission):
    """
    Permission class that requires authentication for all operations.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
