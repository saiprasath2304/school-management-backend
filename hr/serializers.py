from rest_framework import serializers
from .models import LeaveType, LeaveApplication, Payroll


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LeaveType
        fields = "__all__"
        read_only_fields = ["school"]


class LeaveApplicationSerializer(serializers.ModelSerializer):
    staff_name     = serializers.CharField(source="staff.user.get_full_name", read_only=True)
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    total_days     = serializers.IntegerField(read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.get_full_name", read_only=True)

    class Meta:
        model  = LeaveApplication
        fields = [
            "id", "staff", "staff_name", "leave_type", "leave_type_name",
            "from_date", "to_date", "total_days", "reason",
            "status", "applied_on", "reviewed_by", "reviewed_by_name",
            "reviewed_on", "admin_remarks",
        ]
        read_only_fields = ["applied_on", "reviewed_on", "school"]


class PayrollSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.user.get_full_name", read_only=True)
    employee_id = serializers.CharField(source="staff.employee_id", read_only=True)

    class Meta:
        model  = Payroll
        fields = [
            "id", "staff", "staff_name", "employee_id", "month",
            "base_salary", "allowances", "deductions",
            "loss_of_pay_days", "loss_of_pay_amount", "net_salary",
            "status", "payment_date", "payment_reference", "remarks",
            "created_by", "created_at",
        ]
        read_only_fields = ["created_at", "school"]
