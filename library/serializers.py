from rest_framework import serializers
from .models import Book, BookIssue


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Book
        fields = [
            "id", "book_id", "title", "author", "publisher",
            "isbn", "category", "total_copies", "available_copies",
            "is_available", "added_on",
        ]
        read_only_fields = ["added_on", "school"]


class BookIssueSerializer(serializers.ModelSerializer):
    book_title       = serializers.CharField(source="book.title", read_only=True)
    book_code        = serializers.CharField(source="book.book_id", read_only=True)
    student_name     = serializers.CharField(source="student.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    is_overdue       = serializers.BooleanField(read_only=True)
    overdue_days     = serializers.IntegerField(read_only=True)
    issued_by_name   = serializers.CharField(source="issued_by.get_full_name", read_only=True)

    class Meta:
        model  = BookIssue
        fields = [
            "id", "book", "book_title", "book_code",
            "student", "student_name", "admission_number",
            "issued_date", "due_date", "returned_date", "status",
            "is_overdue", "overdue_days",
            "issued_by", "issued_by_name", "returned_remarks",
        ]

        read_only_fields = ["school"]