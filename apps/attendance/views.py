"""Attendance views - QR generation, scan, and management."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import timedelta
import csv

from .models import QRSession, AttendanceRecord
from .utils import generate_qr_code
from apps.academics.models import SemesterCourse, Enrollment
from apps.accounts.models import Role
from apps.accounts.mixins import FacultyRequiredMixin
from apps.core.decorators import faculty_required, student_required


@login_required
def attendance_home(request):
    """Redirect based on role."""
    if request.user.role == Role.FACULTY:
        return redirect('attendance:faculty_dashboard')
    elif request.user.role == Role.STUDENT:
        return redirect('attendance:student_view')
    return redirect('core:home')


@faculty_required
def faculty_dashboard(request):
    """Faculty attendance dashboard."""
    faculty_courses = SemesterCourse.objects.filter(faculty=request.user)
    recent_sessions = QRSession.objects.filter(created_by=request.user)[:10]
    return render(request, 'attendance/faculty_dashboard.html', {
        'faculty_courses': faculty_courses,
        'recent_sessions': recent_sessions,
    })


@faculty_required
def generate_qr(request, semester_course_id):
    """Generate QR code for a class."""
    semester_course = get_object_or_404(SemesterCourse, id=semester_course_id, faculty=request.user)
    validity_minutes = 3  # 2-5 minutes as per spec
    valid_until = timezone.now() + timedelta(minutes=validity_minutes)

    qr_session = QRSession.objects.create(
        semester_course=semester_course,
        created_by=request.user,
        valid_until=valid_until,
    )
    qr_base64 = generate_qr_code(str(qr_session.session_id), valid_until.isoformat())

    return render(request, 'attendance/qr_display.html', {
        'qr_session': qr_session,
        'qr_base64': qr_base64,
        'valid_until': valid_until,
    })


@require_http_methods(["POST"])
@student_required
def scan_qr(request):
    """Student scans QR to mark attendance. Returns JSON."""
    raw = request.POST.get('session_id', '').strip()
    # Parse "UMS_ATTENDANCE:uuid:timestamp" or use raw as session_id
    if raw.startswith('UMS_ATTENDANCE:'):
        parts = raw.split(':')
        session_id = parts[1] if len(parts) > 1 else raw
    else:
        session_id = raw
    if not session_id:
        return JsonResponse({'success': False, 'message': 'Invalid session'}, status=400)

    qr_session = QRSession.objects.filter(session_id=session_id).first()
    if not qr_session:
        return JsonResponse({'success': False, 'message': 'Invalid or expired QR code'}, status=400)

    if not qr_session.is_valid:
        return JsonResponse({'success': False, 'message': 'QR code has expired'}, status=400)

    # Check enrollment
    enrollment = Enrollment.objects.filter(
        student=request.user,
        semester_course=qr_session.semester_course
    ).exists()
    if not enrollment:
        return JsonResponse({'success': False, 'message': 'You are not enrolled in this course'}, status=403)

    # Prevent duplicate
    existing = AttendanceRecord.objects.filter(qr_session=qr_session, student=request.user).first()
    if existing:
        return JsonResponse({'success': False, 'message': 'Attendance already marked'}, status=400)

    # Mark as late if past half of validity window
    session_start = qr_session.created_at
    half_window = session_start + (qr_session.valid_until - session_start) / 2
    is_late = timezone.now() > half_window

    AttendanceRecord.objects.create(
        qr_session=qr_session,
        student=request.user,
        status='LATE' if is_late else 'PRESENT',
        is_late=is_late,
    )
    return JsonResponse({'success': True, 'message': 'Attendance marked successfully'})


@faculty_required
def session_records(request, session_id):
    """View attendance records for a QR session."""
    qr_session = get_object_or_404(QRSession, session_id=session_id, created_by=request.user)
    records = qr_session.records.select_related('student').all()
    return render(request, 'attendance/session_records.html', {
        'qr_session': qr_session,
        'records': records,
    })


@faculty_required
def download_attendance_csv(request, session_id):
    """Download attendance as CSV."""
    qr_session = get_object_or_404(QRSession, session_id=session_id, created_by=request.user)
    records = qr_session.records.select_related('student').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{qr_session.semester_course.course.code}_{qr_session.created_at:%Y%m%d}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student', 'Enrollment', 'Status', 'Marked At'])
    for r in records:
        profile = getattr(r.student, 'student_profile', None)
        enrollment = profile.enrollment_number if profile else '-'
        writer.writerow([r.student.get_full_name(), enrollment, r.status, r.marked_at])

    return response


@student_required
def student_view(request):
    """Student attendance view - scan QR and see own attendance."""
    from apps.academics.models import StudentProfile, Enrollment
    profile = getattr(request.user, 'student_profile', None)
    enrollments = Enrollment.objects.filter(student=request.user).select_related('semester_course__course', 'semester_course__semester')
    return render(request, 'attendance/student_view.html', {
        'enrollments': enrollments,
    })
