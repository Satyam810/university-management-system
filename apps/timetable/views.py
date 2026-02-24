"""Timetable views."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TimetableEntry, Slot
from apps.academics.models import Enrollment, SemesterCourse
from apps.accounts.models import Role


@login_required
def timetable_view(request):
    """View timetable based on role."""
    if request.user.role == Role.STUDENT:
        enrollments = Enrollment.objects.filter(student=request.user).select_related('semester_course__course', 'semester_course__semester')
        semester_courses = [e.semester_course for e in enrollments]
    elif request.user.role == Role.FACULTY:
        semester_courses = list(SemesterCourse.objects.filter(faculty=request.user))
    else:
        semester_courses = []

    entries = TimetableEntry.objects.filter(
        semester_course__in=semester_courses
    ).select_related('slot', 'classroom', 'semester_course__course', 'semester_course__faculty')

    return render(request, 'timetable/view.html', {'entries': entries})


@login_required
def timetable_admin(request):
    """Admin timetable management - conflict detection."""
    entries = TimetableEntry.objects.select_related('slot', 'classroom', 'semester_course__course', 'semester_course__faculty').all()
    # Check for conflicts
    conflicts = []
    seen = {}
    for e in entries:
        key = (e.slot.id, e.classroom_id)
        if key in seen and e.classroom_id:
            conflicts.append(f"Room {e.classroom} double-booked at {e.slot}")
        seen[key] = e
    return render(request, 'timetable/admin.html', {'entries': entries, 'conflicts': conflicts})
