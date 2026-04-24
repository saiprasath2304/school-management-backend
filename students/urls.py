from django.urls import path
from .views import (
    AcademicYearListCreate, AcademicYearDetail,
    GradeListCreate, GradeDetail,
    SubjectListCreate, SubjectDetail,
    ClassRoomListCreate, ClassRoomDetail,
    StudentListCreate, StudentDetail,
    StaffListCreate, StaffDetail,
)

urlpatterns = [
    path("academic-years/",        AcademicYearListCreate.as_view(), name="academic-year-list"),
    path("academic-years/<int:pk>/", AcademicYearDetail.as_view(),   name="academic-year-detail"),

    path("grades/",          GradeListCreate.as_view(), name="grade-list"),
    path("grades/<int:pk>/", GradeDetail.as_view(),     name="grade-detail"),

    path("subjects/",          SubjectListCreate.as_view(), name="subject-list"),
    path("subjects/<int:pk>/", SubjectDetail.as_view(),     name="subject-detail"),

    path("classes/",          ClassRoomListCreate.as_view(), name="classroom-list"),
    path("classes/<int:pk>/", ClassRoomDetail.as_view(),     name="classroom-detail"),

    path("students/",          StudentListCreate.as_view(), name="student-list"),
    path("students/<int:pk>/", StudentDetail.as_view(),     name="student-detail"),

    path("staff/",          StaffListCreate.as_view(), name="staff-list"),
    path("staff/<int:pk>/", StaffDetail.as_view(),     name="staff-detail"),
]
