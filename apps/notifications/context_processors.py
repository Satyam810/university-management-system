"""Context processor for unread notification count."""
from .models import Notification


def unread_count(request):
    """Add unread notification count to template context."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}
