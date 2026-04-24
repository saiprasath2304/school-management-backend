from django.contrib import admin
from .models import AttendanceSession, AttendanceRecord


class AttendanceRecordInline(admin.TabularInline):
    model   = AttendanceRecord
    extra   = 0
    fields  = ("student", "status", "remarks")
    readonly_fields = ("student",)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display  = ("classroom", "date", "is_submitted", "submitted_by")
    list_filter   = ("is_submitted", "classroom__grade", "date")
    search_fields = ("classroom__grade__name",)
    inlines       = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display  = ("student", "session", "status")
    list_filter   = ("status", "session__date")
    search_fields = ("student__admission_number", "student__first_name")
