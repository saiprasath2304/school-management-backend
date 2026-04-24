from django.urls import path
from .views import (
    BookListCreate, BookDetail,
    BookIssueListCreate, BookIssueDetail,
    return_book, overdue_list,
)

urlpatterns = [
    path("books/",           BookListCreate.as_view(), name="book-list"),
    path("books/<int:pk>/",  BookDetail.as_view(),     name="book-detail"),

    path("issues/",             BookIssueListCreate.as_view(), name="book-issue-list"),
    path("issues/<int:pk>/",    BookIssueDetail.as_view(),     name="book-issue-detail"),
    path("issues/<int:pk>/return_book/", return_book,          name="book-return"),
    path("issues/overdue_list/",         overdue_list,         name="book-overdue-list"),
]
