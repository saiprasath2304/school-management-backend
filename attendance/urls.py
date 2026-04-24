from django.urls import path
from .views import (
    AttendanceSessionListCreate,
    AttendanceSessionDetail,
    bulk_submit,
    class_grid,
    daily_report,
    student_monthly,
)

urlpatterns = [
    path("sessions/",          AttendanceSessionListCreate.as_view(), name="attendance-session-list"),
    path("sessions/<int:pk>/", AttendanceSessionDetail.as_view(),     name="attendance-session-detail"),
    path("bulk_submit/",       bulk_submit,                           name="attendance-bulk-submit"),
    path("class_grid/",        class_grid,                            name="attendance-class-grid"),
    path("daily_report/",      daily_report,                          name="attendance-daily-report"),
    path("student_monthly/",   student_monthly,                       name="attendance-student-monthly"),
]
