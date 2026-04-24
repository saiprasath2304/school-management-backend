# ─────────────────────────────────────────────────────────────────
# accounts/models.py  — Custom User with school (tenant) FK
# ─────────────────────────────────────────────────────────────────
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN  = "super_admin",  "Super Admin"
        SCHOOL_ADMIN = "school_admin", "School Admin"
        TEACHER      = "teacher",      "Teacher"
        PARENT       = "parent",       "Parent"
        STUDENT      = "student",      "Student"
        ACCOUNTANT   = "accountant",   "Accountant"
        LIBRARIAN    = "librarian",    "Librarian"
        HR_ADMIN     = "hr_admin",     "HR Admin"

    role   = models.CharField(max_length=20, choices=Role.choices, default=Role.SCHOOL_ADMIN)
    phone  = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    # ── Multi-tenancy: every user belongs to one school ──────────
    # null=True for the platform super-admin who spans all schools
    school = models.ForeignKey(
        "tenants.School",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="users",
    )

    REQUIRED_FIELDS = ["email", "role"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        school_str = f" @ {self.school.name}" if self.school else " [platform]"
        return f"{self.get_full_name()} ({self.role}){school_str}"

    @property
    def is_school_admin(self):
        return self.role in (self.Role.SUPER_ADMIN, self.Role.SCHOOL_ADMIN)

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
