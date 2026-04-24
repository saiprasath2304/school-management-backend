from django.contrib import admin
from .models import Notice, TimetableSlot


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display  = ("title", "priority", "is_published", "target_grade", "created_at", "expires_at")
    list_filter   = ("is_published", "priority")
    search_fields = ("title", "body")


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display  = ("classroom", "get_day_display", "slot_number", "start_time", "end_time", "subject", "teacher", "is_published")
    list_filter   = ("is_published", "day", "classroom__grade")
    search_fields = ("classroom__grade__name", "subject__name")
