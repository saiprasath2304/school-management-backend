from rest_framework import generics, permissions, status
from tenants.mixins import TenantMixin, require_school
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone

from accounts.permissions import IsLibrarianOrAdmin
from .models import Book, BookIssue
from .serializers import BookSerializer, BookIssueSerializer


# ── Books ─────────────────────────────────────────────────────────────────────
class BookListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset           = Book.objects.all()
    serializer_class   = BookSerializer
    permission_classes = [IsLibrarianOrAdmin]
    filterset_fields   = ["category"]
    search_fields      = ["book_id", "title", "author", "isbn"]


class BookDetail(TenantMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset           = Book.objects.all()
    serializer_class   = BookSerializer
    permission_classes = [IsLibrarianOrAdmin]


# ── Book Issues ───────────────────────────────────────────────────────────────
class BookIssueListCreate(TenantMixin, generics.ListCreateAPIView):
    queryset = BookIssue.objects.select_related(
        "book", "student", "issued_by"
    ).all()
    serializer_class   = BookIssueSerializer
    permission_classes = [IsLibrarianOrAdmin]
    filterset_fields   = ["status", "student", "book"]
    search_fields      = ["book__book_id", "student__admission_number", "student__first_name"]

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.available_copies < 1:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"No available copies of '{book.title}'.")
        book.available_copies -= 1
        book.save()
        serializer.save(issued_by=self.request.user)


class BookIssueDetail(TenantMixin, generics.RetrieveUpdateAPIView):
    queryset           = BookIssue.objects.all()
    serializer_class   = BookIssueSerializer
    permission_classes = [IsLibrarianOrAdmin]


@api_view(["POST"])
@permission_classes([IsLibrarianOrAdmin])
def return_book(request, pk):
    """
    school = require_school(request)
    POST /api/library/issues/<pk>/return_book/
    Body (optional): { remarks: "damaged" }
    Marks the issue as returned and increments available copies.
    """
    try:
        issue = BookIssue.objects.select_related("book").get(pk=pk)
    except BookIssue.DoesNotExist:
        return Response({"error": "Issue record not found."}, status=404)

    if issue.status == "returned":
        return Response({"error": "Book already returned."}, status=400)

    issue.status           = "returned"
    issue.returned_date    = timezone.now().date()
    issue.returned_remarks = request.data.get("remarks", "")
    issue.save()

    # Increment available copies
    book = issue.book
    book.available_copies = min(book.available_copies + 1, book.total_copies)
    book.save()

    return Response(BookIssueSerializer(issue).data)


@api_view(["GET"])
@permission_classes([IsLibrarianOrAdmin])
def overdue_list(request):
    """
    school = require_school(request)GET /api/library/issues/overdue_list/ — all currently overdue issues."""
    today = timezone.now().date()
    overdue = BookIssue.objects.filter(
        status="issued",
        due_date__lt=today,
    ).select_related("book", "student")

    data = [
        {
            "issue_id":         i.id,
            "book_id":          i.book.book_id,
            "book_title":       i.book.title,
            "student":          i.student.full_name,
            "admission_number": i.student.admission_number,
            "parent_phone":     i.student.parent_phone,
            "issued_date":      str(i.issued_date),
            "due_date":         str(i.due_date),
            "overdue_days":     i.overdue_days,
        }
        for i in overdue
    ]
    return Response({"count": len(data), "overdue": data})
