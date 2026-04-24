# ─────────────────────────────────────────────────────────────────
# exams/models.py
# ─────────────────────────────────────────────────────────────────
from django.db import models
from students.models import ClassRoom, Student, Subject, AcademicYear


class Exam(models.Model):
    """A named exam event: Mid-Term, End of Term, Mock, etc."""
    class Term(models.TextChoices):
        TERM1 = "term1", "Term 1"
        TERM2 = "term2", "Term 2"
        TERM3 = "term3", "Term 3"

    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="exams")
    name          = models.CharField(max_length=100)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term          = models.CharField(max_length=10, choices=Term.choices)
    start_date    = models.DateField()
    end_date      = models.DateField()
    max_marks     = models.PositiveSmallIntegerField(default=100)
    is_active     = models.BooleanField(default=True)

    class Meta:
        unique_together = ("school", "name", "academic_year", "term")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} — {self.term} {self.academic_year}"


class Mark(models.Model):
    """A mark for one student in one subject for one exam."""
    school    = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="marks")
    exam      = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="marks")
    student   = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    subject   = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    remarks   = models.CharField(max_length=200, blank=True)
    entered_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="entered_marks"
    )
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("school", "exam", "student", "subject")

    def __str__(self):
        return f"{self.student} — {self.subject} — {self.exam}: {self.marks_obtained}"

    @property
    def percentage(self):
        return round((float(self.marks_obtained) / self.exam.max_marks) * 100, 2)

    @property
    def grade_letter(self):
        pct = self.percentage
        if pct >= 80: return "A+"
        if pct >= 70: return "A"
        if pct >= 60: return "B+"
        if pct >= 50: return "B"
        if pct >= 40: return "C"
        if pct >= 33: return "D"
        return "F"


class ReportCard(models.Model):
    """A generated report card PDF for a student for an exam."""
    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="report_cards")
    exam          = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="report_cards")
    student       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="report_cards")
    pdf_file      = models.FileField(upload_to="report_cards/", null=True, blank=True)
    is_released   = models.BooleanField(default=False, help_text="Visible to parent after admin releases")
    generated_at  = models.DateTimeField(null=True, blank=True)
    released_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("school", "exam", "student")

    def __str__(self):
        return f"Report Card — {self.student} — {self.exam}"
