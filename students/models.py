# ─────────────────────────────────────────────────────────────────
# students/models.py  — All models scoped to a School tenant
# ─────────────────────────────────────────────────────────────────
from django.db import models
from accounts.models import User


class AcademicYear(models.Model):
    school     = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="academic_years")
    name       = models.CharField(max_length=20)   # e.g. 2024-2025
    start_date = models.DateField()
    end_date   = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ("school", "name")
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.school.subdomain})"

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(school=self.school).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Grade(models.Model):
    school = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="grades")
    name   = models.CharField(max_length=50)
    order  = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("school", "name")
        ordering = ["order"]

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="classrooms")
    grade         = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="classrooms")
    section       = models.CharField(max_length=10, default="A")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="classrooms")
    class_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="class_teacher_of", limit_choices_to={"role": "teacher"}
    )
    capacity = models.PositiveSmallIntegerField(default=40)

    class Meta:
        unique_together = ("school", "grade", "section", "academic_year")

    def __str__(self):
        return f"{self.grade.name} {self.section} ({self.academic_year.name})"


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE   = "M", "Male"
        FEMALE = "F", "Female"
        OTHER  = "O", "Other"

    school           = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="students")
    admission_number = models.CharField(max_length=30)
    first_name       = models.CharField(max_length=100)
    last_name        = models.CharField(max_length=100)
    date_of_birth    = models.DateField()
    gender           = models.CharField(max_length=1, choices=Gender.choices)
    photo            = models.ImageField(upload_to="students/photos/", null=True, blank=True)
    id_document      = models.FileField(upload_to="students/docs/", null=True, blank=True)
    current_class    = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, related_name="students")
    admission_date   = models.DateField()
    is_active        = models.BooleanField(default=True)
    parent_user      = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="children", limit_choices_to={"role": "parent"}
    )
    parent_name   = models.CharField(max_length=200, blank=True)
    parent_phone  = models.CharField(max_length=20, blank=True)
    parent_email  = models.EmailField(blank=True)
    home_address  = models.TextField(blank=True)

    class Meta:
        unique_together = ("school", "admission_number")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.admission_number} — {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Subject(models.Model):
    school = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="subjects")
    name   = models.CharField(max_length=100)
    code   = models.CharField(max_length=20)
    grade  = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="subjects")

    class Meta:
        unique_together = ("school", "code")

    def __str__(self):
        return f"{self.code} — {self.name}"


class StaffProfile(models.Model):
    class Department(models.TextChoices):
        ACADEMIC  = "academic",  "Academic"
        ADMIN     = "admin",     "Administration"
        FINANCE   = "finance",   "Finance"
        FACILITY  = "facility",  "Facility"
        LIBRARY   = "library",   "Library"

    school          = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="staff")
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    employee_id     = models.CharField(max_length=30)
    department      = models.CharField(max_length=20, choices=Department.choices, default=Department.ACADEMIC)
    designation     = models.CharField(max_length=100)
    date_joined     = models.DateField()
    id_document     = models.FileField(upload_to="staff/docs/", null=True, blank=True)
    subjects_taught = models.ManyToManyField(Subject, blank=True, related_name="teachers")
    base_salary     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bank_account    = models.CharField(max_length=50, blank=True)
    bank_name       = models.CharField(max_length=100, blank=True)
    is_active       = models.BooleanField(default=True)

    class Meta:
        unique_together = ("school", "employee_id")

    def __str__(self):
        return f"{self.employee_id} — {self.user.get_full_name()}"
