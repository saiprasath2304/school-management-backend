from django.contrib import admin
from .models import Book, BookIssue


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display  = ("book_id", "title", "author", "category", "total_copies", "available_copies")
    list_filter   = ("category",)
    search_fields = ("book_id", "title", "author", "isbn")


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display  = ("book", "student", "issued_date", "due_date", "status")
    list_filter   = ("status",)
    search_fields = ("book__book_id", "student__admission_number")
    date_hierarchy = "issued_date"
