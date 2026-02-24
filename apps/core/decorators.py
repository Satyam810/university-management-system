"""Permission decorators for role-based access."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from apps.accounts.models import Role


def admin_required(view_func):
    """Decorator to require Admin role."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != Role.ADMIN:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


def faculty_required(view_func):
    """Decorator to require Faculty role."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != Role.FACULTY:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


def student_required(view_func):
    """Decorator to require Student role."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != Role.STUDENT:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


def admin_or_faculty_required(view_func):
    """Decorator for Admin or Faculty access."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role not in [Role.ADMIN, Role.FACULTY]:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped
