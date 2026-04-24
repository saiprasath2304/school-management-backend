from django.urls import path
from .views import (
    NoticeListCreate, NoticeDetail, publish_notice,
    TimetableListCreate, TimetableDetail,
    timetable_for_class, publish_class_timetable,
    my_dashboard,
)

urlpatterns = [
    path("notices/",           NoticeListCreate.as_view(), name="notice-list"),
    path("notices/<int:pk>/",  NoticeDetail.as_view(),     name="notice-detail"),
    path("notices/<int:pk>/publish/", publish_notice,      name="notice-publish"),

    path("timetable/",         TimetableListCreate.as_view(), name="timetable-list"),
    path("timetable/<int:pk>/", TimetableDetail.as_view(),   name="timetable-detail"),
    path("timetable/for_class/", timetable_for_class,        name="timetable-for-class"),
    path("timetable/publish_class/", publish_class_timetable, name="timetable-publish-class"),

    path("dashboard/",         my_dashboard,                 name="portal-dashboard"),
]
