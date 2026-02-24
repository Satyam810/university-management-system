"""Analytics dashboard views with Chart.js data."""
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import User, Role
from apps.academics.models import Department, Course, Semester, StudentProfile, FacultyProfile
from apps.attendance.models import AttendanceRecord, QRSession
from apps.results.models import Grade, SemesterResult
from apps.core.decorators import admin_required, faculty_required, student_required


@login_required
def analytics_home(request):
    """Redirect based on role."""
    if request.user.role == Role.ADMIN:
        return redirect('analytics:admin_dashboard')
    elif request.user.role == Role.FACULTY:
        return redirect('analytics:faculty_dashboard')
    elif request.user.role == Role.STUDENT:
        return redirect('analytics:student_dashboard')
    return redirect('core:home')


@admin_required
def admin_dashboard(request):
    """Admin analytics: KPIs, charts, attendance heatmap, pass/fail."""
    students = User.objects.filter(role=Role.STUDENT)
    faculty = User.objects.filter(role=Role.FACULTY)
    departments = Department.objects.annotate(student_count=Count('students')).values('name', 'student_count')
    courses = Course.objects.count()

    # Attendance heatmap data (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    attendance_by_day = AttendanceRecord.objects.filter(
        marked_at__gte=week_ago
    ).extra(select={'day': 'date(marked_at)'}).values('day').annotate(count=Count('id'))

    # Pass/Fail ratio
    grades = Grade.objects.select_related('grade_point')
    pass_count = grades.exclude(grade_point__grade='F').count()
    fail_count = grades.filter(grade_point__grade='F').count()

    # Enrollment growth (simplified - by semester)
    semesters = Semester.objects.all()[:6]
    enrollment_data = []
    for s in semesters:
        from apps.academics.models import Enrollment
        count = Enrollment.objects.filter(semester_course__semester=s).values('student').distinct().count()
        enrollment_data.append({'name': s.name, 'count': count})

    return render(request, 'analytics/admin_dashboard.html', {
        'total_students': students.count(),
        'total_faculty': faculty.count(),
        'total_courses': courses,
        'department_data': json.dumps(list(departments)),
        'attendance_by_day': list(attendance_by_day),
        'pass_count': pass_count,
        'fail_count': fail_count,
        'enrollment_data': json.dumps(enrollment_data),
    })


@faculty_required
def faculty_dashboard(request):
    """Faculty: class performance, attendance chart, student ranking."""
    from apps.academics.models import SemesterCourse, Enrollment
    courses = SemesterCourse.objects.filter(faculty=request.user)
    course_ids = [c.id for c in courses]

    # Class performance (grades per course)
    from apps.academics.models import SemesterCourse as SC
    perf_data = []
    for sc in courses:
        avg = Grade.objects.filter(semester_course=sc).aggregate(avg=Avg('grade_point__point'))['avg']
        perf_data.append({'course': sc.course.code, 'avg': float(avg or 0)})

    # Attendance for my sessions
    sessions = QRSession.objects.filter(created_by=request.user)
    att_data = []
    for s in sessions[:10]:
        count = s.records.count()
        att_data.append({'session': str(s.created_at)[:10], 'count': count})

    # Student ranking - students enrolled in our courses
    from apps.academics.models import Enrollment
    from apps.results.models import SemesterResult
    enrolled_students = User.objects.filter(
        enrollments__semester_course__in=courses
    ).distinct()
    rankings = SemesterResult.objects.filter(
        student__in=enrolled_students
    ).select_related('student').order_by('-gpa')[:10]

    total_sessions = sessions.count()
    total_students = enrolled_students.count()
    return render(request, 'analytics/faculty_dashboard.html', {
        'perf_data': perf_data,
        'att_data': att_data,
        'rankings': list(rankings),
        'total_courses': courses.count(),
        'total_sessions': total_sessions,
        'total_students': total_students,
    })


@student_required
def student_dashboard(request):
    """Student: GPA graph, attendance graph, performance trend."""
    results = SemesterResult.objects.filter(student=request.user).order_by('semester__start_date')
    gpa_data = [{'semester': r.semester.name, 'gpa': float(r.gpa)} for r in results]

    # Attendance percentage
    from apps.academics.models import Enrollment
    enrollments = Enrollment.objects.filter(student=request.user)
    total_sessions = 0
    present_count = 0
    for e in enrollments:
        sessions = QRSession.objects.filter(semester_course=e.semester_course)
        for s in sessions:
            total_sessions += 1
            if AttendanceRecord.objects.filter(qr_session=s, student=request.user).exists():
                present_count += 1
    att_pct = (present_count / total_sessions * 100) if total_sessions else 0

    return render(request, 'analytics/student_dashboard.html', {
        'gpa_data': json.dumps(gpa_data),
        'attendance_pct': round(att_pct, 1),
        'results': results,
    })
