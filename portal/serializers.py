from rest_framework import serializers
from .models import Notice, TimetableSlot


class NoticeSerializer(serializers.ModelSerializer):
    published_by_name = serializers.CharField(source="published_by.get_full_name", read_only=True)
    target_grade_name = serializers.CharField(source="target_grade.name", read_only=True)

    class Meta:
        model  = Notice
        fields = [
            "id", "title", "body", "image", "priority",
            "is_published", "target_grade", "target_grade_name",
            "published_by", "published_by_name", "created_at", "expires_at",
        ]
        read_only_fields = ["created_at", "school"]


class TimetableSlotSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    subject_name   = serializers.CharField(source="subject.name", read_only=True)
    teacher_name   = serializers.CharField(source="teacher.get_full_name", read_only=True)
    day_name       = serializers.CharField(source="get_day_display", read_only=True)

    class Meta:
        model  = TimetableSlot
        fields = [
            "id", "classroom", "classroom_name",
            "day", "day_name", "slot_number", "start_time", "end_time",
            "subject", "subject_name", "teacher", "teacher_name", "is_published",
        ]

        read_only_fields = ["school"]