# ─────────────────────────────────────────────────────────────────
# attendance/models.py
# ─────────────────────────────────────────────────────────────────
from django.db import models
from students.models import ClassRoom, Student


class AttendanceSession(models.Model):
    """One attendance-taking session = one class on one date."""
    school    = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="attendance_sessions")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="sessions")
    date      = models.DateField()
    submitted_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="submitted_attendance_sessions"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("school", "classroom", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.classroom} — {self.date}"


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "P", "Present"
        ABSENT  = "A", "Absent"
        LATE    = "L", "Late"
        EXCUSED = "E", "Excused"

    school  = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="attendance_records")
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    status  = models.CharField(max_length=1, choices=Status.choices, default=Status.PRESENT)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("school", "session", "student")

    def __str__(self):
        return f"{self.student.admission_number} — {self.session.date} — {self.status}"
