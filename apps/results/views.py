"""Results views - GPA, grades, analytics."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal

from .models import Grade, SemesterResult
from apps.academics.models import SemesterCourse, GradePointMapping, Enrollment
from apps.accounts.models import Role
from apps.core.decorators import faculty_required, student_required, admin_or_faculty_required


@login_required
def results_home(request):
    if request.user.role == Role.STUDENT:
        return redirect('results:student_results')
    elif request.user.role == Role.FACULTY:
        return redirect('results:faculty_courses')
    return redirect('core:home')


@student_required
def student_results(request):
    """Student view - GPA graph, grades, performance."""
    results = SemesterResult.objects.filter(student=request.user).order_by('-semester__start_date')
    grades = Grade.objects.filter(student=request.user).select_related('semester_course__course', 'grade_point')
    # Calculate CGPA
    total_points = sum(r.gpa * r.total_credits for r in results)
    total_credits = sum(r.total_credits for r in results)
    cgpa = (total_points / total_credits) if total_credits else Decimal('0.00')
    return render(request, 'results/student_results.html', {
        'results': results,
        'grades': grades,
        'cgpa': round(cgpa, 2),
    })


@faculty_required
def faculty_courses(request):
    """Faculty - list courses to upload results."""
    courses = SemesterCourse.objects.filter(faculty=request.user)
    return render(request, 'results/faculty_courses.html', {'courses': courses})


@faculty_required
def upload_grades(request, semester_course_id):
    """Faculty uploads grades for a course."""
    semester_course = get_object_or_404(SemesterCourse, id=semester_course_id, faculty=request.user)
    enrollments = Enrollment.objects.filter(semester_course=semester_course).select_related('student')
    grade_mappings = GradePointMapping.objects.all()

    if request.method == 'POST':
        for enrollment in enrollments:
            grade_key = f"grade_{enrollment.student.id}"
            grade_id = request.POST.get(grade_key)
            if grade_id:
                grade_mapping = GradePointMapping.objects.filter(id=grade_id).first()
                if grade_mapping:
                    Grade.objects.update_or_create(
                        student=enrollment.student,
                        semester_course=semester_course,
                        defaults={'grade_point': grade_mapping, 'created_by': request.user}
                    )
        return redirect('results:course_grades', semester_course_id=semester_course_id)

    return render(request, 'results/upload_grades.html', {
        'semester_course': semester_course,
        'enrollments': enrollments,
        'grade_mappings': grade_mappings,
    })


@faculty_required
def course_grades(request, semester_course_id):
    """View grades for a course."""
    semester_course = get_object_or_404(SemesterCourse, id=semester_course_id, faculty=request.user)
    grades = Grade.objects.filter(semester_course=semester_course).select_related('student', 'grade_point')
    return render(request, 'results/course_grades.html', {
        'semester_course': semester_course,
        'grades': grades,
    })
