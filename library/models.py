# ─────────────────────────────────────────────────────────────────
# library/models.py
# ─────────────────────────────────────────────────────────────────
from django.db import models
from students.models import Student


class Book(models.Model):
    class Category(models.TextChoices):
        FICTION     = "fiction",     "Fiction"
        NON_FICTION = "non_fiction", "Non-Fiction"
        TEXTBOOK    = "textbook",    "Textbook"
        REFERENCE   = "reference",   "Reference"
        PERIODICAL  = "periodical",  "Periodical"
        OTHER       = "other",       "Other"

    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="books")
    book_id       = models.CharField(max_length=30)
    title         = models.CharField(max_length=300)
    author        = models.CharField(max_length=200)
    publisher     = models.CharField(max_length=200, blank=True)
    isbn          = models.CharField(max_length=30, blank=True)
    category      = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    total_copies  = models.PositiveSmallIntegerField(default=1)
    available_copies = models.PositiveSmallIntegerField(default=1)
    added_on      = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "book_id")
        ordering = ["title"]

    def __str__(self):
        return f"[{self.book_id}] {self.title} by {self.author}"

    @property
    def is_available(self):
        return self.available_copies > 0


class BookIssue(models.Model):
    class Status(models.TextChoices):
        ISSUED   = "issued",   "Issued"
        RETURNED = "returned", "Returned"
        LOST     = "lost",     "Lost"

    school           = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="book_issues")
    book             = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issues")
    student          = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="book_issues")
    issued_date      = models.DateField()
    due_date         = models.DateField()
    returned_date    = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=10, choices=Status.choices, default=Status.ISSUED)
    issued_by        = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="issued_books"
    )
    returned_remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-issued_date"]

    def __str__(self):
        return f"{self.book.book_id} → {self.student} [{self.status}]"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.status == "issued":
            return timezone.now().date() > self.due_date
        return False

    @property
    def overdue_days(self):
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
