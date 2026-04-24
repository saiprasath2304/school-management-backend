from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ("username", "email", "get_full_name", "role", "is_active")
    list_filter   = ("role", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering      = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("School Role", {"fields": ("role", "phone", "avatar")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("School Role", {"fields": ("role", "phone")}),
    )
