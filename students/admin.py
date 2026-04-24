from django.contrib import admin
from .models import AcademicYear, Grade, ClassRoom, Student, Subject, StaffProfile


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display  = ("name", "start_date", "end_date", "is_current")
    list_filter   = ("is_current",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering     = ("order",)


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display  = ("__str__", "class_teacher", "capacity")
    list_filter   = ("academic_year", "grade")
    search_fields = ("grade__name", "section")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ("admission_number", "full_name", "current_class", "is_active", "parent_phone")
    list_filter   = ("is_active", "gender", "current_class__grade")
    search_fields = ("admission_number", "first_name", "last_name", "parent_phone")
    list_select_related = True


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display  = ("code", "name", "grade")
    list_filter   = ("grade",)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display  = ("employee_id", "user", "department", "designation", "is_active")
    list_filter   = ("department", "is_active")
    search_fields = ("employee_id", "user__first_name", "user__last_name")
    filter_horizontal = ("subjects_taught",)
