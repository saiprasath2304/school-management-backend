from django.contrib import admin
from .models import LeaveType, LeaveApplication, Payroll


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "max_days_per_year", "is_paid")


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display  = ("staff", "leave_type", "from_date", "to_date", "status", "applied_on")
    list_filter   = ("status", "leave_type")
    search_fields = ("staff__employee_id", "staff__user__first_name")
    readonly_fields = ("applied_on",)


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display  = ("staff", "month", "base_salary", "loss_of_pay_amount", "net_salary", "status")
    list_filter   = ("status", "month")
    search_fields = ("staff__employee_id", "staff__user__first_name")
    readonly_fields = ("created_at",)
