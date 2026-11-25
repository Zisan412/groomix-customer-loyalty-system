from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Groomix account", {"fields": ("role", "business_name", "phone", "address", "is_approved")}),
    )
    list_display = ("username", "email", "role", "business_name", "is_active")
    list_filter = ("role", "is_active", "is_approved")
