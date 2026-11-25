from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Factory Admin"
        WHOLESALER = "WHOLESALER", "Wholesaler"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.WHOLESALER)
    email = models.EmailField(unique=True)
    business_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
            self.is_approved = True
        super().save(*args, **kwargs)

    @property
    def is_factory_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return self.business_name or self.username
