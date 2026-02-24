"""Role-based access control mixins."""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from .models import Role


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to Admin users only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == Role.ADMIN

    def handle_no_permission(self):
        return redirect('core:home')


class FacultyRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to Faculty users only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == Role.FACULTY

    def handle_no_permission(self):
        return redirect('core:home')


class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access to Student users only."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == Role.STUDENT

    def handle_no_permission(self):
        return redirect('core:home')


class AdminOrFacultyMixin(UserPassesTestMixin):
    """Mixin for Admin or Faculty access."""
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in [Role.ADMIN, Role.FACULTY]
