from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Client(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "email")

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In progress"
        ON_HOLD = "on_hold", "On hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user"]),
        ]

    def clean(self):
        super().clean()
        if self.client_id and self.user_id and self.client.user_id != self.user_id:
            raise ValidationError("Client must belong to the same user.")

    def __str__(self) -> str:
        return f"{self.name} ({self.client.name})"


class Invoice(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issue_date"]
        indexes = [
            models.Index(fields=["payment_status"]),
        ]

    def __str__(self) -> str:
        return f"Invoice {self.number}"


class ContactLog(models.Model):
    class ContactType(models.TextChoices):
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"
        MEETING = "meeting", "Meeting"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contact_logs",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="contact_logs",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        related_name="contact_logs",
        null=True,
        blank=True,
    )
    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.EMAIL,
    )
    notes = models.TextField()
    contacted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-contacted_at"]

    def clean(self):
        super().clean()
        user_id = getattr(self, "user_id", None)
        if self.client_id and user_id and self.client.user_id != user_id:
            raise ValidationError("Client must belong to the same user.")
        if self.project_id and user_id and self.project.user_id != user_id:
            raise ValidationError("Project must belong to the same user.")

    def __str__(self) -> str:
        return f"{self.get_contact_type_display()} with {self.client.name}"
