"""
Invoices models
"""

import uuid
from django.db import models
from apps.workspaces.models.workspace import Workspace
from apps.users.models import User


class InvoiceManager(models.Manager):
    """
    Custom manager with helper method to create invoices.
    """

    def create_invoice(self, workspace, created_by, **kwargs):
        """
        Create an invoice with mandatory workspace and creator.
        Optional fields can be passed as kwargs.
        """
        defaults = {
            "description": "",
            "amount": 0.0,
            "status": InvoiceStatus.DRAFT,
            "type": InvoiceType.INVOICE,
            "due_date": None,
            "paid_date": None,
            "file_url": None,
        }
        defaults.update(kwargs)

        return self.create(
            workspace=workspace,
            created_by=created_by,
            description=defaults["description"],
            amount=defaults["amount"],
            status=defaults["status"],
            type=defaults["type"],
            due_date=defaults["due_date"],
            paid_date=defaults["paid_date"],
            file_url=defaults["file_url"],
        )


class InvoiceStatus(models.TextChoices):
    """
    Invoice status choices
    """

    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class InvoiceType(models.TextChoices):
    """
    Invoice type choices
    """

    INVOICE = "invoice", "Invoice"
    ESTIMATE = "estimate", "Estimate"
    RECEIPT = "receipt", "Receipt"
    CREDIT_NOTE = "credit_note", "Credit Note"


class Invoice(models.Model):
    """
    Invoice model
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    type = models.CharField(max_length=20, choices=InvoiceType.choices, default=InvoiceType.INVOICE)
    due_date = models.DateTimeField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = InvoiceManager()

    class Meta:
        """
        Meta class for Invoice model
        """

        db_table = "invoices"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-created_at"]

    def __str__(self):
        """
        String representation of Invoice model
        """

        return f"{self.id} - {self.amount}"
