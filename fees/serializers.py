from rest_framework import serializers
from .models import FeeHead, FeeStructure, FeeReceipt


class FeeHeadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FeeHead
        fields = "__all__"
        read_only_fields = ["school"]


class FeeStructureSerializer(serializers.ModelSerializer):
    fee_head_name  = serializers.CharField(source="fee_head.name", read_only=True)
    grade_name     = serializers.CharField(source="grade.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model  = FeeStructure
        fields = [
            "id", "academic_year", "academic_year_name",
            "grade", "grade_name", "fee_head", "fee_head_name", "amount",
        ]
        read_only_fields = ["school"]


class FeeReceiptSerializer(serializers.ModelSerializer):
    student_name   = serializers.CharField(source="student.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    fee_head_name  = serializers.CharField(source="fee_head.name", read_only=True)
    collected_by_name = serializers.CharField(source="collected_by.get_full_name", read_only=True)

    class Meta:
        model  = FeeReceipt
        fields = [
            "id", "receipt_number", "student", "student_name", "admission_number",
            "academic_year", "fee_head", "fee_head_name", "amount_paid",
            "payment_date", "payment_mode", "reference_number", "remarks",
            "collected_by", "collected_by_name", "created_at", "month",
        ]
        read_only_fields = ["receipt_number", "created_at", "school"]
