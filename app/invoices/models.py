"""
Invoice models
"""

import uuid
from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from app.workspaces.models import Workspace
from app.users.models import User


class InvoiceStatus(models.TextChoices):
    """Enum for invoice status choices."""

    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"


class InvoiceType(models.TextChoices):
    """Enum for invoice type choices."""

    INVOICE = "invoice", "Invoice"
    CREDIT_NOTE = "credit_note", "Credit Note"
    DEBIT_NOTE = "debit_note", "Debit Note"


class InvoiceManager(models.Manager):
    """Custom manager for Invoice model."""

    def by_status(self, status: InvoiceStatus):
        """Return invoices with the given status."""
        return self.filter(status=status)

    def by_type(self, type_: InvoiceType):
        """Return invoices with the given type."""
        return self.filter(type=type_)

    def generate_number(self, workspace: Workspace) -> str:
        """
        Generate the next incremental invoice number for a workspace with date prefix.
        Format: YYYYMMDD-XXXX
        """
        today_str = timezone.now().strftime("%Y%m%d")
        last_invoice = (
            self.filter(workspace=workspace, number__startswith=today_str)
            .order_by("-number")
            .first()
        )
        if last_invoice:
            # Extract last numeric suffix
            last_number = int(last_invoice.number.split("-")[-1])
            next_number = last_number + 1
        else:
            next_number = 1
        return f"{today_str}-{next_number}"


class Invoice(models.Model):
    """
    Invoice model representing billing details.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(
        max_length=50, help_text="Unique invoice number per workspace"
    )

    # Relations
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="invoices",
        help_text="Workspace owning this invoice",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_invoices",
        help_text="User who created the invoice",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="updated_invoices",
        null=True,
        blank=True,
        help_text="User who last updated the invoice",
    )

    # Details
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        help_text="Current invoice status",
    )
    type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.INVOICE,
        help_text="Type of the invoice",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Total invoice amount",
    )
    description = models.TextField(
        blank=True, null=True, help_text="Optional invoice description"
    )

    # Client info
    client = models.JSONField(
        default=dict,
        blank=True,
        help_text="Client details: must contain 'name', optional 'email', 'phone', 'address'",
    )

    # Dates
    due_date = models.DateField(null=True, blank=True, help_text="Payment due date")
    paid_date = models.DateField(
        null=True, blank=True, help_text="Date when invoice was paid"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Invoice creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Invoice last updated timestamp"
    )

    # Manager
    objects = InvoiceManager()

    class Meta:
        """Meta information for the Invoice model."""

        db_table = "invoices"
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-created_at"]
        unique_together = ("workspace", "number")

    def __str__(self) -> str:
        """Readable string representation."""
        client_name = (
            self.client.get("name", "Unknown Client")
            if isinstance(self.client, dict)
            else "Unknown Client"
        )
        return f"Invoice {self.number} - {client_name}"

    def clean(self):
        """Custom validation for client JSON."""
        super().clean()
        if not self.client or not isinstance(self.client, dict):
            raise ValidationError("Client must be a valid JSON object.")
        if not self.client.get("name") if isinstance(self.client, dict) else True:
            raise ValidationError("Client JSON must contain a 'name' field.")

    @property
    def is_paid(self) -> bool:
        """Check if the invoice is paid."""
        return self.status == InvoiceStatus.PAID

    @property
    def is_overdue(self) -> bool:
        """Check if the invoice is overdue."""
        if self.is_paid or self.status == InvoiceStatus.CANCELLED:
            return False
        if not self.due_date:
            return False
        return timezone.now().date() > self.due_date

    def mark_as_paid(self) -> None:
        """Mark the invoice as paid and set the paid date."""
        self.status = InvoiceStatus.PAID
        self.paid_date = timezone.now().date()
        self.save(update_fields=["status", "paid_date", "updated_at"])
