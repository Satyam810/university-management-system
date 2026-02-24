"""Academics views - course management, enrollment."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Semester, Course, SemesterCourse, GradePointMapping, StudentProfile, FacultyProfile, Enrollment
from apps.accounts.models import Role
from apps.core.decorators import admin_required, faculty_required


@login_required
def academics_home(request):
    if request.user.role == Role.ADMIN:
        return redirect('academics:department_list')
    return redirect('core:home')


@admin_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'academics/department_list.html', {'departments': departments})


@admin_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'academics/course_list.html', {'courses': courses})


@login_required
def semester_list(request):
    semesters = Semester.objects.all()
    return render(request, 'academics/semester_list.html', {'semesters': semesters})


@login_required
def semester_course_list(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    courses = SemesterCourse.objects.filter(semester=semester).select_related('course', 'faculty')
    return render(request, 'academics/semester_course_list.html', {'semester': semester, 'courses': courses})


@faculty_required
def faculty_my_students(request):
    """Faculty: List of students enrolled in their courses."""
    courses = SemesterCourse.objects.filter(faculty=request.user)
    enrollments = Enrollment.objects.filter(semester_course__in=courses).select_related('student', 'semester_course__course', 'semester_course__semester')
    students_by_course = {}
    for e in enrollments:
        key = e.semester_course
        if key not in students_by_course:
            students_by_course[key] = []
        profile = getattr(e.student, 'student_profile', None)
        students_by_course[key].append({
            'student': e.student,
            'enrollment': profile.enrollment_number if profile else '-'
        })
    return render(request, 'academics/faculty_my_students.html', {'students_by_course': students_by_course})
