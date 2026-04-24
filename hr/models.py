# ─────────────────────────────────────────────────────────────────
# hr/models.py
# ─────────────────────────────────────────────────────────────────
from django.db import models
from students.models import StaffProfile


class LeaveType(models.Model):
    """Casual Leave, Sick Leave, Earned Leave, etc."""
    school              = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="leave_types")
    name                = models.CharField(max_length=100)
    max_days_per_year   = models.PositiveSmallIntegerField(default=12)
    is_paid             = models.BooleanField(default=True)

    class Meta:
        unique_together = ("school", "name")

    def __str__(self):
        return self.name


class LeaveApplication(models.Model):
    class Status(models.TextChoices):
        PENDING  = "pending",  "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="leave_applications")
    staff         = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name="leave_applications")
    leave_type    = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    from_date     = models.DateField()
    to_date       = models.DateField()
    reason        = models.TextField()
    status        = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    applied_on    = models.DateTimeField(auto_now_add=True)
    reviewed_by   = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_leaves"
    )
    reviewed_on   = models.DateTimeField(null=True, blank=True)
    admin_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-applied_on"]

    def __str__(self):
        return f"{self.staff} — {self.leave_type} — {self.status}"

    @property
    def total_days(self):
        return (self.to_date - self.from_date).days + 1


class Payroll(models.Model):
    """Monthly salary record for each staff member."""
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PAID  = "paid",  "Paid"

    school            = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="payrolls")
    staff             = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name="payrolls")
    month             = models.CharField(max_length=7, help_text="YYYY-MM")
    base_salary       = models.DecimalField(max_digits=12, decimal_places=2)
    allowances        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    loss_of_pay_days  = models.PositiveSmallIntegerField(default=0)
    loss_of_pay_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary        = models.DecimalField(max_digits=12, decimal_places=2)
    status            = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    payment_date      = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    remarks           = models.TextField(blank=True)
    created_by        = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="created_payrolls"
    )
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "staff", "month")
        ordering = ["-month"]

    def __str__(self):
        return f"{self.staff} — {self.month} — {self.net_salary}"

    def calculate_net(self):
        self.net_salary = (
            self.base_salary + self.allowances
            - self.deductions - self.loss_of_pay_amount
        )
        return self.net_salary
