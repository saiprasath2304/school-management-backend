from django.urls import path
from .views import (
    ExamListCreate, ExamDetail,
    MarkListCreate, MarkDetail,
    bulk_enter_marks, class_marksheet,
    ReportCardListCreate,
    generate_report_card, release_report_card, download_report_card_pdf,
)

urlpatterns = [
    path("exams/",          ExamListCreate.as_view(), name="exam-list"),
    path("exams/<int:pk>/", ExamDetail.as_view(),     name="exam-detail"),

    path("marks/",              MarkListCreate.as_view(), name="mark-list"),
    path("marks/<int:pk>/",     MarkDetail.as_view(),     name="mark-detail"),
    path("marks/bulk_enter/",   bulk_enter_marks,         name="mark-bulk-enter"),
    path("marks/class_marksheet/", class_marksheet,       name="mark-class-marksheet"),

    path("report-cards/",                  ReportCardListCreate.as_view(), name="report-card-list"),
    path("report-cards/<int:pk>/generate/", generate_report_card,          name="report-card-generate"),
    path("report-cards/<int:pk>/release/",  release_report_card,           name="report-card-release"),
    path("report-cards/<int:pk>/pdf/",      download_report_card_pdf,      name="report-card-pdf"),
]
