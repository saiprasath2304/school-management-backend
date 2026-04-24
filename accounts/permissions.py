from rest_framework.permissions import BasePermission
from .models import User


class IsSchoolAdmin(BasePermission):
    """Only super_admin and school_admin can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (User.Role.SUPER_ADMIN, User.Role.SCHOOL_ADMIN)
        )


class IsTeacherOrAdmin(BasePermission):
    """Teachers and admins can access."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (
                User.Role.SUPER_ADMIN,
                User.Role.SCHOOL_ADMIN,
                User.Role.TEACHER,
            )
        )


class IsAccountantOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (
                User.Role.SUPER_ADMIN,
                User.Role.SCHOOL_ADMIN,
                User.Role.ACCOUNTANT,
            )
        )


class IsHROrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (
                User.Role.SUPER_ADMIN,
                User.Role.SCHOOL_ADMIN,
                User.Role.HR_ADMIN,
            )
        )


class IsLibrarianOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in (
                User.Role.SUPER_ADMIN,
                User.Role.SCHOOL_ADMIN,
                User.Role.LIBRARIAN,
            )
        )
