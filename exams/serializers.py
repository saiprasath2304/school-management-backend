from rest_framework import serializers
from .models import Exam, Mark, ReportCard


class ExamSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model  = Exam
        fields = [
            "id", "name", "academic_year", "academic_year_name",
            "term", "start_date", "end_date", "max_marks", "is_active",
        ]
        read_only_fields = ["school"]


class MarkSerializer(serializers.ModelSerializer):
    student_name     = serializers.CharField(source="student.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    subject_name     = serializers.CharField(source="subject.name", read_only=True)
    percentage       = serializers.FloatField(read_only=True)
    grade_letter     = serializers.CharField(read_only=True)

    class Meta:
        model  = Mark
        fields = [
            "id", "exam", "student", "student_name", "admission_number",
            "subject", "subject_name", "marks_obtained",
            "percentage", "grade_letter", "remarks",
            "entered_by", "entered_at", "updated_at",
        ]
        read_only_fields = ["entered_at", "updated_at", "school"]


class BulkMarkSerializer(serializers.Serializer):
    """Spreadsheet bulk entry: { exam, subject, records: [{student, marks_obtained}] }"""
    exam    = serializers.IntegerField()
    subject = serializers.IntegerField()
    records = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )


class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    exam_name    = serializers.CharField(source="exam.name", read_only=True)

    class Meta:
        model  = ReportCard
        fields = [
            "id", "exam", "exam_name", "student", "student_name",
            "pdf_file", "is_released", "generated_at", "released_at",
        ]

        read_only_fields = ["school"]