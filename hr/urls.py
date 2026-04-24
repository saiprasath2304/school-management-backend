from django.urls import path
from .views import (
    LeaveTypeListCreate, LeaveTypeDetail,
    LeaveApplicationListCreate, LeaveApplicationDetail,
    approve_leave, reject_leave,
    PayrollListCreate, PayrollDetail,
    process_payroll_month, mark_payroll_paid,
)

urlpatterns = [
    path("leave-types/",          LeaveTypeListCreate.as_view(), name="leave-type-list"),
    path("leave-types/<int:pk>/", LeaveTypeDetail.as_view(),     name="leave-type-detail"),

    path("leaves/",          LeaveApplicationListCreate.as_view(), name="leave-list"),
    path("leaves/<int:pk>/", LeaveApplicationDetail.as_view(),     name="leave-detail"),
    path("leaves/<int:pk>/approve/", approve_leave,                name="leave-approve"),
    path("leaves/<int:pk>/reject/",  reject_leave,                 name="leave-reject"),

    path("salaries/",                PayrollListCreate.as_view(), name="payroll-list"),
    path("salaries/<int:pk>/",       PayrollDetail.as_view(),     name="payroll-detail"),
    path("salaries/process/",        process_payroll_month,       name="payroll-process"),
    path("salaries/<int:pk>/mark_paid/", mark_payroll_paid,       name="payroll-mark-paid"),
]
