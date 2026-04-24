# ─────────────────────────────────────────────────────────────────
# fees/models.py
# ─────────────────────────────────────────────────────────────────
from django.db import models
from students.models import Student, AcademicYear


class FeeHead(models.Model):
    """Categories of fees: Tuition, Uniform, Lab, Transport, etc."""
    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="fee_heads")
    name          = models.CharField(max_length=100)
    description   = models.TextField(blank=True)
    is_recurring  = models.BooleanField(default=True, help_text="Charged monthly")

    class Meta:
        unique_together = ("school", "name")

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """Amount due per fee head per grade per academic year."""
    school        = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="fee_structures")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade         = models.ForeignKey("students.Grade", on_delete=models.CASCADE)
    fee_head      = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount        = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("school", "academic_year", "grade", "fee_head")

    def __str__(self):
        return f"{self.fee_head} — {self.grade} — {self.academic_year} — {self.amount}"


class FeeReceipt(models.Model):
    """A manually entered payment transaction that generates a PDF receipt."""

    class PaymentMode(models.TextChoices):
        CASH         = "cash",         "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        MOBILE_MONEY  = "mobile_money",  "Mobile Money (M-Pesa)"
        CHEQUE       = "cheque",       "Cheque"

    school          = models.ForeignKey("tenants.School", on_delete=models.CASCADE, related_name="fee_receipts")
    receipt_number  = models.CharField(max_length=30)
    student         = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_receipts")
    academic_year   = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    fee_head        = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    amount_paid     = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date    = models.DateField()
    payment_mode    = models.CharField(max_length=20, choices=PaymentMode.choices)
    reference_number = models.CharField(max_length=100, blank=True, help_text="Bank ref / M-Pesa code")
    remarks         = models.TextField(blank=True)
    collected_by    = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, related_name="collected_receipts"
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    month           = models.CharField(max_length=7, blank=True, help_text="YYYY-MM for monthly fees")

    class Meta:
        unique_together = ("school", "receipt_number")
        ordering = ["-payment_date", "-created_at"]

    def __str__(self):
        return f"Receipt #{self.receipt_number} — {self.student}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last = FeeReceipt.objects.filter(school=self.school).order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            self.receipt_number = f"RCP-{next_id:06d}"
        super().save(*args, **kwargs)
