"""Core views: home, messaging, announcements, documents."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

from .models import Announcement, Event, Message
from .forms import AnnouncementForm, EventForm
from apps.accounts.models import Role
from apps.core.decorators import admin_required
from apps.academics.models import StudentProfile
from apps.results.models import SemesterResult, Grade


def home(request):
    """Role-based dashboard redirect."""
    if request.user.is_authenticated:
        if request.user.role == Role.ADMIN:
            return redirect('analytics:admin_dashboard')
        elif request.user.role == Role.FACULTY:
            return redirect('analytics:faculty_dashboard')
        elif request.user.role == Role.STUDENT:
            return redirect('analytics:student_dashboard')
    return redirect('accounts:login')


@login_required
def announcement_list(request):
    """List announcements. Admin sees all with manage options."""
    if request.user.role == Role.ADMIN:
        announcements = Announcement.objects.all().order_by('-created_at')
    else:
        announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'core/announcements.html', {'announcements': announcements})


@admin_required
def announcement_create(request):
    """Create announcement - Admin only."""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            messages.success(request, 'Announcement created.')
            return redirect('core:announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'core/announcement_form.html', {'form': form, 'title': 'Create Announcement'})


@admin_required
def announcement_edit(request, pk):
    """Edit announcement - Admin only."""
    obj = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated.')
            return redirect('core:announcement_list')
    else:
        form = AnnouncementForm(instance=obj)
    return render(request, 'core/announcement_form.html', {'form': form, 'title': 'Edit Announcement'})


@admin_required
def announcement_delete(request, pk):
    """Delete announcement - Admin only."""
    obj = get_object_or_404(Announcement, pk=pk)
    obj.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('core:announcement_list')


@login_required
def event_list(request):
    """List events. Admin sees all with manage options."""
    if request.user.role == Role.ADMIN:
        events = Event.objects.all().order_by('event_date')
    else:
        events = Event.objects.filter(is_active=True, event_date__gte=timezone.now().date()).order_by('event_date')
    return render(request, 'core/events.html', {'events': events})


@admin_required
def event_create(request):
    """Create event - Admin only."""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event created.')
            return redirect('core:event_list')
    else:
        form = EventForm()
    return render(request, 'core/event_form.html', {'form': form, 'title': 'Create Event'})


@admin_required
def event_edit(request, pk):
    """Edit event - Admin only."""
    obj = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated.')
            return redirect('core:event_list')
    else:
        form = EventForm(instance=obj)
    return render(request, 'core/event_form.html', {'form': form, 'title': 'Edit Event'})


@admin_required
def event_delete(request, pk):
    """Delete event - Admin only."""
    obj = get_object_or_404(Event, pk=pk)
    obj.delete()
    messages.success(request, 'Event deleted.')
    return redirect('core:event_list')


@login_required
def message_inbox(request):
    """Inbox - received messages."""
    messages = Message.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, 'core/messages_inbox.html', {'messages': messages})


@login_required
def message_sent(request):
    """Sent messages."""
    messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
    return render(request, 'core/messages_sent.html', {'messages': messages})


@login_required
def message_compose(request):
    """Compose new message."""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        if recipient_id and subject:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.filter(id=recipient_id).first()
            if recipient:
                Message.objects.create(sender=request.user, recipient=recipient, subject=subject, body=body)
                return redirect('core:message_inbox')
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.exclude(id=request.user.id)
    try:
        preselected = int(request.GET.get('to', 0)) or None
    except (ValueError, TypeError):
        preselected = None
    return render(request, 'core/message_compose.html', {'users': users, 'preselected': preselected})


@login_required
def message_detail(request, pk):
    """View message and mark as read."""
    message = get_object_or_404(Message, pk=pk)
    if message.recipient != request.user and message.sender != request.user:
        return redirect('core:message_inbox')
    if message.recipient == request.user:
        message.mark_as_read()
    return render(request, 'core/message_detail.html', {'message': message})


# Document generation - Bonafide, Admit Card, Grade Report
@login_required
def document_bonafide(request):
    """Generate Bonafide certificate PDF."""
    profile = getattr(request.user, 'student_profile', None)
    if not profile or request.user.role != Role.STUDENT:
        return HttpResponse('Unauthorized', status=403)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 700, "BONAFIDE CERTIFICATE")
    p.drawString(100, 650, f"This is to certify that {request.user.get_full_name()} is a bonafide student of this")
    p.drawString(100, 630, f"institution with Enrollment Number: {profile.enrollment_number}")
    p.drawString(100, 610, f"Department: {profile.department.name if profile.department else 'N/A'}")
    p.drawString(100, 590, f"Date: {timezone.now().strftime('%Y-%m-%d')}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='bonafide.pdf')


@login_required
def document_grade_report(request):
    """Generate grade report PDF."""
    if request.user.role != Role.STUDENT:
        return HttpResponse('Unauthorized', status=403)
    profile = getattr(request.user, 'student_profile', None)
    results = SemesterResult.objects.filter(student=request.user).order_by('-semester__start_date')
    grades = Grade.objects.filter(student=request.user).select_related('semester_course__course', 'grade_point')
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "GRADE REPORT")
    p.drawString(100, 720, f"Student: {request.user.get_full_name()}")
    p.drawString(100, 700, f"Enrollment: {profile.enrollment_number if profile else 'N/A'}")
    y = 660
    for r in results:
        p.drawString(100, y, f"{r.semester.name}: GPA {r.gpa} - {r.classification}")
        y -= 20
    y -= 20
    p.drawString(100, y, "Course-wise Grades:")
    y -= 20
    for g in grades[:15]:
        p.drawString(100, y, f"  {g.semester_course.course.code}: {g.grade_point.grade} ({g.grade_point.point})")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='grade_report.pdf')


@login_required
def document_admit_card(request):
    """Generate admit card PDF."""
    profile = getattr(request.user, 'student_profile', None)
    if not profile or request.user.role != Role.STUDENT:
        return HttpResponse('Unauthorized', status=403)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "ADMIT CARD")
    p.drawString(100, 720, f"Name: {request.user.get_full_name()}")
    p.drawString(100, 700, f"Enrollment: {profile.enrollment_number}")
    p.drawString(100, 680, f"Department: {profile.department.name if profile.department else 'N/A'}")
    p.drawString(100, 660, f"Valid for: Semester Examinations")
    p.drawString(100, 640, f"Date: {timezone.now().strftime('%Y-%m-%d')}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='admit_card.pdf')


# AI Chatbot (basic rule-based)
@login_required
def ai_chatbot(request):
    """Basic rule-based chatbot."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.POST.get('query', '').lower().strip()
        response = _chatbot_response(request.user, query)
        from django.http import JsonResponse
        return JsonResponse({'response': response})
    return render(request, 'core/chatbot.html')


def _chatbot_response(user, query):
    """Rule-based response for common queries."""
    if 'attendance' in query or 'attend' in query:
        from apps.academics.models import Enrollment
        from apps.attendance.models import QRSession, AttendanceRecord
        enrollments = Enrollment.objects.filter(student=user)
        total, present = 0, 0
        for e in enrollments:
            for s in QRSession.objects.filter(semester_course=e.semester_course):
                total += 1
                if AttendanceRecord.objects.filter(qr_session=s, student=user).exists():
                    present += 1
        pct = (present / total * 100) if total else 0
        return f"Your attendance is {present}/{total} sessions ({pct:.1f}%)."
    if 'gpa' in query or 'grade' in query or 'result' in query:
        results = SemesterResult.objects.filter(student=user).order_by('-semester__start_date')
        if results:
            total_p = sum(r.gpa * r.total_credits for r in results)
            total_c = sum(r.total_credits for r in results)
            cgpa = total_p / total_c if total_c else 0
            return f"Your CGPA is {cgpa:.2f}. Latest semester: {results[0].semester.name} - GPA {results[0].gpa}"
        return "No results found yet."
    if 'assignment' in query or 'assign' in query:
        from apps.assignments.models import Assignment, Submission
        from apps.academics.models import Enrollment
        enrollments = Enrollment.objects.filter(student=user)
        assignments = Assignment.objects.filter(semester_course__in=[e.semester_course for e in enrollments])
        pending = 0
        for a in assignments:
            if not Submission.objects.filter(assignment=a, student=user).exists() and not a.is_past_deadline:
                pending += 1
        return f"You have {pending} pending assignment(s)."
    if 'hello' in query or 'hi' in query:
        return f"Hello {user.get_full_name() or user.username}! How can I help you?"
    return "I can help with: attendance, GPA/grades, assignments. Ask me anything!"
