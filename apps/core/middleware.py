"""Custom middleware for activity logging and session expiry."""
from django.utils.deprecation import MiddlewareMixin
from .models import ActivityLog


class ActivityLoggingMiddleware(MiddlewareMixin):
    """Log user activity for security auditing."""
    def process_request(self, request):
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'DELETE']:
            # Log significant actions (avoid logging every request)
            path = request.path
            if any(x in path for x in ['/login/', '/logout/', '/create/', '/delete/', '/upload/']):
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"{request.method} {path}",
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
        return None

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class SessionExpiryMiddleware(MiddlewareMixin):
    """Ensure session expiry is respected."""
    def process_request(self, request):
        if request.user.is_authenticated and request.session.get_expiry_age() <= 0:
            from django.contrib.auth import logout
            logout(request)
        return None
