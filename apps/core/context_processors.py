"""Context processors for templates."""
from django.utils import timezone
from .models import Announcement, Event


def site_context(request):
    """Add site-wide context."""
    return {
        'site_name': 'University Management System',
        'recent_announcements': Announcement.objects.filter(is_active=True)[:5],
        'upcoming_events': Event.objects.filter(is_active=True, event_date__gte=timezone.now().date())[:5],
    }
