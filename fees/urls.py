from django.urls import path
from .views import (
    FeeHeadListCreate, FeeHeadDetail,
    FeeStructureListCreate, FeeStructureDetail,
    FeeReceiptListCreate, FeeReceiptDetail,
    download_receipt_pdf, defaulter_list, student_balance,
)

urlpatterns = [
    path("heads/",              FeeHeadListCreate.as_view(),     name="fee-head-list"),
    path("heads/<int:pk>/",     FeeHeadDetail.as_view(),         name="fee-head-detail"),

    path("structures/",         FeeStructureListCreate.as_view(), name="fee-structure-list"),
    path("structures/<int:pk>/", FeeStructureDetail.as_view(),   name="fee-structure-detail"),

    path("receipts/",           FeeReceiptListCreate.as_view(),  name="fee-receipt-list"),
    path("receipts/<int:pk>/",  FeeReceiptDetail.as_view(),      name="fee-receipt-detail"),
    path("receipts/<int:pk>/pdf/", download_receipt_pdf,         name="fee-receipt-pdf"),

    path("defaulter_list/",     defaulter_list,                  name="fee-defaulter-list"),
    path("student_balance/",    student_balance,                  name="fee-student-balance"),
]
