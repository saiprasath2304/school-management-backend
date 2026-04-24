# ─────────────────────────────────────────────────────────────────
# portal/models.py
# ─────────────────────────────────────────────────────────────────
from django.db import models
from students.models import ClassRoom, Grade, AcademicYear, Subject
from accounts.models import User


class Notice(models.Model):
    """School announcements shown on the parent/student portal."""
    class Priority(models.TextChoices):
        LOW    = "low",    "Low"
        NORMAL = "normal", "Normal"
        HIGH   = "high",   "High / Urgent"

    school      = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="notices")
    title       = models.CharField(max_length=200)
    body        = models.TextField()
    image       = models.ImageField(upload_to="notices/", null=True, blank=True)
    priority    = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    is_published = models.BooleanField(default=False)
    # Target audience — null = all
    target_grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="notices")
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TimetableSlot(models.Model):
    """One slot in the weekly class timetable."""
    class Day(models.IntegerChoices):
        MONDAY    = 1, "Monday"
        TUESDAY   = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY  = 4, "Thursday"
        FRIDAY    = 5, "Friday"
        SATURDAY  = 6, "Saturday"

    school       = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="timetable_slots")
    classroom    = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="timetable_slots")
    day          = models.PositiveSmallIntegerField(choices=Day.choices)
    slot_number  = models.PositiveSmallIntegerField(help_text="Period number (1-8)")
    start_time   = models.TimeField()
    end_time     = models.TimeField()
    subject      = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    teacher      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={"role": "teacher"}
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        unique_together = ("school", "classroom", "day", "slot_number")
        ordering = ["day", "slot_number"]

    def __str__(self):
        return f"{self.classroom} — {self.get_day_display()} P{self.slot_number} — {self.subject}"
