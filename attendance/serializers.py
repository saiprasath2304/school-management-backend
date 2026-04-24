from rest_framework import serializers
from .models import AttendanceSession, AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)

    class Meta:
        model  = AttendanceRecord
        fields = ["id", "student", "student_name", "admission_number", "status", "remarks"]
        read_only_fields = ["school"]


class AttendanceSessionSerializer(serializers.ModelSerializer):
    records           = AttendanceRecordSerializer(many=True, read_only=True)
    classroom_name    = serializers.CharField(source="classroom.__str__", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)

    class Meta:
        model  = AttendanceSession
        fields = [
            "id", "classroom", "classroom_name", "date",
            "submitted_by", "submitted_by_name", "submitted_at",
            "is_submitted", "records",
        ]
        read_only_fields = ["school"]


class BulkAttendanceSubmitSerializer(serializers.Serializer):
    """Payload: { classroom, date, records: [{student, status, remarks}] }"""
    classroom = serializers.IntegerField()
    date      = serializers.DateField()
    records   = AttendanceRecordSerializer(many=True)
