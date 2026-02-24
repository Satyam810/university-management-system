"""Notification views."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    """List all notifications."""
    notifications = Notification.objects.filter(user=request.user)[:50]
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def notification_mark_read(request, pk):
    """Mark notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')
