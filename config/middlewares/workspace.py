"""
Workspace Middleware

"""

import uuid
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import ValidationError


class WorkspaceMiddleware(MiddlewareMixin):
    """
    Attaches workspace_id from URL path params to the request object,
    if present and valid UUID.
    """

    def process_request(self, request):
        """
        Process request and attach workspace_id to the request object.
        """
        workspace_id = getattr(request, "resolver_match", None)
        if workspace_id and "workspace_id" in workspace_id.kwargs:
            wid = workspace_id.kwargs["workspace_id"]
            if not self._is_valid_uuid(wid):
                raise ValidationError("Invalid workspace ID")
            request.workspace_id = wid
        else:
            request.workspace_id = None
        return None

    def _is_valid_uuid(self, value):
        """
        Validate if the value is a valid UUID.
        """
        try:
            uuid.UUID(str(value))
            return True
        except (ValueError, TypeError):
            return False
