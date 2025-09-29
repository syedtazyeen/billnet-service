"""
ViewSet for managing invoices.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from app.invoices.models import Invoice
from app.invoices.serializers import InvoiceSerializer
from app.workspaces.members.models import WorkspaceMemberRole


class InvoiceViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing invoices.
    """

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Get serializer class for invoices.
        """
        return InvoiceSerializer

    def get_permissions(self):
        """
        Get permissions for invoices.
        """
        permissions_map = {
            "list": [IsAuthenticated],
            "retrieve": [IsAuthenticated],
            "create": [IsAuthenticated],
            "update": [IsAuthenticated],
        }
        permissions = permissions_map.get(self.action, [IsAuthenticated])
        return [permission() for permission in permissions]

    def get_queryset(self):
        """
        Get queryset for invoices.
        """
        querysets = {
            WorkspaceMemberRole.OWNER: self.queryset.all(),
            WorkspaceMemberRole.MEMBER: self.queryset.filter(
                workspace=self.request.user.workspace
            ),
        }
        queryset = querysets.get(
            self.request.user.workspace_member.role, self.queryset.all()
        )
        return queryset

    def create(self, request):
        """
        Perform create action.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workspace=self.request.user.workspace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self):
        """
        List all invoices for the current user's workspace.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, _, pk=None):
        """
        Retrieve a specific invoice by ID.
        """
        invoice = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Update a specific invoice by ID.
        """
        invoice = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
