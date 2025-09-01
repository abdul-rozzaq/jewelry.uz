from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("bank_operator", "Bank Operator"),
        ("atolye_operator", "Atolye Operator"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="atolye_operator")

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
