from django.contrib import admin
from .models import Exam, Mark, ReportCard


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display  = ("name", "academic_year", "term", "start_date", "end_date", "max_marks", "is_active")
    list_filter   = ("academic_year", "term", "is_active")


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display  = ("student", "exam", "subject", "marks_obtained", "entered_by")
    list_filter   = ("exam", "subject")
    search_fields = ("student__admission_number", "student__first_name")


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display  = ("student", "exam", "is_released", "generated_at", "released_at")
    list_filter   = ("is_released", "exam")
    search_fields = ("student__admission_number",)
    readonly_fields = ("generated_at", "released_at")
