from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRoles(models.TextChoices):
    ADMIN = "admin", "Admin"
    BANK_OPERATOR = "bank_operator", "Bank Operator"
    ATOLYE_OPERATOR = "atolye_operator", "Atolye Operator"


class User(AbstractUser):

    role = models.CharField(max_length=20, choices=UserRoles.choices, default=UserRoles.ATOLYE_OPERATOR)

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
