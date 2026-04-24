from django.contrib import admin
from .models import FeeHead, FeeStructure, FeeReceipt


@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ("name", "is_recurring")


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display  = ("fee_head", "grade", "academic_year", "amount")
    list_filter   = ("academic_year", "grade", "fee_head")


@admin.register(FeeReceipt)
class FeeReceiptAdmin(admin.ModelAdmin):
    list_display  = ("receipt_number", "student", "fee_head", "amount_paid", "payment_date", "payment_mode")
    list_filter   = ("payment_mode", "academic_year", "fee_head")
    search_fields = ("receipt_number", "student__admission_number", "student__first_name")
    date_hierarchy = "payment_date"
    readonly_fields = ("receipt_number", "created_at")
