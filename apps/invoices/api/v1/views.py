"""
Invoices views
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.invoices.models import Invoice
from apps.invoices.api.v1.serializers import InvoiceSerializer
from apps.workspaces.permissions import IsWorkspaceMember


@extend_schema(tags=["Invoices"])
class InvoiceViewSet(viewsets.GenericViewSet):
    """
    Invoice viewset providing invoice retrieval within a workspace.
    """

    permission_classes = [IsAuthenticated, IsWorkspaceMember]

    @action(detail=False, methods=["GET"], url_path="list")
    def get_list(self, request, workspace_id=None):
        """
        Get invoices for a specific workspace by workspace_id path parameter.
        """
        invoices = Invoice.objects.filter(workspace_id=workspace_id)

        # Use DRF pagination if configured globally
        page = self.paginate_queryset(invoices)
        if page is not None:
            serializer = InvoiceSerializer(page, many=True, include_user=True)
            return self.get_paginated_response(serializer.data)

        # Fallback: no pagination
        serializer = InvoiceSerializer(invoices, many=True, include_user=True)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"], url_path="create")
    def create_new(self, request, workspace_id=None):
        """
        Create an invoice for a specific workspace by workspace_id path parameter.
        """
        # Copy request data and add workspace_id
        data = request.data.copy()
        data["workspace_id"] = workspace_id

        created_by = request.user
        serializer = InvoiceSerializer(
            data=data,
            context={"workspace_id": workspace_id, "created_by": created_by},
            include_user=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
