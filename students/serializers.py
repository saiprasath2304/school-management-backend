from rest_framework import serializers
from .models import AcademicYear, Grade, ClassRoom, Student, Subject, StaffProfile
from accounts.serializers import UserSerializer


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AcademicYear
        fields = "__all__"
        read_only_fields = ["school"]


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Grade
        fields = "__all__"
        read_only_fields = ["school"]


class SubjectSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)

    class Meta:
        model  = Subject
        fields = ["id", "name", "code", "grade", "grade_name"]
        read_only_fields = ["school"]


class ClassRoomSerializer(serializers.ModelSerializer):
    grade_name         = serializers.CharField(source="grade.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    class_teacher_name = serializers.CharField(source="class_teacher.get_full_name", read_only=True)
    student_count      = serializers.SerializerMethodField()

    class Meta:
        model  = ClassRoom
        fields = [
            "id", "grade", "grade_name", "section", "academic_year",
            "academic_year_name", "class_teacher", "class_teacher_name",
            "capacity", "student_count",
        ]
        read_only_fields = ["school"]

    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()


class StudentSerializer(serializers.ModelSerializer):
    full_name       = serializers.CharField(read_only=True)
    current_class_name = serializers.CharField(source="current_class.__str__", read_only=True)

    class Meta:
        model  = Student
        fields = [
            "id", "admission_number", "first_name", "last_name", "full_name",
            "date_of_birth", "gender", "photo", "id_document",
            "current_class", "current_class_name", "admission_date", "is_active",
            "parent_user", "parent_name", "parent_phone", "parent_email", "home_address",
        ]
        read_only_fields = ["school"]


class StaffProfileSerializer(serializers.ModelSerializer):
    user            = UserSerializer(read_only=True)
    user_id         = serializers.PrimaryKeyRelatedField(
        source="user", queryset=__import__("accounts.models", fromlist=["User"]).User.objects.all(),
        write_only=True
    )
    subjects_taught_detail = SubjectSerializer(source="subjects_taught", many=True, read_only=True)

    class Meta:
        model  = StaffProfile
        fields = [
            "id", "user", "user_id", "employee_id", "department", "designation",
            "date_joined", "id_document", "subjects_taught", "subjects_taught_detail",
            "base_salary", "bank_account", "bank_name", "is_active",
        ]

        read_only_fields = ["school"]