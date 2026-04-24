from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display  = ("name", "subdomain", "country", "plan", "is_active", "trial_ends_at", "created_at")
    list_filter   = ("plan", "is_active", "country")
    search_fields = ("name", "subdomain", "email")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"subdomain": ("name",)}

    fieldsets = (
        ("Identity",      {"fields": ("name", "subdomain", "logo", "tagline")}),
        ("Contact",       {"fields": ("address", "phone", "email", "website")}),
        ("Locale",        {"fields": ("country", "currency", "timezone")}),
        ("Subscription",  {"fields": ("plan", "is_active", "trial_ends_at")}),
        ("Timestamps",    {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
